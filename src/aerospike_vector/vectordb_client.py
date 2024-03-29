import asyncio
import sys
import time
from typing import Any, Optional, Union

import google.protobuf.empty_pb2
import grpc

from . import conversions
from . import index_pb2
from . import index_pb2_grpc
from . import transact_pb2
from . import transact_pb2_grpc
from . import types
from . import types_pb2
from . import vectordb_channel_provider

empty = google.protobuf.empty_pb2.Empty()


class VectorDbClient(object):
    """
    Vector DB client.

    Attributes:
        __channelProvider (vectordb_channel_provider.VectorDbChannelProvider):
            Channel provider for Vector DB connections.
    """

    def __init__(
        self,
        *,
        seeds: Union[types.HostPort, tuple[types.HostPort, ...]],
        listener_name: str = None,
    ) -> None:
        """
        Initialize the VectorDbClient.

        Args:
            seeds (Union[types.HostPort, tuple[types.HostPort, ...]]):
                Seeds for establishing connections with Vector DB nodes.
            listener_name (str, optional):
                Listener name for the client. Defaults to None.

        Raises:
            Exception: Raised when no seed host is provided.
        """
        if not seeds:
            raise Exception("at least one seed host needed")

        if isinstance(seeds, types.HostPort):
            seeds = (seeds,)

        self.__channelProvider = vectordb_channel_provider.VectorDbChannelProvider(
            seeds, listener_name
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
        Write a record to the Vector DB.

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            record_data (dict[str, Any]): The data to be stored in the record.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Returns:
            None

        Raises:
            [List any exceptions raised]

        Note:
            [Any additional notes]
        """
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.get_channel()
        )
        key = _get_key(key, set_name, namespace)
        binList = [
            types_pb2.Bin(name=k, value=conversions.toVectorDbValue(v))
            for (k, v) in record_data.items()
        ]
        await transact_stub.Put(transact_pb2.PutRequest(key=key, bins=binList))

    async def get(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes, bytearray],
        bin_names: Optional[list[str]] = None,
        set_name: Optional[str] = None,
    ) -> types.RecordWithKey:
        """
        Read a record from the Vector DB.

        Args:
            namespace (str): The namespace for the record.
            key (Union[int, str, bytes, bytearray]): The key for the record.
            bin_names (Optional[list[str]], optional): A list of bin names to retrieve from the record.
                If None, all bins are retrieved. Defaults to None.
            set_name (Optional[str], optional): The name of the set from which to read the record. Defaults to None.

        Returns:
            types.RecordWithKey: A record with its associated key.

        Raises:
            [List any exceptions raised]

        Note:
            [Any additional notes]
        """
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.get_channel()
        )
        key = _get_key(key, set_name, namespace)
        bin_selector = _get_bin_selector(bin_names=bin_names)
        result = await transact_stub.Get(
            transact_pb2.GetRequest(key=key, binSelector=bin_selector)
        )
        return types.RecordWithKey(
            key=conversions.fromVectorDbKey(key),
            bins=conversions.fromVectorDbRecord(result),
        )

    async def exists(
        self, *, namespace: str, key: Any, set_name: Optional[str] = None
    ) -> bool:
        """
        Check if a record exists in the Vector DB.

        Args:
            namespace (str): The namespace for the record.
            key (Any): The key for the record.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Returns:
            bool: True if the record exists, False otherwise.

        Raises:
            [List any exceptions raised]

        Note:
            [Any additional notes]
        """
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.get_channel()
        )
        key = self.__get_key(key, set_name, namespace)
        result = await transact_stub.Exists(key)
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
                If not provided, defaults to the namespace of the record. Defaults to None.
            set_name (Optional[str], optional): The name of the set to which the record belongs. Defaults to None.

        Returns:
            bool: True if the record is indexed, False otherwise.

        Raises:
            [List any exceptions raised]

        Note:
            [Any additional notes]
        """
        if not index_namespace:
            index_namespace = namespace

        index_id = types_pb2.IndexId(namespace=index_namespace, name=index_name)
        key = _get_key(key, set_name, namespace)
        request = transact_pb2.IsIndexedRequest(key=key, indexId=index_id)
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.get_channel()
        )
        result = await transact_stub.IsIndexed(request)
        return result.value

    async def vector_search(
        self,
        *,
        namespace: str,
        index_name: str,
        query: list[Union[bool, float]],
        limit: int,
        search_params: Optional[types_pb2.HnswSearchParams] = None,
        bin_names: Optional[list[str]] = None,
    ) -> list[types.Neighbor]:
        """
        Perform a vector search in the Vector DB.

        Args:
            namespace (str): The namespace for the records.
            index_name (str): The name of the index.
            query (list[Union[bool, float]]): The query vector for the search.
            limit (int): The maximum number of results to return.
            search_params (Optional[types_pb2.HnswSearchParams], optional): Parameters for the search algorithm.
                Defaults to None.
            bin_names (Optional[list[str]], optional): A list of bin names to retrieve from the results.
                If None, all bins are retrieved. Defaults to None.

        Returns:
            list[types.Neighbor]: A list of neighbors found by the search.

        Raises:
            [List any exceptions raised]

        Note:
            [Any additional notes]
        """
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.get_channel()
        )
        results_stream = transact_stub.VectorSearch(
            transact_pb2.VectorSearchRequest(
                index=types_pb2.IndexId(namespace=namespace, name=index_name),
                queryVector=(conversions.toVectorDbValue(query).vectorValue),
                limit=limit,
                hnswSearchParams=search_params,
                binSelector=self.__get_bin_selector(bin_names=bin_names),
            )
        )

        async_results = []
        async for result in results_stream:
            async_results.append(conversions.fromVectorDbNeighbor(result))

        return async_results

    async def wait_for_index_completion(
        self, *, namespace: str, name: str, timeout: int = sys.maxsize
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

        Note:
            The function polls the index status with a wait interval of 10 seconds until either
            the timeout is reached or the index has no pending index update operations.
        """
        # Wait interval between polling
        wait_interval = 10

        unmerged_record_count = sys.maxsize
        start_time = time.monotonic()
        while True:
            if start_time + timeout < time.monotonic():
                raise "timed-out waiting for index completion"
            # Wait for in-memory batches to be flushed to storage.
            time.sleep(wait_interval)

            try:
                index_status = await self.__index_get_status(namespace, name)
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    continue
                else:
                    raise e

            if unmerged_record_count == 0 and index_status.unmergedRecordCount == 0:
                return
            # Update.
            unmerged_record_count = index_status.unmergedRecordCount

    async def _index_get_status(
        self, *, namespace: str, name: str
    ) -> index_pb2.IndexStatusResponse:

        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.get_channel()
        )
        response = await index_stub.GetStatus(
            types_pb2.IndexId(namespace=namespace, name=name)
        )

        return response

    async def close(self):
        """
        Close the VectorDbAdminClient.

        This method closes the connection to Vector DB.

        Note:
            This method should be called when the VectorDbAdminClient is no longer needed to release resources.

        Raises:
            [List any exceptions raised]
        """
        await self.__channelProvider.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.run(self.close())


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


def _get_key(key: Union[int, str, bytes, bytearray], set: str, namespace: str):
    if isinstance(key, str):
        key = types_pb2.Key(namespace=namespace, set=set, stringValue=key)
    elif isinstance(key, int):
        key = types_pb2.Key(namespace=namespace, set=set, longValue=key)
    elif isinstance(key, (bytes, bytearray)):
        key = types_pb2.Key(namespace=namespace, set=set, bytesValue=key)
    else:
        raise Exception("Invalid key type" + type(key))
    return key
