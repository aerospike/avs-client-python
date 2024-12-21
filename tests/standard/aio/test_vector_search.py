import numpy as np
import asyncio
import pytest

from aerospike_vector_search import types
from utils import DEFAULT_NAMESPACE
from .aio_utils import wait_for_index


class vector_search_test_case:
    def __init__(
        self,
        *,
        index_name,
        index_dimensions,
        vector_field,
        limit,
        query,
        namespace,
        include_fields,
        exclude_fields,
        set_name,
        record_data,
        expected_results,
    ):
        self.index_name = index_name
        self.index_dimensions = index_dimensions
        self.vector_field = vector_field
        self.limit = limit
        self.query = query
        self.namespace = namespace
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields
        self.set_name = set_name
        self.record_data = record_data
        self.expected_results = expected_results


# TODO add a teardown
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        vector_search_test_case(
            index_name="basic_search",
            index_dimensions=3,
            vector_field="vecs",
            limit=3,
            query=[0.0, 0.0, 0.0],
            namespace=DEFAULT_NAMESPACE,
            include_fields=None,
            exclude_fields = None,
            set_name=None,
            record_data={
                "rec1": {
                    "bin1": 1,
                    "vecs": [1.0, 1.0, 1.0],
                },
            },
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key="rec1",
                    ),
                    fields={
                        "bin1": 1,
                        "vecs": [1.0, 1.0, 1.0],
                    },
                    distance=3.0,
                ),
            ],
        ),
        vector_search_test_case(
            index_name="field_filter",
            index_dimensions=3,
            vector_field="vecs",
            limit=3,
            query=[0.0, 0.0, 0.0],
            namespace=DEFAULT_NAMESPACE,
            include_fields=["bin1"],
            exclude_fields=["bin1"],
            set_name=None,
            record_data={
                "rec1": {
                    "bin1": 1,
                    "vecs": [1.0, 1.0, 1.0],
                },
            },
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key="rec1",
                    ),
                    fields={},
                    distance=3.0,
                ),
            ],
        ),
    ],
)
async def test_vector_search(
    session_vector_client,
    session_admin_client,
    test_case,
):
    
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.index_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.index_dimensions,
        index_params=types.HnswParams(
            batching_params=types.HnswBatchingParams(
                # 10_000 is the minimum value, in order for the tests to run as
                # fast as possible we set it to the minimum value so records are indexed
                # quickly
                index_interval=10_000,
            ),
            healer_params=types.HnswHealerParams(
                # run the healer every second
                # for fast indexing
                schedule="* * * * * ?"
            )
        )
    )

    tasks = []
    for key, rec in test_case.record_data.items():
        tasks.append(session_vector_client.upsert(
            namespace=test_case.namespace,
            key=key,
            record_data=rec,
            set_name=test_case.set_name,
        ))
    
    tasks.append(
        wait_for_index(
            session_admin_client,
            namespace=test_case.namespace,
            index=test_case.index_name,
        )
    )
    await asyncio.gather(*tasks)

    results = await session_vector_client.vector_search(
        namespace=test_case.namespace,
        index_name=test_case.index_name,
        query=test_case.query,
        limit=test_case.limit,
        include_fields=test_case.include_fields,
        exclude_fields=test_case.exclude_fields,
    )

    assert results == test_case.expected_results

    tasks = []
    for key in test_case.record_data:
        tasks.append(session_vector_client.delete(
            namespace=test_case.namespace,
            key=key,
        ))
    
    await asyncio.gather(*tasks)

    await session_admin_client.index_drop(
        namespace=test_case.namespace,
        name=test_case.index_name,
    )
