import asyncio
import sys
import time
from typing import Any, Optional, Union

import google.protobuf.empty_pb2
from google.protobuf.json_format import MessageToDict
import grpc

from . import index_pb2
from . import index_pb2_grpc
from . import types
from . import types_pb2
from . import vectordb_channel_provider

empty = google.protobuf.empty_pb2.Empty()


class VectorDbAdminClient(object):
    """
    Vector DB Admin client.

    This client allows interaction with the Vector DB administrative features such as index management.

    Attributes:
        __channelProvider (vectordb_channel_provider.VectorDbChannelProvider):
            Channel provider for Vector DB connections.
    """

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
        """
        Initialize the VectorDbAdminClient.

        Args:
            seeds (Union[types.HostPort, tuple[types.HostPort, ...]]):
                Seeds for establishing connections with Vector DB nodes.
            listener_name (Optional[str], optional):
                Listener name for the client. Defaults to None.

        Raises:
            Exception: Raised when no seed host is provided.
        """

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
        """
        Create an index.

        Args:
            namespace (str): The namespace for the index.
            name (str): The name of the index.
            vector_bin_name (str): The name of the bin containing vector data.
            dimensions (int): The number of dimensions in the vector data.
            vector_distance_metric (Optional[types.VectorDistanceMetric], optional):
                The distance metric for the vectors. Defaults to SQUARED_EUCLIDEAN.
            sets (Optional[str], optional): The set filter for the index. Defaults to None.
            index_params (Optional[types_pb2.HnswParams], optional):
                Parameters for the index creation. Defaults to None.
            labels (Optional[dict[str, str]], optional): Additional labels for the index. Defaults to None.

        Raises:
            [List any exceptions raised]

        Note:
            This method creates an index with the specified parameters and waits for the index creation to complete.
            It waits for up to 100,000 seconds for the index creation to complete.
        """
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

        await self._wait_for_index_creation(
            namespace=namespace, name=name, timeout=100_000
        )

    async def index_drop(self, *, namespace: str, name: str):
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.get_channel()
        )
        """
        Drop an index.

        Args:
            namespace (str): The namespace of the index.
            name (str): The name of the index.

        Raises:
            [List any exceptions raised]

        Note:
            This method drops the specified index.
        """
        await index_stub.Drop(types_pb2.IndexId(namespace=namespace, name=name))

    async def index_list(self) -> list[Any]:
        """
        List all indices.

        Returns:
            list[Any]: A list of indices.

        Raises:
            [List any exceptions raised]

        Note:
            This method lists all indices available in the Vector DB.
        """
        try:
            index_stub = index_pb2_grpc.IndexServiceStub(
                self.__channelProvider.get_channel()
            )
            response = await index_stub.List(empty)
            return response.indices
        except Exception as e:
            raise e

    async def index_get(
        self, *, namespace: str, name: str
    ) -> types_pb2.IndexDefinition:
        """
        Retrieve the definition of an index.

        Args:
            namespace (str): The namespace of the index.
            name (str): The name of the index.

        Returns:
            types_pb2.IndexDefinition: The definition of the index.

        Raises:
            [List any exceptions raised]

        Note:
            This method retrieves the definition of the specified index.
        """

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
        Get the status of an index.

        Args:
            namespace (str): The namespace of the index.
            name (str): The name of the index.

        Returns:
            index_pb2.IndexStatusResponse: The status of the index.

        Raises:
            [List any exceptions raised]

        Note:
            This method retrieves the status of the specified index.
            Warning: This API is subject to change.
        """
        index_stub = index_pb2_grpc.IndexServiceStub(
            self.__channelProvider.get_channel()
        )
        response = await index_stub.GetStatus(
            types_pb2.IndexId(namespace=namespace, name=name)
        )

        return response

    async def _wait_for_index_creation(
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
                await self.index_get_status(namespace=namespace, name=name)

                # Index has been created
                return
            except grpc.RpcError as e:
                if e.code() in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.NOT_FOUND):
                    # Wait for some more time.
                    time.sleep(wait_interval)
                else:
                    raise e

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
