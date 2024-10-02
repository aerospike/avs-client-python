import pytest
import random
from aerospike_vector_search import AVSServerError

import grpc

async def test_vector_is_indexed(
    session_vector_client,
):

    result = await session_vector_client.is_indexed(
        namespace="test",
        key=str(random.randrange(10_000)),
        index_name="demo2",
        set_name="demo2",
    )
    assert result is True


async def test_vector_is_indexed_timeout(
    session_vector_client, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    for i in range(10):
        try:
            result = await session_vector_client.is_indexed(
                namespace="test",
                key=str(random.randrange(10_000)),
                index_name="demo2",
                timeout=0.0001,
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"