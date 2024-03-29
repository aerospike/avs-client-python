import sys
import time
import grpc
import asyncio
from typing import Any, Optional, Union

import google.protobuf.empty_pb2

from . import index_pb2_grpc
from . import index_pb2
from . import types
from . import types_pb2
from . import vectordb_channel_provider

empty = google.protobuf.empty_pb2.Empty()
from google.protobuf.json_format import MessageToDict


class VectorDbAdminClient(object):
    """Vector DB Admin client"""

    def __init__(
        self,
        *,
        seeds: Union[types.HostPort, tuple[types.HostPort, ...]],
        listener_name: Optional[str] = None,
    ) -> None:

        if not seeds:
            raise Exception("at least one seed host needed")

        if isinstance(seeds, types.HostPort):
            seeds = (seeds,)

        self.__channelProvider = vectordb_channel_provider.VectorDbChannelProvider(
            seeds, listener_name
        )

    async def index_create(
        self,
        *,
        namespace: str,
        name: str,
        vector_bin_name: str,
        dimensions: int,
        vector_distance_metric: Optional[types.VectorDistanceMetric] = (
            types.VectorDistanceMetric.SQUARED_EUCLIDEAN
        ),
        sets: Optional[str] = None,
        index_params: Optional[types_pb2.HnswParams] = None,
        labels: Optional[dict[str, str]] = None,
    ):
        """Create an index"""

        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.get_channel()
        )
        if sets and not sets.strip():
            sets = None

        await index_stub.Create(
            types_pb2.IndexDefinition(
                id=types_pb2.IndexId(namespace=namespace, name=name),
                vectorDistanceMetric=vector_distance_metric.value,
                setFilter=sets,
                hnswParams=index_params,
                bin=vector_bin_name,
                dimensions=dimensions,
                labels=labels,
            )
        )

        await self.__wait_for_index_creation(
            namespace=namespace, name=name, timeout=100_000
        )

    async def index_drop(self, *, namespace: str, name: str):
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.get_channel()
        )
        await index_stub.Drop(types_pb2.IndexId(namespace=namespace, name=name))

    async def index_list(self) -> list[Any]:

        try:
            index_stub = index_pb2_grpc.IndexServiceStub(
                self.__channelProvider.get_channel()
            )
            response = await index_stub.List(empty)
            return response.indices
        except Exception as e:
            raise

    async def index_get(
        self, *, namespace: str, name: str
    ) -> types_pb2.IndexDefinition:
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.get_channel()
        )
        response = await index_stub.Get(
            types_pb2.IndexId(namespace=namespace, name=name)
        )
        return MessageToDict(response)

    async def index_get_status(
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

    async def __wait_for_index_creation(
        self, *, namespace: str, name: str, timeout: int = sys.maxsize
    ):
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
                res = await self.index_get_status(namespace=namespace, name=name)

                # Index has been created
                return
            except grpc.RpcError as e:
                if (
                    e.code() == grpc.StatusCode.UNAVAILABLE
                    or e.code() == grpc.StatusCode.NOT_FOUND
                ):
                    # Wait for some more time.
                    time.sleep(wait_interval)
                else:
                    raise e

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.run(self.close())

    async def close(self):
        await self.__channelProvider.close()
