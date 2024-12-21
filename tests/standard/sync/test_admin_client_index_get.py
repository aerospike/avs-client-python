from ...utils import DEFAULT_NAMESPACE, DEFAULT_INDEX_DIMENSION, DEFAULT_VECTOR_FIELD
from aerospike_vector_search import AVSServerError

import grpc
from hypothesis import given, settings, Verbosity
import pytest

@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_get(session_admin_client, empty_test_case, index):
    result = session_admin_client.index_get(namespace=DEFAULT_NAMESPACE, name=index, apply_defaults=True)

    assert result["id"]["name"] == index
    assert result["id"]["namespace"] == DEFAULT_NAMESPACE
    assert result["dimensions"] == DEFAULT_INDEX_DIMENSION
    assert result["field"] == DEFAULT_VECTOR_FIELD
    assert result["hnsw_params"]["m"] == 16
    assert result["hnsw_params"]["ef_construction"] == 100
    assert result["hnsw_params"]["ef"] == 100
    assert result["hnsw_params"]["batching_params"]["max_index_records"] == 100000
    assert result["hnsw_params"]["batching_params"]["index_interval"] == 10000
    assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == max(100000 / 10, 1000)
    assert result["hnsw_params"]["batching_params"]["reindex_interval"] == 30000
    assert result["storage"]["namespace"] == DEFAULT_NAMESPACE
    assert result["storage"]["set_name"] == index

    # Defaults
    assert result["sets"] == ""
    assert result["vector_distance_metric"] == 0

    assert result["hnsw_params"]["max_mem_queue_size"] == 1000000
    assert result["hnsw_params"]["index_caching_params"]["max_entries"] == 2000000
    assert result["hnsw_params"]["index_caching_params"]["expiry"] == 3600000

    assert result["hnsw_params"]["healer_params"]["max_scan_rate_per_node"] == 1000
    assert result["hnsw_params"]["healer_params"]["max_scan_page_size"] == 10000
    assert result["hnsw_params"]["healer_params"]["re_index_percent"] == 10.0
    assert result["hnsw_params"]["healer_params"]["schedule"] == "* * * * * ?"
    assert result["hnsw_params"]["healer_params"]["parallelism"] == 1

    # index parallelism and reindex parallelism are dynamic depending on the CPU cores of the host
    # assert result["hnsw_params"]["merge_params"]["index_parallelism"] == 80
    # assert result["hnsw_params"]["merge_params"]["reindex_parallelism"] == 26


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
async def test_index_get_no_defaults(session_admin_client, empty_test_case, index):

    result = session_admin_client.index_get(namespace=DEFAULT_NAMESPACE, name=index, apply_defaults=False)

    assert result["id"]["name"] == index
    assert result["id"]["namespace"] == DEFAULT_NAMESPACE
    assert result["dimensions"] == DEFAULT_INDEX_DIMENSION
    assert result["field"] == DEFAULT_VECTOR_FIELD

    # Defaults
    assert result["sets"] == ""
    assert result["vector_distance_metric"] == 0

    assert result["hnsw_params"]["m"] == 0
    assert result["hnsw_params"]["ef"] == 0
    assert result["hnsw_params"]["ef_construction"] == 0
    assert result["hnsw_params"]["batching_params"]["max_index_records"] == 0
    # This is set by default to 10000 in the index fixture
    assert result["hnsw_params"]["batching_params"]["index_interval"] == 10000
    assert result["hnsw_params"]["max_mem_queue_size"] == 0
    assert result["hnsw_params"]["index_caching_params"]["max_entries"] == 0
    assert result["hnsw_params"]["index_caching_params"]["expiry"] == 0

    assert result["hnsw_params"]["healer_params"]["max_scan_rate_per_node"] == 0
    assert result["hnsw_params"]["healer_params"]["max_scan_page_size"] == 0
    assert result["hnsw_params"]["healer_params"]["re_index_percent"] == 0
    # This is set by default to * * * * * ? in the index fixture
    assert result["hnsw_params"]["healer_params"]["schedule"] == "* * * * * ?"
    assert result["hnsw_params"]["healer_params"]["parallelism"] == 0

    assert result["hnsw_params"]["merge_params"]["index_parallelism"] == 0
    assert result["hnsw_params"]["merge_params"]["reindex_parallelism"] == 0

    assert result["storage"]["namespace"] == ""
    assert result["storage"].set_name == ""
    assert result["storage"]["set_name"] == ""


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_get_timeout(
    session_admin_client, empty_test_case, index, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):
        try:
            result = session_admin_client.index_get(
                namespace=DEFAULT_NAMESPACE, name=index, timeout=0.0001
            )

        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
