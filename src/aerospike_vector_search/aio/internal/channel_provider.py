import re
import asyncio
import logging
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
    """Proximus Channel Provider"""
    def __init__(
        self, seeds: tuple[types.HostPort, ...], listener_name: Optional[str] = None, is_loadbalancer: Optional[bool] = False
    ) -> None:
        super().__init__(seeds, listener_name, is_loadbalancer)
        asyncio.create_task(self._tend())

    async def close(self):
        self._closed = True
        for channel in self._seedChannels:
            await channel.close()

        for k, channelEndpoints in self._node_channels.items():
            if channelEndpoints.channel:
                await channelEndpoints.channel.close()

    async def _tend(self):
        (temp_endpoints, update_endpoints, channels, end_tend) = self.init_tend()
        if end_tend:
            return

        for seedChannel in channels:

            stub = vector_db_pb2_grpc.ClusterInfoStub(seedChannel)
            
            try:
                new_cluster_id = await stub.GetClusterId(empty).id
                if self.check_cluster_id(new_cluster_id):
                    update_endpoints = True
                else:
                    continue

            except Exception as e:
                logger.debug("While tending, failed to get cluster id with error:" + str(e))


            try:
                response = await stub.GetClusterEndpoints(
                    vector_db_pb2.ClusterNodeEndpointsRequest(
                        listenerName=self.listener_name
                    )
                )
            except Exception as e:
                logger.debug("While tending, failed to get cluster endpoints with error:" + str(e))

            temp_endpoints = self.update_temp_endpoints(response, temp_endpoints)

        if update_endpoints:
            for node, newEndpoints in temp_endpoints.items():
                (channel_endpoints, add_new_channel) = self.check_for_new_endpoints(node, newEndpoints)
                if add_new_channel:
                    try:
                        # TODO: Wait for all calls to drain
                        await channel_endpoints.channel.close()
                    except Exception as e:
                        logger.debug("While tending, failed to close GRPC channel:" + str(e))

                    self.add_new_channel_to_node_channels(node, newEndpoints)

            for node, channel_endpoints in self._node_channels.items():
                if not temp_endpoints.get(node):
                    # TODO: Wait for all calls to drain
                    try:
                        await channel_endpoints.channel.close()
                        del self._node_channels[node]
                        
                    except Exception as e:
                        logger.debug("While tending, failed to close GRPC channel:" + str(e))

        # TODO: check tend interval.
        await asyncio.sleep(1)
        asyncio.create_task(self._tend())

    def _create_channel(self, host: str, port: int, is_tls: bool) -> grpc.aio.Channel:
        # TODO: Take care of TLS
        host = re.sub(r"%.*", "", host)
        return grpc.aio.insecure_channel(f"{host}:{port}")