import pytest

from aerospike_vector_search import AVSServerError
from utils import random_name, DEFAULT_NAMESPACE
from utils import wait_for_index

import grpc


def test_vector_is_indexed(
    session_vector_client,
    index,
    record,
):
    # wait for the record to be indexed
    wait_for_index(
        admin_client=session_vector_client,
        namespace=DEFAULT_NAMESPACE,
        index=index
    )

    result = session_vector_client.is_indexed(
        namespace=DEFAULT_NAMESPACE,
        key=record,
        index_name=index,
    )
    assert result is True


def test_vector_is_indexed_timeout(
    session_vector_client,
    with_latency,
    random_name,
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    for _ in range(10):
        try:
            session_vector_client.is_indexed(
                namespace=DEFAULT_NAMESPACE,
                key="0",
                index_name=random_name,
                timeout=0.0001,
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"