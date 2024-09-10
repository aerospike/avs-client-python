from typing import Any, Optional, Union
import time
import numpy as np
from . import conversions

from .proto_generated import transact_pb2
from .proto_generated import transact_pb2_grpc
from .. import types
from .proto_generated import types_pb2
from . import helpers


class BaseClient(object):

    def _prepare_seeds(self, seeds) -> None:
        return helpers._prepare_seeds(seeds)

    def _prepare_put(
        self,
        namespace,
        key,
        record_data,
        set_name,
        write_type,
        ignore_mem_queue_full,
        timeout,
        logger,
    ) -> None:

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
        namespace,
        key,
        record_data,
        set_name,
        ignore_mem_queue_full,
        timeout,
        logger,
    ) -> None:
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

    def _prepare_update(
        self,
        namespace,
        key,
        record_data,
        set_name,
        ignore_mem_queue_full,
        timeout,
        logger,
    ) -> None:
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
        namespace,
        key,
        record_data,
        set_name,
        ignore_mem_queue_full,
        timeout,
        logger,
    ) -> None:
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
        self, namespace, key, field_names, set_name, timeout, logger
    ) -> None:

        logger.debug(
            "Getting record: namespace=%s, key=%s, field_names:%s, set_name:%s, timeout:%s",
            namespace,
            key,
            field_names,
            set_name,
            timeout,
        )

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        key = self._get_key(namespace, set_name, key)
        projection_spec = self._get_projection_spec(field_names=field_names)

        transact_stub = self._get_transact_stub()
        get_request = transact_pb2.GetRequest(key=key, projection=projection_spec)

        return (transact_stub, key, get_request, kwargs)

    def _prepare_exists(self, namespace, key, set_name, timeout, logger) -> None:

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

    def _prepare_delete(self, namespace, key, set_name, timeout, logger) -> None:

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
        self, namespace, key, index_name, index_namespace, set_name, timeout, logger
    ) -> None:

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
        namespace,
        index_name,
        query,
        limit,
        search_params,
        field_names,
        timeout,
        logger,
    ) -> None:

        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout

        logger.debug(
            "Performing vector search: namespace=%s, index_name=%s, query=%s, limit=%s, search_params=%s, field_names=%s, timeout:%s",
            namespace,
            index_name,
            query,
            limit,
            search_params,
            field_names,
            timeout,
        )

        if search_params != None:
            search_params = search_params._to_pb2()

        projection_spec = self._get_projection_spec(field_names=field_names)

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

    def _respond_get(self, response, key) -> None:
        return types.RecordWithKey(
            key=conversions.fromVectorDbKey(key),
            fields=conversions.fromVectorDbRecord(response),
        )

    def _respond_exists(self, response) -> None:
        return response.value

    def _respond_is_indexed(self, response) -> None:
        return response.value

    def _respond_neighbor(self, response) -> None:
        return conversions.fromVectorDbNeighbor(response)

    def _get_projection_spec(
        self,
        *,
        field_names: Optional[list] = None,
        exclude_field_names: Optional[list] = None,
    ):

        if field_names:
            include = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.SPECIFIED, fields=field_names
            )
            exclude = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.NONE, fields=None
            )
        elif exclude_field_names:
            include = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.NONE, fields=None
            )
            exclude = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.SPECIFIED, fields=exclude_field_names
            )
        else:
            include = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.ALL, fields=None
            )
            exclude = transact_pb2.ProjectionFilter(
                type=transact_pb2.ProjectionType.NONE, fields=None
            )

        projection_spec = transact_pb2.ProjectionSpec(include=include, exclude=exclude)

        return projection_spec

    def _get_key(
        self, namespace: str, set: str, key: Union[int, str, bytes, bytearray]
    ):

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

    def _prepare_wait_for_index_waiting(self, namespace, name, wait_interval):
        return helpers._prepare_wait_for_index_waiting(
            self, namespace, name, wait_interval
        )

    def _check_timeout(self, start_time, timeout):
        if start_time + timeout < time.monotonic():
            raise AVSClientError(message="timed-out waiting for index creation")

    def _check_completion_condition(
        self, start_time, timeout, index_status, unmerged_record_initialized
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
