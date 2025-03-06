from typing import Any

from .. import types
from .proto_generated import types_pb2, index_pb2
from ..types import IndexStatusResponse


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


def toMapKey(value) -> types_pb2.MapKey:
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


def fromVectorDbNeighbor(input_vectordb_neighbor: types_pb2.Neighbor) -> types.Neighbor:
    return types.Neighbor(
        key=fromVectorDbKey(input_vectordb_neighbor.key),
        fields=fromVectorDbRecord(input_vectordb_neighbor.record),
        distance=input_vectordb_neighbor.distance,
    )


def fromIndexDefintion(input_data: types_pb2.IndexDefinition) -> types.IndexDefinition:
    return types.IndexDefinition(
        id=types.IndexId(
            namespace=input_data.id.namespace,
            name=input_data.id.name,
        ),
        dimensions=input_data.dimensions,
        vector_distance_metric=types.VectorDistanceMetric(input_data.vectorDistanceMetric),
        field=input_data.field,
        sets=input_data.setFilter,
        hnsw_params=types.HnswParams(
            m=input_data.hnswParams.m,
            ef_construction=input_data.hnswParams.efConstruction,
            ef=input_data.hnswParams.ef,
            enable_vector_integrity_check=input_data.hnswParams.enableVectorIntegrityCheck,
            batching_params=types.HnswBatchingParams(
                max_index_records=input_data.hnswParams.batchingParams.maxIndexRecords,
                index_interval=input_data.hnswParams.batchingParams.indexInterval,
                max_reindex_records = input_data.hnswParams.batchingParams.maxReindexRecords,
                reindex_interval = input_data.hnswParams.batchingParams.reindexInterval
            ),
            max_mem_queue_size=input_data.hnswParams.maxMemQueueSize,
            index_caching_params=types.HnswCachingParams(
                max_entries=input_data.hnswParams.indexCachingParams.maxEntries,
                expiry=input_data.hnswParams.indexCachingParams.expiry,
            ),
            healer_params=types.HnswHealerParams(
                max_scan_rate_per_node=input_data.hnswParams.healerParams.maxScanRatePerNode,
                max_scan_page_size=input_data.hnswParams.healerParams.maxScanPageSize,
                re_index_percent=input_data.hnswParams.healerParams.reindexPercent,
                schedule=input_data.hnswParams.healerParams.schedule,
                parallelism=input_data.hnswParams.healerParams.parallelism,
            ),
            merge_params=types.HnswIndexMergeParams(
                index_parallelism=input_data.hnswParams.mergeParams.indexParallelism,
                reindex_parallelism=input_data.hnswParams.mergeParams.reIndexParallelism,
            ),
        ),
        index_labels=input_data.labels,
        storage=types.IndexStorage(
            namespace=input_data.storage.namespace, set_name=input_data.storage.set
        ),
        mode=types.IndexMode(input_data.mode),
    )


def fromVectorDbValue(input_vector: types_pb2.Value) -> Any:
    if input_vector.HasField("stringValue"):
        return input_vector.stringValue
    elif input_vector.HasField("intValue"):
        return input_vector.intValue
    elif input_vector.HasField("longValue"):
        return input_vector.longValue
    elif input_vector.HasField("bytesValue"):
        return input_vector.bytesValue
    elif input_vector.HasField("mapValue"):
        data = {}
        for entry in input_vector.mapValue.entries:
            k = fromVectorDbValue(entry.key)
            v = fromVectorDbValue(entry.value)
            data[k] = v
        return data
    elif input_vector.HasField("listValue"):
        return [fromVectorDbValue(v) for v in input_vector.listValue.entries]
    elif input_vector.HasField("vectorValue"):
        vector = input_vector.vectorValue
        if vector.HasField("floatData"):
            return [v for v in vector.floatData.value]
        if vector.HasField("boolData"):
            return [v for v in vector.boolData.value]

    return None

def fromStandAloneIndexMetricsResponse(response: index_pb2.StandaloneIndexMetrics) -> types.StandaloneIndexMetrics:
    """
    Converts a protobuf StandaloneIndexMetrics into a StandaloneIndexMetrics object.

    Parameters:
    -----------
    response : types_pb2.StandaloneIndexMetrics
        A protobuf StandaloneIndexMetrics object.

    Returns:
    --------
    StandaloneIndexMetrics
        An instance of StandaloneIndexMetrics with the values from the protobuf message.
    """
    result = types.StandaloneIndexMetrics(
        index_id=types.IndexId(
            namespace=response.indexId.namespace,
            name=response.indexId.name
        ),
        state=types.StandaloneIndexState(response.state),
        scanned_vector_record_count=response.scannedVectorRecordCount,
        indexed_vector_record_count=response.indexedVectorRecordCount,
    )
    return result


def fromIndexStatusResponse(response: 'index_pb2.IndexStatusResponse') -> IndexStatusResponse:
        """
        Converts a protobuf IndexStatusResponse into an IndexStatusResponse object.

        Parameters:
        -----------
        response : index_pb2.IndexStatusResponse
            A protobuf IndexStatusResponse object.

        Returns:
        --------
        IndexStatusResponse
            An instance of IndexStatusResponse with the values from the protobuf message.
        """
        return IndexStatusResponse(
            unmerged_record_count=response.unmergedRecordCount,
            index_healer_vector_records_indexed=response.indexHealerVectorRecordsIndexed,
            index_healer_vertices_valid=response.indexHealerVerticesValid,
            standalone_metrics=fromStandAloneIndexMetricsResponse(response.standaloneIndexMetrics),
            readiness=types.IndexReadiness(response.status)
        )
