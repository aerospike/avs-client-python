import pytest
from ...utils import random_name

from .aio_utils import drop_specified_index
from hypothesis import given, settings, Verbosity

from aerospike_vector_search import AVSServerError
import grpc


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
async def test_index_get(session_admin_client, empty_test_case, random_name):
    await session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="science",
        dimensions=1024,
    )
    result = await session_admin_client.index_get(namespace="test", name=random_name, apply_defaults=True)

    assert result["id"]["name"] == random_name
    assert result["id"]["namespace"] == "test"
    assert result["dimensions"] == 1024
    assert result["field"] == "science"
    assert result["hnsw_params"]["m"] == 16
    assert result["hnsw_params"]["ef_construction"] == 100
    assert result["hnsw_params"]["ef"] == 100
    assert result["hnsw_params"]["batching_params"]["max_records"] == 100000
    assert result["hnsw_params"]["batching_params"]["interval"] == 30000
    assert result["storage"]["namespace"] == "test"
    assert result["storage"].set_name == random_name
    assert result["storage"]["set_name"] == random_name

    # Defaults
    assert result["sets"] == ""
    assert result["vector_distance_metric"] == 0

    assert result["hnsw_params"]["max_mem_queue_size"] == 1000000
    assert result["hnsw_params"]["caching_params"]["max_entries"] == 2000000
    assert result["hnsw_params"]["caching_params"]["expiry"] == 3600000

    assert result["hnsw_params"]["healer_params"]["max_scan_rate_per_node"] == 1000
    assert result["hnsw_params"]["healer_params"]["max_scan_page_size"] == 10000
    assert result["hnsw_params"]["healer_params"]["re_index_percent"] == 10.0
    assert result["hnsw_params"]["healer_params"]["schedule"] == "0 0/15 * ? * * *"
    assert result["hnsw_params"]["healer_params"]["parallelism"] == 1

    # index parallelism and reindex parallelism are dynamic depending on the CPU cores of the host
    # assert result["hnsw_params"]["merge_params"]["index_parallelism"] == 80
    # assert result["hnsw_params"]["merge_params"]["reindex_parallelism"] == 26

    await drop_specified_index(session_admin_client, "test", random_name)


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
async def test_index_get_no_defaults(session_admin_client, empty_test_case, random_name):
    await session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="science",
        dimensions=1024,
    )

    result = await session_admin_client.index_get(namespace="test", name=random_name, apply_defaults=False)

    # AVS server still returns values for these fields even if apply_defaults is False
    # this might change in the future if it is fixed in the server
    assert result["id"]["name"] == random_name
    assert result["id"]["namespace"] == "test"
    assert result["dimensions"] == 1024
    assert result["field"] == "science"
    assert result["hnsw_params"]["m"] == 16
    assert result["hnsw_params"]["ef_construction"] == 100
    assert result["hnsw_params"]["ef"] == 100
    assert result["hnsw_params"]["batching_params"]["max_records"] == 100000
    assert result["hnsw_params"]["batching_params"]["interval"] == 30000
    assert result["storage"]["namespace"] == "test"
    assert result["storage"].set_name == random_name
    assert result["storage"]["set_name"] == random_name

    # Defaults
    assert result["sets"] == ""
    assert result["vector_distance_metric"] == 0

    assert result["hnsw_params"]["max_mem_queue_size"] == 0
    assert result["hnsw_params"]["caching_params"]["max_entries"] == 0
    assert result["hnsw_params"]["caching_params"]["expiry"] == 0

    assert result["hnsw_params"]["healer_params"]["max_scan_rate_per_node"] == 0
    assert result["hnsw_params"]["healer_params"]["max_scan_page_size"] == 0
    assert result["hnsw_params"]["healer_params"]["re_index_percent"] == 0
    assert result["hnsw_params"]["healer_params"]["schedule"] == ""
    assert result["hnsw_params"]["healer_params"]["parallelism"] == 0

    assert result["hnsw_params"]["merge_params"]["index_parallelism"] == 0
    assert result["hnsw_params"]["merge_params"]["reindex_parallelism"] == 0

    await drop_specified_index(session_admin_client, "test", random_name)


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
async def test_index_get_timeout(
    session_admin_client, empty_test_case, random_name, with_latency
):

    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):
        try:
            result = await session_admin_client.index_get(
                namespace="test", name=random_name, timeout=0.0001
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
