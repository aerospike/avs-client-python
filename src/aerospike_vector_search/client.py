import logging
import sys
import time
from typing import Any, Optional, Union
import warnings

import grpc
import numpy as np

from . import types
from .internal import channel_provider
from .shared.client_helpers import BaseClient as BaseClientMixin
from .shared.client_helpers import _patch_public_methods, _raise_closed
from .shared.admin_helpers import BaseClient as AdminBaseClientMixin
from .shared.conversions import fromIndexStatusResponse

logger = logging.getLogger(__name__)


class Client(BaseClientMixin, AdminBaseClientMixin):
    """
    Aerospike Vector Search Client

    This client specializes in performing database operations with vector data.
    Moreover, the client supports Hierarchical Navigable Small World (HNSW) vector searches,
    allowing users to find vectors similar to a given query vector within an index.

    :param seeds: Defines the AVS nodes to which you want AVS to connect. AVS iterates through the seed nodes. After connecting to a node, AVS discovers all of the nodes in the cluster.
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
        self.closed = False

    def insert(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        record_data: dict[str, Any],
        set_name: Optional[str] = None,
        ignore_mem_queue_full: Optional[bool] = False,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Insert a record into Aerospike Vector Search.

        If record does exist, an exception is raised.
        If record doesn't exist, the record is inserted.

        :param namespace: The namespace for the record.
        :type namespace: str

        :param key: The key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param record_data: The data to be stored in the record.
        :type record_data: dict[str, Any]

        :param set_name: The name of the set to which the record belongs. Defaults to None.
        :type set_name: Optional[str]

        :param ignore_mem_queue_full: Ignore the in-memory queue full error. These records will be written to storage
            and later, the index healer will pick them for indexing. Defaults to False.
        :type ignore_mem_queue_full: int

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to insert a vector.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """

        (transact_stub, insert_request, kwargs) = self._prepare_insert(
            namespace,
            key,
            record_data,
            set_name,
            ignore_mem_queue_full,
            timeout,
            logger,
        )

        try:
            transact_stub.Put(
                insert_request, credentials=self._channel_provider.get_token(), **kwargs
            )
        except grpc.RpcError as e:
            logger.error("Failed to insert vector with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def update(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        record_data: dict[str, Any],
        set_name: Optional[str] = None,
        ignore_mem_queue_full: Optional[bool] = False,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Update a record in Aerospike Vector Search.

        :param namespace: The namespace for the record.
        :type namespace: str

        :param key: The key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param record_data: The data to be stored in the record.
        :type record_data: dict[str, Any]

        :param set_name: The name of the set to which the record belongs. Defaults to None.
        :type set_name: Optional[str]

        :param ignore_mem_queue_full: Ignore the in-memory queue full error. These records will be written to storage
            and later, the index healer will pick them for indexing. Defaults to False.
        :type ignore_mem_queue_full: int

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to update a vector.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        (transact_stub, update_request, kwargs) = self._prepare_update(
            namespace,
            key,
            record_data,
            set_name,
            ignore_mem_queue_full,
            timeout,
            logger,
        )

        try:
            transact_stub.Put(
                update_request, credentials=self._channel_provider.get_token(), **kwargs
            )
        except grpc.RpcError as e:
            logger.error("Failed to update vector with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def upsert(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray, np.generic, np.ndarray],
        record_data: dict[str, Any],
        set_name: Optional[str] = None,
        ignore_mem_queue_full: Optional[bool] = False,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Update a record in Aerospike Vector Search.

        If record does exist, update the record.
        If record doesn't exist, the record is inserted.

        :param namespace: The namespace for the record.
        :type namespace: str

        :param key: The key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param record_data: The data to be stored in the record.
        :type record_data: dict[str, Any]

        :param set_name: The name of the set to which the record belongs. Defaults to None.
        :type set_name: Optional[str]

        :param ignore_mem_queue_full: Ignore the in-memory queue full error. These records will be written to storage
            and later, the index healer will pick them for indexing. Defaults to False.
        :type ignore_mem_queue_full: int

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to upsert a vector.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """

        (transact_stub, upsert_request, kwargs) = self._prepare_upsert(
            namespace,
            key,
            record_data,
            set_name,
            ignore_mem_queue_full,
            timeout,
            logger,
        )

        try:
            transact_stub.Put(
                upsert_request, credentials=self._channel_provider.get_token(), **kwargs
            )
        except grpc.RpcError as e:
            logger.error("Failed to upsert vector with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def get(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        include_fields: Optional[list[str]] = None,
        exclude_fields: Optional[list[str]] = None,
        set_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> types.RecordWithKey:
        """
        Read a record from Aerospike Vector Search.

        :param namespace: The namespace for the record.
        :type namespace: str

        :param key: The key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param include_fields: A list of field names to retrieve from the record.
            When used, fields that are not included are not sent by the server,
            saving on network traffic.
            If a field is listed in both include_fields and exclude_fields,
            exclude_fields takes priority, and the field is not returned.
            If None, all fields are retrieved. Defaults to None.
        :type include_fields: Optional[list[str]]

        :param exclude_fields: A list of field names to exclude from the record.
            When used, the excluded fields are not sent by the server,
            saving on network traffic.
            If None, all fields are retrieved. Defaults to None.
        :type exclude_fields: Optional[list[str]]

        :param set_name: The name of the set from which to read the record. Defaults to None.
        :type set_name: Optional[str]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Returns:
            types.RecordWithKey: A record with its associated key.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get a vector.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        (transact_stub, key, get_request, kwargs) = self._prepare_get(
            namespace, key, include_fields, exclude_fields, set_name, timeout, logger
        )

        try:
            response = transact_stub.Get(
                get_request, credentials=self._channel_provider.get_token(), **kwargs
            )
        except grpc.RpcError as e:
            logger.error("Failed to get vector with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        return self._respond_get(response, key)

    def exists(
        self,
        *,
        namespace: str,
        key: Any,
        set_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Check if a record exists in Aerospike Vector Search.

        :param namespace: The namespace for the record.
        :type namespace: str

        :param key: The key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param set_name: The name of the set to which the record belongs. Defaults to None.
        :type set_name: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Returns:
            bool: True if the record exists, False otherwise.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to see if a given vector exists.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        (transact_stub, exists_request, kwargs) = self._prepare_exists(
            namespace, key, set_name, timeout, logger
        )

        try:
            response = transact_stub.Exists(
                exists_request, credentials=self._channel_provider.get_token(), **kwargs
            )
        except grpc.RpcError as e:
            logger.error("Failed to verify vector existence with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        return self._respond_exists(response)

    def delete(
        self,
        *,
        namespace: str,
        key: Any,
        set_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Delete a record from Aerospike Vector Search.

        :param namespace: The namespace for the record.
        :type namespace: str

        :param key: The key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param set_name: The name of the set to which the record belongs. Defaults to None.
        :type set_name: Optional[str]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to delete the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        (transact_stub, delete_request, kwargs) = self._prepare_delete(
            namespace, key, set_name, timeout, logger
        )

        try:
            transact_stub.Delete(
                delete_request, credentials=self._channel_provider.get_token(), **kwargs
            )
        except grpc.RpcError as e:
            logger.error("Failed to delete vector with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def is_indexed(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        index_name: str,
        index_namespace: Optional[str] = None,
        set_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Check if a record is indexed in the Vector DB.

        :param namespace: The namespace for the record.
        :type namespace: str

        :param key: The primary key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param index_name: The name of the index.
        :type index_name: str

        :param index_namespace: The namespace of the index. If None, defaults to the namespace of the record.
        :type index_namespace: optional[str]

        :param set_name: The name of the set to which the record belongs. Defaults to None.
        :type set_name: optional[str]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Returns:
            bool: True if the record is indexed, False otherwise.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to check if the vector is indexed.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        (transact_stub, is_indexed_request, kwargs) = self._prepare_is_indexed(
            namespace, key, index_name, index_namespace, set_name, timeout, logger
        )

        try:
            response = transact_stub.IsIndexed(
                is_indexed_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to verify vector indexing status with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        return self._respond_is_indexed(response)

    def vector_search_by_key(
        self,
        *,
        search_namespace: str,
        index_name: str,
        key: Union[int, str, bytes, bytearray],
        key_namespace: str,
        vector_field: str,
        limit: int = 10,
        key_set: Optional[str] = None,
        search_params: Optional[types.HnswSearchParams] = None,
        include_fields: Optional[list[str]] = None,
        exclude_fields: Optional[list[str]] = None,
        timeout: Optional[int] = None,
    ) -> list[types.Neighbor]:
        """
        Perform a vector search against this index using a record in Aerospike.

        :param search_namespace: The namespace that stores the records to be searched.
        :type search_namespace: str

        :param index_name: The name of the index to use in the search.
        :type index_name: str

        :param key: The primary key of the record that stores the vector to use in the search.
        :type key: Union[int, str, bytes, bytearray]

        :param key_namespace: The namespace that stores the record.
        :type key_namespace: str

        :param vector_field: The name of the field containing vector data.
        :type vector_field: str

        :param limit: An optional maximum number of neighbors to return. K value. Defaults to 10.
        :type limit: int

        :param key_set: The set that stores the record, if any. Defaults to None.
        :type key_set: Optional[str]
        
        :param search_params: Parameters for the HNSW algorithm.
            If None, the default parameters for the index are used. Defaults to None.
        :type search_params: Optional[types_pb2.HnswSearchParams]

        :param include_fields: A list of field names to retrieve from the results.
            When used, fields that are not included are not sent by the server,
            saving on network traffic.
            If a field is listed in both include_fields and exclude_fields,
            exclude_fields takes priority, and the field is not returned.
            If None, all fields are retrieved. Defaults to None.
        :type include_fields: Optional[list[str]]

        :param exclude_fields: A list of field names to exclude from the results.
            When used, the excluded fields are not sent by the server,
            saving on network traffic.
            If None, all fields are retrieved. Defaults to None.
        :type exclude_fields: Optional[list[str]]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Returns:
            list[types.Neighbor]: A list of neighbors records found by the search.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to vector search.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        rec_and_key = self.get(
            namespace=key_namespace,
            key=key,
            set_name=key_set,
            timeout=timeout,
        )

        vector = rec_and_key.fields[vector_field]

        neighbors = self.vector_search(
            namespace=search_namespace,
            index_name=index_name,
            query=vector,
            limit=limit,
            search_params=search_params,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            timeout=timeout,
        )

        return neighbors

        

    def vector_search(
        self,
        *,
        namespace: str,
        index_name: str,
        query: list[Union[bool, float]],
        limit: int = 10,
        search_params: Optional[types.HnswSearchParams] = None,
        include_fields: Optional[list[str]] = None,
        exclude_fields: Optional[list[str]] = None,
        timeout: Optional[int] = None,
    ) -> list[types.Neighbor]:
        """
        Perform a Hierarchical Navigable Small World (HNSW) vector search in Aerospike Vector Search.

        :param namespace: The namespace for the records.
        :type namespace: str

        :param index_name: The name of the index.
        :type index_name: str

        :param query: The query vector for the search.
        :type query: list[Union[bool, float]]

        :param limit: An optional maximum number of neighbors to return. K value. Defaults to 10.
        :type limit: int

        :param search_params: Parameters for the HNSW algorithm.
            If None, the default parameters for the index are used. Defaults to None.
        :type search_params: Optional[types_pb2.HnswSearchParams]

        :param include_fields: A list of field names to retrieve from the results.
            When used, fields that are not included are not sent by the server,
            saving on network traffic.
            If a field is listed in both include_fields and exclude_fields,
            exclude_fields takes priority, and the field is not returned.
            If None, all fields are retrieved. Defaults to None.
        :type include_fields: Optional[list[str]]

        :param exclude_fields: A list of field names to exclude from the results.
            When used, the excluded fields are not sent by the server,
            saving on network traffic.
            If None, all fields are retrieved. Defaults to None.
        :type exclude_fields: Optional[list[str]]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Returns:
            list[types.Neighbor]: A list of neighbors records found by the search.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to vector search.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        (transact_stub, vector_search_request, kwargs) = self._prepare_vector_search(
            namespace,
            index_name,
            query,
            limit,
            search_params,
            include_fields,
            exclude_fields,
            timeout,
            logger,
        )

        try:
            return [
                self._respond_neighbor(result)
                for result in transact_stub.VectorSearch(
                    vector_search_request,
                    credentials=self._channel_provider.get_token(),
                    **kwargs,
                )
            ]
        except grpc.RpcError as e:
            logger.error("Failed to vector search with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    def index_get_percent_unmerged(
        self,
        *,
        namespace: str,
        name: str,
        timeout: Optional[int] = None,
    ) -> float:
        """
        Get the ratio of unmerged records to valid vertices in the index as a percentage.
        This is useful for determining the completeness of the index. Estimating
        the accuracy of search results, checking the progress of index healing,
        and determining if the index healer is keeping up with record writes.

        In general, the lower the percentage, the better the search accuracy.

        It is possible for the percentage to be greater than 100% if the number
        of unmerged records exceeds the number of valid vertices in the index.

        :param namespace: The namespace of the index.
        :type namespace: str

        :param name: The name of the index.
        :type name: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Returns:
            float: The percentage of unmerged records in the index.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get the percentage of unmerged records in the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        (
            index_stub,
            index_status_request,
            kwargs,
        ) = self._prepare_index_get_percent_unmerged(namespace, name, timeout, logger)

        try:
            index_status = index_stub.GetStatus(
                index_status_request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            logger.error("Failed to get index unmerged percent with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        unmergedIndexRecords = index_status.unmergedRecordCount
        vertices = index_status.indexHealerVerticesValid
        if vertices == 0:
            vertices = 100

        return (unmergedIndexRecords / vertices) * 100.0

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
        mode: Optional[types.IndexMode] = None,
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
            Defaults to :attr:`VectorDistanceMetric.SQUARED_EUCLIDEAN`.
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
            The namespace defaults to the namespace of the index and the set defaults to the index name.
        :type index_storage: Optional[types.IndexStorage]

        :param mode: The mode of the index. Defaults to distributed.
        :type mode: Optional[types.IndexMode]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

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
            mode,
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
            logger.error("Failed to create index with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        # Ensure that the created index is synced across all nodes
        self._indexes_in_sync()

    def index_update(
            self,
            *,
            namespace: str,
            name: str,
            index_labels: Optional[dict[str, str]] = None,
            hnsw_update_params: Optional[types.HnswIndexUpdate] = None,
            mode: Optional[types.IndexMode] = None,
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

        :param hnsw_update_params: Parameters for updating HNSW index settings. Defaults to None.
        :type hnsw_update_params: Optional[types.HnswIndexUpdate]

        :param mode: The mode of the index. Defaults to distributed.
        :type mode: Optional[types.IndexMode]

        :param timeout: Time in seconds this operation will wait before raising an error. Defaults to 100_000.
        :type timeout: Optional[int]

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to update the index.
        """
        (index_stub, index_update_request, kwargs) = self._prepare_index_update(
            namespace = namespace,
            name = name,
            index_labels = index_labels,
            hnsw_update_params = hnsw_update_params,
            index_mode = mode,
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
        # Ensure that the index changes are synced across all nodes
        self._indexes_in_sync()

    def index_drop(
        self, *, namespace: str, name: str, timeout: Optional[int] = None
    ) -> None:
        """
        Deletes an index from AVS.

        :param namespace: The namespace of the index.
        :type name: str

        :param name: The name of the index.
        :type name: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

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
            logger.error("Failed waiting for index deletion with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        # Ensure that the index is deleted across all nodes
        self._indexes_in_sync()

    def index_list(
        self, timeout: Optional[int] = None, apply_defaults: Optional[bool] = True
    ) -> list[types.IndexDefinition]:
        """
        List all indices.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

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
        apply_defaults: Optional[bool] = True,
        timeout: Optional[int] = None,
    ) -> types.IndexDefinition:
        """
        Retrieve information related to an index.

        :param namespace: The namespace of the index.
        :type namespace: str

        :param name: The name of the index.
        :type name: str

        :param apply_defaults: Apply default values to parameters which are not set by user. Defaults to True.
        :type apply_defaults: bool

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

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
        :type Optional[timeout]: int

        Returns: IndexStatusResponse: AVS response containing index status information.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get the index status.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
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

    def index(
            self,
            *,
            name: str,
            namespace: str,
            timeout: Optional[int] = None,
    ):
        """
        Get an Index object for a given index.
        The Index object provides methods to interact with and search on an index.
        Index objects are the preferred way to interact with indexes,
        rather than methods such as :meth:`index_get_status` or :meth:`vector_search`
        The index must exist in the AVS server.
        To create an index object, use the :meth:`index_create` client method.

        :param name: The name of the index.
        :type name: str

        :param namespace: The namespace of the index.
        :type namespace: str

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

        Returns: index.Index: An index object for the given index.
        """
        index_info = self.index_get(
            namespace=namespace,
            name=name,
            timeout=timeout,
        )

        # import in function to prevent circular imports
        from . import index

        return index.Index(
            client=self,
            name=name,
            namespace=namespace,
            vector_field=index_info.field,
            dimensions=index_info.dimensions,
            vector_distance_metric=index_info.vector_distance_metric,
            sets=index_info.sets,
            index_storage=index_info.storage,
        )

    def _indexes_in_sync(
            self,
            *,
            timeout: Optional[int] = None,
    ):
        """
        Waits for indexes to be in sync across the cluster.
        This call returns when all nodes in the AVS cluster have the same copy of the index.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int
        """
        index_stub, request, kwargs = self._prepare_indexes_in_sync(timeout, logger)

        try:
            _ = index_stub.AreIndicesInSync(
                request,
                credentials=self._channel_provider.get_token(),
                **kwargs,
            )
        except grpc.RpcError as e:
            # If the server does not support index syncing it means the server is older than 1.1.0
            # This is a non-critical error and can be ignored
            if e.code() == grpc.StatusCode.UNIMPLEMENTED:
                logger.warn("Index sync is not supported in this version of the server, skipping sync")
                return

            logger.error("Failed waiting for indices to sync with error: %s", e)
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
        :type timeout: Optional[int]


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
        :type timeout: Optional[int]


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
        :type timeout: Optional[int]


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
        :type timeout: Optional[int]

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
        :type timeout: Optional[int]

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
        :type timeout: Optional[int]

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
        :type timeout: Optional[int]

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

    def list_roles(self, timeout: Optional[int] = None) -> list[types.Role]:
        """
        List roles available on the AVS server.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: Optional[int]

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

            try:
                self._check_timeout(start_time, timeout)
            except types.AVSClientError as e:
                logger.error("Failed waiting for index creation with error: %s", e)
                raise
            
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

            try:
                self._check_timeout(start_time, timeout)
            except types.AVSClientError as e:
                logger.error("Failed waiting for index deletion with error: %s", e)
                raise

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
        Close the Aerospike Vector Search Client.

        This method closes gRPC channels connected to Aerospike Vector Search.

        Note:
            This method should be called when the client is no longer needed to release resources.
        """
        if not self.closed:
            self.closed = True
            self._channel_provider.close()

            # Patch all public methods to raise a AVSClientErrorClosed
            # the idea is to prevent use after the client is closed
            # without having to check if the client is closed in every method
            _patch_public_methods(self, _raise_closed)

    def __enter__(self):
        """
        Enter a context manager for the client.

        Returns:
            VectorDbClient: Aerospike Vector Search Client instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit a context manager for the client.
        """
        self.close()
