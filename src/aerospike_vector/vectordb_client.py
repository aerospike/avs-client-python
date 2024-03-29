import sys
import time
import grpc
import asyncio
from typing import Any, Optional, Union

import google.protobuf.empty_pb2

from . import conversions
from . import transact_pb2, types_pb2, transact_pb2_grpc
from . import types
from . import vectordb_channel_provider
from . import index_pb2_grpc, index_pb2

empty = google.protobuf.empty_pb2.Empty()


class VectorDbClient(object):
    """Vector DB client"""

    def __init__(
        self,
        *,
        seeds: Union[types.HostPort, tuple[types.HostPort, ...]],
        listener_name: str = None,
    ) -> None:

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
        key: Union[int, str, bytes],
        record_data: dict[str, Any],
        set_name: Optional[str] = None,
    ):
        """Write a record to vector DB"""
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.get_channel()
        )
        key = self.__get_key(key, set_name, namespace)
        binList = [
            types_pb2.Bin(name=k, value=conversions.toVectorDbValue(v))
            for (k, v) in record_data.items()
        ]
        await transact_stub.Put(transact_pb2.PutRequest(key=key, bins=binList))

    async def get(
        self,
        *,
        namespace: str,
        key: Union[int, str, bytes],
        bin_names: Optional[list[str]] = None,
        set_name: Optional[str] = None,
    ) -> types.RecordWithKey:
        """Read a record from vector DB"""
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.get_channel()
        )
        key = self.__get_key(key, set_name, namespace)
        bin_selector = self.__get_bin_selector(bin_names=bin_names)
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
        """Check if a record exists in vector DB"""
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
        key: Any,
        index_name: str,
        index_namespace: Optional[str] = None,
        set_name: Optional[str] = None,
    ) -> bool:
        """Check if a record is indexed in vector DB"""
        if not index_namespace:
            index_namespace = namespace

        index_id = types_pb2.IndexId(namespace=index_namespace, name=index_name)
        key = self.__get_key(key, set_name, namespace)
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
    ):
        """
        Wait for the index to have no pending index update operations.
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.run(self.close())

    async def close(self):
        await self.__channelProvider.close()

    def __get_key(self, key, set, namespace):
        if isinstance(key, str):
            key = types_pb2.Key(namespace=namespace, set=set, stringValue=key)
        elif isinstance(key, int):
            key = types_pb2.Key(namespace=namespace, set=set, longValue=key)
        elif isinstance(key, (bytes, bytearray)):
            key = types_pb2.Key(namespace=namespace, set=set, bytesValue=key)
        else:
            raise Exception("Invalid key type" + type(key))
        return key

    def __get_bin_selector(self, *, bin_names: [list] = None):

        if not bin_names:
            bin_selector = transact_pb2.BinSelector(
                type=transact_pb2.BinSelectorType.ALL, binNames=bin_names
            )
        else:
            bin_selector = transact_pb2.BinSelector(
                type=transact_pb2.BinSelectorType.SPECIFIED, binNames=bin_names
            )
        return bin_selector

    async def __index_get_status(
        self, *, namespace: str, name: str
    ) -> index_pb2.IndexStatusResponse:
        """
        This API is subject to change.
        """

        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.get_channel()
        )
        response = await index_stub.GetStatus(
            types_pb2.IndexId(namespace=namespace, name=name)
        )

        return response
