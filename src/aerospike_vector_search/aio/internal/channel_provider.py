import re
import asyncio
import logging
from typing import Optional, Union

import google.protobuf.empty_pb2
import grpc

from ... import types
from ...shared.proto_generated import vector_db_pb2
from ...shared.proto_generated import vector_db_pb2_grpc
from ...shared import base_channel_provider

empty = google.protobuf.empty_pb2.Empty()

logger = logging.getLogger(__name__)

TEND_INTERVAL : int = 1


class ChannelProvider(base_channel_provider.BaseChannelProvider):
    """AVS Channel Provider"""

    def __init__(
        self,
        seeds: tuple[types.HostPort, ...],
        listener_name: Optional[str] = None,
        is_loadbalancer: Optional[bool] = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        root_certificate: Optional[Union[list[str], str]] = None,
        certificate_chain: Optional[str] = None,
        private_key: Optional[str] = None,
        service_config_path: Optional[str] = None,
        ssl_target_name_override: Optional[str] = None,
    ) -> None:

        super().__init__(
            seeds,
            listener_name,
            is_loadbalancer,
            username,
            password,
            root_certificate,
            certificate_chain,
            private_key,
            service_config_path,
            ssl_target_name_override,
        )

        # When set, client has concluded cluster tending
        self._tend_ended: asyncio.Event = asyncio.Event()

        # When set, client has completed a cluster tend cycle, initialized auth, and verified client-server minimum compatibility
        self._ready: asyncio.Event = asyncio.Event()

        # When locked, new task is being assigned to _auth_task
        self._auth_tending_lock: asyncio.Lock = asyncio.Lock()

        # initializes authentication tending
        self._auth_task: Optional[asyncio.Task] = asyncio.create_task(
            self._tend_token()
        )

        # initializes client tending processes
        asyncio.create_task(self._tend())

        # Exception to progotate to main control flow from errors generated during tending
        self._tend_exception: Exception = None

    async def _is_ready(self):
        # Wait 1 round of cluster tending, auth token initialization, and server client compatibility verification
        await self._ready.wait()

        # This propogates any fatal/unexpected errors from client initialization/tending to the client.
        # Raising errors in a task does not deliver this error information to users
        if self._tend_exception:
            raise self._tend_exception

    async def _tend(self):

        try:
            await self._auth_task

            # verfies server is minimally compatible with client
            await self._check_server_version()

            await self._tend_cluster()

            self._ready.set()

        except  Exception as e:
            # Set all event to prevent hanging if initial tend fails with error
            self._tend_ended.set()
            self._ready.set()

    async def _tend_cluster(self):
        try:
            (channels, end_tend_cluster) = self.init_tend_cluster()

            if end_tend_cluster:
                self._tend_ended.set()
                return

            (cluster_info_stubs, tasks) = (
                self._gather_new_cluster_ids_and_cluster_info_stubs(channels)
            )

            new_cluster_ids = await asyncio.gather(*tasks)

            update_endpoints_stubs = self._gather_stubs_for_endpoint_updating(
                new_cluster_ids, cluster_info_stubs
            )

            tasks = self._gather_temp_endpoints(new_cluster_ids, update_endpoints_stubs)

            cluster_endpoints_list = await asyncio.gather(*tasks)

            temp_endpoints = self._assign_temporary_endpoints(cluster_endpoints_list)

            if update_endpoints_stubs:

                tasks = self._add_new_channels_from_temp_endpoints(temp_endpoints)

                await asyncio.gather(*tasks)

                tasks = self._close_old_channels_from_node_channels(temp_endpoints)

                await asyncio.gather(*tasks)

            await asyncio.sleep(TEND_INTERVAL)

            asyncio.create_task(self._tend_cluster())

        except Exception as e:
            logger.error("Unexpected tend failure: %s", e)
            self._tend_exception = e
            raise e

    async def _get_cluster_id_coroutine(self, stub):
        try:
            return await stub.GetClusterId(
                empty,
                credentials=self._token,
            )
        except Exception as e:
            logger.debug(
                "While tending, failed to get cluster id with error: " + str(e)
            )

    async def _get_cluster_endpoints_coroutine(self, stub):
        try:
            return (
                await stub.GetClusterEndpoints(
                    vector_db_pb2.ClusterNodeEndpointsRequest(
                        listenerName=self.listener_name
                    ),
                    credentials=self._token,
                )
            ).endpoints
        except Exception as e:
            logger.debug(
                "While tending, failed to get cluster endpoints with error: " + str(e)
            )

    async def _close_on_channel_coroutine(self, channel_endpoints):
        try:
            await channel_endpoints.channel.close()
        except Exception as e:
            logger.debug("While tending, failed to close GRPC channel: " + str(e))

    def _call_get_cluster_id(self, stub):
        return asyncio.create_task(self._get_cluster_id_coroutine(stub))

    def _call_get_cluster_endpoints(self, stub):
        return asyncio.create_task(self._get_cluster_endpoints_coroutine(stub))

    def _call_close_on_channel(self, channel_endpoints):
        return asyncio.create_task(self._close_on_channel_coroutine(channel_endpoints))

    async def _tend_token(self):
        try:
            if not self._token:
                return
            elif not self._token:
                await asyncio.sleep((self._ttl * self._ttl_threshold))

            await self._update_token_and_ttl()

            async with self._auth_tending_lock:
                self._auth_task = asyncio.create_task(self._tend_token())

        except Exception as e:
            self._tend_exception = e
            logger.error("Failed to tend token with error: %s", e)
            raise e

    async def _update_token_and_ttl(
        self,
    ) -> None:

        (auth_stub, auth_request) = self._prepare_authenticate(
            self._credentials, logger
        )

        try:
            response = await auth_stub.Authenticate(auth_request)
        except grpc.RpcError as e:
            logger.error("Failed to refresh authentication token with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        self._respond_authenticate(response.token)

    async def _check_server_version(self):
        try:
            stub = vector_db_pb2_grpc.AboutServiceStub(self.get_channel())
            about_request = vector_db_pb2.AboutRequest()
            response = await stub.Get(about_request, credentials=self._token)
            self.current_server_version = response.version
            self.verify_compatible_server()
        except grpc.RpcError as e:
            e = types.AVSServerError(rpc_error=e)
            logger.debug("Failed to retrieve server version: " + str(e))
            self._tend_exception = e
            raise e
        except Exception as e:
            logger.debug("Failed to verify server version: " + str(e))
            self._tend_exception = e
            raise e

    def _create_channel(self, host: str, port: int) -> grpc.Channel:
        host = re.sub(r"%.*", "", host)

        options = []

        if self.ssl_target_name_override:
            options.append(
                ("grpc.ssl_target_name_override", self.ssl_target_name_override)
            )

        if self.service_config_json:
            options.append(("grpc.service_config", self.service_config_json))

        if not options:
            options = None

        if self._root_certificate:

            ssl_credentials = grpc.ssl_channel_credentials(
                root_certificates=self._root_certificate,
                certificate_chain=self._certificate_chain,
                private_key=self._private_key,
            )

            return grpc.aio.secure_channel(
                f"{host}:{port}", ssl_credentials, options=options
            )

        else:
            return grpc.aio.insecure_channel(f"{host}:{port}", options=options)

    async def close(self):
        # signals to tend_cluster to end cluster tending
        self._closed = True

        # wait until cluster tending has ended
        await self._tend_ended.wait()

        for channel in self._seedChannels:
            await channel.close()

        for k, channelEndpoints in self._node_channels.items():
            if channelEndpoints.channel:
                await channelEndpoints.channel.close()

        async with self._auth_tending_lock:
            self._auth_task.cancel()
