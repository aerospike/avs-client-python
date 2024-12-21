import pytest
import time

from utils import DEFAULT_NAMESPACE
from .aio_utils import wait_for_index
from aerospike_vector_search import AVSServerError

import grpc


async def test_vector_is_indexed(
    session_admin_client,
    session_vector_client,
    index,
    record
):
    # wait for the record to be indexed
    await wait_for_index(
        admin_client=session_admin_client,
        namespace=DEFAULT_NAMESPACE,
        index=index
    )

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