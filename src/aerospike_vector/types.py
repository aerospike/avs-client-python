import enum
from typing import Any


class HostPort(object):
    def __init__(
        self, *,
        address: str,
        port: int,
        isTls: Optional[bool]=False) -> None:
        self.address = address
        self.port = port
        self.isTls = isTls


class Key(object):
    def __init__(
        self, *,
        namespace: str,
        set: str,
        digest: bytearray,
        key: Any) -> None:
        self.namespace = namespace
        self.set = set
        self.digest = digest
        self.key = key


class RecordWithKey(object):
    def __init__(
        self, *,
        key: Key, 
        bins: dict[str, Any]) -> None:
        self.key = key
        self.bins = bins


class Neighbor(object):
    def __init__(
        self, *,
        key: Key,
        bins: dict[str, Any],
        distance: float) -> None:
        self.key = key
        self.bins = bins
        self.distance = distance

class VectorDistanceMetric(enum.Enum):
    SQUARED_EUCLIDEAN = types_pb2.VectorDistanceMetric.SQUARED_EUCLIDEAN
    COSINE = types_pb2.VectorDistanceMetric.COSINE
    DOT_PRODUCT = types_pb2.VectorDistanceMetric.DOT_PRODUCT
    MANHATTAN = types_pb2.VectorDistanceMetric.MANHATTAN
    HAMMING = types_pb2.VectorDistanceMetric.HAMMING


class HnswBatchingParams(object):
    def __init__(
        self, *,
        maxRecords: Optional[int] = 10000,
        interval: Optional[int] = 10000,
        disabled: Optional[bool] = False) -> None:
        self.maxRecords = maxRecords
        self.interval = interval
        self.disabled = disabled

class HnswParams(object):
    def __init__(
        self, *,
        m: Optional[int] = 16,
        efConstruction: Optional[int] = 100,
        ef: Optional[int] = 100,
        batchingParams: Optional[HnswBatchingParams] = HnswBatchingParams()) -> None:
        self.m = m
        self.efConstruction = efConstruction
        self.ef = ef
        self.batchingParams = batchingParams

class HnswSearchParams(object):
    def __init__(
        self, *,
        ef: Optional[int] = None) -> None:
        self.ef = ef
#
#// Params for the HNSW index
#message HnswParams {
#  // Maximum number bi-directional links per HNSW vertex. Greater values of
#  // 'm' in general provide better recall for data with high dimensionality, while
#  // lower values work well for data with lower dimensionality.
#  // The storage space required for the index increases proportionally with 'm'.
#  // The default value is 16.
#  optional uint32 m = 1;
#
#  // The number of candidate nearest neighbors shortlisted during index creation.
#  // Larger values provide better recall at the cost of longer index update times.
#  // The default is 100.
#  optional uint32 efConstruction = 2;
#
#  // The default number of candidate nearest neighbors shortlisted during search.
#  // Larger values provide better recall at the cost of longer search times.
#  // The default is 100.
#  optional uint32 ef = 3;
#
#  // Configures batching behaviour for batch based index update.
#  HnswBatchingParams batchingParams = 4;
#}

#// Params for the HNSW index search
#message HnswSearchParams {
#  // The default number of candidate nearest neighbors shortlisted during search.
#  // Larger values provide better recall at the cost of longer search times.
#  // The default is value set in HnswParams for the index.
#  optional uint32 ef = 1;
#}



#// Configures batching behaviour for batch based index update.
#message HnswBatchingParams {
#  // Maximum number of records to fit in a batch.
#  // The default value is 10000.
#  optional uint32 maxRecords = 1;
#
#  // The maximum amount of time in milliseconds to wait before finalizing a batch.
#  // The default value is 10000.
#  optional uint32 interval = 2;
#
#  // Disables batching for index updates.
#  // Default is false meaning batching is enabled.
#  optional bool disabled = 3;
#}
#