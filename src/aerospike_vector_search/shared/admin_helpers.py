import asyncio
import logging
from typing import Any, Optional, Union
import time

import google.protobuf.empty_pb2
from google.protobuf.json_format import MessageToDict
import grpc

from . import helpers
from .proto_generated import index_pb2_grpc, user_admin_pb2_grpc
from .proto_generated import types_pb2, user_admin_pb2
from .. import types

logger = logging.getLogger(__name__)

empty = google.protobuf.empty_pb2.Empty()


class BaseClient(object):

    def _prepare_seeds(self, seeds) -> None:
        return helpers._prepare_seeds(seeds)

    def _prepare_index_create(
        self,
        namespace,
        name,
        vector_field,
        dimensions,
        vector_distance_metric,
        sets,
        index_params,
        index_meta_data,
        index_storage,
        timeout,
        logger,
    ) -> None:

        logger.debug(
            "Creating index: namespace=%s, name=%s, vector_field=%s, dimensions=%d, vector_distance_metric=%s, "
            "sets=%s, index_params=%s, index_meta_data=%s, index_storage=%s, timeout=%s",
            namespace,
            name,
            vector_field,
            dimensions,
            vector_distance_metric,
            sets,
            index_params,
            index_meta_data,
            index_storage,
            timeout
        )

        if sets and not sets.strip():
            sets = None
        if index_params != None:
            index_params = index_params._to_pb2()
        if index_storage != None:
            index_storage = index_storage._to_pb2()

        id = self._get_index_id(namespace, name)
        vector_distance_metric = vector_distance_metric.value

        index_stub = self._get_index_stub()

        index_create_request = types_pb2.IndexDefinition(
            id=id,
            vectorDistanceMetric=vector_distance_metric,
            setFilter=sets,
            hnswParams=index_params,
            field=vector_field,
            dimensions=dimensions,
            labels=index_meta_data,
            storage=index_storage
        )
        return (index_stub, index_create_request)

    def _prepare_index_drop(self, namespace, name, timeout, logger) -> None:

        logger.debug("Dropping index: namespace=%s, name=%s, timeout=%s", namespace, name, timeout)

        index_stub = self._get_index_stub()
        index_drop_request = self._get_index_id(namespace, name)

        return (index_stub, index_drop_request)

    def _prepare_index_list(self, timeout, logger) -> None:

        logger.debug("Getting index list: timeout=%s", timeout)

        index_stub = self._get_index_stub()
        index_list_request = empty

        return (index_stub, index_list_request)

    def _prepare_index_get(self, namespace, name, timeout, logger) -> None:

        logger.debug(
            "Getting index information: namespace=%s, name=%s, timeout=%s", namespace, name, timeout
        )

        index_stub = self._get_index_stub()
        index_get_request = self._get_index_id(namespace, name)

        return (index_stub, index_get_request)

    def _prepare_index_get_status(self, namespace, name, timeout, logger) -> None:

        logger.debug("Getting index status: namespace=%s, name=%s, timeout=%s", namespace, name, timeout)

        index_stub = self._get_index_stub()
        index_get_status_request = self._get_index_id(namespace, name)

        return (index_stub, index_get_status_request)

    def _prepare_add_user(self, username, password, roles, timeout, logger) -> None:
        logger.debug("Getting index status: username=%s, password=%s, roles=%s, timeout=%s", username, password, roles, timeout)

        user_admin_stub = self._get_user_admin_stub()
        credentials = helpers._get_credentials(username, password)
        add_user_request = user_admin_pb2.AddUserRequest(credentials=credentials, roles=roles)

        return (user_admin_stub, add_user_request)

    def _prepare_update_credentials(self, username, password, timeout, logger) -> None:
        logger.debug("Getting index status: username=%s, password=%s, timeout=%s", username, password, timeout)

        user_admin_stub = self._get_user_admin_stub()
        credentials = helpers._get_credentials(username, password)
        update_user_request = user_admin_pb2.UpdateCredentialsRequest(credentials=credentials)

        return (user_admin_stub, update_user_request)

    def _prepare_drop_user(self, username, timeout, logger) -> None:
        logger.debug("Getting index status: username=%s, timeout=%s", username, timeout)

        user_admin_stub = self._get_user_admin_stub()
        drop_user_request = user_admin_pb2.DropUserRequest(username=username)

        return (user_admin_stub, drop_user_request)

    def _prepare_get_user(self, username, timeout, logger) -> None:
        logger.debug("Getting index status: username=%s, timeout=%s", username, timeout)

        user_admin_stub = self._get_user_admin_stub()
        get_user_request = user_admin_pb2.GetUserRequest(username=username)

        return (user_admin_stub, get_user_request)

    def _prepare_list_users(self, timeout, logger) -> None:
        logger.debug("Getting index status")

        user_admin_stub = self._get_user_admin_stub()
        list_users_request = empty

        return (user_admin_stub, list_users_request)

    def _prepare_grant_roles(self, username, roles, timeout, logger) -> None:
        logger.debug("Getting index status: username=%s, roles=%s, timeout=%s", username, roles, timeout)

        user_admin_stub = self._get_user_admin_stub()
        grant_roles_request = user_admin_pb2.GrantRolesRequest(username=username, roles=roles)

        return (user_admin_stub, grant_roles_request)

    def _prepare_revoke_roles(self, username, roles, timeout, logger) -> None:
        logger.debug("Getting index status: username=%s, roles=%s, timeout=%s", username, roles, timeout)

        user_admin_stub = self._get_user_admin_stub()
        revoke_roles_request = user_admin_pb2.RevokeRolesRequest(username=username, roles=roles)

        return (user_admin_stub, revoke_roles_request)

    def _prepare_list_roles(self, timeout, logger) -> None:
        logger.debug("Getting index status: timeout=%s", timeout)

        user_admin_stub = self._get_user_admin_stub()
        list_roles_request = empty

        return (user_admin_stub, list_roles_request)

    def _respond_index_list(self, response) -> None:
        response_list = []
        for index in response.indices:
            response_dict = MessageToDict(index)

            # Modifying dict to adhere to PEP-8 naming
            hnsw_params_dict = response_dict.pop("hnswParams", None)

            hnsw_params_dict["ef_construction"] = hnsw_params_dict.pop(
                "efConstruction", None
            )

            batching_params_dict = hnsw_params_dict.pop("batchingParams", None)
            batching_params_dict["max_records"] = batching_params_dict.pop(
                "maxRecords", None
            )
            hnsw_params_dict["batching_params"] = batching_params_dict

            response_dict["hnsw_params"] = hnsw_params_dict
            response_list.append(response_dict)
        return response_list

    def _respond_index_get(self, response) -> None:
        response_dict = MessageToDict(response)

        # Modifying dict to adhere to PEP-8 naming
        hnsw_params_dict = response_dict.pop("hnswParams", None)

        hnsw_params_dict["ef_construction"] = hnsw_params_dict.pop(
            "efConstruction", None
        )

        batching_params_dict = hnsw_params_dict.pop("batchingParams", None)
        batching_params_dict["max_records"] = batching_params_dict.pop(
            "maxRecords", None
        )
        hnsw_params_dict["batching_params"] = batching_params_dict

        response_dict["hnsw_params"] = hnsw_params_dict
        return response_dict

    def _respond_get_user(self, response) -> None:
        

        return types.User(username=response.username, roles=list(response.roles))

    def _respond_list_users(self, response) -> None:
        user_list = []
        for user in response.users:
            user_list.append(types.User(username=user.username, roles=list(user.roles)))
        return user_list

    def _respond_list_roles(self, response) -> None:
        return list(response.roles)
        
    def _respond_index_get_status(self, response) -> None:
        return response.unmergedRecordCount

    def _get_index_stub(self):
        return index_pb2_grpc.IndexServiceStub(self._channel_provider.get_channel())

    def _get_user_admin_stub(self):
        return user_admin_pb2_grpc.UserAdminServiceStub(self._channel_provider.get_channel())

    def _get_index_id(self, namespace, name):
        return types_pb2.IndexId(namespace=namespace, name=name)

    def _get_add_user_request(self, namespace, name):
        return user_admin_pb2.AddUserRequest(namespace=namespace, name=name)

    def _prepare_wait_for_index_waiting(self, namespace, name, wait_interval):
        return helpers._prepare_wait_for_index_waiting(
            self, namespace, name, wait_interval
        )

    def _check_timeout(self, start_time, timeout):
        if start_time + timeout < time.monotonic():
            raise "timed-out waiting for index creation"