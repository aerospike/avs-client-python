import time
import logging
import threading
import asyncio
from typing import Optional, Union, Any, Dict

import jwt
import grpc

from . import helpers
from .proto_generated import auth_pb2, auth_pb2_grpc, types_pb2
from .. import types

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manages authentication token lifecycle including acquisition, renewal, and validation.
    Handles clock skew between client and server.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ttl_threshold: float = 0.9,  # Renew when 90% of TTL has elapsed
    ) -> None:
        logger.debug(
            "Initializing TokenManager (username=%s, ttl_threshold=%.2f)",
            username, ttl_threshold
        )
        self._credentials = helpers._get_credentials(username, password) if username and password else None
        self._token: Optional[str] = None
        self._token_credentials: Optional[grpc.CallCredentials] = None
        self._ttl: int = 0
        self._ttl_start: int = 0
        self._ttl_threshold: float = ttl_threshold
        self._auth_timer: Optional[Union[threading.Timer, asyncio.Task]] = None
        
        # Split locks for sync and async operations
        self._sync_auth_lock: threading.Lock = threading.Lock()
        self._async_auth_lock: Optional[asyncio.Lock] = None

        self._is_async: bool = False
        logger.debug("TokenManager initialized with credentials: %s", "present" if self._credentials else "none")

    def configure_async(self, lock: asyncio.Lock) -> None:
        """Configure the token manager for async operation"""
        logger.debug("Configuring TokenManager for async operation")
        self._is_async = True
        self._async_auth_lock = lock

    def has_credentials(self) -> bool:
        """Check if credentials are available"""
        has_creds = self._credentials is not None
        logger.debug("Checking credentials availability: %s", has_creds)
        return has_creds

    def get_token_credentials(self) -> Optional[grpc.CallCredentials]:
        """Get the current token credentials for gRPC calls"""
        credentials = self._token_credentials
        logger.debug("Getting token credentials: %s", "present" if credentials else "none")
        return credentials

    def _decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token and handle potential clock skew"""
        logger.debug("Decoding JWT token")
        
        # Decode without verification to get TTL info
        payload = jwt.decode(
            token, "", algorithms=["RS256"], options={"verify_signature": False}
        )
        logger.debug("Token payload decoded: exp=%s, iat=%s", payload["exp"], payload["iat"])
        
        # Store token issue time using client's current time
        current_time = int(time.time())
        server_iat = payload["iat"]
        
        # Log significant clock skew for diagnostic purposes
        clock_skew = server_iat - current_time
        logger.debug("Current time: %d, Server IAT: %d, Clock skew: %d seconds", 
                    current_time, server_iat, clock_skew)
        
        if abs(clock_skew) > 15:  # log if skew is greater than 15 seconds
            logger.warning(
                "Detected significant clock skew of %d seconds between client and server",
                clock_skew
            )
        
        # Always use client's current time as reference
        self._ttl_start = current_time
            
        # Calculate TTL
        self._ttl = payload["exp"] - payload["iat"]
        logger.debug("Token TTL calculated: %d seconds", self._ttl)
        
        return payload

    def _update_token(self, token: str) -> None:
        """Update the token and related state"""
        logger.debug("Updating token and related state")
        self._token = token
        self._decode_token(token)
        self._token_credentials = grpc.access_token_call_credentials(token)
        logger.debug("Token updated successfully, TTL: %d seconds, TTL start: %d", 
                    self._ttl, self._ttl_start)

    def _get_next_refresh_time(self) -> float:
        """Calculate when the token should be refreshed next"""
        # Calculate refresh time based on TTL threshold
        refresh_time = self._ttl * self._ttl_threshold
        
        # Calculate time elapsed since token was issued
        current_time = int(time.time())
        elapsed = current_time - self._ttl_start

        if self._ttl < elapsed:
            logger.warning("Token has expired, refresh over is overdue by %d seconds", elapsed - self._ttl)

        # Adjust refresh time based on elapsed time
        # If the token has expired, we need to refresh it immediately
        # But avoid passing a negative refresh time to the timer
        adjusted_refresh_time = max(0, refresh_time - elapsed)
        
        logger.debug(
            "Calculated next refresh time: TTL=%d, threshold=%.2f, elapsed=%d, adjusted_refresh_time=%.2f",
            self._ttl, self._ttl_threshold, elapsed, adjusted_refresh_time
        )
        
        return adjusted_refresh_time

    def _get_auth_request(self) -> auth_pb2.AuthRequest:
        """Create an authentication request"""
        logger.debug("Creating authentication request")
        return auth_pb2.AuthRequest(credentials=self._credentials)

    # Synchronous methods
    def refresh_token(self, auth_stub: auth_pb2_grpc.AuthServiceStub) -> None:
        """Refresh the authentication token synchronously"""
        if not self._credentials:
            logger.debug("Skipping token refresh - no credentials available")
            return

        logger.debug("Starting synchronous token refresh")
        auth_request = self._get_auth_request()

        try:
            logger.debug("Sending authentication request to server")
            response = auth_stub.Authenticate(auth_request)
            logger.debug("Received authentication response from server")
            self._update_token(response.token)
            self._schedule_token_refresh(auth_stub)
        except grpc.RpcError as e:
            logger.error("Failed to refresh authentication token with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def _schedule_token_refresh(self, auth_stub: auth_pb2_grpc.AuthServiceStub) -> None:
        """Schedule the next token refresh"""
        if not self._is_async:
            logger.debug("Scheduling next synchronous token refresh")
            with self._sync_auth_lock:
                if self._auth_timer:
                    logger.debug("Cancelling existing refresh timer")
                    self._auth_timer.cancel()
                refresh_time = self._get_next_refresh_time()
                logger.debug("Creating new refresh timer for %.2f seconds", refresh_time)
                self._auth_timer = threading.Timer(
                    refresh_time, 
                    self.refresh_token,
                    args=[auth_stub]
                )
                self._auth_timer.daemon = True
                self._auth_timer.start()
                logger.debug("Token refresh timer started")

    # Asynchronous methods
    async def refresh_token_async(self, auth_stub: auth_pb2_grpc.AuthServiceStub) -> None:
        """Refresh the authentication token asynchronously"""
        if not self._credentials:
            logger.debug("Skipping async token refresh - no credentials available")
            return

        logger.debug("Starting asynchronous token refresh")
        auth_request = self._get_auth_request()

        try:
            logger.debug("Sending async authentication request to server")
            response = await auth_stub.Authenticate(auth_request)
            logger.debug("Received async authentication response from server")
            self._update_token(response.token)
            await self._schedule_token_refresh_async(auth_stub)
        except grpc.RpcError as e:
            logger.error("Failed to refresh authentication token asynchronously with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    async def _schedule_token_refresh_async(self, auth_stub: auth_pb2_grpc.AuthServiceStub) -> None:
        """Schedule the next token refresh asynchronously"""
        if self._is_async and self._async_auth_lock is not None:
            logger.debug("Scheduling next asynchronous token refresh")
            async with self._async_auth_lock:
                if isinstance(self._auth_timer, asyncio.Task) and not self._auth_timer.done():
                    logger.debug("Cancelling existing async refresh task")
                    self._auth_timer.cancel()
                refresh_time = self._get_next_refresh_time()
                logger.debug("Creating new async refresh task for %.2f seconds", refresh_time)
                self._auth_timer = asyncio.create_task(
                    self._wait_and_refresh(refresh_time, auth_stub)
                )
                logger.debug("Async token refresh task created")
        else:
            logger.error("Cannot schedule async refresh: not in async mode or async lock not configured")
            raise types.AVSClientError(message=f"Async lock not configured: is_async={self._is_async}, async_lock={self._async_auth_lock}")

    async def _wait_and_refresh(self, wait_time: float, auth_stub: auth_pb2_grpc.AuthServiceStub) -> None:
        """Wait for the specified time and then refresh the token"""
        logger.debug("Waiting %.2f seconds before refreshing token", wait_time)
        await asyncio.sleep(wait_time)
        logger.debug("Wait complete, starting token refresh")
        await self.refresh_token_async(auth_stub)

    def cancel_refresh(self) -> None:
        """Cancel any scheduled token refresh synchronously"""
        logger.debug("Cancelling scheduled token refresh")

        if self._is_async:
            logger.error("Attempting to synchronously cancel refresh in async mode. "
                         "Use async method instead.")
            raise TypeError("Attempting to synchronously cancel refresh in async mode. "
                            "Use async method instead.")
        
        # Synchronous cancellation
        with self._sync_auth_lock:
            if self._auth_timer is None:
                logger.debug("No sync refresh timer to cancel")
                return
            
            logger.debug("Cancelling synchronous refresh timer")
            self._auth_timer.cancel()
            self._auth_timer = None
            logger.debug("Synchronous token refresh cancelled")

    async def cancel_refresh_async(self) -> None:
        """Cancel any scheduled token refresh asynchronously"""
        logger.debug("Cancelling scheduled async token refresh")
        
        if not self._is_async:
            logger.error("Attempting to asynchronously cancel refresh in sync mode. "
                         "Use sync method instead.")
            raise TypeError("Attempting to asynchronously cancel refresh in sync mode. "
                            "Use sync method instead.")
        
        if self._async_auth_lock is None:
            logger.error("Async lock not configured")
            raise TypeError("Async lock not configured")
        
        # Asynchronous cancellation
        async with self._async_auth_lock:
            if self._auth_timer is None:
                logger.debug("No async refresh task to cancel")
                return
            
            if isinstance(self._auth_timer, asyncio.Task) and not self._auth_timer.done():
                logger.debug("Cancelling asynchronous refresh task")
                self._auth_timer.cancel()
                # previous self._auth_timer is None check ensures this is not None
                # ignore linter type check error
                await self._auth_timer() # type: ignore
                self._auth_timer = None
