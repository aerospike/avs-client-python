import numpy as np
import asyncio
import pytest
import random
from aerospike_vector_search import types, AVSServerError

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

async def put_vector(client, vector, j, set_name):
    await client.upsert(
        namespace="test", key=str(j), record_data={"unit_test": vector}, set_name=set_name
    )


async def get_vector(client, j, set_name):
    result = await client.get(namespace="test", key=str(j), set_name=set_name)


async def vector_search(client, vector, name):
    result = await client.vector_search(
        namespace="test",
        index_name=name,
        query=vector,
        limit=100,
        field_names=["unit_test"],
    )
    return result


async def vector_search_ef_80(client, vector, name):
    result = await client.vector_search(
        namespace="test",
        index_name=name,
        query=vector,
        limit=100,
        field_names=["unit_test"],
        search_params=types.HnswSearchParams(ef=80)
    )
    return result

async def grade_results(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
    name
):
    # Vector search all query vectors
    tasks = []
    count = 0
    for i in query_numpy:
        if count % 2:
            tasks.append(vector_search(session_vector_client, i, name))
        else:
            tasks.append(vector_search_ef_80(session_vector_client, i, name))
        count += 1

    results = await asyncio.gather(*tasks)
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


async def test_vector_search(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
):

    await session_admin_client.index_create(
        namespace="test",
        name="demo1",
        vector_field="unit_test",
        dimensions=128,
    )

    # Put base vectors for search
    tasks = []

    for j, vector in enumerate(base_numpy):
        tasks.append(put_vector(session_vector_client, vector, j, None))

    tasks.append(session_vector_client.wait_for_index_completion(namespace='test', name='demo1'))
    await asyncio.gather(*tasks)
    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name='demo1'
    )

async def test_vector_search_with_set_same_as_index(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
):

    await session_admin_client.index_create(
        namespace="test",
        name="demo2",
        sets="demo2",
        vector_field="unit_test",
        dimensions=128,
        index_storage=types.IndexStorage(namespace="test", set_name="demo2")
    )

    # Put base vectors for search
    tasks = []

    for j, vector in enumerate(base_numpy):
        tasks.append(put_vector(session_vector_client, vector, j, "demo2"))

    tasks.append(session_vector_client.wait_for_index_completion(namespace='test', name='demo2'))
    await asyncio.gather(*tasks)
    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name='demo2'
    )

async def test_vector_search_with_set_different_than_name(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
):

    await session_admin_client.index_create(
        namespace="test",
        name="demo3",
        vector_field="unit_test",
        dimensions=128,
        sets="example1",
        index_storage=types.IndexStorage(namespace="test", set_name="demo3")

    )

    # Put base vectors for search
    tasks = []

    for j, vector in enumerate(base_numpy):
        tasks.append(put_vector(session_vector_client, vector, j, "example1"))

    tasks.append(session_vector_client.wait_for_index_completion(namespace='test', name='demo3'))
    await asyncio.gather(*tasks)
    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name="demo3"
    )

async def test_vector_search_with_index_storage_different_than_name(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
):

    await session_admin_client.index_create(
        namespace="test",
        name="demo4",
        vector_field="unit_test",
        dimensions=128,
        sets="demo4",
        index_storage=types.IndexStorage(namespace="test", set_name="example2")

    )

    # Put base vectors for search
    tasks = []

    for j, vector in enumerate(base_numpy):
        tasks.append(put_vector(session_vector_client, vector, j,  "demo4"))

    tasks.append(session_vector_client.wait_for_index_completion(namespace='test', name='demo4'))
    await asyncio.gather(*tasks)
    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name="demo4"
    )



async def test_vector_search_with_index_storage_different_location(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
):

    await session_admin_client.index_create(
        namespace="test",
        name="demo5",
        vector_field="unit_test",
        dimensions=128,
        sets="example3",
        index_storage=types.IndexStorage(namespace="test", set_name="example4")

    )

    # Put base vectors for search
    tasks = []

    for j, vector in enumerate(base_numpy):
        tasks.append(put_vector(session_vector_client, vector, j, "example3"))

    tasks.append(session_vector_client.wait_for_index_completion(namespace='test', name='demo5'))
    await asyncio.gather(*tasks)
    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name='demo5'
    )

async def test_vector_search_with_separate_namespace(
    base_numpy,
    truth_numpy,
    query_numpy,
    session_vector_client,
    session_admin_client,
):

    await session_admin_client.index_create(
        namespace="test",
        name="demo6",
        vector_field="unit_test",
        dimensions=128,
        sets="demo6",
        index_storage=types.IndexStorage(namespace="index_storage", set_name="demo6")

    )

    # Put base vectors for search
    tasks = []

    for j, vector in enumerate(base_numpy):
        tasks.append(put_vector(session_vector_client, vector, j, "demo6"))

    tasks.append(session_vector_client.wait_for_index_completion(namespace='test', name='demo6'))
    await asyncio.gather(*tasks)
    grade_results(
        base_numpy,
        truth_numpy,
        query_numpy,
        session_vector_client,
        session_admin_client,
        name='demo6'
    )

async def test_vector_is_indexed(session_vector_client, session_admin_client, local_latency):
    if local_latency:
        pytest.skip("Server latency too low to test timeout")
    result = await session_vector_client.is_indexed(
        namespace="test",
        key=str(random.randrange(10_000)),
        index_name="demo",
    )
    assert result is True

async def test_vector_is_indexed_timeout(session_vector_client, session_admin_client, local_latency):
    if local_latency:
        pytest.skip("Server latency too low to test timeout")    
    for i in range(10):
        try:
            result = await session_vector_client.is_indexed(
                namespace="test",
                key=str(random.randrange(10_000)),
                index_name="demo",
                timeout=0.0001
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return        
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"

async def test_vector_vector_search_timeout(session_vector_client, session_admin_client, local_latency):
    if local_latency:
        pytest.skip("Server latency too low to test timeout")    
    
    for i in range(10):
        try:
            result = await session_vector_client.vector_search(
                namespace="test",
                index_name="demo",
                query=[0, 1, 2],
                limit=100,
                field_names=["unit_test"],
                timeout=0.0001
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"