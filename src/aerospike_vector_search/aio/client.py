import asyncio
import logging
import sys
from typing import Any, Optional, Union

import grpc

from .. import types
from .internal import channel_provider
from ..shared.client_helpers import BaseClient

logger = logging.getLogger(__name__)


class Client(BaseClient):
    """
    Aerospike Vector Search Asyncio Admin Client

    This client specializes in performing database operations with vector data.
    Moreover, the client supports Hierarchical Navigable Small World (HNSW) vector searches,
    allowing users to find vectors similar to a given query vector within an index.
    """

    def __init__(
        self,
        *,
        seeds: Union[types.HostPort, tuple[types.HostPort, ...]],
        listener_name: Optional[str] = None,
        is_loadbalancer: Optional[bool] = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        root_certificate: Optional[str] = None,
        certificate_chain: Optional[str] = None,
        private_key: Optional[str] = None,
        service_config_path: Optional[str] = None,
    ) -> None:
        """
        Initialize the Aerospike Vector Search Vector Client.

        Args:
            seeds (Union[types.HostPort, tuple[types.HostPort, ...]]):
                Used to create appropriate gRPC channels for interacting with Aerospike Vector Search.
            listener_name (Optional[str], optional):
                Advertised listener for the client. Defaults to None.
            is_loadbalancer (bool, optional):
                If true, the first seed address will be treated as a load balancer node.

        Raises:
            Exception: Raised when no seed host is provided.
        """
        seeds = self._prepare_seeds(seeds)
        self._channel_provider = channel_provider.ChannelProvider(
            seeds, listener_name, is_loadbalancer, username, password, root_certificate, certificate_chain, private_key, service_config_path
        )

    async def insert(
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

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            record_data (dict[str, Any]): The data to be stored in the record.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """

        await self._channel_provider._is_ready()

        (transact_stub, insert_request) = self._prepare_insert(
            namespace, key, record_data, set_name, ignore_mem_queue_full, timeout, logger
        )

        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout

        try:
            await transact_stub.Put(insert_request, credentials=self._channel_provider._token, **kwargs)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    async def update(
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
        If record doesn't exist, an exception is raised.

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            record_data (dict[str, Any]): The data to be stored in the record.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """

        await self._channel_provider._is_ready()

        (transact_stub, update_request) = self._prepare_update(
            namespace, key, record_data, set_name, ignore_mem_queue_full, timeout, logger
        )

        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout

        try:
            await transact_stub.Put(update_request, credentials=self._channel_provider._token, **kwargs)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    async def upsert(
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

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            record_data (dict[str, Any]): The data to be stored in the record.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """

        await self._channel_provider._is_ready()

        (transact_stub, upsert_request) = self._prepare_upsert(
            namespace, key, record_data, set_name, ignore_mem_queue_full, timeout, logger
        )

        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout

        try:
            await transact_stub.Put(upsert_request, credentials=self._channel_provider._token, **kwargs)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    async def get(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        field_names: Optional[list[str]] = None,
        set_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> types.RecordWithKey:
        """
        Read a record from Aerospike Vector Search.

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            field_names (Optional[list[str]], optional): A list of field names to retrieve from the record.
            If None, all fields are retrieved. Defaults to None.
            set_name (Optional[str], optional): The name of the set from which to read the record. Defaults to None.

        Returns:
            types.RecordWithKey: A record with its associated key.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        await self._channel_provider._is_ready()

        (transact_stub, key, get_request) = self._prepare_get(
            namespace, key, field_names, set_name, timeout, logger
        )

        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout

        try:
            response = await transact_stub.Get(get_request, credentials=self._channel_provider._token, **kwargs)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        return self._respond_get(response, key)

    async def exists(
        self, *, namespace: str, key: Any, set_name: Optional[str] = None, timeout: Optional[int] = None,
    ) -> bool:
        """
        Check if a record exists in Aerospike Vector Search.

        Args:
            namespace (str): The namespace for the record.
            key (Any): The key for the record.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Returns:
            bool: True if the record exists, False otherwise.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        await self._channel_provider._is_ready()

        (transact_stub, exists_request) = self._prepare_exists(
            namespace, key, set_name, timeout, logger
        )

        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout

        try:
            response = await transact_stub.Exists(exists_request, credentials=self._channel_provider._token, **kwargs)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

        return self._respond_exists(response)

    async def delete(
        self, *, namespace: str, key: Any, set_name: Optional[str] = None, timeout: Optional[int] = None,
    ) -> None:
        """
        Delete a record from Aerospike Vector Search.

        Args:
            namespace (str): The namespace for the record.
            key (Any): The key for the record.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        await self._channel_provider._is_ready()

        (transact_stub, delete_request) = self._prepare_delete(
            namespace, key, set_name, timeout, logger
        )

        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout

        try:
            await transact_stub.Delete(delete_request, credentials=self._channel_provider._token, **kwargs)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    async def is_indexed(
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

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            index_name (str): The name of the index.
            index_namespace (Optional[str], optional): The namespace of the index.
            If None, defaults to the namespace of the record. Defaults to None.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Returns:
            bool: True if the record is indexed, False otherwise.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        await self._channel_provider._is_ready()

        (transact_stub, is_indexed_request) = self._prepare_is_indexed(
            namespace, key, index_name, index_namespace, set_name, timeout, logger
        )

        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout

        try:
            response = await transact_stub.IsIndexed(is_indexed_request, credentials=self._channel_provider._token, **kwargs)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)
        return self._respond_is_indexed(response)

    async def vector_search(
        self,
        *,
        namespace: str,
        index_name: str,
        query: list[Union[bool, float]],
        limit: int,
        search_params: Optional[types.HnswSearchParams] = None,
        field_names: Optional[list[str]] = None,
        timeout: Optional[int] = None,
    ) -> list[types.Neighbor]:
        """
        Perform a Hierarchical Navigable Small World (HNSW) vector search in Aerospike Vector Search.

        Args:
            namespace (str): The namespace for the records.
            index_name (str): The name of the index.
            query (list[Union[bool, float]]): The query vector for the search.
            limit (int): The maximum number of neighbors to return. K value.
            search_params (Optional[types_pb2.HnswSearchParams], optional): Parameters for the HNSW algorithm.
            If None, the default parameters for the index are used. Defaults to None.
            field_names (Optional[list[str]], optional): A list of field names to retrieve from the results.
            If None, all fields are retrieved. Defaults to None.

        Returns:
            list[types.Neighbor]: A list of neighbors records found by the search.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        await self._channel_provider._is_ready()

        (transact_stub, vector_search_request) = self._prepare_vector_search(
            namespace, index_name, query, limit, search_params, field_names, timeout, logger
        )

        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout

        try:
            return [self._respond_neighbor(result) async for result in transact_stub.VectorSearch(vector_search_request, credentials=self._channel_provider._token, **kwargs)]
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise types.AVSServerError(rpc_error=e)

    async def wait_for_index_completion(
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

        Args:
            namespace (str): The namespace of the index.
            name (str): The name of the index.
            timeout (int, optional): The maximum time (in seconds) to wait for the index to complete.
            Defaults to sys.maxsize.
            wait_interval (int, optional): The time (in seconds) to wait between index completion status request to the server.
            Lowering this value increases the chance that the index completion status is incorrect, which can result in poor search accuracy.

        Raises:
            Exception: Raised when the timeout occurs while waiting for index completion.
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            The function polls the index status with a wait interval of 10 seconds until either
            the timeout is reached or the index has no pending index update operations.
        """
        await self._channel_provider._is_ready()

        # Wait interval between polling
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
                index_status = await index_stub.GetStatus(index_completion_request, credentials=self._channel_provider._token)

            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    continue
                else:
                    logger.error("Failed with error: %s", e)
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
            await asyncio.sleep(wait_interval)

    async def close(self):
        """
        Close the Aerospike Vector Search Vector Client.

        This method closes gRPC channels connected to Aerospike Vector Search.

        Note:
            This method should be called when the VectorDbAdminClient is no longer needed to release resources.
        """
        await self._channel_provider.close()

    async def __aenter__(self):
        """
        Enter an asynchronous context manager for the vector client.

        Returns:
            VectorDbClient: Aerospike Vector Search Vector Client instance.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit an asynchronous context manager for the vector client.
        """
        await self.close()
