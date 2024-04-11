import asyncio
import logging
import sys
import time
from typing import Any, Optional, Union

import google.protobuf.empty_pb2
import grpc

from .private import conversions
from .private import index_pb2
from .private import index_pb2_grpc
from .private import transact_pb2
from .private import transact_pb2_grpc
from . import types
from .private import types_pb2
from .private import vectordb_channel_provider

empty = google.protobuf.empty_pb2.Empty()
logger = logging.getLogger(__name__)


class VectorDbClient(object):
    """
    Aerospike Vector Vector Client

    This client specializes in performing database operations with vector data.
    Moreover, the client supports Hierarchical Navigable Small World (HNSW) vector searches,
    allowing users to find vectors similar to a given query vector within an index.
    """

    def __init__(
        self,
        *,
        seeds: Union[types.HostPort, tuple[types.HostPort, ...]],
        listener_name: str = None,
        is_loadbalancer: Optional[bool] = False,
    ) -> None:
        """
        Initialize the Aerospike Vector Vector Client.

        Args:
            seeds (Union[types.HostPort, tuple[types.HostPort, ...]]):
                Used to create appropriate gRPC channels for interacting with Aerospike Vector.
            listener_name (Optional[str], optional):
                Advertised listener for the client. Defaults to None.
            is_loadbalancer (bool, optional):
                If true, the first seed address will be treated as a load balancer node.

        Raises:
            Exception: Raised when no seed host is provided.
        """
        if not seeds:
            raise Exception("at least one seed host needed")

        if isinstance(seeds, types.HostPort):
            seeds = (seeds,)

        self._channelProvider = vectordb_channel_provider.VectorDbChannelProvider(
            seeds, listener_name, is_loadbalancer
        )

    async def put(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        record_data: dict[str, Any],
        set_name: Optional[str] = None,
    ) -> None:
        """
        Write a record to Aerospike Vector.

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            record_data (dict[str, Any]): The data to be stored in the record.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        transact_stub = transact_pb2_grpc.TransactStub(
            self._channelProvider.get_channel()
        )
        key = _get_key(namespace, set_name, key)
        bin_list = [
            types_pb2.Bin(name=k, value=conversions.toVectorDbValue(v))
            for (k, v) in record_data.items()
        ]
        logger.debug(
            "Putting record: namespace=%s, key=%s, record_data:%s, set_name:%s",
            namespace,
            key,
            record_data,
            set_name,
        )
        try:
            await transact_stub.Put(transact_pb2.PutRequest(key=key, bins=bin_list))
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e

    async def get(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        bin_names: Optional[list[str]] = None,
        set_name: Optional[str] = None,
    ) -> types.RecordWithKey:
        """
        Read a record from Aerospike Vector.

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            bin_names (Optional[list[str]], optional): A list of bin names to retrieve from the record.
            If None, all bins are retrieved. Defaults to None.
            set_name (Optional[str], optional): The name of the set from which to read the record. Defaults to None.

        Returns:
            types.RecordWithKey: A record with its associated key.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        transact_stub = transact_pb2_grpc.TransactStub(
            self._channelProvider.get_channel()
        )
        key = _get_key(namespace, set_name, key)
        bin_selector = _get_bin_selector(bin_names=bin_names)
        logger.debug(
            "Getting record: namespace=%s, key=%s, bin_names:%s, set_name:%s",
            namespace,
            key,
            bin_names,
            set_name,
        )
        try:
            result = await transact_stub.Get(
                transact_pb2.GetRequest(key=key, binSelector=bin_selector)
            )
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e

        return types.RecordWithKey(
            key=conversions.fromVectorDbKey(key),
            bins=conversions.fromVectorDbRecord(result),
        )

    async def exists(
        self, *, namespace: str, key: Any, set_name: Optional[str] = None
    ) -> bool:
        """
        Check if a record exists in Aerospike Vector.

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
        transact_stub = transact_pb2_grpc.TransactStub(
            self._channelProvider.get_channel()
        )
        key = _get_key(namespace, set_name, key)
        logger.debug(
            "Getting record existence: namespace=%s, key=%s, set_name:%s",
            namespace,
            key,
            set_name,
        )
        try:
            result = await transact_stub.Exists(key)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e

        return result.value

    async def is_indexed(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        index_name: str,
        index_namespace: Optional[str] = None,
        set_name: Optional[str] = None,
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
        if not index_namespace:
            index_namespace = namespace

        index_id = types_pb2.IndexId(namespace=index_namespace, name=index_name)
        key = _get_key(namespace, set_name, key)
        request = transact_pb2.IsIndexedRequest(key=key, indexId=index_id)
        transact_stub = transact_pb2_grpc.TransactStub(
            self._channelProvider.get_channel()
        )
        logger.debug(
            "Checking if index exists: namespace=%s, key=%s, index_name=%s, index_namespace=%s, set_name=%s",
            namespace,
            key,
            index_name,
            index_namespace,
            set_name,
        )
        try:
            result = await transact_stub.IsIndexed(request)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e
        return result.value

    async def vector_search(
        self,
        *,
        namespace: str,
        index_name: str,
        query: list[Union[bool, float]],
        limit: int,
        search_params: Optional[types.HnswSearchParams] = None,
        bin_names: Optional[list[str]] = None,
    ) -> list[types.Neighbor]:
        """
        Perform a Hierarchical Navigable Small World (HNSW) vector search in Aerospike Vector.

        Args:
            namespace (str): The namespace for the records.
            index_name (str): The name of the index.
            query (list[Union[bool, float]]): The query vector for the search.
            limit (int): The maximum number of neighbors to return. K value.
            search_params (Optional[types_pb2.HnswSearchParams], optional): Parameters for the HNSW algorithm.
            If None, the default parameters for the index are used. Defaults to None.
            bin_names (Optional[list[str]], optional): A list of bin names to retrieve from the results.
            If None, all bins are retrieved. Defaults to None.

        Returns:
            list[types.Neighbor]: A list of neighbors records found by the search.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        transact_stub = transact_pb2_grpc.TransactStub(
            self._channelProvider.get_channel()
        )
        logger.debug(
            "Performing vector search: namespace=%s, index_name=%s, query=%s, limit=%s, search_params=%s, bin_names=%s",
            namespace,
            index_name,
            query,
            limit,
            search_params,
            bin_names,
        )
        if search_params != None:
            search_params = search_params._to_pb2()
        try:
            results_stream = transact_stub.VectorSearch(
                transact_pb2.VectorSearchRequest(
                    index=types_pb2.IndexId(namespace=namespace, name=index_name),
                    queryVector=(conversions.toVectorDbValue(query).vectorValue),
                    limit=limit,
                    hnswSearchParams=search_params,
                    binSelector=_get_bin_selector(bin_names=bin_names),
                )
            )
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e
        async_results = []
        async for result in results_stream:
            async_results.append(conversions.fromVectorDbNeighbor(result))

        return async_results

    async def wait_for_index_completion(
        self, *, namespace: str, name: str, timeout: Optional[int] = sys.maxsize
    ) -> None:
        """
        Wait for the index to have no pending index update operations.

        Args:
            namespace (str): The namespace of the index.
            name (str): The name of the index.
            timeout (int, optional): The maximum time (in seconds) to wait for the index to complete.
            Defaults to sys.maxsize.

        Raises:
            Exception: Raised when the timeout occurs while waiting for index completion.
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            The function polls the index status with a wait interval of 10 seconds until either
            the timeout is reached or the index has no pending index update operations.
        """
        # Wait interval between polling
        index_stub = index_pb2_grpc.IndexServiceStub(
            self._channelProvider.get_channel()
        )

        wait_interval = 1

        unmerged_record_count = sys.maxsize
        start_time = time.monotonic()
        unmerged_record_initialized = False
        while True:
            if start_time + timeout < time.monotonic():
                raise "timed-out waiting for index completion"
            # Wait for in-memory batches to be flushed to storage.
            if start_time + 10 < time.monotonic():
                unmerged_record_initialized = True
            try:
                index_status = await index_stub.GetStatus(
                    types_pb2.IndexId(namespace=namespace, name=name)
                )

            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    continue
                else:
                    logger.error("Failed with error: %s", e)
                    raise e

            if index_status.unmergedRecordCount > 0:
                unmerged_record_initialized = True

            if (
                unmerged_record_count == 0
                and index_status.unmergedRecordCount == 0
                and unmerged_record_initialized == True
            ):
                return
            # Update.
            unmerged_record_count = index_status.unmergedRecordCount
            await asyncio.sleep(wait_interval)

    async def close(self):
        """
        Close the Aerospike Vector Vector Client.

        This method closes gRPC channels connected to Aerospike Vector.

        Note:
            This method should be called when the VectorDbAdminClient is no longer needed to release resources.
        """
        await self._channelProvider.close()

    async def __aenter__(self):
        """
        Enter an asynchronous context manager for the vector client.

        Returns:
            VectorDbClient: Aerospike Vector Vector Client instance.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit an asynchronous context manager for the vector client.
        """
        await self.close()


def _get_bin_selector(*, bin_names: Optional[list] = None):

    if not bin_names:
        bin_selector = transact_pb2.BinSelector(
            type=transact_pb2.BinSelectorType.ALL, binNames=bin_names
        )
    else:
        bin_selector = transact_pb2.BinSelector(
            type=transact_pb2.BinSelectorType.SPECIFIED, binNames=bin_names
        )
    return bin_selector


def _get_key(namespace: str, set: str, key: Union[int, str, bytes, bytearray]):
    if isinstance(key, str):
        key = types_pb2.Key(namespace=namespace, set=set, stringValue=key)
    elif isinstance(key, int):
        key = types_pb2.Key(namespace=namespace, set=set, longValue=key)
    elif isinstance(key, (bytes, bytearray)):
        key = types_pb2.Key(namespace=namespace, set=set, bytesValue=key)
    else:
        raise Exception("Invalid key type" + type(key))
    return key
