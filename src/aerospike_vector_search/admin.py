import logging
import sys
import time
from typing import Optional, Union

import grpc

from . import types
from .internal import channel_provider
from .shared.admin_helpers import BaseClient
from .shared.conversions import fromIndexStatusResponse
from .types import IndexDefinition, Role

logger = logging.getLogger(__name__)


class Client(BaseClient):
    """
    Aerospike Vector Search Admin Client

    This client is designed to conduct Aerospike Vector Search administrative operation such as creating indexes, querying index information, and dropping indexes.

    :param seeds: Defines the AVS nodes to which you want AVS to connect. AVS iterates through the seed nodes. After connecting to a node, AVS discovers all the nodes in the cluster.
    :type seeds: Union[types.HostPort, tuple[types.HostPort, ...]]

    :param listener_name: An external (NATed) address and port combination that differs from the actual address and port where AVS is listening. Clients can access AVS on a node using the advertised listener address and port. Defaults to None.
    :type listener_name: Optional[str]

    :param is_loadbalancer: If true, the first seed address will be treated as a load balancer node. Defaults to False.
    :type is_loadbalancer: Optional[bool]

    :param service_config_path: Path to the service configuration file. Defaults to None.
    :type service_config_path: Optional[str]

    :param username: Username for Role-Based Access. Defaults to None.
    :type username: Optional[str]

    :param password: Password for Role-Based Access. Defaults to None.
    :type password: Optional[str]

    :param root_certificate: The PEM-encoded root certificates as a byte string. Defaults to None.
    :type root_certificate: Optional[list[bytes], bytes]

    :param certificate_chain: The PEM-encoded certificate chain as a byte string. Defaults to None.
    :type certificate_chain: Optional[bytes]

    :param private_key: The PEM-encoded private key as a byte string. Defaults to None.
    :type private_key: Optional[bytes]

    :raises AVSClientError: Raised when no seed host is provided.

    """

    def __init__(
        self,
        *,
        seeds: Union[types.HostPort, tuple[types.HostPort, ...]],
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
        seeds = self._prepare_seeds(seeds)

        self._channel_provider = channel_provider.ChannelProvider(
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

    def index_create(
        self,
        *,
        namespace: str,
        name: str,
        vector_field: str,
        dimensions: int,
        vector_distance_metric: types.VectorDistanceMetric = (
            types.VectorDistanceMetric.SQUARED_EUCLIDEAN
        ),
        sets: Optional[str] = None,
        index_params: Optional[types.HnswParams] = None,
        index_labels: Optional[dict[str, str]] = None,
        index_storage: Optional[types.IndexStorage] = None,
        timeout: Optional[int] = 100_000,
    ) -> None:
        """
        Create an index.

        :param namespace: The namespace for the index.
        :type namespace: str

        :param name: The name of the index.
        :type name: str

        :param vector_field: The name of the field containing vector data.
        :type vector_field: str

        :param dimensions: The number of dimensions in the vector data.
        :type dimensions: int

        :param vector_distance_metric:
            The distance metric used to compare when performing a vector search.
            Defaults to :class:`VectorDistanceMetric.SQUARED_EUCLIDEAN`.
        :type vector_distance_metric: types.VectorDistanceMetric

        :param sets: The set used for the index. Defaults to None.
        :type sets: Optional[str]

        :param index_params: (Optional[types.HnswParams], optional): Parameters used for tuning
            vector search. Defaults to None. If index_params is None, then the default values
            specified for :class:`types.HnswParams` will be used.
        :type index_params: Optional[types.HnswParams]

        :param index_labels: Metadata associated with the index. Defaults to None.
        :type index_labels: Optional[dict[str, str]]

        :param index_storage: Namespace and set where index overhead (non-vector data) is stored.
        :type index_storage: Optional[types.IndexStorage]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            This method creates an index with the specified parameters and waits for the index creation to complete.
            It waits for up to 100,000 seconds for the index creation to complete.
        """

        (index_stub, index_create_request, kwargs) = self._prepare_index_create(
            namespace,
            name,
            vector_field,
            dimensions,
            vector_distance_metric,
            sets,
            index_params,
            index_labels,
            index_storage,
            timeout,
            logger,
        )

        try:
            index_stub.Create(
                index_create_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to create index with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        try:
            self._wait_for_index_creation(
                namespace=namespace, name=name, timeout=100_000
            )
        except grpc.RpcError as e:
            logger.error("Failed waiting for creation with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def index_update(
            self,
            *,
            namespace: str,
            name: str,
            index_labels: Optional[dict[str, str]] = None,
            hnsw_update_params: Optional[types.HnswIndexUpdate] = None,
            timeout: Optional[int] = 100_000,
    ) -> None:
        """
        Update an existing index.

        :param namespace: The namespace for the index.
        :type namespace: str

        :param name: The name of the index.
        :type name: str

        :param index_labels: Optional labels associated with the index. Defaults to None.
        :type index_labels: Optional[dict[str, str]]

        :param hnsw_update_params: Parameters for updating HNSW index settings.
        :type hnsw_update_params: Optional[types.HnswIndexUpdate]

        :param timeout: Time in seconds (default 100_000) this operation will wait before raising an error.
        :type timeout: int

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to update the index.
        """
        (index_stub, index_update_request, kwargs) = self._prepare_index_update(
            namespace = namespace,
            name = name,
            index_labels = index_labels,
            hnsw_update_params = hnsw_update_params,
            timeout = timeout,
            logger = logger,
        )

        try:
            index_stub.Update(
                index_update_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to update index with error: %s", e)
            raise types.AVSServerError(rpc_error=e)


    def index_drop(
        self, *, namespace: str, name: str, timeout: Optional[int] = None
    ) -> None:
        """
        Drop an index.

        :param namespace: The namespace of the index.
        :type name: str

        :param name: The name of the index.
        :type name: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to drop the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            This method drops an index with the specified parameters and waits for the index deletion to complete.
            It waits for up to 100,000 seconds for the index deletion to complete.
        """

        (index_stub, index_drop_request, kwargs) = self._prepare_index_drop(
            namespace, name, timeout, logger
        )

        try:
            index_stub.Drop(
                index_drop_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to drop index with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        try:
            self._wait_for_index_deletion(
                namespace=namespace, name=name, timeout=100_000
            )
        except grpc.RpcError as e:
            logger.error("Failed waiting for deletion with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def index_list(
        self, timeout: Optional[int] = None, apply_defaults: Optional[bool] = True
    ) -> list[IndexDefinition]:
        """
        List all indices.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        :param apply_defaults: Apply default values to parameters which are not set by user. Defaults to True.
        :type apply_defaults: bool

        Returns: list[dict]: A list of indices.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to list the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        (index_stub, index_list_request, kwargs) = self._prepare_index_list(
            timeout, logger, apply_defaults
        )

        try:
            response = index_stub.List(
                index_list_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to list indexes with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        return self._respond_index_list(response)

    def index_get(
        self,
        *,
        namespace: str,
        name: str,
        timeout: Optional[int] = None,
        apply_defaults: Optional[bool] = True,
    ) -> IndexDefinition:
        """
        Retrieve the information related with an index.

        :param namespace: The namespace of the index.
        :type namespace: str

        :param name: The name of the index.
        :type name: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        :param apply_defaults: Apply default values to parameters which are not set by user. Defaults to True.
        :type apply_defaults: bool

        Returns: dict[str, Union[int, str]: Information about an index.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """

        (index_stub, index_get_request, kwargs) = self._prepare_index_get(
            namespace, name, timeout, logger, apply_defaults
        )

        try:
            response = index_stub.Get(
                index_get_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to get index with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        return self._respond_index_get(response)

    def index_get_status(
        self, *, namespace: str, name: str, timeout: Optional[int] = None
    ) -> types.IndexStatusResponse:
        """
        Retrieve the number of records queued to be merged into an index.

        :param namespace: The namespace of the index.
        :type name: str

        :param name: The name of the index.
        :type name: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Returns: IndexStatusResponse: AVS response containing index status information.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get the index status.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            This method retrieves the status of the specified index. If index_get_status is called the vector client puts some records into Aerospike Vector Search,
            the records may not immediately begin to merge into the index. To wait for all records to be merged into an index, use vector_client.wait_for_index_completion.

            Warning: This API is subject to change.
        """
        (index_stub, index_get_status_request, kwargs) = self._prepare_index_get_status(
            namespace, name, timeout, logger
        )

        try:
            response = index_stub.GetStatus(
                index_get_status_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
            return fromIndexStatusResponse(response)
        except grpc.RpcError as e:
            logger.error("Failed to get index status with error: %s", e)
            raise types.AVSServerError(rpc_error=e)




    def add_user(
        self,
        *,
        username: str,
        password: str,
        roles: list[str],
        timeout: Optional[int] = None,
    ) -> None:
        """
        Add role-based access AVS User to the AVS Server.

        :param username: Username for the new user.
        :type username: str

        :param password: Password for the new user.
        :type password: str

        :param roles: Roles for the new user.
        :type roles: list[str]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int


        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to add a user.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        (user_admin_stub, add_user_request, kwargs) = self._prepare_add_user(
            username, password, roles, timeout, logger
        )

        try:
            user_admin_stub.AddUser(
                add_user_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to add user with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def update_credentials(
        self, *, username: str, password: str, timeout: Optional[int] = None
    ) -> None:
        """
        Update AVS User credentials.

        :param username: Username of the user to update.
        :type username: str

        :param password: New password for the user.
        :type password: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int


        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to update a users credentials.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        (user_admin_stub, update_credentials_request, kwargs) = (
            self._prepare_update_credentials(username, password, timeout, logger)
        )

        try:
            user_admin_stub.UpdateCredentials(
                update_credentials_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to update credentials with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def drop_user(self, *, username: str, timeout: Optional[int] = None) -> None:
        """
        Drops AVS User from the AVS Server.

        :param username: Username of the user to drop.
        :type username: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int


        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to drop a user
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        (user_admin_stub, drop_user_request, kwargs) = self._prepare_drop_user(
            username, timeout, logger
        )

        try:
            user_admin_stub.DropUser(
                drop_user_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to drop user with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def get_user(self, *, username: str, timeout: Optional[int] = None) -> types.User:
        """
        Retrieves AVS User information from the AVS Server.

        :param username: Username of the user to be retrieved.
        :type username: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        return: types.User: AVS User

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get a user.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        (user_admin_stub, get_user_request, kwargs) = self._prepare_get_user(
            username, timeout, logger
        )

        try:
            response = user_admin_stub.GetUser(
                get_user_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to get user with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        return self._respond_get_user(response)

    def list_users(self, timeout: Optional[int] = None) -> list[types.User]:
        """
        List all users existing on the AVS Server.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        return: list[types.User]: list of AVS Users

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to list users.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        (user_admin_stub, list_users_request, kwargs) = self._prepare_list_users(
            timeout, logger
        )

        try:
            response = user_admin_stub.ListUsers(
                list_users_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to list user with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        return self._respond_list_users(response)

    def grant_roles(
        self, *, username: str, roles: list[str], timeout: Optional[int] = None
    ) -> None:
        """
        Grant roles to existing AVS Users.

        :param username: Username of the user which will receive the roles.
        :type username: str

        :param roles: Roles the specified user will receive.
        :type roles: list[str]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to grant roles.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        (user_admin_stub, grant_roles_request, kwargs) = self._prepare_grant_roles(
            username, roles, timeout, logger
        )

        try:
            user_admin_stub.GrantRoles(
                grant_roles_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to grant roles with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def revoke_roles(
        self, *, username: str, roles: list[str], timeout: Optional[int] = None
    ) -> None:
        """
        Revoke roles from existing AVS Users.

        :param username: Username of the user undergoing role removal.
        :type username: str

        :param roles: Roles to be revoked.
        :type roles: list[str]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to revoke roles.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        (user_admin_stub, revoke_roles_request, kwargs) = self._prepare_revoke_roles(
            username, roles, timeout, logger
        )

        try:
            user_admin_stub.RevokeRoles(
                revoke_roles_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to revoke roles with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def list_roles(self, timeout: Optional[int] = None) -> list[Role]:
        """
        List roles available on the AVS server.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        returns: list[str]: Roles available in the AVS Server.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to list roles.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        (user_admin_stub, list_roles_request, kwargs) = self._prepare_list_roles(
            timeout, logger
        )

        try:
            response = user_admin_stub.ListRoles(
                list_roles_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to list roles with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        return self._respond_list_roles(response)

    def _wait_for_index_creation(
        self,
        *,
        namespace: str,
        name: str,
        timeout: int = sys.maxsize,
        wait_interval: float = 0.1,
    ) -> None:
        """
        Wait for the index to be created.
        """

        (index_stub, wait_interval, start_time, _, _, index_creation_request) = (
            self._prepare_wait_for_index_waiting(namespace, name, wait_interval)
        )
        while True:
            self._check_timeout(start_time, timeout)
            try:
                index_stub.GetStatus(
                    index_creation_request,
                    credentials=self._channel_provider.get_token(),
                )
                logger.debug("Index created successfully")
                # Index has been created
                return
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:

                    # Wait for some more time.
                    time.sleep(wait_interval)
                else:
                    logger.error("Failed waiting for index creation with error: %s", e)
                    raise types.AVSServerError(rpc_error=e)

    def _wait_for_index_deletion(
        self,
        *,
        namespace: str,
        name: str,
        timeout: int = sys.maxsize,
        wait_interval: float = 0.1,
    ) -> None:
        """
        Wait for the index to be deleted.
        """

        # Wait interval between polling
        (index_stub, wait_interval, start_time, _, _, index_deletion_request) = (
            self._prepare_wait_for_index_waiting(namespace, name, wait_interval)
        )

        while True:
            self._check_timeout(start_time, timeout)

            try:
                index_stub.GetStatus(
                    index_deletion_request,
                    credentials=self._channel_provider.get_token(),
                )
                # Wait for some more time.
                time.sleep(wait_interval)
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    logger.debug("Index deleted successfully")
                    # Index has been created
                    return
                else:
                    logger.error("Failed waiting for index deletion with error: %s", e)
                    raise types.AVSServerError(rpc_error=e)

    def close(self):
        """
        Close the Aerospike Vector Search Admin Client.

        This method closes gRPC channels connected to Aerospike Vector Search.

        Note:
            This method should be called when the VectorDbAdminClient is no longer needed to release resources.
        """
        self._channel_provider.close()

    def __enter__(self):
        """
        Enter a context manager for the admin client.

        Returns:
            VectorDbAdminClient: Aerospike Vector Search Admin Client instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a context manager for the admin client.
        """
        self.close()
