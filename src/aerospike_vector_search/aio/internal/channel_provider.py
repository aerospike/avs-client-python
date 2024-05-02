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
        """
        If tending is in progress and completed one tend iteration. _tend_lock will locked.  
        If tending is stopped, _tend_lock will be unlocked
        threading.Lock is used over asyncio.Lock since asyncio.Lock does not support the blocking parameter
        """
        self._tend_initalized: bool = False
        self._tend_ended: bool = False
        self._task: Optional[asyncio.Task] = None



    async def close(self):
        self._closed = True
        while not self._tend_ended:
            await asyncio.sleep(0.01)

        for channel in self._seedChannels:
            await channel.close()

        for k, channelEndpoints in self._node_channels.items():
            if channelEndpoints.channel:
                await channelEndpoints.channel.close()

        if self._task != None:
            await self._task

    async def _check_tend(self):
        while not self._tend_initalized:
            await asyncio.sleep(0.01)

    async def _tend(self):
        (temp_endpoints, update_endpoints_stub, channels, end_tend) = self.init_tend()

        if end_tend:
            self._tend_ended = True
            return

        stubs = []
        tasks = []

        for channel in channels:

            stub = vector_db_pb2_grpc.ClusterInfoStub(channel)
            stubs.append(stub)
            try:
                tasks.append(stub.GetClusterId(empty))

            except Exception as e:
                logger.debug("While tending, failed to get cluster id with error:" + str(e))

        new_cluster_ids = await asyncio.gather(*tasks)

        for index, value in enumerate(new_cluster_ids):
            if self.check_cluster_id(value.id):
                update_endpoints_stub = stubs[index]
                break

        if update_endpoints_stub:
            try:
                response = await update_endpoints_stub.GetClusterEndpoints(
                    vector_db_pb2.ClusterNodeEndpointsRequest(
                        listenerName=self.listener_name
                    )
                )
                temp_endpoints = self.update_temp_endpoints(response, temp_endpoints)
            except Exception as e:
                logger.debug("While tending, failed to get cluster endpoints with error:" + str(e))

            tasks = []
            add_new_channel_info = []

            for node, newEndpoints in temp_endpoints.items():
                (channel_endpoints, add_new_channel) = self.check_for_new_endpoints(node, newEndpoints)
                
                if add_new_channel:
                    try:
                        # TODO: Wait for all calls to drain
                        tasks.append(channel_endpoints.channel.close())
                    except Exception as e:
                        logger.debug("While tending, failed to close GRPC channel:" + str(e))
                    add_new_channel_info.append((node, newEndpoints))


            for node, newEndpoints in add_new_channel_info:
                self.add_new_channel_to_node_channels(node, newEndpoints)


            temp_node_channels = self._node_channels.items()
            for node, channel_endpoints in temp_node_channels:
                if not temp_endpoints.get(node):
                    try:
                        # TODO: Wait for all calls to drain
                        tasks.append(channel_endpoints.channel.close())
                        del self._node_channels[node]
                        
                    except Exception as e:
                        logger.debug("While tending, failed to close GRPC channel:" + str(e))

            await asyncio.gather(*tasks)

        self._tend_initalized = True

        # TODO: check tend interval.
        await asyncio.sleep(1)
        self._task = asyncio.create_task(self._tend())

    def _create_channel(self, host: str, port: int, is_tls: bool) -> grpc.aio.Channel:
        # TODO: Take care of TLS
        host = re.sub(r"%.*", "", host)
        return grpc.aio.insecure_channel(f"{host}:{port}")