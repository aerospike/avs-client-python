from typing import Any

from .. import types
from .proto_generated import types_pb2


def toVectorDbValue(value: Any) -> types_pb2.Value:
    if isinstance(value, str):
        return types_pb2.Value(stringValue=value)
    elif isinstance(value, int):
        return types_pb2.Value(longValue=value)
    elif isinstance(value, float):
        return types_pb2.Value(doubleValue=value)
    elif isinstance(value, (bytes, bytearray)):
        return types_pb2.Value(bytesValue=value)
    elif isinstance(value, bool):
        return types_pb2.Value(booleanValue=value)
    elif isinstance(value, list) and value:
        # TODO: Convert every element correctly to destination type.
        if isinstance(value[0], float):
            return types_pb2.Value(
                vectorValue=types_pb2.Vector(
                    floatData={"value": [float(x) for x in value]}
                )
            )
        elif isinstance(value[0], bool):
            return types_pb2.Value(
                vectorValue=types_pb2.Vector(
                    boolData={"value": [True if x else False for x in value]}
                )
            )
        else:
            return types_pb2.Value(
                listValue=types_pb2.List(entries=[toVectorDbValue(x) for x in value])
            )
    elif isinstance(value, dict):
        d = types_pb2.Value(
            mapValue=types_pb2.Map(
                entries=[
                    types_pb2.MapEntry(key=toMapKey(k), value=toVectorDbValue(v))
                    for k, v in value.items()
                ]
            )
        )
        return d
    else:
        raise Exception("Invalid type " + str(type(value)))


def toMapKey(value):
    if isinstance(value, str):
        return types_pb2.MapKey(stringValue=value)
    elif isinstance(value, int):
        return types_pb2.MapKey(longValue=value)
    elif isinstance(value, (bytes, bytearray)):
        return types_pb2.MapKey(bytesValue=value)
    elif isinstance(value, float):
        return types_pb2.MapKey(doubleValue=value)
    else:
        raise Exception("Invalid map key type " + str(type(value)))


def fromVectorDbKey(key: types_pb2.Key) -> types.Key:
    keyValue = None
    if key.HasField("stringValue"):
        keyValue = key.stringValue
    elif key.HasField("intValue"):
        keyValue = key.intValue
    elif key.HasField("longValue"):
        keyValue = key.longValue
    elif key.HasField("bytesValue"):
        keyValue = key.bytesValue

    return types.Key(namespace=key.namespace, set=key.set, key=keyValue)


def fromVectorDbRecord(record: types_pb2.Record) -> dict[str, Any]:
    fields = {}
    for field in record.fields:
        fields[field.name] = fromVectorDbValue(field.value)

    return fields


def fromVectorDbNeighbor(input: types_pb2.Neighbor) -> types.Neighbor:
    return types.Neighbor(
        key=fromVectorDbKey(input.key),
        fields=fromVectorDbRecord(input.record),
        distance=input.distance,
    )


def fromIndexDefintion(input: types_pb2.IndexDefinition) -> types.IndexDefinition:
    return types.IndexDefinition(
        id=types.IndexId(
            namespace=input.id.namespace,
            name=input.id.name,
        ),
        dimensions=input.dimensions,
        vector_distance_metric=input.vectorDistanceMetric,
        field=input.field,
        sets=input.setFilter,
        hnsw_params=types.HnswParams(
            m=input.hnswParams.m,
            ef_construction=input.hnswParams.efConstruction,
            ef=input.hnswParams.ef,
            batching_params=types.HnswBatchingParams(
                max_records=input.hnswParams.batchingParams.maxRecords,
                interval=input.hnswParams.batchingParams.interval,
            ),
            max_mem_queue_size=input.hnswParams.maxMemQueueSize,
            caching_params=types.HnswCachingParams(
                max_entries=input.hnswParams.cachingParams.maxEntries,
                expiry=input.hnswParams.cachingParams.expiry,
            ),
            healer_params=types.HnswHealerParams(
                max_scan_rate_per_node=input.hnswParams.healerParams.maxScanRatePerNode,
                max_scan_page_size=input.hnswParams.healerParams.maxScanPageSize,
                re_index_percent=input.hnswParams.healerParams.reindexPercent,
                schedule=input.hnswParams.healerParams.schedule,
                parallelism=input.hnswParams.healerParams.parallelism,
            ),
            merge_params=types.HnswIndexMergeParams(
                index_parallelism=input.hnswParams.mergeParams.indexParallelism,
                reindex_parallelism=input.hnswParams.mergeParams.reIndexParallelism,
            ),
        ),
        index_labels=input.labels,
        storage=types.IndexStorage(
            namespace=input.storage.namespace, set_name=input.storage.set
        ),
    )


def fromVectorDbValue(input: types_pb2.Value) -> Any:
    if input.HasField("stringValue"):
        return input.stringValue
    elif input.HasField("intValue"):
        return input.intValue
    elif input.HasField("longValue"):
        return input.longValue
    elif input.HasField("bytesValue"):
        return input.bytesValue
    elif input.HasField("mapValue"):
        dict = {}
        for entry in input.mapValue.entries:
            k = fromVectorDbValue(entry.key)
            v = fromVectorDbValue(entry.value)
            dict[k] = v
        return dict
    elif input.HasField("listValue"):
        return [fromVectorDbValue(v) for v in input.listValue.entries]
    elif input.HasField("vectorValue"):
        vector = input.vectorValue
        if vector.HasField("floatData"):
            return [v for v in vector.floatData.value]
        if vector.HasField("boolData"):
            return [v for v in vector.boolData.value]

    return None
