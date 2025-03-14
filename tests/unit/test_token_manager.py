import time
import asyncio
import threading
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import jwt
import grpc

from aerospike_vector_search.shared.token_manager import TokenManager
from aerospike_vector_search import types


class TestTokenManager:
    """Test suite for the TokenManager class"""

    @pytest.fixture
    def mock_auth_stub(self):
        """Create a mock auth stub for testing"""
        stub = Mock()
        stub.Authenticate = Mock()
        stub.Authenticate.return_value = Mock(token="test_token")
        return stub

    @pytest.fixture
    def mock_async_auth_stub(self):
        """Create a mock async auth stub for testing"""
        stub = AsyncMock()
        stub.Authenticate = AsyncMock()
        stub.Authenticate.return_value = Mock(token="test_token")
        return stub

    @pytest.fixture
    def mock_jwt_decode(self):
        """Mock the JWT decode function"""
        with patch('jwt.decode') as mock_decode:
            current_time = int(time.time())
            mock_decode.return_value = {
                'exp': current_time + 3600,  # 1 hour expiration
                'iat': current_time - 10,    # Issued 10 seconds ago
            }
            yield mock_decode

    def test_init(self):
        """Test TokenManager initialization"""
        # Test with credentials
        manager = TokenManager(username="test_user", password="test_pass")
        assert manager.has_credentials() is True
        assert manager._is_async is False

        # Test without credentials
        manager = TokenManager()
        assert manager.has_credentials() is False

    async def test_configure_async(self):
        """Test configuring TokenManager for async operation"""
        manager = TokenManager(username="test_user", password="test_pass")
        assert manager._is_async is False

        # Configure for async
        mock_lock = asyncio.Lock()
        manager.configure_async(mock_lock)
        assert manager._is_async is True
        assert manager._auth_lock is mock_lock

    def test_has_credentials(self):
        """Test has_credentials method"""
        # With credentials
        manager = TokenManager(username="test_user", password="test_pass")
        assert manager.has_credentials() is True

        # Without credentials
        manager = TokenManager()
        assert manager.has_credentials() is False

    def test_get_token_credentials(self):
        """Test get_token_credentials method"""
        manager = TokenManager(username="test_user", password="test_pass")
        # Initially no token credentials
        assert manager.get_token_credentials() is None

        # Set token credentials
        mock_credentials = Mock(spec=grpc.CallCredentials)
        manager._token_credentials = mock_credentials
        assert manager.get_token_credentials() is mock_credentials

    @patch('time.time')
    def test_decode_token(self, mock_time, mock_jwt_decode):
        """Test _decode_token method"""
        manager = TokenManager(username="test_user", password="test_pass")
        
        # Mock current time
        current_time = 1600000000
        mock_time.return_value = current_time
        
        # Test with normal token
        payload = manager._decode_token("test_token")
        
        # Verify JWT decode was called
        mock_jwt_decode.assert_called_once_with(
            "test_token", "", algorithms=["RS256"], options={"verify_signature": False}
        )
        
        # Verify TTL calculation
        assert manager._ttl == 3610  # exp - iat = (current_time + 3600) - (current_time - 10)
        assert manager._ttl_start == current_time

    @patch('time.time')
    def test_decode_token_with_clock_skew(self, mock_time, mock_jwt_decode):
        """Test _decode_token method with significant clock skew"""
        manager = TokenManager(username="test_user", password="test_pass")
        
        # Mock current time
        current_time = 1600000000
        mock_time.return_value = current_time
        
        # Set up significant clock skew (server ahead by 30 seconds)
        mock_jwt_decode.return_value = {
            'exp': current_time + 3600,
            'iat': current_time + 30,  # Server time is ahead
        }
        
        # Test with token having clock skew
        with patch('logging.Logger.warning') as mock_warning:
            payload = manager._decode_token("test_token")
            # Verify warning was logged
            mock_warning.assert_called_once()
        
        # Verify TTL calculation
        assert manager._ttl == 3570  # exp - iat = (current_time + 3600) - (current_time + 30)
        assert manager._ttl_start == current_time  # Should use client time

    @patch('grpc.access_token_call_credentials')
    def test_update_token(self, mock_credentials, mock_jwt_decode):
        """Test _update_token method"""
        manager = TokenManager(username="test_user", password="test_pass")
        
        # Mock credentials
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds
        
        # Test token update
        manager._update_token("test_token")
        
        # Verify token was updated
        assert manager._token == "test_token"
        assert manager._token_credentials == mock_creds
        mock_credentials.assert_called_once_with("test_token")

    @patch('time.time')
    def test_get_next_refresh_time(self, mock_time):
        """Test _get_next_refresh_time method"""
        manager = TokenManager(username="test_user", password="test_pass", ttl_threshold=0.8)
        
        # Set up TTL and start time
        manager._ttl = 3600  # 1 hour
        manager._ttl_start = 1600000000
        
        # Test with no elapsed time
        mock_time.return_value = 1600000000
        refresh_time = manager._get_next_refresh_time()
        assert refresh_time == 3600 * 0.8  # 80% of TTL
        
        # Test with some elapsed time
        mock_time.return_value = 1600000000 + 1000  # 1000 seconds elapsed
        refresh_time = manager._get_next_refresh_time()
        assert refresh_time == (3600 * 0.8) - 1000  # 80% of TTL minus elapsed time
        
        # Test with elapsed time exceeding threshold
        mock_time.return_value = 1600000000 + 3000  # 3000 seconds elapsed
        refresh_time = manager._get_next_refresh_time()
        assert refresh_time == 0.1  # Minimum refresh time

    def test_refresh_token(self, mock_auth_stub, mock_jwt_decode):
        """Test refresh_token method"""
        manager = TokenManager(username="test_user", password="test_pass")
        
        # Test refresh token
        with patch.object(manager, '_schedule_token_refresh') as mock_schedule:
            manager.refresh_token(mock_auth_stub)
            
            # Verify auth request was made
            mock_auth_stub.Authenticate.assert_called_once()
            
            # Verify token was updated
            assert manager._token == "test_token"
            
            # Verify refresh was scheduled
            mock_schedule.assert_called_once_with(mock_auth_stub)

    def test_refresh_token_no_credentials(self, mock_auth_stub):
        """Test refresh_token method with no credentials"""
        manager = TokenManager()  # No credentials
        
        # Test refresh token
        manager.refresh_token(mock_auth_stub)
        
        # Verify no auth request was made
        mock_auth_stub.Authenticate.assert_not_called()

    def test_refresh_token_error(self, mock_auth_stub):
        """Test refresh_token method with error"""
        manager = TokenManager(username="test_user", password="test_pass")
        
        # Set up error
        mock_auth_stub.Authenticate.side_effect = grpc.RpcError()
        
        # Test refresh token with error
        with pytest.raises(types.AVSServerError):
            manager.refresh_token(mock_auth_stub)

    def test_schedule_token_refresh(self, mock_auth_stub):
        """Test _schedule_token_refresh method"""
        manager = TokenManager(username="test_user", password="test_pass")
        
        # Mock timer
        with patch('threading.Timer') as mock_timer:
            mock_timer_instance = Mock()
            mock_timer.return_value = mock_timer_instance
            
            # Test schedule refresh
            with patch.object(manager, '_get_next_refresh_time', return_value=1800):
                manager._schedule_token_refresh(mock_auth_stub)
                
                # Verify timer was created
                mock_timer.assert_called_once_with(
                    1800, manager.refresh_token, args=[mock_auth_stub]
                )
                
                # Verify timer was started
                mock_timer_instance.start.assert_called_once()
                
                # Verify timer is daemon
                assert mock_timer_instance.daemon is True

    def test_schedule_token_refresh_cancel_existing(self, mock_auth_stub):
        """Test _schedule_token_refresh method with existing timer"""
        manager = TokenManager(username="test_user", password="test_pass")
        
        # Set up existing timer
        existing_timer = Mock()
        manager._auth_timer = existing_timer
        
        # Mock new timer
        with patch('threading.Timer') as mock_timer:
            mock_timer_instance = Mock()
            mock_timer.return_value = mock_timer_instance
            
            # Test schedule refresh
            with patch.object(manager, '_get_next_refresh_time', return_value=1800):
                manager._schedule_token_refresh(mock_auth_stub)
                
                # Verify existing timer was cancelled
                existing_timer.cancel.assert_called_once()
                
                # Verify new timer was created and started
                mock_timer.assert_called_once()
                mock_timer_instance.start.assert_called_once()

    async def test_refresh_token_async(self, mock_async_auth_stub, mock_jwt_decode):
        """Test refresh_token_async method"""
        manager = TokenManager(username="test_user", password="test_pass")
        manager._is_async = True
        
        # Test refresh token async
        with patch.object(manager, '_schedule_token_refresh_async') as mock_schedule:
            mock_schedule.return_value = asyncio.Future()
            mock_schedule.return_value.set_result(None)
            
            await manager.refresh_token_async(mock_async_auth_stub)
            
            # Verify auth request was made
            mock_async_auth_stub.Authenticate.assert_called_once()
            
            # Verify token was updated
            assert manager._token == "test_token"
            
            # Verify refresh was scheduled
            mock_schedule.assert_called_once_with(mock_async_auth_stub)

    async def test_refresh_token_async_no_credentials(self, mock_async_auth_stub):
        """Test refresh_token_async method with no credentials"""
        manager = TokenManager()  # No credentials
        manager._is_async = True
        
        # Test refresh token async
        await manager.refresh_token_async(mock_async_auth_stub)
        
        # Verify no auth request was made
        mock_async_auth_stub.Authenticate.assert_not_called()

    async def test_refresh_token_async_error(self, mock_async_auth_stub):
        """Test refresh_token_async method with error"""
        manager = TokenManager(username="test_user", password="test_pass")
        manager._is_async = True
        
        # Set up error
        mock_async_auth_stub.Authenticate.side_effect = grpc.RpcError()
        
        # Test refresh token async with error
        with pytest.raises(types.AVSServerError):
            await manager.refresh_token_async(mock_async_auth_stub)

    async def test_schedule_token_refresh_async_cancel_existing(self):
        """Test that scheduling a token refresh cancels any existing refresh"""
        manager = TokenManager("user", "pass")
        manager._is_async = True
        manager._auth_lock = asyncio.Lock()
        auth_stub = MagicMock()
        
        # Create a mock task with done and cancel methods
        mock_task = AsyncMock(spec=asyncio.Task)  # Use AsyncMock with spec=asyncio.Task
        mock_task.done.return_value = False
        manager._auth_timer = mock_task
        
        # Mock the _wait_and_refresh method to return a completed future
        # This prevents the "coroutine never awaited" warning
        with patch.object(manager, '_wait_and_refresh') as mock_wait_and_refresh:
            mock_future = asyncio.Future()
            mock_future.set_result(None)
            mock_wait_and_refresh.return_value = mock_future
            
            # Mock create_task to return a new mock task
            with patch('asyncio.create_task') as mock_create_task:
                new_mock_task = MagicMock()
                mock_create_task.return_value = new_mock_task
                
                # Schedule a new refresh
                await manager._schedule_token_refresh_async(auth_stub)
                
                # Verify the old task was cancelled
                mock_task.cancel.assert_called_once()
                
                # Verify a new task was created with the coroutine
                mock_create_task.assert_called_once()
                
                # Verify the new task was assigned
                assert manager._auth_timer is new_mock_task

    async def test_wait_and_refresh(self, mock_async_auth_stub):
        """Test _wait_and_refresh method"""
        manager = TokenManager("user", "pass")
        manager._is_async = True
        
        # Mock sleep and refresh
        with patch('asyncio.sleep') as mock_sleep:
            mock_sleep_future = asyncio.Future()
            mock_sleep_future.set_result(None)
            mock_sleep.return_value = mock_sleep_future
            
            with patch.object(manager, 'refresh_token_async') as mock_refresh:
                mock_refresh_future = asyncio.Future()
                mock_refresh_future.set_result(None)
                mock_refresh.return_value = mock_refresh_future
                
                # Test wait and refresh
                await manager._wait_and_refresh(10, mock_async_auth_stub)
                
                # Verify sleep was called
                mock_sleep.assert_called_once_with(10)
                
                # Verify refresh was called
                mock_refresh.assert_called_once_with(mock_async_auth_stub)

    def test_cancel_refresh_sync(self):
        """Test cancel_refresh method in sync mode"""
        manager = TokenManager(username="test_user", password="test_pass")
        
        # Set up timer
        mock_timer = Mock()
        manager._auth_timer = mock_timer
        
        # Test cancel refresh
        manager.cancel_refresh()
        
        # Verify timer was cancelled
        mock_timer.cancel.assert_called_once()
        
        # Verify timer was cleared
        assert manager._auth_timer is None

    def test_cancel_refresh_async(self):
        """Test cancel_refresh method in async mode"""
        manager = TokenManager(username="test_user", password="test_pass")
        manager._is_async = True
        
        # Set up task
        mock_task = AsyncMock(spec=asyncio.Task)
        mock_task.done.return_value = False
        manager._auth_timer = mock_task
        
        # Test cancel refresh
        manager.cancel_refresh()
        
        # Verify task was cancelled
        mock_task.cancel.assert_called_once()
        
        # Verify task was cleared
        assert manager._auth_timer is None

    async def test_schedule_token_refresh_async(self, mock_async_auth_stub):
        """Test _schedule_token_refresh_async method"""
        manager = TokenManager("user", "pass")
        manager._is_async = True
        manager._auth_lock = asyncio.Lock()
        
        # Mock the _wait_and_refresh method to return a completed future
        with patch.object(manager, '_wait_and_refresh') as mock_wait_and_refresh:
            mock_future = asyncio.Future()
            mock_future.set_result(None)
            mock_wait_and_refresh.return_value = mock_future
            
            # Mock create_task
            with patch('asyncio.create_task') as mock_create_task:
                mock_task = MagicMock()
                mock_create_task.return_value = mock_task
                
                # Test schedule refresh async
                with patch.object(manager, '_get_next_refresh_time', return_value=1800):
                    await manager._schedule_token_refresh_async(mock_async_auth_stub)
                    
                    # Verify task was created
                    mock_create_task.assert_called_once()
                    
                    # Verify _wait_and_refresh was called with correct parameters
                    mock_wait_and_refresh.assert_called_once()
                    wait_args, wait_kwargs = mock_wait_and_refresh.call_args
                    assert wait_args[0] == 1800  # refresh_time
                    assert wait_args[1] == mock_async_auth_stub  # auth_stub 