import time

import pytest


class index_get_percent_unmerged_test_case:
    def __init__(
            self,
            *,
            namespace,
            timeout,
            expected_unmerged_percent
        ):
            self.namespace = namespace
            self.timeout = timeout
            self.expected_unmerged_percent = expected_unmerged_percent


@pytest.mark.parametrize(
    "records,test_case",
    [
        (
            {"num_records": 1_000},
            index_get_percent_unmerged_test_case(
                namespace="test",
                timeout=None,
                expected_unmerged_percent=0.0,
            )
        ),
        (
            {"num_records": 1_000},
            index_get_percent_unmerged_test_case(
                namespace="test",
                timeout=60,
                expected_unmerged_percent=0.0,
            ),
        ),
        # the 500 records won't be indexed until index_interval
        # is hit so we should expect 500.0% unmerged
        (
            {"num_records": 500},
            index_get_percent_unmerged_test_case(
                namespace="test",
                timeout=None,
                expected_unmerged_percent=500.0,
            ),
        )
    ],
    indirect=["records"],
)
def test_client_index_get_percent_unmerged(
    session_vector_client,
    index,
    records,
    test_case,
):
    # need some time for index stats to be counted server side
    time.sleep(1)

    percent_unmerged = session_vector_client.index_get_percent_unmerged(
        namespace=test_case.namespace,
        name=index,
        timeout=test_case.timeout,
    )

    assert percent_unmerged >= test_case.expected_unmerged_percent
