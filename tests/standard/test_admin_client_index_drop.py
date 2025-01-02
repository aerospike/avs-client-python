import pytest

from aerospike_vector_search import AVSServerError
import grpc

from utils import DEFAULT_NAMESPACE

from hypothesis import given, settings, Verbosity


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_drop(session_vector_client, empty_test_case, index):
    session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=index)

    result = session_vector_client.index_list()
    result = result
    for index in result:
        assert index["id"]["name"] != index


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_drop_timeout(
    session_vector_client,
    empty_test_case,
    index,
    with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):
        try:
            session_vector_client.index_drop(
                namespace=DEFAULT_NAMESPACE, name=index, timeout=0.0001
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
