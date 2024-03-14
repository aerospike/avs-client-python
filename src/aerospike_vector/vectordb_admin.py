import sys
import time
import grpc
from typing import Any

import google.protobuf.empty_pb2

from . import index_pb2_grpc
from . import index_pb2
from . import types
from . import types_pb2
from . import vectordb_channel_provider

empty = google.protobuf.empty_pb2.Empty()


class VectorDbAdminClient(object):
    """Vector DB Admin client"""

    def __init__(self, seeds: types.HostPort | tuple[types.HostPort, ...],
                 listener_name: str = None):
        if not seeds:
            raise Exception("at least one seed host needed")

        if isinstance(seeds, types.HostPort):
            seeds = (seeds,)

        self.__channelProvider = vectordb_channel_provider.VectorDbChannelProvider(
            seeds, listener_name)

    def indexCreate(self, namespace: str, name: str,
                    vector_bin_name: str, dimensions: int,
                    vector_distance_metric: types_pb2.VectorDistanceMetric =
                    types_pb2.VectorDistanceMetric.SQUARED_EUCLIDEAN,
                    setFilter: str = None,
                    indexParams: types_pb2.HnswParams = None,
                    labels: dict[str, str] = None):
        """Create an index"""
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.getChannel())
        if setFilter and not setFilter.strip():
            setFilter = None

        index_stub.Create(
            types_pb2.IndexDefinition(
                id=types_pb2.IndexId(namespace=namespace, name=name),
                vectorDistanceMetric=vector_distance_metric,
                setFilter=setFilter,
                hnswParams=indexParams,
                bin=vector_bin_name,
                dimensions=dimensions,
                labels=labels))

        self.__waitForIndexCreation(namespace, name, 100_000)

    def indexDrop(self, namespace: str, name: str):
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.getChannel())
        index_stub.Drop(types_pb2.IndexId(namespace=namespace, name=name))

    def indexList(self) -> list[Any]:
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.getChannel())
        return index_stub.List(empty).indices

    def indexGet(self, namespace: str, name: str) -> types_pb2.IndexDefinition:
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.getChannel())
        return index_stub.Get(types_pb2.IndexId(namespace=namespace, name=name))

    def indexGetStatus(self, namespace: str,
                       name: str) -> index_pb2.IndexStatusResponse:
        """
        This API is subject to change.
        """
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.getChannel())
        return index_stub.GetStatus(
            types_pb2.IndexId(namespace=namespace, name=name))

    def __waitForIndexCreation(self, namespace: str, name: str,
                               timeout: int = sys.maxsize):
        """
        Wait for the index to be created.
        """

        # Wait interval between polling
        wait_interval = 10

        start_time = time.monotonic()
        while True:
            if start_time + timeout < time.monotonic():
                raise "timed-out waiting for index creation"
            try:
                index_status = self.indexGet(namespace, name)
                # Index has been created
                return
            except grpc.RpcError as e:
                if (e.code() == grpc.StatusCode.UNAVAILABLE or
                        e.code() == grpc.StatusCode.NOT_FOUND):
                    # Wait for some more time.
                    time.sleep(wait_interval)
                else:
                    raise e

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.__channelProvider.close()
