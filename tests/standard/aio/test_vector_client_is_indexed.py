import pytest
import time

from utils import DEFAULT_NAMESPACE
from aerospike_vector_search import AVSServerError

import grpc


async def test_vector_is_indexed(
    session_vector_client, index, record
):
    # give the record some time to be indexed
    time.sleep(1)
    result = await session_vector_client.is_indexed(
        namespace=DEFAULT_NAMESPACE,
        key=record,
        index_name=index,
    )
    assert result is True


async def test_vector_is_indexed_timeout(
    session_vector_client, with_latency, index, record
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    for _ in range(10):
        try:
            await session_vector_client.is_indexed(
                namespace=DEFAULT_NAMESPACE,
                key=record,
                index_name=index,
                timeout=0.0001,
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"