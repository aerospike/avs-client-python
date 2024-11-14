import logging
import random
from logging import Logger
from typing import Optional, Union, Tuple

import grpc
import jwt

from . import helpers
from .proto_generated import auth_pb2_grpc
from .proto_generated import vector_db_pb2, auth_pb2, types_pb2
from .proto_generated import vector_db_pb2_grpc
from .. import types

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
        ssl_target_name_override: Optional[str] = None,
    ) -> None:
        self.seeds: tuple[types.HostPort, ...] = seeds
        self.listener_name: Optional[str] = listener_name
        self._is_loadbalancer: Optional[bool] = is_loadbalancer

        if service_config_path:
            with open(service_config_path, "rb") as f:
                self.service_config_json = f.read()
        else:
            self.service_config_json = None

        self.ssl_target_name_override = ssl_target_name_override

        self._credentials : Optional[types_pb2.Credentials] = helpers._get_credentials(username, password)
        if self._credentials:
            self._token = True
        else:
            self._token = None

        self._root_certificate = root_certificate
        self._certificate_chain = certificate_chain
        self._private_key = private_key
        self._ttl = 0
        self._ttl_start = 0
        self._ttl_threshold = 0.9
        # dict of Node Number and ChannelAndEndponts object
        self._node_channels: dict[int, ChannelAndEndpoints] = {}
        self._seedChannels: Union[list[grpc.Channel], list[grpc.Channel.aio]] = [
            self._create_channel_from_host_port(seed) for seed in self.seeds
        ]
        self._closed: bool = False
        self._cluster_id: int = 0
        self.current_server_version = ""
        self.minimum_required_version = "0.11.0"
        self.client_server_compatible = False

    def get_token(self) -> grpc.access_token_call_credentials:
        return self._token

    def _prepare_about(self) -> Tuple[vector_db_pb2_grpc.AboutServiceStub, vector_db_pb2.AboutRequest]:
        stub = vector_db_pb2_grpc.AboutServiceStub(self.get_channel())
        about_request = vector_db_pb2.AboutRequest()
        return (stub, about_request)

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
        return self._create_channel(host.host, host.port)

    def _create_channel_from_server_endpoint_list(
        self, endpoints: vector_db_pb2.ServerEndpointList
    ) -> Union[grpc.aio.Channel, grpc.Channel]:
        # TODO: Create channel with all endpoints
        for endpoint in endpoints.endpoints:
            if ":" in endpoint.address:
                # TODO: Ignoring IPv6 for now. Needs fix
                continue
            try:
                return self._create_channel(endpoint.address, endpoint.port)
            except Exception as e:
                logger.debug("failure creating channel: " + str(e))

    def add_new_channel_to_node_channels(self, node, newEndpoints):

        # We have discovered a new node
        new_channel = self._create_channel_from_server_endpoint_list(newEndpoints)
        self._node_channels[node] = ChannelAndEndpoints(new_channel, newEndpoints)

    def init_tend_cluster(self) -> tuple[list[ChannelAndEndpoints], bool]:

        end_tend_cluster = False
        if self._is_loadbalancer or self._closed:
            # Skip tend if we are behind a load-balancer
            end_tend_cluster = True

        channels = self._seedChannels + [
            x.channel for x in self._node_channels.values()
        ]

        return (channels, end_tend_cluster)

    def check_cluster_id(self, new_cluster_id) -> bool:
        if new_cluster_id == self._cluster_id:
            return False

        self._cluster_id = new_cluster_id

        return True

    def update_temp_endpoints(self, endpoints, temp_endpoints) -> dict[int, vector_db_pb2.ServerEndpointList]:
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

        return (channel_endpoints, add_new_channel)

    def _get_ttl(self, payload) -> int:
        return payload["exp"] - payload["iat"]

    def _prepare_authenticate(self, credentials: Optional[types_pb2.Credentials], logger: Logger):
        logger.debug("Refreshing auth token")
        auth_stub = self._get_auth_stub()

        auth_request = self._get_authenticate_request(self._credentials)

        return (auth_stub, auth_request)

    def _get_auth_stub(self) -> auth_pb2_grpc.AuthServiceStub:
        return auth_pb2_grpc.AuthServiceStub(self.get_channel())

    def _get_authenticate_request(self, credentials) -> auth_pb2.AuthRequest:
        return auth_pb2.AuthRequest(credentials=credentials)

    def _respond_authenticate(self, token) -> None:
        payload = jwt.decode(
            token, "", algorithms=["RS256"], options={"verify_signature": False}
        )
        self._ttl = self._get_ttl(payload)
        self._ttl_start = payload["iat"]

        self._token = grpc.access_token_call_credentials(token)

    def verify_compatible_server(self):
        def parse_version(v: str):
            return tuple(str(part) if part.isdigit() else part for part in v.split("."))

        if parse_version(self.current_server_version) < parse_version(
            self.minimum_required_version
        ):
            self._tend_ended.set()
            raise types.AVSClientError(
                message="This AVS Client version is only compatible with AVS Servers above the following version number: "
                + self.minimum_required_version
            )
        else:
            self.client_server_compatible = True

    def _gather_new_cluster_ids_and_cluster_info_stubs(self, channels):

        stubs = []
        responses = []

        for channel in channels:

            stub = vector_db_pb2_grpc.ClusterInfoServiceStub(channel)
            stubs.append(stub)

            response = self._call_get_cluster_id(stub)
            responses.append(response)

        return (stubs, responses)

    def _gather_stubs_for_endpoint_updating(self, new_cluster_ids, cluster_info_stubs):
        update_endpoints_stubs = []
        for index, value in enumerate(new_cluster_ids):

            if not value:
                continue
            if self.check_cluster_id(value.id):
                update_endpoints_stub = cluster_info_stubs[index]

                update_endpoints_stubs.append(update_endpoints_stub)
        return update_endpoints_stubs

    def _gather_temp_endpoints(self, new_cluster_ids, update_endpoints_stubs):

        responses = []
        for stub in update_endpoints_stubs:
            response = self._call_get_cluster_endpoints(stub)

            responses.append(response)
        return responses

    def _assign_temporary_endpoints(self, cluster_endpoints_list) -> dict[int, vector_db_pb2.ServerEndpointList]:
        # TODO: Worry about thread safety
        temp_endpoints: dict[int, vector_db_pb2.ServerEndpointList] = {}
        for endpoints in cluster_endpoints_list:
            temp_endpoints = self.update_temp_endpoints(endpoints, temp_endpoints)
        return temp_endpoints

    def _add_new_channels_from_temp_endpoints(self, temp_endpoints):
        responses = []

        for node, newEndpoints in temp_endpoints.items():

            # Compare node channel result
            (channel_endpoints, add_new_channel) = self.check_for_new_endpoints(
                node, newEndpoints
            )

            if add_new_channel:
                if channel_endpoints:
                    response = self._call_close_on_channel(channel_endpoints)
                    responses.append(response)

                self.add_new_channel_to_node_channels(node, newEndpoints)

        return responses

    def _close_old_channels_from_node_channels(self, temp_endpoints):
        responses = []

        for node, channel_endpoints in list(self._node_channels.items()):
            if not temp_endpoints.get(node):
                # TODO: Wait for all calls to drain
                response = self._call_close_on_channel(channel_endpoints)
                responses.append(response)

                del self._node_channels[node]

        return responses
