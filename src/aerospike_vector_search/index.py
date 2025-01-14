import logging
from typing import Union, Optional

from aerospike_vector_search.client import Client, types

logger = logging.getLogger(__name__)

class Index():
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
        self._client = client
        self._name = name
        self._namespace = namespace
        self._vector_field = vector_field
        self._dimensions = dimensions
        self._vector_distance_metric = vector_distance_metric
        self._sets = sets
        self._index_storage = index_storage
    
    def vector_search(
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

        :param field_names: Deprecated, use include_fields instead.
        :type field_names: Optional[list[str]]

        Returns:
            list[types.Neighbor]: A list of neighbors records found by the search.

        Raises:
            AVSServerError: Raised if an error occurs during the RPC communication with the server while attempting to vector search.
            This error could occur due to various reasons such as network issues, server-side failures, or invalid request parameters.
        """

        # exclude vector data from the results by default to
        # avoid sending large amounts of data over the network
        # users can override this by passing the vector field in the include_fields
        exclusions = [self._vector_field]

        if exclude_fields:
            exclusions.extend(exclude_fields)

        return self._client.vector_search(
            namespace=self._namespace,
            index_name=self._name,
            query=query,
            limit=limit,
            search_params=search_params,
            include_fields=include_fields,
            exclude_fields=exclusions,
            timeout=timeout,
        )
    
    def vector_search_by_key(
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

        # exclude vector data from the results by default to
        # avoid sending large amounts of data over the network
        # users can override this by passing the vector field in the include_fields
        exclusions = [self._vector_field]

        if exclude_fields:
            exclusions.extend(exclude_fields)
        
        return self._client.vector_search_by_key(
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

    def is_indexed(
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

        return self._client.is_indexed(
            namespace=self._namespace,
            key=key,
            index_name=self._name,
            index_namespace=self._namespace, #TODO does this need to be the index overhead namespace?
            set_name=set_name or self._sets,
            timeout=timeout,
        )

    def get_percent_unmerged(
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
        return self._client.index_get_percent_unmerged(
            namespace=self._namespace,
            name=self._name,
            timeout=timeout,
        )





