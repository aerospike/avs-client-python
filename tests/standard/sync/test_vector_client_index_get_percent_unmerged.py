import time

import pytest
from aerospike_vector_search import types

class index_get_percent_unmerged_test_case:
    def __init__(
            self,
            *,
            namespace,
            name,
            timeout,
            num_records,
            expected_unmerged_percent
        ):
            self.namespace = namespace
            self.name = name
            self.timeout = timeout
            self.num_records = num_records
            self.expected_unmerged_percent = expected_unmerged_percent

def gen_records(count: int, vec_bin: str, vec_dim: int):
    num = 0
    while num < count:
        yield {
            "bin1": num,
            vec_bin: [float(num)] * vec_dim,
        }
        num += 1

@pytest.mark.parametrize(
    "test_case",
    [
        index_get_percent_unmerged_test_case(
            namespace="test",
            name="pumIndex0",
            timeout=None,
            num_records=1_000,
            expected_unmerged_percent=0.0,
        ),
        index_get_percent_unmerged_test_case(
            namespace="test",
            name="pumIndex1",
            timeout=60,
            num_records=1_000,
            expected_unmerged_percent=0.0,
        ),
        # the 500 records won't be indexed until index_interval
        # is hit so we should expect 500.0% unmerged
        index_get_percent_unmerged_test_case(
            namespace="test",
            name="pumIndex2",
            timeout=None,
            num_records=500,
            expected_unmerged_percent=500.0,
        ),
    ],
)
def test_client_index_get_percent_unmerged(
    session_vector_client,
    session_admin_client,
    test_case,
):
    
    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_field="vector",
        dimensions=3,
        index_params=types.HnswParams(
            batching_params=types.HnswBatchingParams(
                max_index_records=1_000,
                index_interval=600_000,
            ),
        ),
    )

    key = 0
    for record in gen_records(test_case.num_records, "vector", 3):
        session_vector_client.upsert(
            namespace=test_case.namespace,
            key=key,
            record_data=record,
        )
        key += 1

    # need some time for index stats to be counted server side
    time.sleep(1)

    percent_unmerged = session_vector_client.index_get_percent_unmerged(
        namespace=test_case.namespace,
        name=test_case.name,
        timeout=test_case.timeout,
    )

    session_admin_client.index_drop(
        namespace=test_case.namespace,
        name=test_case.name,
    )

    assert percent_unmerged >= test_case.expected_unmerged_percent
