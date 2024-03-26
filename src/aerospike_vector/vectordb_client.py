import sys
import time
import grpc

from typing import Any, Optional

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
        self, *,
        seeds: Union[types.HostPort, tuple[types.HostPort, ...]],
        listener_name: str = None) -> None:

        if not seeds:
            raise Exception("at least one seed host needed")

        if isinstance(seeds, types.HostPort):
            seeds = (seeds,)

        self.__channelProvider = (
            vectordb_channel_provider.VectorDbChannelProvider(
                seeds, listener_name))

    def put(
        self, *,
        namespace: str,
        key: Union[int, str, bytes],
        record_data: dict[str, Any], 
        set_name: Optional[str] = None):
        """Write a record to vector DB"""
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.getChannel())
        key = self.__getKey(key, set_name, namespace)
        binList = [types_pb2.Bin(name=k, value=conversions.toVectorDbValue(v))
                   for (k, v) in record_data.items()]
        transact_stub.Put(
            transact_pb2.PutRequest(key=key, bins=binList))

    def get(
        self, *,
        namespace: str, 
        key: Union[int, str, bytes],
        bin_names: Optional[list[str]] = None,
        set_name: Optional[str] = None) -> types.RecordWithKey:
        """Read a record from vector DB"""
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.getChannel())
        key = self.__getKey(key, set_name, namespace)
        bin_selector = self.__getBinSelector(*bin_names)

        result = transact_stub.Get(
            transact_pb2.GetRequest(key=key, binSelector=bin_selector))
        return types.RecordWithKey(conversions.fromVectorDbKey(key),
                              conversions.fromVectorDbRecord(result))

    def exists(
        self, *,
        namespace: str,
        key: Any,
        set_name: Optional[str] = None) -> bool:
        """Check if a record exists in vector DB"""
        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.getChannel())
        key = self.__getKey(key, set_name, namespace)

        return transact_stub.Exists(key).value

    def isIndexed(
        self, *,
        namespace: str,
        key: Any,
        index_name: str,
        index_namespace: Optional[str] = None,
        set_name: Optional[str] = None) -> bool:
        """Check if a record is indexed in vector DB"""
        if not index_namespace:
            index_namespace = namespace

        index_id = types_pb2.IndexId(namespace=index_namespace, name=index_name)
        key = self.__getKey(key, set_name, namespace)
        request = transact_pb2.IsIndexedRequest(key=key, indexId=index_id)
        transact_stub = transact_pb2_grpc.TransactStub(self.__channelProvider.getChannel())
        return transact_stub.IsIndexed(request).value

    def vectorSearch(
        self, *, 
        namespace: str,
        index_name: str,
        query: list[Union[bool, float]],
        limit: int,
        search_params: Optional[types_pb2.HnswSearchParams] = None,
        bin_names: Optional[list[str]] = None) -> list[types.Neighbor]:

        transact_stub = transact_pb2_grpc.TransactStub(
            self.__channelProvider.getChannel())
        results = transact_stub.VectorSearch(
            transact_pb2.VectorSearchRequest(
                index=types_pb2.IndexId(namespace=namespace, name=index_name),
                queryVector=(conversions.toVectorDbValue(query).vectorValue),
                limit=limit,
                hnswSearchParams=search_params,
                binSelector=self.__getBinSelector(*bin_names)
            )
        )
        return [conversions.fromVectorDbNeighbor(result) for result in
                results]

    def waitForIndexCompletion(
        self, *,
        namespace: str,
        name: str,
        timeout: int = sys.maxsize):
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
                index_status = self.__indexGetStatus(namespace, name)
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    continue
                else:
                    raise e

            if unmerged_record_count == 0 and index_status.unmergedRecordCount == 0:
                return
            # Update.
            unmerged_record_count = index_status.unmergedRecordCount

    def close(self):
        self.__channelProvider.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getKey(self, key, set, namespace):
        if isinstance(key, str):
            key = types_pb2.Key(namespace=namespace, set=set, stringValue=key)
        elif isinstance(key, int):
            key = types_pb2.Key(namespace=namespace, set=set, longValue=key)
        elif isinstance(key, (bytes, bytearray)):
            key = types_pb2.Key(namespace=namespace, set=set, bytesValue=key)
        else:
            raise Exception("Invalid key type" + type(key))
        return key

    def __getBinSelector(self, bin_names):
        if not bin_names:
            bin_selector = transact_pb2.BinSelector(
                type=transact_pb2.BinSelectorType.ALL, binNames=bin_names)
        else:
            bin_selector = transact_pb2.BinSelector(
                type=transact_pb2.BinSelectorType.SPECIFIED, binNames=bin_names)
        return bin_selector

    def __indexGetStatus(self, namespace: str,name: str) -> index_pb2.IndexStatusResponse:
        """
        This API is subject to change.
        """
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.getChannel())
        return index_stub.GetStatus(
            types_pb2.IndexId(namespace=namespace, name=name))