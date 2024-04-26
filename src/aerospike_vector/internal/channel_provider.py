import re
import logging
import threading
from typing import Optional, Union

import google.protobuf.empty_pb2
import grpc

from .. import types
from ..shared.proto_generated import vector_db_pb2
from ..shared.proto_generated import vector_db_pb2_grpc
from ..shared import base_channel_provider
from ..shared import channel_provider_helpers

empty = google.protobuf.empty_pb2.Empty()

logger = logging.getLogger(__name__)


class ChannelProvider(base_channel_provider.BaseChannelProvider):
    """Proximus Channel Provider"""
    def __init__(
        self, seeds: tuple[types.HostPort, ...], listener_name: Optional[str] = None, is_loadbalancer: Optional[bool] = False
    ) -> None:
        super().__init__(seeds, listener_name, is_loadbalancer)
        self._tend()

    def close(self):
        self._closed = True
        for channel in self._seedChannels:
            channel.close()

        for k, channelEndpoints in self._nodeChannels.items():
            if channelEndpoints.channel:
                channelEndpoints.channel.close()

    def _tend(self):
        (temp_endpoints, update_endpoints, channels, end_tend) = channel_provider_helpers.init_tend(self)

        if end_tend:
            return

        for seedChannel in channels:

            stub = vector_db_pb2_grpc.ClusterInfoStub(seedChannel)
            
            try:
                new_cluster_id = stub.GetClusterId(empty).id
                if channel_provider_helpers.check_cluster_id(self, new_cluster_id):
                    update_endpoints = True
                else:
                    continue

            except Exception as e:
                logger.debug("While tending, failed to get cluster id with error:" + str(e))


            try:
                response = stub.GetClusterEndpoints(
                    vector_db_pb2.ClusterNodeEndpointsRequest(
                        listenerName=self.listener_name
                    )
                )
            except Exception as e:
                logger.debug("While tending, failed to get cluster endpoints with error:" + str(e))

            temp_endpoints = channel_provider_helpers.update_temp_endpoints(response, temp_endpoints)

        if update_endpoints:
            for node, newEndpoints in temp_endpoints.items():
                (channel_endpoints, add_new_channel) = channel_provider_helpers.check_for_new_endpoints(self, node, newEndpoints)

                if add_new_channel:
                    try:
                        # TODO: Wait for all calls to drain
                        channel_endpoints.channel.close()
                    except Exception as e:
                        logger.debug("While tending, failed to close GRPC channel:" + str(e))

                    self.add_new_channel_to_node_channels(node, newEndpoints)

            for node, channel_endpoints in self._nodeChannels.items():
                if not temp_endpoints.get(node):
                    # TODO: Wait for all calls to drain
                    try:
                        channel_endpoints.channel.close()
                        del self._nodeChannels[node]
                        
                    except Exception as e:
                        logger.debug("While tending, failed to close GRPC channel:" + str(e))

        # TODO: check tend interval.
        threading.Timer(1, self._tend).start()

    def _create_channel(self, host: str, port: int, isTls: bool) -> grpc.Channel:
        # TODO: Take care of TLS
        host = re.sub(r"%.*", "", host)
        return grpc.insecure_channel(f"{host}:{port}")