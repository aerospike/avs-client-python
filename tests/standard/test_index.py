import pytest
import grpc
import time

from aerospike_vector_search import Client, types, AVSServerError
from aerospike_vector_search.aio import Client as AioClient
from utils import DEFAULT_NAMESPACE, DEFAULT_INDEX_DIMENSION, DEFAULT_VECTOR_FIELD, wait_for_index


def test_index(session_vector_client, index):
    index_name = index
    idxobj = session_vector_client.index(
        name = index_name,
        namespace = DEFAULT_NAMESPACE,
    )

    # Support testing with sync and async clients
    assert isinstance(idxobj._client, Client) or isinstance(idxobj._client, AioClient)
    assert idxobj._name == index_name
    assert idxobj._namespace == DEFAULT_NAMESPACE
    assert idxobj._vector_field == DEFAULT_VECTOR_FIELD
    assert idxobj._dimensions == DEFAULT_INDEX_DIMENSION
    # SQUARED_EUCLIDEAN is the default distance metric as of writing
    assert idxobj._vector_distance_metric == types.VectorDistanceMetric.SQUARED_EUCLIDEAN
    # The server returns '' as the default value for sets instead of None
    assert idxobj._sets == ''
    assert idxobj._index_storage == types.IndexStorage(namespace=DEFAULT_NAMESPACE, set_name=index_name)


def test_index_vector_search(session_vector_client, index_obj, records):
    # Wait for the index to stabilize
    wait_for_index(session_vector_client, DEFAULT_NAMESPACE, index_obj._name)

    query_vector = [0.0] * DEFAULT_INDEX_DIMENSION
    neighbors = index_obj.vector_search(query=query_vector, limit=5)

    assert isinstance(neighbors, list)
    assert len(neighbors) == 5
    for i, neighbor in enumerate(neighbors):
        assert isinstance(neighbor, types.Neighbor)
        # This expected data is based off of how the records fixture generates data
        # by default, see conftest.py records and gen_records in utils.py
        assert neighbor == types.Neighbor(
            key=types.Key(
                namespace=DEFAULT_NAMESPACE,
                set='',
                key=i,
            ),
            # Index.vector_search excludes the vector bin by default so don't expect it
            fields={"id": i},
            # This calculation only holds for squared euclidean distance
            distance=(i ** 2) * DEFAULT_INDEX_DIMENSION,
        )


def test_index_vector_search_with_vector_field(session_vector_client, index_obj, records):
    # Wait for the index to stabilize
    wait_for_index(session_vector_client, DEFAULT_NAMESPACE, index_obj._name)

    query_vector = [0.0] * DEFAULT_INDEX_DIMENSION
    neighbors = index_obj.vector_search(
        query=query_vector,
        limit=5,
        # Include the vector field in the response
        include_fields=[DEFAULT_VECTOR_FIELD],
    )

    assert isinstance(neighbors, list)
    assert len(neighbors) == 5

    for i, neighbor in enumerate(neighbors):
        assert isinstance(neighbor, types.Neighbor)
        # This expected data is based off of how the records fixture generates data
        # by default, see conftest.py records and gen_records in utils.py
        assert neighbor == types.Neighbor(
            key=types.Key(
                namespace=DEFAULT_NAMESPACE,
                set='',
                key=i,
            ),
            # When include_fields is used, only the specified fields are returned
            # so we expect the vector field but not the "id" field
            fields={DEFAULT_VECTOR_FIELD: [1.0 * i] * DEFAULT_INDEX_DIMENSION},
            # This calculation only holds for squared euclidean distance
            distance=(i ** 2) * DEFAULT_INDEX_DIMENSION,
        )


def test_index_vector_search_by_key(session_vector_client, index_obj, records):
    index_name = index_obj._name

    # Wait for the index to stabilize
    wait_for_index(session_vector_client, DEFAULT_NAMESPACE, index_name)

    neighbors = index_obj.vector_search_by_key(key=0, limit=5)

    assert isinstance(neighbors, list)
    assert len(neighbors) == 5
    for i, neighbor in enumerate(neighbors):
        assert isinstance(neighbor, types.Neighbor)
        # This expected data is based off of how the records fixture generates data
        # by default, see conftest.py records and gen_records in utils.py
        assert neighbor == types.Neighbor(
            key=types.Key(
                namespace=DEFAULT_NAMESPACE,
                set='',
                key=i,
            ),
            # Index.vector_search excludes the vector bin by default so don't expect it
            fields={"id": i},
            # This calculation only holds for squared euclidean distance
            distance=(i ** 2) * DEFAULT_INDEX_DIMENSION,
        )


def test_index_vector_search_by_key_with_vector_field(session_vector_client, index_obj, records):
    index_name = index_obj._name

    # Wait for the index to stabilize
    wait_for_index(session_vector_client, DEFAULT_NAMESPACE, index_name)

    neighbors = index_obj.vector_search_by_key(
        key=0,
        limit=5,
        include_fields=[DEFAULT_VECTOR_FIELD],
    )

    assert isinstance(neighbors, list)
    assert len(neighbors) == 5
    for i, neighbor in enumerate(neighbors):
        assert isinstance(neighbor, types.Neighbor)
        # This expected data is based off of how the records fixture generates data
        # by default, see conftest.py records and gen_records in utils.py
        assert neighbor == types.Neighbor(
            key=types.Key(
                namespace=DEFAULT_NAMESPACE,
                set='',
                key=i,
            ),
            # When include_fields is used, only the specified fields are returned
            # so we expect the vector field but not the "id" field
            fields={DEFAULT_VECTOR_FIELD: [1.0 * i] * DEFAULT_INDEX_DIMENSION},
            # This calculation only holds for squared euclidean distance
            distance=(i ** 2) * DEFAULT_INDEX_DIMENSION,
        )


def test_index_is_indexed(session_vector_client, index_obj, record):
    index_name = index_obj._name

    # Wait for the index to stabilize
    wait_for_index(session_vector_client, DEFAULT_NAMESPACE, index_name)

    indexed = index_obj.is_indexed(key=record)

    assert indexed


def test_index_get_percent_unmerged(session_vector_client, index_obj, records):
    index_name = index_obj._name

    # Wait for the index to stabilize
    wait_for_index(session_vector_client, DEFAULT_NAMESPACE, index_name)

    percent_unmerged = index_obj.get_percent_unmerged()

    # The index should be fully merged after the records are written
    assert percent_unmerged == 0.0


def test_index_update(session_vector_client, index_obj):
    index_name = index_obj._name

    index_def = index_obj.get()
    assert index_def.hnsw_params.enable_vector_integrity_check == True

    index_obj.update(
        hnsw_update_params=types.HnswIndexUpdate(
            enable_vector_integrity_check=False,
        )
    )

    # Wait for the index update to finish
    time.sleep(1)

    index_def = index_obj.get()
    assert index_def.hnsw_params.enable_vector_integrity_check == False


def test_index_get(session_vector_client, index_obj):
    index_name = index_obj._name

    index_def = index_obj.get()

    assert index_def.id == types.IndexId(namespace=DEFAULT_NAMESPACE, name=index_name)
    assert index_def.dimensions == DEFAULT_INDEX_DIMENSION
    # SQUARED_EUCLIDEAN is the default distance metric as of writing
    assert index_def.vector_distance_metric == types.VectorDistanceMetric.SQUARED_EUCLIDEAN
    assert index_def.field == DEFAULT_VECTOR_FIELD
    # The server returns '' as the default value for sets instead of None
    assert index_def.sets == ''
    assert index_def.hnsw_params is not None
    assert index_def.storage == types.IndexStorage(namespace=DEFAULT_NAMESPACE, set_name=index_name)
    assert index_def.index_labels == {}


def test_index_status(session_vector_client, index_obj, record):
    index_name = index_obj._name

    # Wait for the record to be indexed completely so that stats are accurate
    wait_for_index(session_vector_client, DEFAULT_NAMESPACE, index_name)

    status = index_obj.status()

    assert status.unmerged_record_count == 0
    assert status.index_healer_vector_records_indexed == 1
    assert status.index_healer_vertices_valid >= 1


def test_index_drop(index_obj):
    index_name = index_obj._name

    index_obj.drop()

    with pytest.raises(AVSServerError) as excinfo:
        index_obj.get()

    assert excinfo.value.rpc_error.code() == grpc.StatusCode.NOT_FOUND
    assert excinfo.value.rpc_error.details() == f"index {DEFAULT_NAMESPACE}:{index_name} not found"