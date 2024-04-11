import asyncio
import logging
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
logger = logging.getLogger(__name__)


class VectorDbAdminClient(object):
    """
    Aerospike Vector Admin Client

    This client is designed to conduct Aerospike Vector administrative operation such as creating indexes, querying index information, and dropping indexes.
    """

    def __init__(
        self,
        *,
        seeds: Union[types.HostPort, tuple[types.HostPort, ...]],
        listener_name: Optional[str] = None,
        is_loadbalancer: Optional[bool] = False,
    ) -> None:

        if not seeds:
            raise Exception("at least one seed host needed")

        if isinstance(seeds, types.HostPort):
            seeds = (seeds,)

        self._channelProvider = vectordb_channel_provider.VectorDbChannelProvider(
            seeds, listener_name, is_loadbalancer
        )
        """
        Initialize the Aerospike Vector Admin Client.

        Args:
            seeds (Union[types.HostPort, tuple[types.HostPort, ...]]): Used to create appropriate gRPC channels for interacting with Aerospike Vector.
            listener_name (Optional[str], optional): Advertised listener for the client. Defaults to None.
            is_loadbalancer (bool, optional): If true, the first seed address will be treated as a load balancer node.

        Raises:
            Exception: Raised when no seed host is provided.

        """

    async def index_create(
        self,
        *,
        namespace: str,
        name: str,
        vector_field: str,
        dimensions: int,
        vector_distance_metric: Optional[types.VectorDistanceMetric] = (
            types.VectorDistanceMetric.SQUARED_EUCLIDEAN
        ),
        sets: Optional[str] = None,
        index_params: Optional[types.HnswParams] = None,
        index_meta_data: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Create an index.

        Args:
            namespace (str): The namespace for the index.
            name (str): The name of the index.
            vector_field (str): The name of the field containing vector data.
            dimensions (int): The number of dimensions in the vector data.
            vector_distance_metric (Optional[types.VectorDistanceMetric], optional):
                The distance metric used to compare when performing a vector search.
                Defaults to VectorDistanceMetric.SQUARED_EUCLIDEAN.
            sets (Optional[str], optional): The set used for the index. Defaults to None.
            index_params (Optional[types.HnswParams], optional):
                Parameters used for tuning vector search. Defaults to None. If index_params is None, then the default values specified for
                types.HnswParams will be used.
            index_meta_data (Optional[dict[str, str]], optional): Meta data associated with the index. Defaults to None.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            This method creates an index with the specified parameters and waits for the index creation to complete.
            It waits for up to 100,000 seconds for the index creation to complete.
        """
        index_stub = index_pb2_grpc.IndexServiceStub(
            self._channelProvider.get_channel()
        )
        if sets and not sets.strip():
            sets = None

        logger.debug(
            "Creating index: namespace=%s, name=%s, vector_field=%s, dimensions=%d, vector_distance_metric=%s, "
            "sets=%s, index_params=%s, index_meta_data=%s",
            namespace,
            name,
            vector_field,
            dimensions,
            vector_distance_metric,
            sets,
            index_params,
            index_meta_data,
        )
        if index_params != None:
            index_params = index_params._to_pb2()
        try:
            await index_stub.Create(
                types_pb2.IndexDefinition(
                    id=types_pb2.IndexId(namespace=namespace, name=name),
                    vectorDistanceMetric=vector_distance_metric.value,
                    setFilter=sets,
                    hnswParams=index_params,
                    bin=vector_field,
                    dimensions=dimensions,
                    labels=index_meta_data,
                )
            )
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e
        try:
            await self._wait_for_index_creation(
                namespace=namespace, name=name, timeout=100_000
            )
        except grpc.RpcError as e:
            logger.error("Failed waiting for creation with error: %s", e)
            raise e

    async def index_drop(self, *, namespace: str, name: str) -> None:
        index_stub = index_pb2_grpc.IndexServiceStub(
            self._channelProvider.get_channel()
        )
        """
        Drop an index.

        Args:
            namespace (str): The namespace of the index.
            name (str): The name of the index.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            This method drops an index with the specified parameters and waits for the index deletion to complete.
            It waits for up to 100,000 seconds for the index deletion to complete.
        """
        logger.debug("Dropping index: namespace=%s, name=%s", namespace, name)
        try:
            await index_stub.Drop(types_pb2.IndexId(namespace=namespace, name=name))
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e
        try:
            await self._wait_for_index_deletion(
                namespace=namespace, name=name, timeout=100_000
            )
        except grpc.RpcError as e:
            logger.error("Failed waiting for deletion with error: %s", e)
            raise e

    async def index_list(self) -> list[dict]:
        """
        List all indices.

        Returns:
            list[dict]: A list of indices.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        index_stub = index_pb2_grpc.IndexServiceStub(
            self._channelProvider.get_channel()
        )

        logger.debug("Getting index list")
        try:
            response = await index_stub.List(empty)
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e
        response_list = []
        for index in response.indices:
            response_dict = MessageToDict(index)

            # Modifying dict to adhere to PEP-8 naming
            hnsw_params_dict = response_dict.pop("hnswParams", None)

            hnsw_params_dict["ef_construction"] = hnsw_params_dict.pop(
                "efConstruction", None
            )

            batching_params_dict = hnsw_params_dict.pop("batchingParams", None)
            batching_params_dict["max_records"] = batching_params_dict.pop(
                "maxRecords", None
            )
            hnsw_params_dict["batching_params"] = batching_params_dict

            response_dict["hnsw_params"] = hnsw_params_dict
            response_list.append(response_dict)
        return response_list

    async def index_get(
        self, *, namespace: str, name: str
    ) -> dict[str, Union[int, str]]:
        """
        Retrieve the information related with an index.

        Args:
            namespace (str): The namespace of the index.
            name (str): The name of the index.

        Returns:
            dict[str, Union[int, str]: Information about an index.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """

        index_stub = index_pb2_grpc.IndexServiceStub(
            self._channelProvider.get_channel()
        )

        logger.debug(
            "Getting index information: namespace=%s, name=%s", namespace, name
        )
        try:
            response = await index_stub.Get(
                types_pb2.IndexId(namespace=namespace, name=name)
            )
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e

        response_dict = MessageToDict(response)

        # Modifying dict to adhere to PEP-8 naming
        hnsw_params_dict = response_dict.pop("hnswParams", None)

        hnsw_params_dict["ef_construction"] = hnsw_params_dict.pop(
            "efConstruction", None
        )

        batching_params_dict = hnsw_params_dict.pop("batchingParams", None)
        batching_params_dict["max_records"] = batching_params_dict.pop(
            "maxRecords", None
        )
        hnsw_params_dict["batching_params"] = batching_params_dict

        response_dict["hnsw_params"] = hnsw_params_dict
        return response_dict

    async def index_get_status(self, *, namespace: str, name: str) -> int:
        """
        Retrieve the number of records queued to be merged into an index.

        Args:
            namespace (str): The namespace of the index.
            name (str): The name of the index.

        Returns:
            int: Records queued to be merged into an index.

        Raises:
            grpc.RpcError: Raised if an error occurs during the RPC communication with the server while attempting to create the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            This method retrieves the status of the specified index. If index_get_status is called the vector client puts some records into Aerospike Vector,
            the records may not immediately begin to merge into the index. To wait for all records to be merged into an index, use vector_client.wait_for_index_completion.

            Warning: This API is subject to change.
        """
        index_stub = index_pb2_grpc.IndexServiceStub(
            self._channelProvider.get_channel()
        )
        logger.debug("Getting index status: namespace=%s, name=%s", namespace, name)
        try:
            response = await index_stub.GetStatus(
                types_pb2.IndexId(namespace=namespace, name=name)
            )
        except grpc.RpcError as e:
            logger.error("Failed with error: %s", e)
            raise e

        return response.unmergedRecordCount

    async def _wait_for_index_creation(
        self, *, namespace: str, name: str, timeout: int = sys.maxsize
    ) -> None:
        """
        Wait for the index to be created.
        """

        # Wait interval between polling
        index_stub = index_pb2_grpc.IndexServiceStub(
            self._channelProvider.get_channel()
        )
        wait_interval = 0.100

        start_time = time.monotonic()
        while True:
            if start_time + timeout < time.monotonic():
                raise "timed-out waiting for index creation"
            try:
                await index_stub.GetStatus(
                    types_pb2.IndexId(namespace=namespace, name=name)
                )
                logger.debug("Index created succesfully")
                # Index has been created
                return
            except grpc.RpcError as e:
                if e.code() in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.NOT_FOUND):

                    # Wait for some more time.
                    await asyncio.sleep(wait_interval)
                else:
                    logger.error("Failed with error: %s", e)
                    raise e

    async def _wait_for_index_deletion(
        self, *, namespace: str, name: str, timeout: int = sys.maxsize
    ) -> None:
        """
        Wait for the index to be deleted.
        """

        # Wait interval between polling
        index_stub = index_pb2_grpc.IndexServiceStub(
            self._channelProvider.get_channel()
        )
        wait_interval = 0.100

        start_time = time.monotonic()
        while True:
            if start_time + timeout < time.monotonic():
                raise "timed-out waiting for index creation"
            try:
                await index_stub.GetStatus(
                    types_pb2.IndexId(namespace=namespace, name=name)
                )
                # Wait for some more time.
                await asyncio.sleep(wait_interval)
            except grpc.RpcError as e:
                if e.code() in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.NOT_FOUND):
                    logger.debug("Index deleted succesfully")
                    # Index has been created
                    return
                else:
                    raise e

    async def close(self):
        """
        Close the Aerospike Vector Admin Client.

        This method closes gRPC channels connected to Aerospike Vector.

        Note:
            This method should be called when the VectorDbAdminClient is no longer needed to release resources.
        """
        await self._channelProvider.close()

    async def __aenter__(self):
        """
        Enter an asynchronous context manager for the admin client.

        Returns:
            VectorDbAdminlient: Aerospike Vector Admin Client instance.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit an asynchronous context manager for the admin client.
        """
        await self.close()
