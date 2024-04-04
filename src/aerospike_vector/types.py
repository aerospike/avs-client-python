import enum
from typing import Any, Optional

from . import types_pb2


class HostPort(object):
    def __init__(self, *, host: str, port: int, isTls: Optional[bool] = False) -> None:
        self.host = host
        self.port = port
        self.isTls = isTls


class Key(object):
    def __init__(
        self, *, namespace: str, set: str, digest: bytearray, key: Any
    ) -> None:
        self.namespace = namespace
        self.set = set
        self.digest = digest
        self.key = key
    def __str__(self):
        return f"Key: namespace='{self.namespace}', set='{self.set}', digest={self.digest}, key={self.key}"

class RecordWithKey(object):
    def __init__(self, *, key: Key, bins: dict[str, Any]) -> None:
        self.key = key
        self.bins = bins
    def __str__(self):
        bins_info = ""
        for key, value in self.bins.items():
            if isinstance(value, list):
                if len(value) > 4:
                    value_str = "[\n" + ",\n".join("\t\t\t{}".format(val) for val in value[:3]) + ",\n\t\t\t...\n\t\t]"
                else:
                    value_str = str(value)
            else:
                value_str = str(value)
            bins_info += "\n\t\t{}: {}".format(key, value_str)
        return "{{\n\t{},\n\tbins: {{\n{}\n\t}}\n}}".format(self.key, bins_info)

class Neighbor(object):
    def __init__(self, *, key: Key, bins: dict[str, Any], distance: float) -> None:
        self.key = key
        self.bins = bins
        self.distance = distance
    def __str__(self):
        bins_info = ""
        for key, value in self.bins.items():
            if isinstance(value, list):
                if len(value) > 4:
                    value_str = "[\n" + ",\n".join("\t\t\t{}".format(val) for val in value[:3]) + ",\n\t\t\t...\n\t\t]"
                else:
                    value_str = str(value)
            else:
                value_str = str(value)
            bins_info += "\n\t\t{}: {}".format(key, value_str)
        return "{{\n\t{},\n\tdistance: {},\n\tbins: {{\n{}\n\t}}\n}}".format(self.key, self.distance, bins_info)

class VectorDistanceMetric(enum.Enum):
    SQUARED_EUCLIDEAN = types_pb2.VectorDistanceMetric.SQUARED_EUCLIDEAN
    COSINE = types_pb2.VectorDistanceMetric.COSINE
    DOT_PRODUCT = types_pb2.VectorDistanceMetric.DOT_PRODUCT
    MANHATTAN = types_pb2.VectorDistanceMetric.MANHATTAN
    HAMMING = types_pb2.VectorDistanceMetric.HAMMING


class HnswBatchingParams(object):
    def __init__(
        self,
        *,
        maxRecords: Optional[int] = 10000,
        interval: Optional[int] = 10000,
        disabled: Optional[bool] = False,
    ) -> None:
        self.maxRecords = maxRecords
        self.interval = interval
        self.disabled = disabled


class HnswParams(object):
    def __init__(
        self,
        *,
        m: Optional[int] = 16,
        efConstruction: Optional[int] = 100,
        ef: Optional[int] = 100,
        batchingParams: Optional[HnswBatchingParams] = HnswBatchingParams(),
    ) -> None:
        self.m = m
        self.efConstruction = efConstruction
        self.ef = ef
        self.batchingParams = batchingParams


class HnswSearchParams(object):
    def __init__(self, *, ef: Optional[int] = None) -> None:
        self.ef = ef
