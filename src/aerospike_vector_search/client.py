import logging
import sys
import time
from typing import Any, Optional, Union
import warnings

import grpc

from . import types
from .internal import channel_provider
from .shared.client_helpers import BaseClient

logger = logging.getLogger(__name__)


class Client(BaseClient):
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
        :type timeout: int

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
        :type timeout: int

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
        key: Union[int, str, bytes, bytearray],
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
        :type timeout: int

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
        # field_names is deprecated, use include_fields
        field_names: Optional[list[str]] = None,
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
        :type timeout: int

        :param field_names: Deprecated, use include_fields instead.
        :type field_names: Optional[list[str]]

        Returns:
            types.RecordWithKey: A record with its associated key.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get a vector.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        # TODO remove this when 'field_names' is removed
        if field_names is not None:
            warnings.warn(
                "The 'field_names' argument is deprecated. Use 'include_fields' instead",
                FutureWarning,
            )
            include_fields = field_names


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
        :type timeout: int

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
            logger.error("Failed to verfiy vector existence with error: %s", e)
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
        :type timeout: int

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

        :param key: The key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param index_name: The name of the index.
        :type index_name: str

        :param index_namespace: The namespace of the index. If None, defaults to the namespace of the record. Defaults to None.
        :type index_namespace: optional[str]

        :param set_name: The name of the set to which the record belongs. Defaults to None.
        :type set_name: optional[str]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

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
        limit: int,
        key_set: Optional[str] = None,
        search_params: Optional[types.HnswSearchParams] = None,
        include_fields: Optional[list[str]] = None,
        exclude_fields: Optional[list[str]] = None,
        timeout: Optional[int] = None,
    ) -> list[types.Neighbor]:
        """
        Perform a Hierarchical Navigable Small World (HNSW) vector search in Aerospike Vector Search by primary record key.

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

        :param limit: The maximum number of neighbors to return. K value.
        :type limit: int

        :param key_set: The name of the set from which to read the record to search by. Defaults to None.
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
        :type timeout: int

        :param field_names: Deprecated, use include_fields instead.
        :type field_names: Optional[list[str]]

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
        limit: int,
        search_params: Optional[types.HnswSearchParams] = None,
        include_fields: Optional[list[str]] = None,
        exclude_fields: Optional[list[str]] = None,
        timeout: Optional[int] = None,
        # field_names is deprecated, use include_fields
        field_names: Optional[list[str]] = None,
    ) -> list[types.Neighbor]:
        """
        Perform a Hierarchical Navigable Small World (HNSW) vector search in Aerospike Vector Search.

        :param namespace: The namespace for the records.
        :type namespace: str

        :param index_name: The name of the index.
        :type index_name: str

        :param query: The query vector for the search.
        :type query: list[Union[bool, float]]

        :param limit: The maximum number of neighbors to return. K value.
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
        :type timeout: int

        :param field_names: Deprecated, use include_fields instead.
        :type field_names: Optional[list[str]]

        Returns:
            list[types.Neighbor]: A list of neighbors records found by the search.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to vector search.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        # TODO remove this when 'field_names' is removed
        if field_names is not None:
            warnings.warn(
                "The 'field_names' argument is deprecated. Use 'include_fields' instead",
                FutureWarning,
            )
            include_fields = field_names

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

    def wait_for_index_completion(
        self,
        *,
        namespace: str,
        name: str,
        timeout: Optional[int] = sys.maxsize,
        wait_interval: Optional[int] = 12,
        validation_threshold: Optional[int] = 2,
    ) -> None:
        """
        Wait for the index to have no pending index update operations.

        :param namespace (str): The namespace of the index.
        :type namespace: str

        :param name (str): The name of the index.
        :type name: str

        :param timeout (int, optional): The maximum time (in seconds) to wait for the index to complete.
            Defaults to sys.maxsize.
        :type timeout: int

        :param wait_interval: The time (in seconds) to wait between index completion status request to the server.
            Lowering this value increases the chance that the index completion status is incorrect, which can result in poor search accuracy.
        :type wait_interval: int

        Raises:
            Exception: Raised when the timeout occurs while waiting for index completion.
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to wait for index completion.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            The function polls the index status with a wait interval of 10 seconds until either
            the timeout is reached or the index has no pending index update operations.
        """
        (
            index_stub,
            wait_interval,
            start_time,
            unmerged_record_initialized,
            validation_count,
            index_completion_request,
        ) = self._prepare_wait_for_index_waiting(namespace, name, wait_interval)

        while True:
            try:
                index_status = index_stub.GetStatus(
                    index_completion_request,
                    credentials=self._channel_provider.get_token(),
                )
            except grpc.RpcError as e:

                logger.error("Failed waiting for index completion with error: %s", e)
                raise types.AVSServerError(rpc_error=e)
            if self._check_completion_condition(
                start_time, timeout, index_status, unmerged_record_initialized
            ):
                if validation_count == validation_threshold:
                    return
                else:
                    validation_count += 1
            else:
                validation_count = 0
            time.sleep(wait_interval)

    def close(self):
        """
        Close the Aerospike Vector Search Client.

        This method closes gRPC channels connected to Aerospike Vector Search.

        Note:
            This method should be called when the VectorDbAdminClient is no longer needed to release resources.
        """
        self._channel_provider.close()

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
