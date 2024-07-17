import enum
from typing import Any, Optional

from .shared.proto_generated import types_pb2


class HostPort(object):
    """
    represents host, port and TLS usage information.
    Used primarily when intializing client.

    Args:
        host (str): The host address.
        port (int): The port number.
        is_tls (Optional[bool], optional): Indicates if TLS is enabled. Defaults to False.
    """

    def __init__(self, *, host: str, port: int, is_tls: Optional[bool] = False) -> None:
        self.host = host
        self.port = port
        self.is_tls = is_tls


class Key(object):
    """
    Represents a record key.
    Used in RecordWithKey.

    Args:
        namespace (str): The namespace for the key.
        set (str): The set for the key.
        key (Any): The key itself.
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

    Args:
        key (Key): The key of the record.
        fields (dict[str, Any]): The fields associated with the record.
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

    This class represents a neighboring record in relation to a query record. It includes information such as the key, fields, and distance from the query record.

    Args:
        key (Key): The Key instance identifying the neighboring record.
        fields (dict[str, Any]): A dictionary representing fields associated with the neighboring record.
        distance (float): The distance between the neighboring record and the query record, calculated based on the chosen VectorDistanceMetric.

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
    Enumeration of vector distance metrics.
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

class User(object):
    """

    PLACEHOLDER FOR TEXT 
    Args:
        max_records (Optional[int], optional): Maximum number of records to fit in a batch. Defaults to 10000.
        interval (Optional[int], optional): The maximum amount of time in milliseconds to wait before finalizing a batch. Defaults to 10000.
        disabled (Optional[bool], optional): Disables batching for index updates. Default is False.
    """

    def __init__(
        self,
        *,
        username: str,
        roles: Optional[list[int]] = 10000,
    ) -> None:
        self.username = username
        self.roles = roles

class HnswBatchingParams(object):
    """
    Parameters for configuring batching behaviour for batch based index update.

    Args:
        max_records (Optional[int], optional): Maximum number of records to fit in a batch. Defaults to 10000.
        interval (Optional[int], optional): The maximum amount of time in milliseconds to wait before finalizing a batch. Defaults to 10000.
        disabled (Optional[bool], optional): Disables batching for index updates. Default is False.
    """

    def __init__(
        self,
        *,
        max_records: Optional[int] = 10000,
        interval: Optional[int] = 10000,
    ) -> None:
        self.max_records = max_records
        self.interval = interval

    def _to_pb2(self):
        params = types_pb2.HnswBatchingParams()
        params.maxRecords = self.max_records
        params.interval = self.interval
        return params


class HnswHealerParams(object):
    def __init__(self, *, max_scan_rate_per_node: Optional[int] = None, max_scan_page_size: Optional[int] = None, re_index_percent: Optional[int] = None, schedule_delay: Optional[int] = None, parallelism: Optional[int] = None) -> None:
        self.max_scan_rate_per_node = max_scan_rate_per_node
        self.max_scan_page_size = max_scan_page_size
        self.re_index_percent = re_index_percent
        self.schedule_delay = schedule_delay
        self.parallelism = parallelism

    def _to_pb2(self):
        params = types_pb2.HnswHealerParams()
        if self.max_scan_rate_per_node:
            params.maxScanRatePerNode = self.max_scan_rate_per_node

        if self.max_scan_page_size:

            params.maxScanPageSize = self.max_scan_page_size

        if self.re_index_percent:

            params.reindexPercent = self.re_index_percent

        if self.schedule_delay:

            params.scheduleDelay = self.schedule_delay

        if self.parallelism:

            params.parallelism = self.parallelism

        return params


class HnswCachingParams(object):
    def __init__(self, *, max_entries: Optional[int] = None, expiry: Optional[int] = None) -> None:
        self.max_entries = max_entries
        self.expiry = expiry

    def _to_pb2(self):
        params = types_pb2.HnswCachingParams()
        if self.max_entries:
            params.maxEntries = self.max_entries
        if self.expiry:
            params.expiry = self.expiry
        return params

class HnswIndexMergeParams(object):
    def __init__(self, *, parallelism: Optional[int] = None) -> None:
        self.parallelism = parallelism

    def _to_pb2(self):
        params = types_pb2.HnswIndexMergeParams()
        if self.parallelism:
            params.parallelism = self.parallelism
        return params


class HnswParams(object):
    """
    Parameters for the Hierarchical Navigable Small World (HNSW) algorithm, used for approximate nearest neighbor search.

    Args:
        m (Optional[int], optional): The number of bi-directional links created per level during construction. Larger 'm' values lead to higher recall but slower construction. Defaults to 16.
        ef_construction (Optional[int], optional): The size of the dynamic list for the nearest neighbors (candidates) during the index construction. Larger 'ef_construction' values lead to higher recall but slower construction. Defaults to 100.
        ef (Optional[int], optional): The size of the dynamic list for the nearest neighbors (candidates) during the search phase. Larger 'ef' values lead to higher recall but slower search. Defaults to 100.
        batching_params (Optional[HnswBatchingParams], optional): Parameters related to configuring batch processing, such as the maximum number of records per batch and batching interval. Defaults to HnswBatchingParams().
    """

    def __init__(
        self,
        *,
        m: Optional[int] = 16,
        ef_construction: Optional[int] = 100,
        ef: Optional[int] = 100,
        batching_params: Optional[HnswBatchingParams] = HnswBatchingParams(),
        max_mem_queue_size: Optional[int] = None,
        caching_params: Optional[HnswCachingParams] = HnswCachingParams(),
        healer_params: Optional[HnswHealerParams] = HnswHealerParams(),
        merge_params: Optional[HnswIndexMergeParams] = HnswIndexMergeParams()
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
        params.m = self.m
        params.efConstruction = self.ef_construction
        params.ef = self.ef
        if self.max_mem_queue_size:
            params.maxMemQueueSize = self.max_mem_queue_size

        params.batchingParams.CopyFrom(self.batching_params._to_pb2())
        params.cachingParams.CopyFrom(self.caching_params._to_pb2())

        params.healerParams.CopyFrom(self.healer_params._to_pb2())

        params.mergeParams.CopyFrom(self.merge_params._to_pb2())

        return params



class HnswSearchParams(object):
    def __init__(self, *, ef: Optional[int] = None) -> None:
        """
        Parameters for Hierarchical Navigable Small World (HNSW) search.

        HNSW is an algorithm used for approximate nearest neighbor search.

        Args:
            ef (Optional[int], optional): The parameter 'ef' controls the trade-off between search quality and search efficiency. It determines the size of the dynamic list of nearest neighbors (candidates) examined during the search phase. Larger values of 'ef' typically yield higher recall but slower search times. Defaults to None, meaning the algorithm uses a library-defined default value.

        Notes:
            - 'ef' stands for "exploration factor."
            - Setting 'ef' to a higher value increases the recall (i.e., the likelihood of finding the true nearest neighbors) at the cost of increased computational overhead during the search process.

        """
        self.ef = ef

    def _to_pb2(self):
        params = types_pb2.HnswSearchParams()
        params.ef = self.ef
        return params

class IndexStorage(object):
    def __init__(self, *, namespace: Optional[str] = None, set_name: Optional[str] = None) -> None:
        self.namespace = namespace
        self.set_name = set_name

    def _to_pb2(self):
        index_storage = types_pb2.IndexStorage()
        index_storage.namespace = self.namespace
        index_storage.set = self.set_name
        return index_storage


class AVSError(Exception):
    """
    Custom exception raised for errors related to AVS.
    """

    pass


class AVSServerError(AVSError):
    """
    Custom exception raised for errors related to the AVS server.

    Attributes:
        status (int): The status code associated with the error.
        details (str): Details about the error.
        debug_error_string (str): Debug error string providing additional error information.

    Args:
        rpc_error (Exception): The original gRPC error object from which AVSError is derived.
            This error object is used to extract status, details, and debug information.
    """

    def __init__(self, *, rpc_error) -> None:
        self.rpc_error = rpc_error
