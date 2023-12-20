import sys
import time
from typing import Any

import google.protobuf.empty_pb2

from . import conversions, index_pb2_grpc
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

        self.channelProvider = vectordb_channel_provider.VectorDbChannelProvider(
            seeds, listener_name)

    def indexCreate(self, namespace: str, name: str, set: str,
                    vector_bin_name: str, dimensions: int,
                    params: dict[str, Any] = None,
                    index_similarity_metric: types_pb2.VectorDistanceMetric =
                    types_pb2.VectorDistanceMetric.SQUARED_EUCLIDEAN):
        """Create an index"""
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.channelProvider.getChannel())
        if params is None:
            params = {}

        grpcParams = {}
        for k, v in params.items():
            grpcParams[k] = conversions.toVectorDbValue(v)

        if not set.strip():
            set = None
            
        index_stub.Create(
            types_pb2.IndexDefinition(
                id=types_pb2.IndexId(namespace=namespace, name=name),
                set=set,
                vectorDistanceMetric=index_similarity_metric,
                bin=vector_bin_name,
                dimensions=dimensions,
                params=grpcParams))

    def indexDrop(self, namespace: str, name: str):
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.channelProvider.getChannel())
        index_stub.Drop(types_pb2.IndexId(namespace=namespace, name=name))

    def indexList(self) -> list[Any]:
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.channelProvider.getChannel())
        return index_stub.List(empty).indices

    def indexGet(self, namespace: str, name: str) -> types_pb2.IndexDefinition:
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.channelProvider.getChannel())
        return index_stub.Get(types_pb2.IndexId(namespace=namespace, name=name))

    def indexGetStatus(self, namespace: str,
                       name: str) -> index_pb2.IndexStatusResponse:
        """
        This API is subject to change.
        """
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.channelProvider.getChannel())
        return index_stub.GetStatus(
            types_pb2.IndexId(namespace=namespace, name=name))

    def waitForIndexCompletion(self, namespace: str, name: str,
                               timeout: int = sys.maxsize):
        """
        Wait for the index to have no pending index update operations.
        """
        index_definition = self.indexGet(namespace, name)

        # Fetch batch wait interval
        batching_config = \
            conversions.fromVectorDbValue(index_definition.params[
                                              "batching-config"])

        # TODO: server should return defaults for batching-config if missing.
        if not batching_config:
            batching_config = {}
        if "batch-interval" not in batching_config:
            batching_config["batch-interval"] = 10_000
        batch_interval = batching_config["batch-interval"]

        unmerged_record_count = self.indexGetStatus(namespace,
                                                    name).unmergedRecordCount
        start_time = time.monotonic()
        while True:
            if start_time + timeout < time.monotonic():
                raise "timed-out waiting for index completion"
            # Wait for in-memory batches to be flushed to storage.
            time.sleep(2 * batch_interval / 1000.0)
            index_status = self.indexGetStatus(namespace, name)
            if unmerged_record_count == 0 and index_status.unmergedRecordCount == 0:
                return
            # Update.
            unmerged_record_count = index_status.unmergedRecordCount

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.channelProvider.close()
