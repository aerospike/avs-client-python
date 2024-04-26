import logging
import random

from typing import Optional, Union

import grpc

from .. import types
from .proto_generated import vector_db_pb2

logger = logging.getLogger(__name__)

class ChannelAndEndpoints(object):
    def __init__(
        self, channel: Union[grpc.Channel, grpc.aio.Channel], endpoints: vector_db_pb2.ServerEndpointList
    ) -> None:
        self.channel = channel
        self.endpoints = endpoints


class BaseChannelProvider(object):
    """Proximus Channel Provider"""
    def __init__(
        self, seeds: tuple[types.HostPort, ...], listener_name: Optional[str] = None, is_loadbalancer: Optional[bool] = False
    ) -> None:
        if not seeds:
            raise Exception("at least one seed host needed")
        self._nodeChannels: dict[int, ChannelAndEndpoints] = {}
        self._seedChannels: Union[dict[grpc.Channel], dict[grpc.Channel.aio]] = {}
        self._closed = False
        self._clusterId = 0
        self.seeds = seeds
        self.listener_name = listener_name
        self._is_loadbalancer = is_loadbalancer
        self._seedChannels = [
            self._create_channel_from_host_port(seed) for seed in self.seeds
        ]

    def get_channel(self) -> Union[grpc.aio.Channel, grpc.Channel]:
        if not self._is_loadbalancer:
            discovered_channels: list[ChannelAndEndpoints] = list(
                self._nodeChannels.values())
            if len(discovered_channels) <= 0:
                return self._seedChannels[0]


            # Return a random channel.
            channel = random.choice(discovered_channels).channel
            if channel:
                return channel

        return self._seedChannels[0]
    def _create_channel_from_host_port(self, host: types.HostPort) -> Union[grpc.aio.Channel, grpc.Channel]:
        return self._create_channel(host.host, host.port, host.isTls)

    def _create_channel_from_server_endpoint_list(
        self, endpoints: vector_db_pb2.ServerEndpointList
    ) -> Union[grpc.aio.Channel, grpc.Channel]:
        # TODO: Create channel with all endpoints
        for endpoint in endpoints.endpoints:
            if ":" in endpoint.address:
                # TODO: Ignoring IPv6 for now. Needs fix
                continue
            try:
                return self._create_channel(
                    endpoint.address, endpoint.port, endpoint.isTls
                )
            except Exception as e:
                logger.debug("failure creating channel: " + str(e))

    def add_new_channel_to_node_channels(self, node, newEndpoints):

        # We have discovered a new node
        new_channel = self._create_channel_from_server_endpoint_list(
            newEndpoints
        )
        self._nodeChannels[node] = ChannelAndEndpoints(
            new_channel, newEndpoints
        )
