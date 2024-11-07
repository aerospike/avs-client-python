import time

import pytest
from aerospike_vector_search import types, AVSServerError
import grpc

from .aio_utils import drop_specified_index

server_defaults = {
    "m": 16,
    "ef_construction": 100,
    "ef": 100,
    "batching_params": {
        "max_index_records": 10000,
        "index_interval": 10000,
    }
}


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
                batching_params=types.HnswBatchingParams(max_index_records=150000, index_interval=40000),
                max_mem_queue_size=1000010,
            ),
            timeout=None,
        ),
    ],
)
async def test_index_update_async(session_admin_client, test_case):
    # Create the index
    trimmed_random = "nzhAS"
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=trimmed_random,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        index_labels=test_case.initial_labels,
        timeout=test_case.timeout,
    )

    # Update the index with new labels and parameters
    await session_admin_client.index_update(
        namespace=test_case.namespace,
        name=trimmed_random,
        # index_labels=test_case.update_labels,
        hnsw_update_params=test_case.hnsw_index_update,
        timeout=test_case.timeout,
    )

    time.sleep(100_000)

    # Verify the update
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == trimmed_random:
            found = True
            print("Found Result test_index_update_async: ", result)
            assert result["id"]["namespace"] == test_case.namespace
            # assert result["index_labels"] == test_case.update_labels
            assert result["hnsw_params"]["batching_params"][
                       "max_index_records"] == test_case.hnsw_index_update.batching_params.max_index_records
            assert result["hnsw_params"]["batching_params"][
                       "index_interval"] == test_case.hnsw_index_update.batching_params.index_interval
            assert result["hnsw_params"]["max_mem_queue_size"] == test_case.hnsw_index_update.max_mem_queue_size
    assert found is True
    await drop_specified_index(session_admin_client, test_case.namespace, trimmed_random)
