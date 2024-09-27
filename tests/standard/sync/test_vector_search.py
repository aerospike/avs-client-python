import numpy as np
import pytest
import random
import time
from aerospike_vector_search import types
from aerospike_vector_search import AVSServerError
import grpc

dimensions = 128
truth_vector_dimensions = 100
base_vector_number = 10_000
query_vector_number = 100


# Print the current working directory
def parse_sift_to_numpy_array(length, dim, byte_buffer, dtype):
    numpy = np.empty((length,), dtype=object)

    record_length = (dim * 4) + 4

    for i in range(length):
        current_offset = i * record_length
        begin = current_offset
        vector_begin = current_offset + 4
        end = current_offset + record_length
        if np.frombuffer(byte_buffer[begin:vector_begin], dtype=np.int32)[0] != dim:
            raise Exception("Failed to parse byte buffer correctly")
        numpy[i] = np.frombuffer(byte_buffer[vector_begin:end], dtype=dtype)
    return numpy


@pytest.fixture
def base_numpy():
    base_filename = "siftsmall/siftsmall_base.fvecs"
    with open(base_filename, "rb") as file:
        base_bytes = bytearray(file.read())

    base_numpy = parse_sift_to_numpy_array(
        base_vector_number, dimensions, base_bytes, np.float32
    )

    return base_numpy


@pytest.fixture
def truth_numpy():
    truth_filename = "siftsmall/siftsmall_groundtruth.ivecs"
    with open(truth_filename, "rb") as file:
        truth_bytes = bytearray(file.read())

    truth_numpy = parse_sift_to_numpy_array(
        query_vector_number, truth_vector_dimensions, truth_bytes, np.int32
    )

    return truth_numpy


@pytest.fixture
def query_numpy():
    query_filename = "siftsmall/siftsmall_query.fvecs"
    with open(query_filename, "rb") as file:
        query_bytes = bytearray(file.read())

    truth_numpy = parse_sift_to_numpy_array(
        query_vector_number, dimensions, query_bytes, np.float32
    )

    return truth_numpy


def put_vector(client, vector, j, set_name):
    client.upsert(
        namespace="test",
        key=str(j),
        record_data={"unit_test": vector},
        set_name=set_name,
    )


def get_vector(client, j, set_name):
    result = client.get(namespace="test", key=str(j), set_name=set_name)


def vector_search(client, vector, name):
    result = client.vector_search(
        namespace="test",
        index_name=name,
        query=vector,
        limit=100,
        include_fields=["unit_test"],
    )
    return result


def vector_search_ef_80(client, vector, name):
    result = client.vector_search(
        namespace="test",
        index_name=name,
        query=vector,
        limit=100,
        include_fields=["unit_test"],
        search_params=types.HnswSearchParams(ef=80),
    )
    return result


def grade_results(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
    name,
):

    # Vector search all query vectors
    results = []
    count = 0
    for i in query_numpy:
        if count % 2:
            results.append(vector_search(session_vector_client, i, name))
        else:
            results.append(vector_search_ef_80(session_vector_client, i, name))
        count += 1

    # Get recall numbers for each query
    recall_for_each_query = []
    for i, outside in enumerate(truth_numpy):
        true_positive = 0
        false_negative = 0
        # Parse all fields for each neighbor into an array
        field_list = []

        for j, result in enumerate(results[i]):
            field_list.append(result.fields["unit_test"])
        for j, index in enumerate(outside):
            vector = base_numpy[index].tolist()
            if vector in field_list:
                true_positive = true_positive + 1
            else:
                false_negative = false_negative + 1

        recall = true_positive / (true_positive + false_negative)
        recall_for_each_query.append(recall)

    # Calculate the sum of all values
    recall_sum = sum(recall_for_each_query)

    # Calculate the average
    average = recall_sum / len(recall_for_each_query)

    assert average > 0.95
    for recall in recall_for_each_query:
        assert recall > 0.9


class vector_search_test_case:
    def __init__(
        self,
        *,
        index_name,
        index_dimensions,
        vector_field,
        limit,
        query,
        namespace,
        include_fields,
        exclude_fields,
        set_name,
        record_data,
        expected_results,
    ):
        self.index_name = index_name
        self.index_dimensions = index_dimensions
        self.vector_field = vector_field
        self.limit = limit
        self.query = query
        self.namespace = namespace
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields
        self.set_name = set_name
        self.record_data = record_data
        self.expected_results = expected_results

# TODO add a teardown
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        vector_search_test_case(
            index_name="basic_search",
            index_dimensions=3,
            vector_field="vector",
            limit=3,
            query=[0.0, 0.0, 0.0],
            namespace="test",
            include_fields=None,
            exclude_fields = None,
            set_name=None,
            record_data={
                "rec1": {
                    "bin1": 1,
                    "vector": [1.0, 1.0, 1.0],
                },
            },
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace="test",
                        set="",
                        key="rec1",
                    ),
                    fields={
                        "bin1": 1,
                        "vector": [1.0, 1.0, 1.0],
                    },
                    distance=3.0,
                ),
            ],
        ),
        vector_search_test_case(
            index_name="field_filter",
            index_dimensions=3,
            vector_field="vector",
            limit=3,
            query=[0.0, 0.0, 0.0],
            namespace="test",
            include_fields=["bin1"],
            exclude_fields=["bin1"],
            set_name=None,
            record_data={
                "rec1": {
                    "bin1": 1,
                    "vector": [1.0, 1.0, 1.0],
                },
            },
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace="test",
                        set="",
                        key="rec1",
                    ),
                    fields={},
                    distance=3.0,
                ),
            ],
        ),
    ],
)
async def test_vector_search_field_filters(
    session_vector_client,
    session_admin_client,
    test_case,
):
    
    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.index_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.index_dimensions,
    )

    for key, rec in test_case.record_data.items():
        session_vector_client.upsert(
            namespace=test_case.namespace,
            key=key,
            record_data=rec,
            set_name=test_case.set_name,
        )
    
    session_vector_client.wait_for_index_completion(
        namespace=test_case.namespace,
        name=test_case.index_name,
    )

    results = session_vector_client.vector_search(
        namespace=test_case.namespace,
        index_name=test_case.index_name,
        query=test_case.query,
        limit=test_case.limit,
        include_fields=test_case.include_fields,
        exclude_fields=test_case.exclude_fields,
    )

    assert results == test_case.expected_results

    for key in test_case.record_data:
        session_vector_client.delete(
            namespace=test_case.namespace,
            key=key,
        )

    session_admin_client.index_drop(
        namespace=test_case.namespace,
        name=test_case.index_name,
    )

def test_vector_search(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
    extensive_vector_search,
):

    if not extensive_vector_search:
        pytest.skip("Extensive vector tests disabled")

    session_admin_client.index_create(
        namespace="test",
        name="demo1",
        vector_field="unit_test",
        dimensions=128,
    )

    for j, vector in enumerate(base_numpy):
        put_vector(session_vector_client, vector, j, None)

    session_vector_client.wait_for_index_completion(namespace="test", name="demo1")

    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name="demo1",
    )


def test_vector_search_with_set_same_as_index(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
):

    session_admin_client.index_create(
        namespace="test",
        name="demo2",
        sets="demo2",
        vector_field="unit_test",
        dimensions=128,
        index_storage=types.IndexStorage(namespace="test", set_name="demo2"),
    )

    for j, vector in enumerate(base_numpy):
        put_vector(session_vector_client, vector, j, "demo2")

    for j, vector in enumerate(base_numpy):
        get_vector(session_vector_client, j, "demo2")

    session_vector_client.wait_for_index_completion(namespace="test", name="demo2")

    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name="demo2",
    )


def test_vector_search_with_set_different_than_name(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
    extensive_vector_search,
):

    if not extensive_vector_search:
        pytest.skip("Extensive vector tests disabled")

    session_admin_client.index_create(
        namespace="test",
        name="demo3",
        vector_field="unit_test",
        dimensions=128,
        sets="example1",
        index_storage=types.IndexStorage(namespace="test", set_name="demo3"),
    )

    for j, vector in enumerate(base_numpy):
        put_vector(session_vector_client, vector, j, "example1")

    session_vector_client.wait_for_index_completion(namespace="test", name="demo3")

    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name="demo3",
    )


def test_vector_search_with_index_storage_different_than_name(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
    extensive_vector_search,
):

    if not extensive_vector_search:
        pytest.skip("Extensive vector tests disabled")

    session_admin_client.index_create(
        namespace="test",
        name="demo4",
        vector_field="unit_test",
        dimensions=128,
        sets="demo4",
        index_storage=types.IndexStorage(namespace="test", set_name="example2"),
    )

    for j, vector in enumerate(base_numpy):
        put_vector(session_vector_client, vector, j, "demo4")

    session_vector_client.wait_for_index_completion(namespace="test", name="demo4")

    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name="demo4",
    )


def test_vector_search_with_index_storage_different_location(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
    extensive_vector_search,
):

    if not extensive_vector_search:
        pytest.skip("Extensive vector tests disabled")

    session_admin_client.index_create(
        namespace="test",
        name="demo5",
        vector_field="unit_test",
        dimensions=128,
        sets="example3",
        index_storage=types.IndexStorage(namespace="test", set_name="example4"),
    )

    for j, vector in enumerate(base_numpy):
        put_vector(session_vector_client, vector, j, "example3")

    session_vector_client.wait_for_index_completion(namespace="test", name="demo5")

    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name="demo5",
    )


def test_vector_search_with_separate_namespace(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
    extensive_vector_search,
):

    if not extensive_vector_search:
        pytest.skip("Extensive vector tests disabled")

    session_admin_client.index_create(
        namespace="test",
        name="demo6",
        vector_field="unit_test",
        dimensions=128,
        sets="demo6",
        index_storage=types.IndexStorage(namespace="index_storage", set_name="demo6"),
    )

    for j, vector in enumerate(base_numpy):
        put_vector(session_vector_client, vector, j, "demo6")

    session_vector_client.wait_for_index_completion(namespace="test", name="demo6")

    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name="demo6",
    )


def test_vector_is_indexed(session_vector_client, session_admin_client):

    result = session_vector_client.is_indexed(
        namespace="test",
        key=str(random.randrange(10_000)),
        index_name="demo2",
        set_name="demo2",
    )

    assert result is True


def test_vector_is_indexed_timeout(
    session_vector_client, session_admin_client, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):
        try:
            result = session_vector_client.is_indexed(
                namespace="test", key=500, index_name="demo2", timeout=0.0001
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"


def test_vector_vector_search_timeout(
    session_vector_client, session_admin_client, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):
        try:
            result = session_vector_client.vector_search(
                namespace="test",
                index_name="demo2",
                query=[0, 1, 2],
                limit=100,
                include_fields=["unit_test"],
                timeout=0.0001,
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
