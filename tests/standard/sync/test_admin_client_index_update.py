import time

from aerospike_vector_search import types
from utils import DEFAULT_NAMESPACE

import pytest

class index_update_test_case:
    def __init__(
            self,
            *,
            vector_field,
            dimensions,
            initial_labels,
            update_labels,
            hnsw_index_update,
            timeout
    ):
        self.vector_field = vector_field
        self.dimensions = dimensions
        self.initial_labels = initial_labels
        self.update_labels = update_labels
        self.hnsw_index_update = hnsw_index_update
        self.timeout = timeout


@pytest.mark.parametrize(
    "test_case",
    [
        index_update_test_case(
            vector_field="update_2",
            dimensions=256,
            initial_labels={"status": "active"},
            update_labels={"status": "inactive", "region": "us-west"},
            hnsw_index_update=types.HnswIndexUpdate(
                batching_params=types.HnswBatchingParams(max_index_records=2000, index_interval=20000, max_reindex_records=1500, reindex_interval=70000),
                max_mem_queue_size=1000030,
                index_caching_params=types.HnswCachingParams(max_entries=10, expiry=3000),
                merge_params=types.HnswIndexMergeParams(index_parallelism=10,reindex_parallelism=3),
                healer_params=types.HnswHealerParams(max_scan_rate_per_node=80),
                enable_vector_integrity_check=False,
            ),
            timeout=None,
        ),
    ],
)
def test_index_update(session_admin_client, test_case, index):
    # Update the index with parameters based on the test case
    session_admin_client.index_update(
        namespace=test_case.namespace,
        name=index,
        index_labels=test_case.update_labels,
        hnsw_update_params=test_case.hnsw_index_update,
        timeout=100_000,
    )
    #wait for index to get updated
    time.sleep(10)

    # Verify the update
    result = session_admin_client.index_get(namespace=test_case.namespace, name=index, apply_defaults=True)
    assert result, "Expected result to be non-empty but got an empty dictionary."

    # Assertions
    if test_case.hnsw_index_update.batching_params:
        assert result["hnsw_params"]["batching_params"]["max_index_records"] == test_case.hnsw_index_update.batching_params.max_index_records
        assert result["hnsw_params"]["batching_params"]["index_interval"] == test_case.hnsw_index_update.batching_params.index_interval
        assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == test_case.hnsw_index_update.batching_params.max_reindex_records
        assert result["hnsw_params"]["batching_params"]["reindex_interval"] == test_case.hnsw_index_update.batching_params.reindex_interval

    assert result["hnsw_params"]["max_mem_queue_size"] == test_case.hnsw_index_update.max_mem_queue_size

    if test_case.hnsw_index_update.index_caching_params:
        assert result["hnsw_params"]["index_caching_params"]["max_entries"] == test_case.hnsw_index_update.index_caching_params.max_entries
        assert result["hnsw_params"]["index_caching_params"]["expiry"] == test_case.hnsw_index_update.index_caching_params.expiry

    if test_case.hnsw_index_update.merge_params:
        assert result["hnsw_params"]["merge_params"]["index_parallelism"] == test_case.hnsw_index_update.merge_params.index_parallelism
        assert result["hnsw_params"]["merge_params"]["reindex_parallelism"] == test_case.hnsw_index_update.merge_params.reindex_parallelism

    if test_case.hnsw_index_update.healer_params:
        assert result["hnsw_params"]["healer_params"]["max_scan_rate_per_node"] == test_case.hnsw_index_update.healer_params.max_scan_rate_per_node

    assert result["hnsw_params"]["enable_vector_integrity_check"] == test_case.hnsw_index_update.enable_vector_integrity_check
