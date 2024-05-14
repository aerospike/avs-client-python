import logging
import random

from typing import Optional, Union

import grpc

from .. import types
from .proto_generated import vector_db_pb2

logger = logging.getLogger(__name__)


class ChannelAndEndpoints(object):
    def __init__(
        self,
        channel: Union[grpc.Channel, grpc.aio.Channel],
        endpoints: vector_db_pb2.ServerEndpointList,
    ) -> None:
        self.channel = channel
        self.endpoints = endpoints


class BaseChannelProvider(object):
    """Proximus Channel Provider"""

    def __init__(
        self,
        seeds: tuple[types.HostPort, ...],
        listener_name: Optional[str] = None,
        is_loadbalancer: Optional[bool] = False,
    ) -> None:
        self.seeds: tuple[types.HostPort, ...] = seeds
        self.listener_name: Optional[str] = listener_name
        self._is_loadbalancer: Optional[bool] = is_loadbalancer
        # dict of Node Number and ChannelAndEndponts object
        self._node_channels: dict[int, ChannelAndEndpoints] = {}
        self._seedChannels: Union[list[grpc.Channel], list[grpc.Channel.aio]] = [
            self._create_channel_from_host_port(seed) for seed in self.seeds
        ]
        self._closed: bool = False
        self._cluster_id: int = 0

    def get_channel(self) -> Union[grpc.aio.Channel, grpc.Channel]:
        if not self._is_loadbalancer:
            discovered_channels: list[ChannelAndEndpoints] = list(
                self._node_channels.values()
            )
            if len(discovered_channels) <= 0:
                return self._seedChannels[0]

            # Return a random channel.
            channel = random.choice(discovered_channels).channel
            if channel:
                return channel

        return self._seedChannels[0]

    def _create_channel_from_host_port(
        self, host: types.HostPort
    ) -> Union[grpc.aio.Channel, grpc.Channel]:
        return self._create_channel(host.host, host.port, host.is_tls)

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
        new_channel = self._create_channel_from_server_endpoint_list(newEndpoints)
        self._node_channels[node] = ChannelAndEndpoints(new_channel, newEndpoints)

    def init_tend(self) -> None:
        end_tend = False
        if self._is_loadbalancer:
            # Skip tend if we are behind a load-balancer
            end_tend = True

        if self._closed:
            end_tend = True

        # TODO: Worry about thread safety
        temp_endpoints: dict[int, vector_db_pb2.ServerEndpointList] = {}

        update_endpoints_stub = None
        channels = self._seedChannels + [
            x.channel for x in self._node_channels.values()
        ]
        return (temp_endpoints, update_endpoints_stub, channels, end_tend)

    def check_cluster_id(self, new_cluster_id) -> None:
        if new_cluster_id == self._cluster_id:
            return False

        self._cluster_id = new_cluster_id

        return True

    def update_temp_endpoints(self, response, temp_endpoints):
        endpoints = response.endpoints
        if len(endpoints) > len(temp_endpoints):
            return endpoints
        else:
            return temp_endpoints

    def check_for_new_endpoints(self, node, newEndpoints):

        channel_endpoints = self._node_channels.get(node)
        add_new_channel = True

        if channel_endpoints:
            # We have this node. Check if the endpoints changed.
            if channel_endpoints.endpoints == newEndpoints:
                # Nothing to be done for this node
                add_new_channel = False
            else:
                add_new_channel = True

        return (channel_endpoints, add_new_channel)
