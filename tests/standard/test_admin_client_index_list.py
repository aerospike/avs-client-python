from aerospike_vector_search import AVSServerError
from utils import drop_specified_index

import pytest
import grpc
from hypothesis import given, settings, Verbosity


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_list(session_vector_client, empty_test_case, index):
    result = session_vector_client.index_list(apply_defaults=True)
    assert len(result) > 0
    for index in result:
        assert isinstance(index["id"]["name"], str)
        assert isinstance(index["id"]["namespace"], str)
        assert isinstance(index["dimensions"], int)
        assert isinstance(index["field"], str)
        assert isinstance(index["hnsw_params"]["m"], int)
        assert isinstance(index["hnsw_params"]["ef_construction"], int)
        assert isinstance(index["hnsw_params"]["ef"], int)
        assert isinstance(index["hnsw_params"]["batching_params"]["max_index_records"], int)
        assert isinstance(index["hnsw_params"]["batching_params"]["index_interval"], int)
        assert isinstance(index["hnsw_params"]["batching_params"]["max_reindex_records"], int)
        assert isinstance(index["hnsw_params"]["batching_params"]["reindex_interval"], int)
        assert isinstance(index["storage"]["namespace"], str)
        assert isinstance(index["storage"]["set_name"], str)


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_list_timeout(
    session_vector_client, empty_test_case, with_latency
):

    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):

        try:
            result = session_vector_client.index_list(timeout=0.0001)

        except AVSServerError as se:
            if se.rpc_error.code() != grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
