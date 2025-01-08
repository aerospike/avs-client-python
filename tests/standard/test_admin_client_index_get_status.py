import pytest
import grpc

from utils import DEFAULT_NAMESPACE

from utils import drop_specified_index
from hypothesis import given, settings, Verbosity

from aerospike_vector_search import AVSServerError
import grpc


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_get_status(session_vector_client, empty_test_case, index):
    result = session_vector_client.index_get_status(namespace=DEFAULT_NAMESPACE, name=index)

    assert result.unmerged_record_count == 0
    drop_specified_index(session_vector_client, DEFAULT_NAMESPACE, index)


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_get_status_timeout(
    session_vector_client, empty_test_case, index, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):
        try:
            result = session_vector_client.index_get_status(
                namespace=DEFAULT_NAMESPACE, name=index, timeout=0.0001
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return

    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
