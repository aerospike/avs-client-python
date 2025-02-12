import asyncio
import logging
from typing import Union, Optional

from aerospike_vector_search import types
from aerospike_vector_search.aio.client import Client
from ..shared import helpers

logger = logging.getLogger(__name__)

class Index():
    """
    Index represents a HNSW index in Aerospike Vector Search (AVS).
    It provides methods to interact with the index, such as performing vector searches,
    updating index configuration, and getting index status.

    You should create an Index object by calling the :meth:`aerospike_vector_search.aio.Client.index` method.
    Creating an index object has some overhead, so they should be reused where possible.

    Using Index objects is the recommended way to interact with AVS indexes.

    .. code-block:: python

        import asyncio

        import aerospike_vector_search.aio as avs
        from aerospike_vector_search import types

        async def main():
            # Create and connect a client
            client = avs.Client(
                seeds=types.HostPort(
                    host="127.0.0.1",
                    port=5000,
                ),
                # comment out the below line if you are not using a load balancer
                # or are not using a single node AVS cluster.
                is_loadbalancer=True,
            )

            # Create the index in AVS
            await client.index_create(
                namespace="test",
                name="test_index",
                vector_field="vector",
                dimensions=3,
            )

            # Get an index object targeting the index we just created
            index = await client.index(
                namespace="test",
                name="test_index",
            )

            # Now you can perform targeted operations on the index
            tasks = []

            # Get the index definition
            tasks.append(index.get())

            # Perform an HNSW similarity search on the index
            tasks.append(index.vector_search(
                query=[1.0, 2.0, 3.0],
                limit=3,
            ))

            # Delete the index from AVS.
            tasks.append(index.drop())

            await asyncio.gather(*tasks)

            # Close the client
            # NOTE: This will also close any index objects created from this client
            # Index objects need the client that created them to be open to function
            # so only close the client when you are done with the index objects
            await client.close()

        asyncio.run(main())
    """
    def __init__(
            self,
            *,
            client: Client,
            name: str,
            namespace: str,
            vector_field: str,
            dimensions: int,
            vector_distance_metric: types.VectorDistanceMetric = (
                types.VectorDistanceMetric.SQUARED_EUCLIDEAN
            ),
            sets: Optional[str] = None,
            index_storage: Optional[types.IndexStorage] = None,
        ):
        self._client: Client = client
        self._name: str = name
        self._namespace: str = namespace
        self._vector_field: str = vector_field
        self._dimensions: int = dimensions
        self._vector_distance_metric: types.VectorDistanceMetric = vector_distance_metric
        self._sets: Optional[str] = sets
        self._index_storage: Optional[types.IndexStorage] = index_storage
    
    async def vector_search(
            self,
            *,
            query: list[Union[bool, float]],
            limit: int = 10,
            search_params: Optional[types.HnswSearchParams] = None,
            include_fields: Optional[list[str]] = None,
            exclude_fields: Optional[list[str]] = None,
            timeout: Optional[int] = None,
        ) -> list[types.Neighbor]:
        """
        Perform a vector search against this index.
        By default, the search results include all fields except the vector field.
        To include the vector field, add it to the include_fields list.
        
        :param query: The query vector for the search.
        :type query: list[Union[bool, float]]

        :param limit: The maximum number of neighbors to return. K value. Defaults to 10.
        :type limit: int

        :param search_params: Parameters for the HNSW algorithm.
            If None, the default parameters for the index are used. Defaults to None.
        :type search_params: Optional[types_pb2.HnswSearchParams]

        :param include_fields: A list of field names to retrieve from the results.
            When used, fields that are not included are not sent by the server,
            saving on network traffic.
            If a field is listed in both include_fields and exclude_fields,
            exclude_fields takes priority, and the field is not returned.
            If None, all fields are retrieved. Defaults to None.
        :type include_fields: Optional[list[str]]

        :param exclude_fields: A list of field names to exclude from the results.
            When used, the excluded fields are not sent by the server,
            saving on network traffic.
            If None, all fields are retrieved. Defaults to None.
        :type exclude_fields: Optional[list[str]]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Returns:
            list[types.Neighbor]: A list of neighbors records found by the search.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to vector search.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        exclusions = helpers._get_index_exclusions(
            self._vector_field,
            include_fields,
            exclude_fields
        )

        return await self._client.vector_search(
            namespace=self._namespace,
            index_name=self._name,
            query=query,
            limit=limit,
            search_params=search_params,
            include_fields=include_fields,
            exclude_fields=exclusions,
            timeout=timeout,
        )
    
    async def vector_search_by_key(
            self,
            *,
            key: Union[int, str, bytes, bytearray],
            namespace: Optional[str] = None,
            vector_field: Optional[str] = None,
            limit: int = 10,
            set_name: Optional[str] = None,
            search_params: Optional[types.HnswSearchParams] = None,
            include_fields: Optional[list[str]] = None,
            exclude_fields: Optional[list[str]] = None,
            timeout: Optional[int] = None,
        ) -> list[types.Neighbor]:
        """
        Perform a vector search against this index using a record in Aerospike.
        By default, the search results include all fields except the vector field.
        To include the vector field, add it to the include_fields list.
        
        :param key: The primary key of the record that stores the vector to use in the search.
        :type key: Union[int, str, bytes, bytearray]

        :param namespace: The namespace that stores the record. Defaults to the namespace of the index.
        :type namespace: Optional[str]

        :param vector_field: The name of the field within the record containing vector data. Defaults to the vector field of the index.
        :type vector_field: Optional[str]

        :param limit: The maximum number of neighbors to return. K value. Defaults to 10.
        :type limit: int

        :param set_name: The set that stores the record, if any. Defaults to None.
        :type set_name: Optional[str]

        :param search_params: Parameters for the HNSW algorithm.
            If None, the default parameters for the index are used. Defaults to None.
        :type search_params: Optional[types_pb2.HnswSearchParams]

        :param include_fields: A list of field names to retrieve from the results.
            When used, fields that are not included are not sent by the server,
            saving on network traffic.
            If a field is listed in both include_fields and exclude_fields,
            exclude_fields takes priority, and the field is not returned.
            If None, all fields are retrieved. Defaults to None.
        :type include_fields: Optional[list[str]]

        :param exclude_fields: A list of field names to exclude from the results.
            When used, the excluded fields are not sent by the server,
            saving on network traffic.
            If None, all fields are retrieved. Defaults to None.
        :type exclude_fields: Optional[list[str]]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Returns:
            list[types.Neighbor]: A list of neighbors records found by the search.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to vector search.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        exclusions = helpers._get_index_exclusions(
            self._vector_field,
            include_fields,
            exclude_fields
        )

        return await self._client.vector_search_by_key(
            search_namespace=self._namespace,
            index_name=self._name,
            key=key,
            key_namespace=namespace or self._namespace,
            vector_field=vector_field or self._vector_field,
            limit=limit,
            key_set=set_name,
            search_params=search_params,
            include_fields=include_fields,
            exclude_fields=exclusions,
            timeout=timeout,
        )

    async def is_indexed(
            self,
            *,
            key: Union[int, str, bytes, bytearray],
            set_name: Optional[str] = None,
            timeout: Optional[int] = None,
        ) -> bool:
        """
        Check if a record is indexed.

        :param key: The primary key for the record.
        :type key: Union[int, str, bytes, bytearray, np.generic, np.ndarray]

        :param set_name: The name of the set to which the record belongs. Defaults to None.
        :type set_name: optional[str]

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Returns:
            bool: True if the record is indexed, False otherwise.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to check if the vector is indexed.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        return await self._client.is_indexed(
            namespace=self._namespace,
            key=key,
            index_name=self._name,
            index_namespace=self._namespace,
            set_name=set_name,
            timeout=timeout,
        )

    async def get_percent_unmerged(
            self,
            *,
            timeout: Optional[int] = None,
        ) -> float:
        """
        Get the ratio of unmerged records to valid verticies in the index as a percentage.
        This is useful for determining the completeness of the index. Estimating
        the accuracy of search results, checking the progress of index healing,
        and determining if the index healer is keeping up with record writes.

        In general, the lower the percentage, the better the search accuracy.

        It is possible for the percentage to be greater than 100% if the number
        of unmerged records exceeds the number of valid vertices in the index.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Returns:
            float: The percentage of unmerged records in the index.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get the percentage of unmerged records in the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        return await self._client.index_get_percent_unmerged(
            namespace=self._namespace,
            name=self._name,
            timeout=timeout,
        )

    async def update(
            self,
            *,
            labels: Optional[dict[str, str]] = None,
            hnsw_update_params: Optional[types.HnswIndexUpdate] = None,
            mode: Optional[types.IndexMode] = None,
            timeout: Optional[int] = None,
        ) -> None:
        """
        Update index configuration.

        :param index_labels: Optional labels associated with the index. Defaults to None.
        :type index_labels: Optional[dict[str, str]]

        :param hnsw_update_params: Parameters for updating HNSW index settings. Defaults to None.
        :type hnsw_update_params: Optional[types.HnswIndexUpdate]

        :param mode: The mode of the index. Defaults to distributed.
        :type mode: Optional[types.IndexMode]

        :param timeout: Time in seconds this operation will wait before raising an error. Defaults to None.
        :type timeout: int

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to update the index.
        """

        await self._client.index_update(
            namespace=self._namespace,
            name=self._name,
            index_labels=labels,
            hnsw_update_params=hnsw_update_params,
            mode=mode,
            timeout=timeout,
        )
    
    async def get(
            self,
            *,
            apply_defaults: bool = True,
            timeout: Optional[int] = None,
        ) -> types.IndexDefinition:
        """
        Retrieve information related to the index from AVS.

        :param apply_defaults: Apply default values to parameters which are not set by user. Defaults to True.
        :type apply_defaults: bool

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Returns: dict[str, Union[int, str]: Information about an index.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        """
        return await self._client.index_get(
            namespace=self._namespace,
            name=self._name,
            apply_defaults=apply_defaults,
            timeout=timeout,
        )
    
    async def status(
            self,
            *,
            timeout: Optional[int] = None,
        ) -> types.IndexStatusResponse:
        """
        Retrieve index status information. Results include metrics like the number of vertices in the index, 
        the number of unmerged index records, and the number of vector records indexed.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Returns: IndexStatusResponse: AVS response containing index status information.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to get the index status.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """
        return await self._client.index_get_status(
            namespace=self._namespace,
            name=self._name,
            timeout=timeout,
        )

    async def drop(
            self,
            *,
            timeout: Optional[int] = None,
        ) -> None:
        """
        Deletes the index from AVS.

        :param timeout: Time in seconds this operation will wait before raising an :class:`AVSServerError <aerospike_vector_search.types.AVSServerError>`. Defaults to None.
        :type timeout: int

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to drop the index.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.

        Note:
            This method drops an index with the specified parameters and waits for the index deletion to complete.
            It waits for up to 100,000 seconds for the index deletion to complete.
        """
        return await self._client.index_drop(
            namespace=self._namespace,
            name=self._name,
            timeout=timeout,
        )



