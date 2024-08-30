import enum
from typing import Any, Optional

from .shared.proto_generated import types_pb2


class HostPort(object):
    """
    represents host, port and TLS usage information.
    Used primarily when intializing client.

    :param host: The host address.
    :type host: str

    :param port: The port number.
    :type port: int

    """

    def __init__(self, *, host: str, port: int) -> None:
        self.host = host
        self.port = port


class Key(object):
    """
    Represents a record key.
    Used in RecordWithKey.

    :param namespace (str): The namespace for the key.
    :type namespace: str

    :param set: (optional[str]): The set for the key.
    :type set: optional[str]

    :param key: (Any): The key itself.
    :type key: Union[int, str, bytes, bytearray, np.ndarray, np.generic]

    """

    def __init__(self, *, namespace: str, set: str, key: Any) -> None:
        self.namespace = namespace
        self.set = set
        self.key = key

    def __str__(self):
        """
        Returns a string representation of the key.
        """
        return f"Key: namespace='{self.namespace}', set='{self.set}', key={self.key}"


class RecordWithKey(object):
    """
    Represents a record, including a key and fields.
    Return value for VectorDbClient.get.

    :param key: (Key): The key of the record.
    :type key: Key

    :param fields: : The fields associated with the record.
    :type fields: dict[str, Any]
    """

    def __init__(self, *, key: Key, fields: dict[str, Any]) -> None:
        self.key = key
        self.fields = fields

    def __str__(self):
        """
        Returns a string representation of the record, including a key and fields.
        """
        fields_info = ""
        for key, value in self.fields.items():
            if isinstance(value, list):
                if len(value) > 4:
                    value_str = (
                        "[\n"
                        + ",\n".join("\t\t\t{}".format(val) for val in value[:3])
                        + ",\n\t\t\t...\n\t\t]"
                    )
                else:
                    value_str = str(value)
            else:
                value_str = str(value)
            fields_info += "\n\t\t{}: {}".format(key, value_str)
        return "{{\n\t{},\n\tfields: {{\n{}\n\t}}\n}}".format(self.key, fields_info)


class Neighbor(object):
    """
    Represents a neighboring record in the context of approximate nearest neighbor search.

    This class represents a neighboring record in relation to a query record. It includes information such as the key, fields,
        and distance from the query record.


    :param key: The Key instance identifying the neighboring record.
    :type distance: Key

    :param fields: A dictionary representing fields associated with the neighboring record.
    :type distance: dict[str, Any]

    :param distance: The distance between the neighboring record and the query record, calculated based on the chosen
        VectorDistanceMetric.
    :type distance: float

    Notes:
        - The distance metric used to calculate the distance between records is determined by the chosen VectorDistanceMetric.
        - The neighbor's distance indicates how similar or dissimilar it is to the query record based on the chosen distance metric.
        - A smaller distance typically implies greater similarity between records.

    """

    def __init__(self, *, key: Key, fields: dict[str, Any], distance: float) -> None:
        self.key = key
        self.fields = fields
        self.distance = distance

    def __str__(self):
        """
        Returns a string representation of the neighboring record.
        """
        fields_info = ""
        for key, value in self.fields.items():
            if isinstance(value, list):
                if len(value) > 4:
                    value_str = (
                        "[\n"
                        + ",\n".join("\t\t\t{}".format(val) for val in value[:3])
                        + ",\n\t\t\t...\n\t\t]"
                    )
                else:
                    value_str = str(value)
            else:
                value_str = str(value)
            fields_info += "\n\t\t{}: {}".format(key, value_str)
        return "{{\n\t{},\n\tdistance: {},\n\tfields: {{\n{}\n\t}}\n}}".format(
            self.key, self.distance, fields_info
        )


class VectorDistanceMetric(enum.Enum):
    """
    Enumeration of vector distance metrics used for comparing vectors.

    This enumeration defines various metrics for calculating the distance or similarity between vectors:

    - **SQUARED_EUCLIDEAN**: Represents the squared Euclidean distance metric.
    - **COSINE**: Represents the cosine similarity metric.
    - **DOT_PRODUCT**: Represents the dot product similarity metric.
    - **MANHATTAN**: Represents the Manhattan distance (L1 norm) metric.
    - **HAMMING**: Represents the Hamming distance metric.

    Each metric provides a different method for comparing vectors, affecting how distances and similarities are computed in vector-based operations.
    """

    SQUARED_EUCLIDEAN: types_pb2.VectorDistanceMetric = (
        types_pb2.VectorDistanceMetric.SQUARED_EUCLIDEAN
    )
    COSINE: types_pb2.VectorDistanceMetric = types_pb2.VectorDistanceMetric.COSINE
    DOT_PRODUCT: types_pb2.VectorDistanceMetric = (
        types_pb2.VectorDistanceMetric.DOT_PRODUCT
    )
    MANHATTAN: types_pb2.VectorDistanceMetric = types_pb2.VectorDistanceMetric.MANHATTAN
    HAMMING: types_pb2.VectorDistanceMetric = types_pb2.VectorDistanceMetric.HAMMING


class Role(object):
    """
    AVS Role Object used in role-based authentication.

    :param id: Unique id to identify role
    :type id: str

    """

    def __init__(
        self,
        *,
        id: str,
    ) -> None:
        self.id = id

    def __repr__(self) -> str:
        return f"Role(id={self.id!r})"

    def __str__(self) -> str:
        return f"Role {{\n  id: {self.id}\n}}"

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(f"'Role' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


class User(object):
    """
    AVS User Object used in role-based authentication.

    :param username: Username associated with user.
    :type username: str

    :param roles: roles associated with user.
    :type roles: list[str]

    """

    def __init__(
        self,
        *,
        username: str,
        roles: Optional[list[Role]],
    ) -> None:
        self.username = username
        self.roles = roles


class HnswBatchingParams(object):
    """
    Parameters for configuring batching behaviour for batch based index update.

    :param max_records: Maximum number of records to fit in a batch. Defaults to server default..
    :param interval: The maximum amount of time in milliseconds to wait before finalizing a batch. Defaults to server default..
    """

    def __init__(
        self,
        *,
        max_records: Optional[int] = None,
        interval: Optional[int] = None,
    ) -> None:
        self.max_records = max_records
        self.interval = interval

    def _to_pb2(self):
        params = types_pb2.HnswBatchingParams()
        if self.max_records:
            params.maxRecords = self.max_records
        if self.interval:
            params.interval = self.interval
        return params

    def __repr__(self) -> str:
        return (
            f"batchingParams(max_records={self.max_records}, "
            f"interval={self.interval})"
        )

    def __str__(self) -> str:
        return (
            f"batchingParams {{\n"
            f"  maxRecords: {self.max_records}\n"
            f"  interval: {self.interval}\n"
            f"}}"
        )

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(
                f"'HnswBatchingParams' object has no attribute '{key}'"
            )
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class HnswHealerParams(object):
    """
    Parameters to configure the HNSW healer

    :param max_scan_rate_per_node: Maximum allowed record scan rate per vector db node.  Default is the global healer config, which is configured in the AVS Server.
    :type max_scan_rate_per_node: Optional[int]

    :param max_scan_page_size: Maximum number of records in a single scanned page.
        Default is the global healer config, which is configured in the AVS Server.
    :type max_scan_page_size: Optional[int]

    :param re_index_percent: Percentage of good records randomly selected for reindexing in a healer cycle.
        Default is the global healer config, which is configured in the AVS Server.
    :type re_index_percent: Optional[int]

    :param schedule: The quartz cron expression defining schedule at which the healer cycle is invoked.
        Default is the global healer config, which is configured in the AVS Server.
    :type schedule: Optional[str]

    :param parallelism: Maximum number of records to heal in parallel.
        Default is the global healer config, which is configured in the AVS Server.
    :type parallelism: Optional[int]
    """

    def __init__(
        self,
        *,
        max_scan_rate_per_node: Optional[int] = None,
        max_scan_page_size: Optional[int] = None,
        re_index_percent: Optional[int] = None,
        schedule: Optional[str] = None,
        parallelism: Optional[int] = None,
    ) -> None:
        self.max_scan_rate_per_node = max_scan_rate_per_node
        self.max_scan_page_size = max_scan_page_size
        self.re_index_percent = re_index_percent
        self.schedule = schedule
        self.parallelism = parallelism

    def _to_pb2(self):
        params = types_pb2.HnswHealerParams()
        if self.max_scan_rate_per_node:
            params.maxScanRatePerNode = self.max_scan_rate_per_node

        if self.max_scan_page_size:

            params.maxScanPageSize = self.max_scan_page_size

        if self.re_index_percent:

            params.reindexPercent = self.re_index_percent

        if self.schedule:

            params.schedule = self.schedule

        if self.parallelism:

            params.parallelism = self.parallelism

        return params

    def __repr__(self) -> str:
        return (
            f"HnswHealerParams(max_scan_rate_per_node={self.max_scan_rate_per_node}, "
            f"max_scan_page_size={self.max_scan_page_size}, "
            f"re_index_percent={self.re_index_percent}, "
            f"schedule={self.schedule}, "
            f"parallelism={self.parallelism})"
        )

    def __str__(self) -> str:
        return (
            f"HnswHealerParams {{\n"
            f"  max_scan_rate_per_node: {self.max_scan_rate_per_node}\n"
            f"  max_scan_page_size: {self.max_scan_page_size}\n"
            f"  re_index_percent: {self.re_index_percent}\n"
            f"  schedule: {self.schedule}\n"
            f"  parallelism: {self.parallelism}\n"
            f"}}"
        )

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(f"'HnswHealerParams' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class HnswCachingParams(object):
    """
    Parameters to configure the HNSW index cache

    :param max_entries: maximum number of entries to cache.  Default is the global cache config, which is configured in the AVS Server.
    :type max_entries: Optional[int]

    :param expiry: Cache entries will expire after this time in millseconds has expired after the entry was add to the cache.
        Default is the global cache config, which is configured in the AVS Server.
    :type expiry: Optional[int]

    """

    def __init__(
        self, *, max_entries: Optional[int] = None, expiry: Optional[int] = None
    ) -> None:
        self.max_entries = max_entries
        self.expiry = expiry

    def _to_pb2(self):
        params = types_pb2.HnswCachingParams()
        if self.max_entries:
            params.maxEntries = self.max_entries
        if self.expiry:
            params.expiry = self.expiry
        return params

    def __repr__(self) -> str:
        return (
            f"HnswCachingParams(max_entries={self.max_entries}, "
            f"expiry={self.expiry})"
        )

    def __str__(self) -> str:
        return (
            f"HnswCachingParams {{\n"
            f"  max_entries: {self.max_entries}\n"
            f"  expiry: {self.expiry}\n"
            f"}}"
        )

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(f"'HnswCachingParams' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class HnswIndexMergeParams(object):
    """
    Parameters to configure the HNSW index merge behavior.

    :param index_parallelism: The number of vectors merged in parallel from an indexing record batch-index to the main
        index. Default is the global healer config, which is configured in the AVS Server.
    :type index_parallelism: Optional[int]

    :param reindex_parallelism: The number of vectors merged in parallel from an indexing record batch-index to the main
        index. Default is the global healer config, which is configured in the AVS Server.
    :type reindex_parallelism: Optional[int]
    """

    def __init__(
        self,
        *,
        index_parallelism: Optional[int] = None,
        reindex_parallelism: Optional[int] = None,
    ) -> None:
        self.index_parallelism = index_parallelism
        self.reindex_parallelism = reindex_parallelism

    def _to_pb2(self):
        params = types_pb2.HnswIndexMergeParams()
        if self.index_parallelism:
            params.indexParallelism = self.index_parallelism
        if self.reindex_parallelism:
            params.reIndexParallelism = self.reindex_parallelism
        return params

    def __repr__(self) -> str:
        return (
            f"HnswIndexMergeParams(index_parallelism={self.index_parallelism}, "
            f"reindex_parallelism={self.reindex_parallelism})"
        )

    def __str__(self) -> str:
        return (
            f"HnswIndexMergeParams {{\n"
            f"  index_parallelism: {self.index_parallelism}\n"
            f"  reindex_parallelism: {self.reindex_parallelism}\n"
            f"}}"
        )

    def __getitem__(self, key):
        key = str(key)
        if not hasattr(self, key):
            raise AttributeError(
                f"'HnswIndexMergeParams' object has no attribute '{key}'"
            )
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class HnswParams(object):
    """
    Parameters for the Hierarchical Navigable Small World (HNSW) algorithm, used for approximate nearest neighbor search.

    :param m: The number of bi-directional links created per level during construction. Larger 'm' values lead to higher recall but slower construction. Defaults to 16.
    :type m: Optional[int]

    :param ef_construction: The size of the dynamic list for the nearest neighbors (candidates) during the index construction. Larger 'ef_construction' values lead to higher recall but slower construction. Defaults to 100.
    :type ef_construction: Optional[int]

    :param ef: The size of the dynamic list for the nearest neighbors (candidates) during the search phase. Larger 'ef' values lead to higher recall but slower search. Defaults to 100.
    :type ef: Optional[int]

    :param batching_params: Parameters related to configuring batch processing, such as the maximum number of records per batch and batching interval. Defaults to HnswBatchingParams().
    :type batching_params: Optional[HnswBatchingParams]
    """

    def __init__(
        self,
        *,
        m: Optional[int] = None,
        ef_construction: Optional[int] = None,
        ef: Optional[int] = None,
        batching_params: Optional[HnswBatchingParams] = HnswBatchingParams(),
        max_mem_queue_size: Optional[int] = None,
        caching_params: Optional[HnswCachingParams] = HnswCachingParams(),
        healer_params: Optional[HnswHealerParams] = HnswHealerParams(),
        merge_params: Optional[HnswIndexMergeParams] = HnswIndexMergeParams(),
    ) -> None:
        self.m = m
        self.ef_construction = ef_construction
        self.ef = ef
        self.batching_params = batching_params
        self.max_mem_queue_size = max_mem_queue_size
        self.caching_params = caching_params
        self.healer_params = healer_params
        self.merge_params = merge_params

    def _to_pb2(self):
        params = types_pb2.HnswParams()
        if self.m:
            params.m = self.m

        if self.ef_construction:
            params.efConstruction = self.ef_construction

        if self.ef:
            params.ef = self.ef

        if self.max_mem_queue_size:
            params.maxMemQueueSize = self.max_mem_queue_size

        params.batchingParams.CopyFrom(self.batching_params._to_pb2())
        params.cachingParams.CopyFrom(self.caching_params._to_pb2())

        params.healerParams.CopyFrom(self.healer_params._to_pb2())

        params.mergeParams.CopyFrom(self.merge_params._to_pb2())

        return params

    def __repr__(self) -> str:
        batching_repr = repr(self.batching_params)
        caching_repr = repr(self.caching_params)
        healer_repr = repr(self.healer_params)
        merge_repr = repr(self.merge_params)
        return (
            f"HnswParams(m={self.m}, ef_construction={self.ef_construction}, "
            f"ef={self.ef}, batching_params={batching_repr}, max_mem_queue_size={self.max_mem_queue_size}, "
            f"caching_params={caching_repr}, healer_repr={healer_repr}, merge_repr={merge_repr})"
        )

    def __str__(self) -> str:
        batching_str = str(self.batching_params)
        caching_str = str(self.caching_params)
        healer_str = str(self.healer_params)
        merge_str = str(self.merge_params)
        return (
            f"hnswParams {{\n"
            f"  m: {self.m}\n"
            f"  efConstruction: {self.ef_construction}\n"
            f"  ef: {self.ef}\n"
            f"  {batching_str}\n"
            f"  maxMemQueueSize: {self.max_mem_queue_size}\n"
            f"  {caching_str}\n"
            f"  {healer_str}\n"
            f"  {merge_str}\n"
            f"}}"
        )

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(f"'HnswParams' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class HnswSearchParams(object):
    """
    Parameters for Hierarchical Navigable Small World (HNSW) search.

    HNSW is an algorithm used for approximate nearest neighbor search.

    :param ef: The parameter 'ef' controls the trade-off between search quality and search efficiency.
        It determines the size of the dynamic list of nearest neighbors (candidates) examined during the
        search phase. Larger values of 'ef' typically yield higher recall but slower search times.
        Defaults to None, meaning the algorithm uses a library-defined default value.
    :type ef: Optional[int]

    Notes:
        - 'ef' stands for "exploration factor."
        - Setting 'ef' to a higher value increases the recall (i.e., the likelihood of finding the true nearest neighbors) at the cost of increased computational overhead during the search process.

    """

    def __init__(self, *, ef: Optional[int] = None) -> None:

        self.ef = ef

    def _to_pb2(self):
        params = types_pb2.HnswSearchParams()
        params.ef = self.ef
        return params


class IndexStorage(object):
    """
    Helper class primarily used to specify which namespace and set to build the index on.

    :param namespace: The name of the namespace to build the index on.
    :type namespace: str

    :param set_name: The name of the set to build the index on. Defaults to None.
    :type set_name: Optional[str]

    """

    def __init__(
        self, *, namespace: Optional[str], set_name: Optional[str] = None
    ) -> None:
        self.namespace = namespace
        self.set_name = set_name

    def _to_pb2(self):
        index_storage = types_pb2.IndexStorage()
        if self.namespace:

            index_storage.namespace = self.namespace
        if self.set_name:
            index_storage.set = self.set_name
        return index_storage

    def __repr__(self) -> str:
        return (
            f"IndexStorage(namespace={self.namespace!r}, "
            f"set_name={self.set_name!r})"
        )

    def __str__(self) -> str:
        return (
            f"IndexStorage {{\n"
            f"  namespace: {self.namespace}\n"
            f"  set_name: {self.set_name}\n"
            f"}}"
        )

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(f"'IndexStorage' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class IndexId(object):
    """
    AVS IndexId used in :class:`IndexDefintion`

    :param namespace: The name of the namespace in which to index records.
    :type namespace: str

    :param set_name: The name of the index.
    :type set_name: Optional[str]

    """

    def __init__(self, *, namespace: str, name: str) -> None:
        self.namespace = namespace
        self.name = name

    def __repr__(self) -> str:
        return f"IndexId(namespace={self.namespace!r}, name={self.name!r})"

    def __str__(self) -> str:
        return f"IndexId(namespace={self.namespace}, name={self.name})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, IndexId):
            return NotImplemented
        return self.namespace == other.namespace and self.name == other.name

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(f"'IndexId' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class IndexDefinition(object):
    """
    AVS Index Definition

    :param id: Index ID.
    :type id: str

    :param dimensions: Number of dimensions.
    :type dimensions: int

    :param vector_distance_metric: Metric used to evaluate vector searches on the given index
    :type vector_distance_metric: VectorDistanceMetric

    :param field: Field name.
    :type field: str

    :param sets: Set name
    :type sets: str

    :param hnsw_params: HNSW parameters.
    :type hnsw_params: HnswParams

    :param storage: Index storage details.
    :type storage: IndexStorage

    :param index_labels: Meta data associated with the index. Defaults to None.
    :type index_labels: Optional[dict[str, str]]
    """

    def __init__(
        self,
        *,
        id: str,
        dimensions: int,
        vector_distance_metric: types_pb2.VectorDistanceMetric,
        field: str,
        sets: str,
        hnsw_params: HnswParams,
        storage: IndexStorage,
        index_labels: dict[str, str],
    ) -> None:
        self.id = id
        self.dimensions = dimensions
        self.vector_distance_metric = vector_distance_metric
        self.field = field
        self.sets = sets
        self.hnsw_params = hnsw_params
        self.storage = storage
        self.index_labels = index_labels

    def __repr__(self) -> str:
        return (
            f"IndexDefinition(id={self.id!r}, dimensions={self.dimensions}, field={self.field!r}, sets={self.sets!r},"
            f"vector_distance_metric={self.vector_distance_metric!r}, hnsw_params={self.hnsw_params!r}, storage={self.storage!r}, "
            f"index_labels={self.index_labels}"
        )

    # TODO make this representation consistent with HNSWParams, i.e. use newlines and indentation, or remove it completely
    def __str__(self) -> str:
        return (
            f"IndexDefinition(id={self.id}, dimensions={self.dimensions}, field={self.field}, sets={self.sets!r}, "
            f"vector_distance_metric={self.vector_distance_metric}, hnsw_params={self.hnsw_params}, storage={self.storage}, "
            f"index_labels={self.index_labels}"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, IndexDefinition):
            return NotImplemented
        return (
            self.id == other.id
            and self.dimensions == other.dimensions
            and self.vector_distance_metric == other.vector_distance_metric
            and self.field == other.field
            and self.sets == other.sets
            and self.hnsw_params == other.hnsw_params
            and self.storage == other.storage
            and self.index_labels == other.index_labels
        )

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(f"'IndexDefinition' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class AVSError(Exception):
    """
    Custom exception raised for errors related to AVS.
    """

    pass


class AVSServerError(AVSError):
    """
    Custom exception raised for errors related to the AVS server.

    :param rpc_error: exception thrown by the grpc Python library on server calls. Defaults to None.
    :type set_name: grpc.RpcError

    """

    def __init__(self, *, rpc_error) -> None:
        self.rpc_error = rpc_error

    def __str__(self):
        return f"AVSServerError(rpc_error={self.rpc_error})"


class AVSClientError(AVSError):
    """
    Custom exception raised for errors related to AVS client-side failures..

    :param message: error messaging raised by the AVS Client. Defaults to None.
    :type set_name: str

    """

    def __init__(self, *, message) -> None:
        self.message = message

    def __str__(self):
        return f"AVSClientError(message={self.message})"
