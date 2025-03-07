import enum
from typing import Any, Optional

from .shared.proto_generated import types_pb2

###########################
#### ENUMS ################
###########################

class _ProtoEnum(enum.Enum):
    """
    Base class for enums that map to protobuf enums.
    """

    @classmethod
    def _from_proto(cls, value):
        """
        Convert a protobuf enum value to a Python enum value.
        """
        return cls(value)

    def _to_proto(self):
        """
        Convert a Python enum value to a protobuf enum value.
        """
        return self.value


class IndexReadiness(_ProtoEnum):
    """
    Index ready status.

    This enumeration defines the readiness of an index:

    - **READY**: The index is ready to handle updates and queries.
    - **NOT_READY**: The index is not yet fully built and shouldn't be considered ready to handle updates or queries.

    This corresponds to the Status protobuf message.
    """

    READY = types_pb2.Status.READY
    NOT_READY = types_pb2.Status.NOT_READY


class StandaloneIndexState(_ProtoEnum):
    """
    Standalone index state.

    This enumeration defines the states a standalone index can be in:

    - **CREATING**: Index is being created.
    - **CREATED**: Index has been created but is not yet persisted.
    - **PERSISTING**: The index is being persisted to storage.
    - **PERSISTED**: The index has been persisted to storage.
    - **UPDATING**: The index is being marked DISTRIBUTED.
    - **UPDATED**: The index has been updated.
    - **FAILED**: The index has failed.
    """

    CREATING = types_pb2.StandaloneIndexState.CREATING
    CREATED = types_pb2.StandaloneIndexState.CREATED
    PERSISTING = types_pb2.StandaloneIndexState.PERSISTING
    PERSISTED = types_pb2.StandaloneIndexState.PERSISTED
    UPDATING = types_pb2.StandaloneIndexState.UPDATING
    UPDATED = types_pb2.StandaloneIndexState.UPDATED
    FAILED = types_pb2.StandaloneIndexState.FAILED


class VectorDistanceMetric(_ProtoEnum):
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

    SQUARED_EUCLIDEAN = types_pb2.VectorDistanceMetric.SQUARED_EUCLIDEAN
    COSINE = types_pb2.VectorDistanceMetric.COSINE
    DOT_PRODUCT = types_pb2.VectorDistanceMetric.DOT_PRODUCT
    MANHATTAN = types_pb2.VectorDistanceMetric.MANHATTAN
    HAMMING = types_pb2.VectorDistanceMetric.HAMMING


class IndexMode(_ProtoEnum):
    """
    Index mode.

    This enumeration defines the modes an index can operate in:

    - **DISTRIBUTED**: The index is maintained by any node in the cluster.
    - **STANDALONE**: The index is maintained by a single node in the cluster. The node must have the standalone-indexer role.

    DISTRIBUTED is used when an index has streaming updates and needs to searchable.
    STANDALONE is used when an index needs to index offline data quickly and does not need to be searchable.
    STANDALONE indexes switch to DISTRIBUTED mode when they finish indexing.
    """

    DISTRIBUTED = types_pb2.IndexMode.DISTRIBUTED
    STANDALONE = types_pb2.IndexMode.STANDALONE


###########################
#### DATA CLASSES #########
###########################


class HostPort(object):
    """
    represents host, port and TLS usage information.
    Used primarily when initializing client.

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

    :param set: str: The set for the key. Use the empty string "" to signify no set.
    :type set: str

    :param key: (Any): The key itself.
    :type key: Union[int, str, bytes, bytearray, np.ndarray, np.generic]

    """

    def __init__(self, *, namespace: str, set: str, key: Any) -> None:
        self.namespace = namespace
        self.set = set
        self.key = key

    def __repr__(self) -> str:
        return (
            f"Key(namespace={self.namespace}, "
            f"set={self.set}, "
            f"key={self.key})"
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the key.
        """
        return f"Key: namespace='{self.namespace}', set='{self.set}', key={self.key}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Key):
            return NotImplemented

        return (
            self.namespace == other.namespace
            and self.set == other.set
            and self.key == other.key
        )



class RecordWithKey(object):
    """
    Represents a record, including a key and fields.
    Return value for VectorDbClient.get.

    :param key: (Key): The key of the record.
    :type key: Key

    :param fields:  The fields associated with the record.
    :type fields: dict[str, Any]
    """

    def __init__(self, *, key: Key, fields: dict[str, Any]) -> None:
        self.key = key
        self.fields = fields

    def __str__(self) -> str:
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

    def __repr__(self) -> str:
        return (
            f"Neighbor(key={self.key}, "
            f"fields={self.fields}, "
            f"distance={self.distance})"
        )

    def __str__(self) -> str:
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
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Neighbor):
            return NotImplemented
        return (
            self.distance == other.distance
            and self.key == other.key
            and self.fields == other.fields
        )


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

    :param max_index_records: Maximum number of index records to fit in a batch.
                              Must be >= 1000. Defaults to 100,000.
    :param index_interval: The maximum amount of time in milliseconds to wait before
                           finalizing a batch of index records. Must be >= 10,000. Defaults to 30,000.
    :param max_reindex_records: Maximum number of reindex records to fit in a batch.
                                Defaults to max(max_index_records / 10, 1000).
    :param reindex_interval: The maximum amount of time in milliseconds to wait before
                             finalizing a batch of reindex records. Must be >= 10,000. Defaults to index_interval.
    """

    def __init__(
        self,
        *,
        max_index_records: Optional[int] = None,
        index_interval: Optional[int] = None,
        max_reindex_records: Optional[int] = None,
        reindex_interval: Optional[int] = None,
    ) -> None:

        self.max_index_records = max_index_records
        self.index_interval = index_interval
        self.max_reindex_records = max_reindex_records
        self.reindex_interval = reindex_interval


    def _to_pb2(self):
        params = types_pb2.HnswBatchingParams()
        if self.max_index_records:
            params.maxIndexRecords = self.max_index_records
        if self.index_interval:
            params.indexInterval = self.index_interval
        if self.max_reindex_records:
            params.maxReindexRecords = self.max_reindex_records
        if self.reindex_interval:
            params.reindexInterval = self.reindex_interval
        return params

    def __repr__(self) -> str:
        return (
            f"HnswBatchingParams(max_index_records={self.max_index_records}, "
            f"index_interval={self.index_interval}, "
            f"max_reindex_records={self.max_reindex_records}, "
            f"reindex_interval={self.reindex_interval})"
        )

    def __str__(self) -> str:
        return (
            f"HnswBatchingParams {{\n"
            f"  max_index_records: {self.max_index_records}\n"
            f"  index_interval: {self.index_interval}\n"
            f"  max_reindex_records: {self.max_reindex_records}\n"
            f"  reindex_interval: {self.reindex_interval}\n"
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

    :param max_scan_rate_per_node: Maximum allowed record scan rate per vector db node.  Defaults to 1_000.
    :type max_scan_rate_per_node: Optional[int]

    :param max_scan_page_size: Maximum number of records in a single scanned page. Defaults to 10_000.
    :type max_scan_page_size: Optional[int]

    :param re_index_percent: Percentage of good records randomly selected for reindexing in a healer cycle. Defaults to 10.
    :type re_index_percent: Optional[int]

    :param schedule: The quartz cron expression defining schedule at which the healer cycle is invoked. Defaults to "0 0/15 * ? * * *" (every 15 minutes).
        See more information on quartz cron expressions at https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html.
    :type schedule: Optional[str]

    :param parallelism: Maximum number of records to heal in parallel. Defaults to 1.
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

    :param max_entries: maximum number of entries to cache.  Defaults to 2_000_000.
    :type max_entries: Optional[int]

    :param expiry: Cache entries will expire after this time in milliseconds has expired after the entry was add to the cache. Defaults to 3_600_000 (1 hour).
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
        index. Defaults to 10 times the number of available CPU cores.
    :type index_parallelism: Optional[int]

    :param reindex_parallelism: The number of vectors merged in parallel from an indexing record batch-index to the main
        index. Defaults to either 1 or index_parallelism / 3, whichever is higher.
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

    :param m: The number of bi-directional links created per level during construction. Larger 'm' values lead to higher recall but slower construction. Optional, Defaults to 16.
    :type m: Optional[int]

    :param ef_construction: The size of the dynamic list for the nearest neighbors (candidates) during the index construction. Larger 'ef_construction' values lead to higher recall but slower construction. Optional, Defaults to 100.
    :type ef_construction: Optional[int]

    :param ef: The size of the dynamic list for the nearest neighbors (candidates) during the search phase. Larger 'ef' values lead to higher recall but slower search. Optional, Defaults to 100.
    :type ef: Optional[int]

    :param batching_params: Parameters related to configuring batch processing, such as the maximum number of records per batch and batching interval. Optional, Defaults to HnswBatchingParams().
    :type batching_params: HnswBatchingParams

    :param max_mem_queue_size: Maximum size of in-memory queue for inserted/updated vector records. Optional, Defaults to 1_000_000 records.
    :type max_mem_queue_size: Optional[int]

    :param index_caching_params: Parameters related to configuring caching for the HNSW index. Optional, Defaults to HnswCachingParams().
    :type index_caching_params: HnswCachingParams

    :param healer_params: Parameters related to configuring the HNSW index healer. Optional, Defaults to HnswHealerParams().
    :type healer_params: HnswHealerParams

    :param merge_params: Parameters related to configuring the merging of index records. Optional, Defaults to HnswIndexMergeParams().
    :type merge_params: HnswIndexMergeParams

    :param enable_vector_integrity_check: Verifies if the underlying vector has changed before returning the kANN result. Optional, Defaults to True.
    :type enable_vector_integrity_check: Optional[bool]

    :param record_caching_params: Parameters related to configuring caching for vector records. Optional, Defaults to HnswCachingParams().
    :type record_caching_params: HnswCachingParams

    """

    def __init__(
        self,
        *,
        m: Optional[int] = None,
        ef_construction: Optional[int] = None,
        ef: Optional[int] = None,
        batching_params: HnswBatchingParams = HnswBatchingParams(),
        max_mem_queue_size: Optional[int] = None,
        index_caching_params: HnswCachingParams = HnswCachingParams(),
        healer_params: HnswHealerParams = HnswHealerParams(),
        merge_params: HnswIndexMergeParams = HnswIndexMergeParams(),
        enable_vector_integrity_check : Optional[bool] = None,
        record_caching_params : HnswCachingParams = HnswCachingParams()
    ) -> None:
        self.m = m
        self.ef_construction = ef_construction
        self.ef = ef
        self.batching_params = batching_params
        self.max_mem_queue_size = max_mem_queue_size
        self.index_caching_params = index_caching_params
        self.healer_params = healer_params
        self.merge_params = merge_params
        self.enable_vector_integrity_check = enable_vector_integrity_check
        self.record_caching_params = record_caching_params

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

        if self.enable_vector_integrity_check is not None:
            params.enableVectorIntegrityCheck = self.enable_vector_integrity_check

        params.batchingParams.CopyFrom(self.batching_params._to_pb2())
        params.indexCachingParams.CopyFrom(self.index_caching_params._to_pb2())

        params.healerParams.CopyFrom(self.healer_params._to_pb2())

        params.mergeParams.CopyFrom(self.merge_params._to_pb2())

        params.recordCachingParams.CopyFrom(self.record_caching_params._to_pb2())

        return params

    def __repr__(self) -> str:
        batching_repr = repr(self.batching_params)
        index_caching_repr = repr(self.index_caching_params)
        healer_repr = repr(self.healer_params)
        merge_repr = repr(self.merge_params)
        record_caching_repr = repr(self.record_caching_params)
        return (
            f"HnswParams(m={self.m}, ef_construction={self.ef_construction}, "
            f"ef={self.ef}, batching_params={batching_repr}, max_mem_queue_size={self.max_mem_queue_size}, "
            f"index_caching_params={index_caching_repr}, healer_repr={healer_repr}, merge_repr={merge_repr}, enableVectorIntegrityCheck={self.enable_vector_integrity_check}, "
            f"record_caching_params={record_caching_repr}  )"
        )

    def __str__(self) -> str:
        batching_str = str(self.batching_params)
        index_caching_str = str(self.index_caching_params)
        healer_str = str(self.healer_params)
        merge_str = str(self.merge_params)
        record_caching_params = str(self.record_caching_params)
        return (
            f"hnswParams {{\n"
            f"  m: {self.m}\n"
            f"  efConstruction: {self.ef_construction}\n"
            f"  ef: {self.ef}\n"
            f"  {batching_str}\n"
            f"  maxMemQueueSize: {self.max_mem_queue_size}\n"
            f"  {index_caching_str}\n"
            f"  {healer_str}\n"
            f"  {merge_str}\n"
            f"  {self.enable_vector_integrity_check}\n"
            f"  {record_caching_params}\n"
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
        Defaults to 100.
    :type ef: Optional[int]

    Notes:
        - 'ef' stands for "exploration factor."
        - Setting 'ef' to a higher value increases the recall (i.e., the likelihood of finding the true nearest neighbors) at the cost of increased computational overhead during the search process.

    """

    def __init__(self, *, ef: Optional[int] = None) -> None:

        self.ef = ef

    def _to_pb2(self) -> types_pb2.HnswSearchParams:
        params = types_pb2.HnswSearchParams()
        params.ef = self.ef
        return params


class HnswIndexUpdate:
    """
    Represents parameters for updating HNSW index settings.

    :param batching_params: Configures batching behavior for batch-based index update.
    :type batching_params: Optional[HnswBatchingParams]

    :param max_mem_queue_size: Maximum size of in-memory queue for inserted/updated vector records.
    :type max_mem_queue_size: Optional[int]

    :param index_caching_params: Configures caching for HNSW index.
    :type index_caching_params: Optional[HnswCachingParams]

    :param healer_params: Configures index healer parameters.
    :type healer_params: Optional[HnswHealerParams]

    :param merge_params: Configures merging of batch indices to the main index.
    :type merge_params: Optional[HnswIndexMergeParams]

    :param enable_vector_integrity_check: Verifies if the underlying vector has changed before returning the kANN result.
    :type enable_vector_integrity_check: Optional[bool]

    :param record_caching_params: Configures caching for vector records.
    :type record_caching_params: Optional[HnswCachingParams]
    """

    def __init__(
            self,
            *,
            batching_params: Optional[HnswBatchingParams] = None,
            max_mem_queue_size: Optional[int] = None,
            index_caching_params: Optional[HnswCachingParams] = None,
            healer_params: Optional[HnswHealerParams] = None,
            merge_params: Optional[HnswIndexMergeParams] = None,
            enable_vector_integrity_check: Optional[bool] = True,
            record_caching_params: Optional[HnswCachingParams] = None,
    ) -> None:
        self.batching_params = batching_params
        self.max_mem_queue_size = max_mem_queue_size
        self.index_caching_params = index_caching_params
        self.healer_params = healer_params
        self.merge_params = merge_params
        self.enable_vector_integrity_check = enable_vector_integrity_check
        self.record_caching_params = record_caching_params

    def _to_pb2(self) -> types_pb2.HnswIndexUpdate:
        """
        Converts the HnswIndexUpdate instance to its protobuf representation.
        """
        params: types_pb2.HnswIndexUpdate = types_pb2.HnswIndexUpdate()

        if self.batching_params:
            params.batchingParams.CopyFrom(self.batching_params._to_pb2())

        if self.max_mem_queue_size is not None:
            params.maxMemQueueSize = self.max_mem_queue_size

        if self.index_caching_params:
            params.indexCachingParams.CopyFrom(self.index_caching_params._to_pb2())

        if self.healer_params:
            params.healerParams.CopyFrom(self.healer_params._to_pb2())

        if self.merge_params:
            params.mergeParams.CopyFrom(self.merge_params._to_pb2())

        if self.enable_vector_integrity_check is not None:
            params.enableVectorIntegrityCheck = self.enable_vector_integrity_check

        if self.record_caching_params:
            params.recordCachingParams.CopyFrom(self.record_caching_params._to_pb2())

        return params

    def __repr__(self) -> str:
        return (
            f"HnswIndexUpdate(batching_params={self.batching_params}, "
            f"max_mem_queue_size={self.max_mem_queue_size}, "
            f"index_caching_params={self.index_caching_params}, "
            f"healer_params={self.healer_params}, "
            f"merge_params={self.merge_params}, "
            f"enable_vector_integrity_check={self.enable_vector_integrity_check}, "
            f"record_caching_params={self.record_caching_params})"
        )

    def __str__(self) -> str:
        return (
            f"HnswIndexUpdate {{\n"
            f"  batching_params: {self.batching_params},\n"
            f"  max_mem_queue_size: {self.max_mem_queue_size},\n"
            f"  index_caching_params: {self.index_caching_params},\n"
            f"  healer_params: {self.healer_params},\n"
            f"  merge_params: {self.merge_params},\n"
            f"  enable_vector_integrity_check: {self.enable_vector_integrity_check},\n"
            f"  record_caching_params: {self.record_caching_params}\n"
            f"}}"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, HnswIndexUpdate):
            return NotImplemented
        return (
                self.batching_params == other.batching_params
                and self.max_mem_queue_size == other.max_mem_queue_size
                and self.index_caching_params == other.index_caching_params
                and self.healer_params == other.healer_params
                and self.merge_params == other.merge_params
                and self.enable_vector_integrity_check == other.enable_vector_integrity_check
                and self.record_caching_params == other.record_caching_params
        )

    def __getitem__(self, key):
        if not hasattr(self, key):
            raise AttributeError(f"'HnswIndexUpdate' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


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

    def __eq__(self, other) -> bool:
        if not isinstance(other, IndexStorage):
            return NotImplemented
        return self.namespace == other.namespace and self.set_name == other.set_name

    def __getitem__(self, key):
        key = str(key)  # Ensure key is a string
        if not hasattr(self, key):
            raise AttributeError(f"'IndexStorage' object has no attribute '{key}'")
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class IndexId(object):
    """
    AVS IndexId used in :class:`IndexDefinition`

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


# TBD add index type in future refactoring
class IndexDefinition(object):
    """
    AVS Index Definition

    :param id: Index ID.
    :type id: str

    :param dimensions: Number of dimensions.
    :type dimensions: int

    :param vector_distance_metric: Metric used to evaluate vector searches on the given index. Defaults to :attr:VectorDistanceMetric.SQUARED_EUCLIDEAN
    :type vector_distance_metric: VectorDistanceMetric

    :param field: Field name.
    :type field: str

    :param sets: Set name
    :type sets: str

    :param hnsw_params: HNSW parameters.
    :type hnsw_params: HnswParams

    :param storage: Index storage details. Defaults to None.
    :type storage: Optional[IndexStorage]

    :param index_labels: Metadata associated with the index. Defaults to None.
    :type index_labels: Optional[dict[str, str]]

    :param mode: Index mode. Defaults to :attr:IndexMode.DISTRIBUTED.
    :type mode: IndexMode
    """

    def __init__(
        self,
        *,
        id: str,
        dimensions: int,
        vector_distance_metric: VectorDistanceMetric = VectorDistanceMetric.SQUARED_EUCLIDEAN,
        field: str,
        sets: str,
        hnsw_params: HnswParams,
        storage: Optional[IndexStorage] = None,
        index_labels: dict[str, str],
        mode: IndexMode = IndexMode.DISTRIBUTED
    ) -> None:
        self.id = id
        self.dimensions = dimensions
        self.vector_distance_metric = vector_distance_metric
        self.field = field
        self.sets = sets
        self.hnsw_params = hnsw_params
        self.storage = storage
        self.index_labels = index_labels
        self.mode = mode

    def __repr__(self) -> str:
        return (
            f"IndexDefinition(id={self.id!r}, dimensions={self.dimensions}, field={self.field!r}, sets={self.sets!r},"
            f"vector_distance_metric={self.vector_distance_metric!r}, hnsw_params={self.hnsw_params!r}, storage={self.storage!r}, "
            f"index_labels={self.index_labels}, mode={self.mode!r})"
        )

    # TODO make this representation consistent with HNSWParams, i.e. use newlines and indentation, or remove it completely
    def __str__(self) -> str:
        return (
            f"IndexDefinition(id={self.id}, dimensions={self.dimensions}, field={self.field}, sets={self.sets!r}, "
            f"vector_distance_metric={self.vector_distance_metric}, hnsw_params={self.hnsw_params}, storage={self.storage}, "
            f"index_labels={self.index_labels}, mode={self.mode}"
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
            and self.mode == other.mode
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
    :type rpc_error: grpc.RpcError
    """

    def __init__(self, *, rpc_error) -> None:
        self.rpc_error = rpc_error

    def __str__(self) -> str:
        return f"AVSServerError(rpc_error={self.rpc_error})"


class AVSClientError(AVSError):
    """
    Custom exception raised for errors related to AVS client-side failures.

    :param message: error message raised by the AVS Client. Defaults to None.
    :type message: str
    """

    def __init__(self, *, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"AVSClientError(message={self.message})"


class AVSClientErrorClosed(AVSClientError):
    """
    Raised when an operation is attempted on a closed client.

    :param message: error message raised by the AVS Client. Defaults to None.
    :type message: str
    """

    def __str__(self) -> str:
        return f"AVSClientErrorClosed(message={self.message})"


class StandaloneIndexMetrics:
    """
    Represents metrics for a standalone index.

    Attributes:
    -----------
    index_id : IndexID
        The ID of the index with these metrics.
    
    state : StandaloneIndexState
        The state of the standalone index.
    
    scanned_vector_record_count : int
        The number of vector records scanned for indexing so far.
    
    indexed_vector_record_count : int
        The number of vector records indexed so far.
    """

    def __init__(
        self,
        *,
        index_id: IndexId,
        state: StandaloneIndexState,
        scanned_vector_record_count: int,
        indexed_vector_record_count: int
    ) -> None:
        self.index_id = index_id
        self.state = state
        self.scanned_vector_record_count = scanned_vector_record_count
        self.indexed_vector_record_count = indexed_vector_record_count

    def __str__(self) -> str:
        return (
            f"StandaloneIndexMetrics(index_id={self.index_id}, state={self.state}, "
            f"scanned_vector_record_count={self.scanned_vector_record_count}, "
            f"indexed_vector_record_count={self.indexed_vector_record_count})"
        )

    def __repr__(self) -> str:
        return (
            f"StandaloneIndexMetrics(index_id={self.index_id!r}, state={self.state!r}, "
            f"scanned_vector_record_count={self.scanned_vector_record_count!r}, "
            f"indexed_vector_record_count={self.indexed_vector_record_count!r})"
        )


class IndexStatusResponse:
    """
    Represents the response containing index status information.

    Attributes:
    -----------
    unmerged_record_count : int
        The number of unmerged index records.

    index_healer_vector_records_indexed : int
        The number of vector records indexed (0 if the healer has not yet run).

    index_healer_vertices_valid : int
        The number of vertices in the main index (0 if the healer has not yet run).
    
    standalone_metrics : Optional[StandaloneIndexMetrics]
        Extra metrics populated if the index is in standalone mode.
    
    readiness : IndexReady
        The readiness of the index.
    """

    def __init__(
            self,
            *,
            unmerged_record_count: int,
            index_healer_vector_records_indexed: int,
            index_healer_vertices_valid: int,
            standalone_metrics: Optional[StandaloneIndexMetrics],
            readiness: IndexReadiness,
        ) -> None:
        self.unmerged_record_count = unmerged_record_count
        self.index_healer_vector_records_indexed = index_healer_vector_records_indexed
        self.index_healer_vertices_valid = index_healer_vertices_valid
        self.standalone_metrics = standalone_metrics
        self.readiness = readiness

    def __str__(self) -> str:
        return (f"IndexStatusResponse("
                f"unmerged_record_count={self.unmerged_record_count}, "
                f"index_healer_vector_records_indexed={self.index_healer_vector_records_indexed}, "
                f"index_healer_vertices_valid={self.index_healer_vertices_valid}, "
                f"standalone_metrics={self.standalone_metrics}, "
                f"readiness={self.readiness})")

    def __repr__(self) -> str:
        return (f"IndexStatusResponse(unmerged_record_count={self.unmerged_record_count}, "
                f"index_healer_vector_records_indexed={self.index_healer_vector_records_indexed}, "
                f"index_healer_vertices_valid={self.index_healer_vertices_valid}, "
                f"standalone_metrics={self.standalone_metrics!r}, " 
                f"readiness={self.readiness!r})")
