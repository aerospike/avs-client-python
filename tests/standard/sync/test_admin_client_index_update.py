import pytest
from aerospike_vector_search import types, AVSServerError
import grpc

from ...utils import random_name
from .sync_utils import drop_specified_index


class index_update_test_case:
    def __init__(
            self,
            *,
            namespace,
            vector_field,
            dimensions,
            initial_labels,
            update_labels,
            hnsw_index_update,
            timeout
    ):
        self.namespace = namespace
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
            namespace="test",
            vector_field="update_1",
            dimensions=512,
            initial_labels={"environment": "staging"},
            update_labels={"environment": "production", "priority": "high"},
            hnsw_index_update=types.HnswIndexUpdate(
                batching_params=types.HnswBatchingParams(max_index_records=5000, index_interval=20000),
                max_mem_queue_size=2000,
            ),
            timeout=None,
        ),
    ],
)
def test_index_update(session_admin_client, test_case, random_name):
    try:
        session_admin_client.index_drop(namespace="test", name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass

    # Step 1: Create the index
    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        index_labels=test_case.initial_labels,
        timeout=test_case.timeout,
    )

    # Step 2: Update the index with new labels and parameters
    session_admin_client.index_update(
        namespace=test_case.namespace,
        name=random_name,
        index_labels=test_case.update_labels,
        hnsw_update_params=test_case.hnsw_index_update,
        timeout=test_case.timeout,
    )

    # Step 3: Verify the update
    results = session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["index_labels"] == test_case.update_labels
            assert result["hnsw_params"]["batching_params"][
                       "max_index_records"] == test_case.hnsw_index_update.batching_params.max_index_records
            assert result["hnsw_params"]["batching_params"][
                       "index_interval"] == test_case.hnsw_index_update.batching_params.index_interval
            assert result["hnsw_params"]["max_mem_queue_size"] == test_case.hnsw_index_update.max_mem_queue_size
    assert found is True
    drop_specified_index(session_admin_client, test_case.namespace, random_name)


@pytest.mark.parametrize(
    "test_case",
    [
        index_update_test_case(
            namespace="test",
            vector_field="update_2",
            dimensions=256,
            initial_labels={"status": "active"},
            update_labels={"status": "inactive", "region": "us-west"},
            hnsw_index_update=types.HnswIndexUpdate(
                healer_params=types.HnswHealerParams(max_scan_rate_per_node=80),
            ),
            timeout=None,
        ),
    ],
)
def test_index_update_with_healer_params(session_admin_client, test_case, random_name):
    trimmed_random= random_name[:10]
    try:
        session_admin_client.index_drop(namespace="test", name=trimmed_random)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass

    # Step 1: Create the index
    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=trimmed_random,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        index_labels=test_case.initial_labels,
        timeout=test_case.timeout,
    )

    # Step 2: Update the index with healer parameters
    session_admin_client.index_update(
        namespace=test_case.namespace,
        name=trimmed_random,
        index_labels=test_case.update_labels,
        hnsw_update_params=test_case.hnsw_index_update,
        timeout=test_case.timeout,
    )

    # Step 3: Verify the update
    results = session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == trimmed_random:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["index_labels"] == test_case.update_labels
            assert result["hnsw_params"]["healer_params"][
                       "max_scan_rate_per_node"] == test_case.hnsw_index_update.healer_params.max_scan_rate_per_node
    assert found is True
    drop_specified_index(session_admin_client, test_case.namespace, trimmed_random)
