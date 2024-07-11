import re
import time
import logging
import threading
from typing import Optional, Union

import google.protobuf.empty_pb2
import grpc

from .. import types
from ..shared.proto_generated import vector_db_pb2
from ..shared.proto_generated import vector_db_pb2_grpc
from ..shared import base_channel_provider

empty = google.protobuf.empty_pb2.Empty()

logger = logging.getLogger(__name__)


class ChannelProvider(base_channel_provider.BaseChannelProvider):
    """Proximus Channel Provider"""

    def __init__(
        self,
        seeds: tuple[types.HostPort, ...],
        listener_name: Optional[str] = None,
        is_loadbalancer: Optional[bool] = False,
    ) -> None:
        super().__init__(seeds, listener_name, is_loadbalancer)
        self._tend_ended = threading.Event()
        self._timer = None
        self._tend()

    def close(self):
        self._closed = True
        self._tend_ended.wait()

        for channel in self._seedChannels:
            channel.close()

        for k, channelEndpoints in self._node_channels.items():
            if channelEndpoints.channel:
                channelEndpoints.channel.close()

        if self._timer != None:
            self._timer.join()

    def _tend(self):
        (temp_endpoints, update_endpoints_stub, channels, end_tend) = self.init_tend()

        if end_tend:
            self._tend_ended.set()

            return
        for channel in channels:

            stub = vector_db_pb2_grpc.ClusterInfoServiceStub(channel)

            try:
                new_cluster_id = stub.GetClusterId(empty).id
                if self.check_cluster_id(new_cluster_id):
                    update_endpoints_stub = stub
                    break
                else:
                    continue

            except Exception as e:
                logger.debug(
                    "While tending, failed to get cluster id with error:" + str(e)
                )

        if update_endpoints_stub:
            try:
                response = stub.GetClusterEndpoints(
                    vector_db_pb2.ClusterNodeEndpointsRequest(
                        listenerName=self.listener_name
                    )
                )
                temp_endpoints = self.update_temp_endpoints(response, temp_endpoints)
            except Exception as e:
                logger.debug(
                    "While tending, failed to get cluster endpoints with error:"
                    + str(e)
                )

            for node, newEndpoints in temp_endpoints.items():
                (channel_endpoints, add_new_channel) = self.check_for_new_endpoints(
                    node, newEndpoints
                )

                if add_new_channel:
                    try:
                        # TODO: Wait for all calls to drain
                        channel_endpoints.channel.close()
                    except Exception as e:
                        logger.debug(
                            "While tending, failed to close GRPC channel:" + str(e)
                        )

                    self.add_new_channel_to_node_channels(node, newEndpoints)

            for node, channel_endpoints in list(self._node_channels.items()):
                if not self._node_channels.get(node):
                    try:
                        # TODO: Wait for all calls to drain
                        channel_endpoints.channel.close()
                        del self._node_channels[node]

                    except Exception as e:
                        logger.debug(
                            "While tending, failed to close GRPC channel:" + str(e)
                        )
        # TODO: check tend interval.
        self._timer = threading.Timer(1, self._tend).start()

    def _create_channel(self, host: str, port: int, is_tls: bool) -> grpc.Channel:
        # TODO: Take care of TLS
        host = re.sub(r"%.*", "", host)
        return grpc.insecure_channel(f"{host}:{port}")
