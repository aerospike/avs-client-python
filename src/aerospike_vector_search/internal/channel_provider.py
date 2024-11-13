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

TEND_INTERVAL: int = 1


class ChannelProvider(base_channel_provider.BaseChannelProvider):
    """Proximus Channel Provider"""

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
        self._tend_ended = threading.Event()

        # When locked, new task is being assigned to _auth_task
        self._auth_tending_lock: threading.Lock = threading.Lock()

        self._auth_timer = None

        # initializes authentication tending
        self._tend_token()

        # verfies server is minimally compatible with client
        self._check_server_version()

        # initializes cluster tending
        self._tend_cluster()

    def _tend_cluster(self):
        try:
            (channels, end_tend_cluster) = self.init_tend_cluster()

            if end_tend_cluster:
                self._tend_ended.set()
                return

            (cluster_info_stubs, new_cluster_ids) = (
                self._gather_new_cluster_ids_and_cluster_info_stubs(channels)
            )

            update_endpoints_stubs = self._gather_stubs_for_endpoint_updating(
                new_cluster_ids, cluster_info_stubs
            )

            cluster_endpoints_list = self._gather_temp_endpoints(
                new_cluster_ids, update_endpoints_stubs
            )

            temp_endpoints = self._assign_temporary_endpoints(cluster_endpoints_list)

            if update_endpoints_stubs:

                self._add_new_channels_from_temp_endpoints(temp_endpoints)

                self._close_old_channels_from_node_channels(temp_endpoints)

            threading.Timer(TEND_INTERVAL, self._tend_cluster).start()

        except Exception as e:
            logger.error("Tending failed at unindentified location: %s", e)
            raise e

    def _call_get_cluster_id(self, stub):
        try:
            return stub.GetClusterId(
                empty,
                credentials=self._token,
            )
        except Exception as e:
            logger.debug(
                "While tending, failed to get cluster id with error: " + str(e)
            )

    def _call_get_cluster_endpoints(self, stub) -> vector_db_pb2.ServerEndpointList:
        try:
            return (
                stub.GetClusterEndpoints(
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

    def _call_close_on_channel(self, channel_endpoints):
        try:
            channel_endpoints.channel.close()
        except Exception as e:
            logger.debug("While tending, failed to close GRPC channel: " + str(e))

    def _tend_token(self):

        if not self._token:
            return

        self._update_token_and_ttl()

        with self._auth_tending_lock:
            self._auth_timer = threading.Timer(
                (self._ttl * self._ttl_threshold), self._tend_token
            )
            self._auth_timer.start()

    def _update_token_and_ttl(
        self,
    ) -> None:

        (auth_stub, auth_request) = self._prepare_authenticate(
            self._credentials, logger
        )

        try:
            response = auth_stub.Authenticate(auth_request)
        except grpc.RpcError as e:
            logger.error("Failed to refresh authentication token with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        self._respond_authenticate(response.token)

    def _check_server_version(self):
        stub = vector_db_pb2_grpc.AboutServiceStub(self.get_channel())
        about_request = vector_db_pb2.AboutRequest()

        try:
            response = stub.Get(about_request, credentials=self._token)
            self.current_server_version = response.version
        except grpc.RpcError as e:
            logger.debug("Failed to retrieve server version: " + str(e))
            raise types.AVSServerError(rpc_error=e)
        self.verify_compatible_server()

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

            return grpc.secure_channel(
                f"{host}:{port}", ssl_credentials, options=options
            )

        else:
            return grpc.insecure_channel(f"{host}:{port}", options=options)

    def close(self):
        self._closed = True
        self._tend_ended.wait()

        for channel in self._seedChannels:
            channel.close()

        for k, channelEndpoints in self._node_channels.items():
            if channelEndpoints.channel:
                channelEndpoints.channel.close()

        with self._auth_tending_lock:
            if self._auth_timer is not None:
                self._auth_timer.cancel()
