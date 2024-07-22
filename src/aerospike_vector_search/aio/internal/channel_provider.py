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
        certificate_chain: Optional[str] = None,
        private_key: Optional[str] = None,
        service_config_path: Optional[str] = None,

    ) -> None:

        super().__init__(seeds, listener_name, is_loadbalancer, username, password, root_certificate, certificate_chain, private_key, service_config_path)

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

        if not self.client_server_compatible:
            raise types.AVSClientError(message="This AVS Client version is only compatbile with AVS Servers above the following version number: " + self.minimum_required_version)

    async def _tend(self):
        try:
            (temp_endpoints, update_endpoints_stub, channels, end_tend) = self.init_tend()
            if self._token:
                if self._check_if_token_refresh_needed():
                    await self._update_token_and_ttl()

            if end_tend:
                self._tend_initalized.set()

                self._tend_ended.set()
                return

            stubs = []
            tasks = []
            update_endpoints_stubs = []
            for channel in channels:

                stub = vector_db_pb2_grpc.ClusterInfoServiceStub(channel)
                stubs.append(stub)
                try:
                    tasks.append(await stub.GetClusterId(empty, credentials=self._token))
                except Exception as e:
                    logger.debug(
                        "While tending, failed to get cluster id with error:" + str(e)
                    )

            try:
                new_cluster_ids = tasks
            except Exception as e:
                logger.debug(
                    "While tending, failed to gather results from GetClusterId:" + str(e)
                )

            for index, value in enumerate(new_cluster_ids):
                if self.check_cluster_id(value.id):
                    update_endpoints_stubs.append(stubs[index])
        


            for stub in update_endpoints_stubs:
                try:
                    response = await stub.GetClusterEndpoints(
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

            if update_endpoints_stubs:
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
                        self.add_new_channel_to_node_channels(node, newEndpoints)

                for node, channel_endpoints in list(self._node_channels.items()):
                    if not temp_endpoints.get(node):
                        try:
                            # TODO: Wait for all calls to drain
                            tasks.append(channel_endpoints.channel.close())
                            del self._node_channels[node]

                        except Exception as e:
                            logger.debug(
                                "While tending, failed to close GRPC channel:" + str(e)
                            )

                await asyncio.gather(*tasks)

            if not self.client_server_compatible:

                stub = vector_db_pb2_grpc.AboutServiceStub(self.get_channel())
                about_request = vector_db_pb2.AboutRequest()

                self.current_server_version = (await stub.Get(about_request, credentials=self._token)).version
                self.client_server_compatible = self.verify_compatibile_server()

                self._tend_initalized.set() 

            # TODO: check tend interval.
            await asyncio.sleep(1)
            self._task = asyncio.create_task(self._tend())
        except Exception as e:

            print(e)


    def _create_channel(self, host: str, port: int, is_tls: bool) -> grpc.Channel:
        host = re.sub(r"%.*", "", host)
        
        if self.service_config_json:
            options = []
            options.append(("grpc.service_config", self.service_config_json))
        else:
            options = None

        if self._root_certificate:
            with open(self._root_certificate, 'rb') as f:
                root_certificate = f.read()

            if self._private_key:
                with open(self._private_key, 'rb') as f:
                    private_key = f.read()
            else:
                private_key = None
                
            if self._certificate_chain:
                with open(self._certificate_chain, 'rb') as f:
                    certificate_chain = f.read()
            else:
                certificate_chain = None


            ssl_credentials = grpc.ssl_channel_credentials(root_certificates=root_certificate, certificate_chain=certificate_chain, private_key=private_key)


            return grpc.aio.secure_channel(f"{host}:{port}", ssl_credentials, options=options)

        else:
            return grpc.aio.insecure_channel(f"{host}:{port}", options=options)


    async def _update_token_and_ttl(
        self,
    ) -> None:
        (auth_stub, auth_request) = self._prepare_authenticate(
            self._credentials, logger
        )

        try:
            response = await auth_stub.Authenticate(auth_request)
        except grpc.RpcError as e:
            print("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        self._respond_authenticate(response.token)