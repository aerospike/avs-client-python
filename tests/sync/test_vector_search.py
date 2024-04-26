import numpy as np
import pytest
import random
from aerospike_vector import types

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


def put_vector(client, vector, j):
    client.put(
        namespace="test", key=str(j), record_data={"unit_test": vector}, set_name="demo"
    )


def get_vector(client, j):
    result = client.get(namespace="test", key=str(j), set_name="demo")


def vector_search(client, vector):
    result = client.vector_search(
        namespace="test",
        index_name="demo",
        query=vector,
        limit=100,
        bin_names=["unit_test"],
    )
    return result


def vector_search_ef_80(client, vector):
    result = client.vector_search(
        namespace="test",
        index_name="demo",
        query=vector,
        limit=100,
        bin_names=["unit_test"],
        search_params=types.HnswSearchParams(ef=80)
    )
    return result

def test_vector_search(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
):

    session_admin_client.index_create(
        namespace="test",
        name="demo",
        vector_field="unit_test",
        dimensions=128,
        sets="demo",
    )

    # Put base vectors for search
    for j, vector in enumerate(base_numpy):
        put_vector(session_vector_client, vector.tolist(), j)

    session_vector_client.wait_for_index_completion(namespace='test', name='demo')


    # Vector search all query vectors
    results = []
    count = 0
    for i in query_numpy:
        if count % 2:
            results.append(vector_search(session_vector_client, i.tolist()))
        else:
            results.append(vector_search_ef_80(session_vector_client, i.tolist()))
        count += 1

    # Get recall numbers for each query
    recall_for_each_query = []
    for i, outside in enumerate(truth_numpy):
        true_positive = 0
        false_negative = 0
        # Parse all bins for each neighbor into an array
        binList = []

        for j, result in enumerate(results[i]):
            binList.append(result.bins["unit_test"])
        for j, index in enumerate(outside):
            vector = base_numpy[index].tolist()
            if vector in binList:
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


def test_vector_is_indexed(session_vector_client, session_admin_client):
    result = session_vector_client.is_indexed(
        namespace="test",
        key=str(random.randrange(10_000)),
        set_name="demo",
        index_name="demo",
    )
    assert result is True
