import logging
from logging import Logger
from typing import Any, Optional, Union, Tuple, Dict, List
import time
import numpy as np
from . import conversions

from .proto_generated import transact_pb2, index_pb2, index_pb2_grpc
from .proto_generated import transact_pb2_grpc
from .proto_generated.transact_pb2_grpc import TransactServiceStub
from .. import types, RecordWithKey, Neighbor
from .proto_generated import types_pb2
from . import helpers
from ..types import AVSClientError


class BaseClient(object):

    def _prepare_seeds(self, seeds) -> None:
        return helpers._prepare_seeds(seeds)

    def _prepare_put(
        self,
        namespace: str,
        key: Union[int, str, bytes, bytearray, np.generic, np.ndarray],
        record_data: Dict[str, Any],
        set_name: Optional[str],
        write_type: transact_pb2.WriteType,  # Adjust based on the specific type if available
        ignore_mem_queue_full: Optional[bool],
        timeout: Optional[int],
        logger: logging.Logger,
    ) -> tuple[TransactServiceStub, transact_pb2.PutRequest, dict[str, Any]]:

        logger.debug(
            "Putting record: namespace=%s, key=%s, record_data:%s, set_name:%s, ignore_mem_queue_full %s, timeout:%s",
            namespace,
            key,
            record_data,
            set_name,
            ignore_mem_queue_full,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        key = self._get_key(namespace, set_name, key)
        field_list = []

        for k, v in record_data.items():
            if isinstance(v, np.ndarray):
                field_list.append(
                    types_pb2.Field(
                        name=k, value=conversions.toVectorDbValue(v.tolist())
                    )
                )

            else:
                field_list.append(
                    types_pb2.Field(name=k, value=conversions.toVectorDbValue(v))
                )

        transact_stub = self._get_transact_stub()
        put_request = transact_pb2.PutRequest(
            key=key,
            writeType=write_type,
            fields=field_list,
            ignoreMemQueueFull=ignore_mem_queue_full,
        )

        return (transact_stub, put_request, kwargs)

    def _prepare_insert(
        self,
        namespace: str,
        key: Union[int, str, bytes, bytearray, np.generic, np.ndarray],
        record_data: Dict[str, Any],
        set_name: Optional[str],
        ignore_mem_queue_full: Optional[bool],
        timeout: Optional[int],
        logger: logging.Logger,
    ) -> tuple[TransactServiceStub, transact_pb2.PutRequest, dict[str, Any]]:
        return self._prepare_put(
            namespace,
            key,
            record_data,
            set_name,
            transact_pb2.WriteType.INSERT_ONLY,
            ignore_mem_queue_full,
            timeout,
            logger,
        )


    set_name: Optional[str] = None,
    ignore_mem_queue_full: Optional[bool] = False,
    timeout: Optional[int] = None,

    def _prepare_update(
        self,
        namespace: str,
        key: Union[int, str, bytes, bytearray, np.generic, np.ndarray],
        record_data: dict[str, Any],
        set_name: Optional[str],
        ignore_mem_queue_full: Optional[bool],
        timeout: Optional[int],
        logger: logging.Logger,
    ) -> tuple[TransactServiceStub, transact_pb2.PutRequest, dict[str, Any]]:
        return self._prepare_put(
            namespace,
            key,
            record_data,
            set_name,
            transact_pb2.WriteType.UPDATE_ONLY,
            ignore_mem_queue_full,
            timeout,
            logger,
        )


    def _prepare_upsert(
        self,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        record_data: dict[str, Any],
        set_name: Optional[str],
        ignore_mem_queue_full: Optional[bool],
        timeout: Optional[int],
        logger: Logger,
    ) -> tuple[TransactServiceStub, transact_pb2.PutRequest, dict[str, Any]]:
        return self._prepare_put(
            namespace,
            key,
            record_data,
            set_name,
            transact_pb2.WriteType.UPSERT,
            ignore_mem_queue_full,
            timeout,
            logger,
        )

    def _prepare_get(
        self, namespace, key, include_fields, exclude_fields, set_name, timeout, logger
    ) -> tuple[TransactServiceStub, types_pb2.Key, transact_pb2.GetRequest, dict[str, Any]]:

        logger.debug(
            "Getting record: namespace=%s, key=%s, include_fields:%s, exclude_fields:%s, set_name:%s, timeout:%s",
            namespace,
            key,
            include_fields,
            exclude_fields,
            set_name,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        key: types_pb2.Key = self._get_key(namespace, set_name, key)
        projection_spec = self._get_projection_spec(include_fields=include_fields, exclude_fields=exclude_fields)

        transact_stub = self._get_transact_stub()
        get_request = transact_pb2.GetRequest(key=key, projection=projection_spec)

        return (transact_stub, key, get_request, kwargs)

    def _prepare_exists(self, namespace, key, set_name, timeout, logger) -> tuple[
        TransactServiceStub, transact_pb2.ExistsRequest, dict[str, Any]]:

        logger.debug(
            "Getting record existence: namespace=%s, key=%s, set_name:%s, timeout:%s",
            namespace,
            key,
            set_name,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        key = self._get_key(namespace, set_name, key)

        transact_stub = self._get_transact_stub()
        exists_request = transact_pb2.ExistsRequest(key=key)

        return (transact_stub, exists_request, kwargs)

    def _prepare_delete(self, namespace, key, set_name, timeout, logger) -> tuple[
        TransactServiceStub, transact_pb2.DeleteRequest, dict[str, Any]]:

        logger.debug(
            "Deleting record: namespace=%s, key=%s, set_name=%s, timeout:%s",
            namespace,
            key,
            set_name,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        key = self._get_key(namespace, set_name, key)

        transact_stub = self._get_transact_stub()
        delete_request = transact_pb2.DeleteRequest(key=key)

        return (transact_stub, delete_request, kwargs)

    def _prepare_is_indexed(
        self, namespace: str, key: Union[int, str, bytes, bytearray, np.generic, np.ndarray], index_name: str, index_namespace: Optional[str], set_name: Optional[str], timeout: Optional[int],logger: logging.Logger
    ) -> tuple[TransactServiceStub, transact_pb2.IsIndexedRequest, dict[str, Any]]:

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        logger.debug(
            "Checking if index exists: namespace=%s, key=%s, index_name=%s, index_namespace=%s, set_name=%s, timeout:%s",
            namespace,
            key,
            index_name,
            index_namespace,
            set_name,
            timeout,
        )

        if not index_namespace:
            index_namespace = namespace
        index_id = types_pb2.IndexId(namespace=index_namespace, name=index_name)
        key = self._get_key(namespace, set_name, key)

        transact_stub = self._get_transact_stub()
        is_indexed_request = transact_pb2.IsIndexedRequest(key=key, indexId=index_id)

        return (transact_stub, is_indexed_request, kwargs)

    def _prepare_vector_search(
        self,
        namespace: str,
        index_name: str,
        query: Union[List[Union[bool, float]], np.ndarray],
        limit: int,
        search_params: Optional[types.HnswSearchParams],
        include_fields: Optional[List[str]],
        exclude_fields: Optional[List[str]],
        timeout: Optional[int],
        logger: logging.Logger,
    ) -> tuple[TransactServiceStub, Any, dict[str, Any]]:

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        logger.debug(
            "Performing vector search: namespace=%s, index_name=%s, query=%s, limit=%s, search_params=%s, include_fields=%s, exclude_fields=%s, timeout:%s",
            namespace,
            index_name,
            query,
            limit,
            search_params,
            include_fields,
            exclude_fields,
            timeout,
        )

        if search_params != None:
            search_params = search_params._to_pb2()

        projection_spec = self._get_projection_spec(include_fields=include_fields, exclude_fields=exclude_fields)

        index = types_pb2.IndexId(namespace=namespace, name=index_name)

        if isinstance(query, np.ndarray):
            query_vector = conversions.toVectorDbValue(query.tolist()).vectorValue
        else:
            query_vector = conversions.toVectorDbValue(query).vectorValue

        transact_stub = self._get_transact_stub()

        vector_search_request = transact_pb2.VectorSearchRequest(
            index=index,
            queryVector=query_vector,
            limit=limit,
            hnswSearchParams=search_params,
            projection=projection_spec,
        )

        return (transact_stub, vector_search_request, kwargs)

    def _get_transact_stub(self):
        return transact_pb2_grpc.TransactServiceStub(
            self._channel_provider.get_channel()
        )

    def _respond_get(self, response, key) -> RecordWithKey:
        return types.RecordWithKey(
            key=conversions.fromVectorDbKey(key),
            fields=conversions.fromVectorDbRecord(response),
        )

    def _respond_exists(self, response) -> None:
        return response.value

    def _respond_is_indexed(self, response) -> None:
        return response.value

    def _respond_neighbor(self, response) -> Neighbor:
        return conversions.fromVectorDbNeighbor(response)

    def _get_projection_spec(
        self,
        *,
        include_fields: Optional[list] = None,
        exclude_fields: Optional[list] = None,
    ) -> transact_pb2.ProjectionSpec:
        # include all fields by default
        if include_fields is None:
            include = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.ALL, fields=None
            )
        else:
            include = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.SPECIFIED, fields=include_fields
            )

        if exclude_fields is None:
            exclude = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.NONE, fields=None
            )
        else:
            exclude = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.SPECIFIED, fields=exclude_fields
            )

        projection_spec = transact_pb2.ProjectionSpec(include=include, exclude=exclude)

        return projection_spec

    def _get_key(
        self, namespace: str, set: str, key: Union[int, str, bytes, bytearray]
    ) -> types_pb2.Key:

        if isinstance(key, np.ndarray):
            key = key.tobytes()

        if isinstance(key, np.generic):
            key = key.item()

        if isinstance(key, str):
            key = types_pb2.Key(namespace=namespace, set=set, stringValue=key)
        elif isinstance(key, int):
            key = types_pb2.Key(namespace=namespace, set=set, longValue=key)
        elif isinstance(key, (bytes, bytearray)):
            key = types_pb2.Key(namespace=namespace, set=set, bytesValue=key)
        else:
            raise Exception("Invalid key type" + str(type(key)))
        return key

    def _prepare_wait_for_index_waiting(self, namespace: str, name: str, wait_interval: int) -> (
        Tuple)[index_pb2_grpc.IndexServiceStub, float, float, bool, int, index_pb2.IndexGetRequest]:
        return helpers._prepare_wait_for_index_waiting(
            self, namespace, name, wait_interval
        )

    def _check_timeout(self, start_time: int, timeout: int):
        if start_time + timeout < time.monotonic():
            raise AVSClientError(message="timed-out waiting for index creation")

    def _check_completion_condition(
        self, start_time: int, timeout:int , index_status, unmerged_record_initialized
    ):
        self._check_timeout(start_time, timeout)

        if start_time + 10 < time.monotonic():
            unmerged_record_initialized = True

        if index_status.unmergedRecordCount > 0:
            unmerged_record_initialized = True

        if (
            index_status.unmergedRecordCount == 0
            and unmerged_record_initialized == True
        ):
            return True
        else:
            return False
