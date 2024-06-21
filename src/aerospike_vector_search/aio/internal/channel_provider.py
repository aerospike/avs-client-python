import re
import asyncio
import logging
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Optional, Union

import google.protobuf.empty_pb2
import grpc
import random

from ... import types
from ...shared.proto_generated import vector_db_pb2
from ...shared.proto_generated import vector_db_pb2_grpc
from ...shared import base_channel_provider

empty = google.protobuf.empty_pb2.Empty()

logger = logging.getLogger(__name__)


class ChannelProvider(base_channel_provider.BaseChannelProvider):
    """AVS Channel Provider"""

    def __init__(
        self,
        seeds: tuple[types.HostPort, ...],
        listener_name: Optional[str] = None,
        is_loadbalancer: Optional[bool] = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        root_certificate: Optional[str] = None,
    ) -> None:

        super().__init__(seeds, listener_name, is_loadbalancer, username, password, root_certificate)

        self._tend_initalized: asyncio.Event = asyncio.Event()
        self._tend_ended: asyncio.Event = asyncio.Event()
        self._task: Optional[asyncio.Task] = None

        asyncio.create_task(self._tend())

    async def close(self):
        self._closed = True
        await self._tend_ended.wait()

        for channel in self._seedChannels:
            await channel.close()

        for k, channelEndpoints in self._node_channels.items():
            if channelEndpoints.channel:
                await channelEndpoints.channel.close()

        if self._task != None:
            await self._task

    async def _is_ready(self):
        await self._tend_initalized.wait()

    async def _tend(self):
        (temp_endpoints, update_endpoints_stub, channels, end_tend) = self.init_tend()

        if self._token:
            if self._check_if_token_refresh_needed():
                await self._update_token_and_ttl()

        if end_tend:
            self._tend_ended.set()
            return

        stubs = []
        tasks = []

        for channel in channels:

            stub = vector_db_pb2_grpc.ClusterInfoStub(channel)
            stubs.append(stub)
            try:
                tasks.append(stub.GetClusterId(empty, credentials=self._token))
            except Exception as e:
                logger.debug(
                    "While tending, failed to get cluster id with error:" + str(e)
                )

        try:
            new_cluster_ids = await asyncio.gather(*tasks)
        except Exception as e:
            logger.debug(
                "While tending, failed to gather results from GetClusterId:" + str(e)
            )

        for index, value in enumerate(new_cluster_ids):
            if self.check_cluster_id(value.id):
                update_endpoints_stub = stubs[index]
                break


        if update_endpoints_stub:
            try:
                response = await update_endpoints_stub.GetClusterEndpoints(
                    vector_db_pb2.ClusterNodeEndpointsRequest(
                        listenerName=self.listener_name
                    ),
                    credentials=self._token
                )
                temp_endpoints = self.update_temp_endpoints(response, temp_endpoints)
            except Exception as e:
                logger.debug(
                    "While tending, failed to get cluster endpoints with error:"
                    + str(e)
                )

            tasks = []
            add_new_channel_info = []

            for node, newEndpoints in temp_endpoints.items():
                (channel_endpoints, add_new_channel) = self.check_for_new_endpoints(
                    node, newEndpoints
                )

                if add_new_channel:
                    try:
                        # TODO: Wait for all calls to drain
                        tasks.append(channel_endpoints.channel.close())
                    except Exception as e:
                        logger.debug(
                            "While tending, failed to close GRPC channel:" + str(e)
                        )
                    add_new_channel_info.append((node, newEndpoints))

            for node, newEndpoints in add_new_channel_info:
                self.add_new_channel_to_node_channels(node, newEndpoints)

            for node, channel_endpoints in list(self._node_channels.items()):
                if not self._node_channels.get(node):
                    try:
                        # TODO: Wait for all calls to drain
                        tasks.append(channel_endpoints.channel.close())
                        del self._node_channels[node]

                    except Exception as e:
                        logger.debug(
                            "While tending, failed to close GRPC channel:" + str(e)
                        )

            await asyncio.gather(*tasks)

        self._tend_initalized.set()

        # TODO: check tend interval.
        await asyncio.sleep(1)
        self._task = asyncio.create_task(self._tend())


    def _create_channel(self, host: str, port: int, is_tls: bool) -> grpc.aio.Channel:
        host = re.sub(r"%.*", "", host)
        if self._root_certificate:
            with open(self._root_certificate, 'rb') as f:
                root_certificate = f.read()

            ssl_credentials = grpc.ssl_channel_credentials(root_certificates=root_certificate)

            return grpc.aio.secure_channel(f"{host}:{port}", ssl_credentials)

        else:
            return grpc.aio.insecure_channel(f"{host}:{port}")


    async def _update_token_and_ttl(
        self,
    ) -> None:
        try: 
            (auth_stub, auth_request) = self._prepare_authenticate(
                self._credentials, logger
            )

            try:
                response = await auth_stub.Authenticate(auth_request)
            except grpc.RpcError as e:
                print("Failed with error: %s", e)
                raise types.AVSServerError(rpc_error=e)

            self._respond_authenticate(response.token)
        except Exception as e:
            print(e)