import asyncio
import logging
from typing import Any, Optional, Tuple, List
import time

from google.protobuf.json_format import MessageToDict
import grpc

from . import helpers
from .proto_generated import index_pb2_grpc, user_admin_pb2_grpc
from .proto_generated import types_pb2, user_admin_pb2, index_pb2
from .. import types
from . import conversions
from ..types import AVSClientError, IndexDefinition, HostPort


class BaseClient(object):

    def _prepare_seeds(self, seeds) -> tuple[HostPort, ...]:
        return helpers._prepare_seeds(seeds)

    def _prepare_index_create(
            self,
            namespace: str,
            name: str,
            vector_field: str,
            dimensions: int,
            vector_distance_metric: types.VectorDistanceMetric,
            sets: Optional[str],
            index_params: Optional[types.HnswParams],
            index_labels: Optional[dict[str, str]],
            index_storage: Optional[types.IndexStorage],
            index_mode: Optional[types.IndexMode],
            timeout: Optional[int],
            logger: logging.Logger
    ) -> Tuple[index_pb2_grpc.IndexServiceStub, index_pb2.IndexCreateRequest, dict[str, Any]] :

        logger.debug(
            "Creating index: namespace=%s, name=%s, vector_field=%s, dimensions=%d, vector_distance_metric=%s, "
            "sets=%s, index_params=%s, index_labels=%s, index_storage=%s, index_mode=%s, timeout=%s",
            namespace,
            name,
            vector_field,
            dimensions,
            vector_distance_metric,
            sets,
            index_params,
            index_labels,
            index_storage,
            index_mode,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        if sets and not sets.strip():
            sets = None
        if index_params != None:
            index_params = index_params._to_pb2()
        if index_storage is not None:
            index_storage = index_storage._to_pb2()

        index_id = self._get_index_id(namespace, name)
        index_stub = self._get_index_stub()

        vector_distance_metric = vector_distance_metric._to_proto()

        if index_mode is not None:
            index_mode = index_mode._to_proto()

        index_definition = types_pb2.IndexDefinition(
            id=index_id,
            vectorDistanceMetric=vector_distance_metric,
            setFilter=sets,
            hnswParams=index_params,
            field=vector_field,
            dimensions=dimensions,
            labels=index_labels,
            storage=index_storage,
            mode=index_mode,
        )
        index_create_request = index_pb2.IndexCreateRequest(definition=index_definition)
        return (index_stub, index_create_request, kwargs)

    def _prepare_index_update(
            self,
            namespace: str,
            name: str,
            index_labels: Optional[dict[str, str]],
            hnsw_update_params: Optional[types.HnswIndexUpdate],
            index_mode: Optional[types.IndexMode],
            timeout: Optional[int],
            logger: logging.Logger
    ) -> tuple[index_pb2_grpc.IndexServiceStub, index_pb2.IndexUpdateRequest, dict[str, Any]]:
        """
        Prepares the index update request for updating an existing index.
        """

        logger.debug(
            "Updating index: namespace=%s, name=%s, labels=%s, hnsw_update_params=%s, index_mode=%s, timeout=%s",
            namespace,
            name,
            index_labels,
            hnsw_update_params,
            index_mode,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        index_stub = self._get_index_stub()
        index_id = self._get_index_id(namespace, name)

        # Prepare HNSW update parameters if provided
        hnsw_update = None
        if hnsw_update_params is not None:
            hnsw_update = hnsw_update_params._to_pb2()

        if index_mode is not None:
            index_mode = index_mode._to_proto()

        # Create the IndexUpdateRequest with optional fields
        index_update_request = index_pb2.IndexUpdateRequest(
            indexId=index_id,
            labels=index_labels,
            hnswIndexUpdate=hnsw_update,
            mode=index_mode,
        )

        return (index_stub, index_update_request, kwargs)

    def _prepare_index_drop(self, namespace: str, name: str, timeout: Optional[int], logger: logging.Logger) -> tuple[index_pb2_grpc.IndexServiceStub, index_pb2.IndexDropRequest, dict[str, Any]]:

        logger.debug(
            "Dropping index: namespace=%s, name=%s, timeout=%s",
            namespace,
            name,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        index_stub = self._get_index_stub()
        index_id = self._get_index_id(namespace, name)
        index_drop_request = index_pb2.IndexDropRequest(indexId=index_id)
        return (index_stub, index_drop_request, kwargs)

    def _prepare_index_list(self, timeout: Optional[int], logger: logging.Logger, apply_defaults: Optional[bool]) -> tuple[index_pb2_grpc.IndexServiceStub, index_pb2.IndexListRequest, dict[str, Any]]:

        logger.debug(
            "Getting index list: timeout=%s, apply_defaults=%s",
            timeout,
            apply_defaults,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        index_stub = self._get_index_stub()
        index_list_request: index_pb2.IndexListRequest = index_pb2.IndexListRequest(applyDefaults=apply_defaults)
        return (index_stub, index_list_request, kwargs)

    def _prepare_index_get(
        self, namespace: str, name: str, timeout: Optional[int], logger: logging.Logger, apply_defaults: Optional[bool]
    ) -> tuple[index_pb2_grpc.IndexServiceStub, index_pb2.IndexGetRequest, dict[str, Any]]:

        logger.debug(
            "Getting index information: namespace=%s, name=%s, timeout=%s, apply_defaults=%s",
            namespace,
            name,
            timeout,
            apply_defaults,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        index_stub = self._get_index_stub()
        index_id = self._get_index_id(namespace, name)
        index_get_request = index_pb2.IndexGetRequest(
            indexId=index_id, applyDefaults=apply_defaults
        )
        return (index_stub, index_get_request, kwargs)

    def _prepare_index_get_status(self, namespace: str, name: str, timeout: Optional[int], logger: logging.Logger) -> tuple[
        index_pb2_grpc.IndexServiceStub, index_pb2.IndexStatusRequest, dict[str, Any]]:

        logger.debug(
            "Getting index status: namespace=%s, name=%s, timeout=%s",
            namespace,
            name,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        index_stub = self._get_index_stub()
        index_id = self._get_index_id(namespace, name)
        index_get_status_request = index_pb2.IndexStatusRequest(indexId=index_id)
        return (index_stub, index_get_status_request, kwargs)

    def _prepare_add_user(self, username: str, password: str, roles: list[str], timeout: Optional[int], logger: logging.Logger) -> tuple[
        user_admin_pb2_grpc.UserAdminServiceStub, user_admin_pb2.AddUserRequest, dict[str, Any]]:
        logger.debug(
            "Getting index status: username=%s, password=%s, roles=%s, timeout=%s",
            username,
            password,
            roles,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        user_admin_stub = self._get_user_admin_stub()
        credentials = helpers._get_credentials(username, password)
        add_user_request = user_admin_pb2.AddUserRequest(
            credentials=credentials, roles=roles
        )

        return (user_admin_stub, add_user_request, kwargs)

    def _prepare_update_credentials(self, username: str, password: str, timeout: Optional[int], logger: logging.Logger) -> tuple[
        user_admin_pb2_grpc.UserAdminServiceStub, user_admin_pb2.UpdateCredentialsRequest, dict[str, Any]]:
        logger.debug(
            "Getting index status: username=%s, password=%s, timeout=%s",
            username,
            password,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        user_admin_stub = self._get_user_admin_stub()
        credentials = helpers._get_credentials(username, password)
        update_user_request = user_admin_pb2.UpdateCredentialsRequest(
            credentials=credentials
        )

        return (user_admin_stub, update_user_request, kwargs)

    def _prepare_drop_user(self, username: str, timeout: Optional[int], logger: logging.Logger) -> tuple[user_admin_pb2_grpc.UserAdminServiceStub, user_admin_pb2.DropUserRequest, dict[str, Any]]:
        logger.debug("Getting index status: username=%s, timeout=%s", username, timeout)

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        user_admin_stub = self._get_user_admin_stub()
        drop_user_request = user_admin_pb2.DropUserRequest(username=username)

        return (user_admin_stub, drop_user_request, kwargs)

    def _prepare_get_user(self, username: str, timeout : Optional[int], logger: logging.Logger) -> tuple[user_admin_pb2_grpc.UserAdminServiceStub, user_admin_pb2.GetUserRequest, dict[str, Any]]:
        logger.debug("Getting index status: username=%s, timeout=%s", username, timeout)

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        user_admin_stub = self._get_user_admin_stub()
        get_user_request = user_admin_pb2.GetUserRequest(username=username)

        return (user_admin_stub, get_user_request, kwargs)

    def _prepare_list_users(self, timeout : Optional[int], logger: logging.Logger) -> tuple[user_admin_pb2_grpc.UserAdminServiceStub, Any, dict[str, Any]]:
        logger.debug("Getting index status")

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        user_admin_stub = self._get_user_admin_stub()
        list_users_request = helpers.empty

        return (user_admin_stub, list_users_request, kwargs)

    def _prepare_grant_roles(self, username: str, roles: list[str], timeout: Optional[int], logger: logging.Logger) -> tuple[
        user_admin_pb2_grpc.UserAdminServiceStub, user_admin_pb2.GrantRolesRequest, dict[str, Any]]:
        logger.debug(
            "Getting index status: username=%s, roles=%s, timeout=%s",
            username,
            roles,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        user_admin_stub = self._get_user_admin_stub()
        grant_roles_request = user_admin_pb2.GrantRolesRequest(
            username=username, roles=roles
        )

        return (user_admin_stub, grant_roles_request, kwargs)

    def _prepare_revoke_roles(self, username: str, roles: list[str], timeout: Optional[int], logger) -> tuple[
        user_admin_pb2_grpc.UserAdminServiceStub, user_admin_pb2.RevokeRolesRequest, dict[str, Any]]:
        logger.debug(
            "Getting index status: username=%s, roles=%s, timeout=%s",
            username,
            roles,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        user_admin_stub = self._get_user_admin_stub()
        revoke_roles_request = user_admin_pb2.RevokeRolesRequest(
            username=username, roles=roles
        )

        return (user_admin_stub, revoke_roles_request, kwargs)

    def _prepare_list_roles(self, timeout: Optional[int], logger: logging.Logger) -> tuple[user_admin_pb2_grpc.UserAdminServiceStub, Any, dict[str, Any]]:
        logger.debug("Getting index status: timeout=%s", timeout)

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        user_admin_stub = self._get_user_admin_stub()
        list_roles_request = helpers.empty

        return (user_admin_stub, list_roles_request, kwargs)

    def _respond_index_list(self, response) -> List[types.IndexDefinition]:
        response_list = []
        for index in response.indices:
            response_list.append(conversions.fromIndexDefintion(index))
        return response_list

    def _respond_index_get(self, response: types_pb2.IndexDefinition) -> IndexDefinition:
        return conversions.fromIndexDefintion(response)

    def _respond_get_user(self, response) -> types.User:
        return types.User(username=response.username, roles=list(response.roles))

    def _respond_list_users(self, response) -> List[types.User]:
        user_list = []
        for user in response.users:
            user_list.append(types.User(username=user.username, roles=list(user.roles)))
        return user_list

    def _respond_list_roles(self, response) -> List[types.Role]:
        role_list = []
        for role in response.roles:
            role_list.append(types.Role(id=role.id))
        return role_list


    def _get_index_stub(self) -> index_pb2_grpc.IndexServiceStub:
        return index_pb2_grpc.IndexServiceStub(self._channel_provider.get_channel())

    def _get_user_admin_stub(self) -> user_admin_pb2_grpc.UserAdminServiceStub:
        return user_admin_pb2_grpc.UserAdminServiceStub(
            self._channel_provider.get_channel()
        )

    def _get_index_id(self, namespace, name) -> types_pb2.IndexId:
        return types_pb2.IndexId(namespace=namespace, name=name)

    def _get_add_user_request(self, namespace, name) -> user_admin_pb2.AddUserRequest :
        return user_admin_pb2.AddUserRequest(namespace=namespace, name=name)

    def _prepare_wait_for_index_waiting(self, namespace, name, wait_interval) -> (
        Tuple)[index_pb2_grpc.IndexServiceStub, int, float, bool, int, index_pb2.IndexGetRequest]:
        return helpers._prepare_wait_for_index_waiting(
            self, namespace, name, wait_interval
        )

    def _check_timeout(self, start_time: float, timeout: int):
        if start_time + timeout < time.monotonic():
            raise AVSClientError(message="timed-out waiting for index creation")
