import numpy as np
import pytest

from utils import DEFAULT_NAMESPACE
from .aio_utils import wait_for_index
from aerospike_vector_search import types

INDEX = "sbk_index"
NAMESPACE = DEFAULT_NAMESPACE
DIMENSIONS = 3
VEC_BIN = "vector"
SET_NAME = "test_set"


class vector_search_by_key_test_case:
    def __init__(
        self,
        *,
        index_dimensions,
        vector_field,
        limit,
        key,
        key_namespace,
        search_namespace,
        include_fields,
        exclude_fields,
        key_set,
        expected_results,
    ):
        self.index_dimensions = index_dimensions
        self.vector_field = vector_field
        self.limit = limit
        self.key = key
        self.search_namespace = search_namespace
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields
        self.key_set = key_set
        self.expected_results = expected_results
        self.key_namespace = key_namespace


@pytest.fixture(scope="module", autouse=True)
async def setup_index(
    session_admin_client,
):
    await session_admin_client.index_create(
        namespace=DEFAULT_NAMESPACE,
        name=INDEX,
        vector_field=VEC_BIN,
        dimensions=DIMENSIONS,
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

    yield

    await session_admin_client.index_drop(
        namespace=DEFAULT_NAMESPACE,
        name=INDEX,
    )


@pytest.fixture(scope="module", autouse=True)
async def setup_records(
    session_vector_client,
):
    recs = {
        "rec1": {
            "bin": 1,
            VEC_BIN: [1.0] * DIMENSIONS,
        },
        2: {
            "bin": 2,
            VEC_BIN: [2.0] * DIMENSIONS,
        },
        bytes("rec5", "utf-8"): {
            "bin": 5,
            VEC_BIN: [5.0] * DIMENSIONS,
        },
    }

    keys = []
    for key, record in recs.items():
        await session_vector_client.upsert(
            namespace=DEFAULT_NAMESPACE,
            key=key,
            record_data=record,
        )
        keys.append(key)
    
    # write some records for set tests
    set_recs = {
        "srec100": {
            "bin": 100,
            VEC_BIN: [100.0] * DIMENSIONS,
        },
        "srec101": {
            "bin": 101,
            VEC_BIN: [101.0] * DIMENSIONS,
        },
    }

    for key, record in set_recs.items():
        await session_vector_client.upsert(
            namespace=DEFAULT_NAMESPACE,
            key=key,
            record_data=record,
            set_name=SET_NAME,
        )
        keys.append(key)

    yield

    for key in keys:
        await session_vector_client.delete(
            namespace=DEFAULT_NAMESPACE,
            key=key,
        )
    


#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        # test string key
        vector_search_by_key_test_case(
            index_dimensions=3,
            vector_field="vector",
            limit=2,
            key="rec1",
            key_namespace=DEFAULT_NAMESPACE,
            search_namespace=DEFAULT_NAMESPACE,
            include_fields=None,
            exclude_fields=None,
            key_set=None,
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key="rec1",
                    ),
                    fields={
                        "bin": 1,
                        "vector": [1.0, 1.0, 1.0],
                    },
                    distance=0.0,
                ),
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key=2,
                    ),
                    fields={
                        "bin": 2,
                        "vector": [2.0, 2.0, 2.0],
                    },
                    distance=3.0,
                ),
            ],
        ),
        # test int key
        vector_search_by_key_test_case(
            index_dimensions=3,
            vector_field="vector",
            limit=3,
            key=2,
            key_namespace=DEFAULT_NAMESPACE,
            search_namespace=DEFAULT_NAMESPACE,
            include_fields=["bin"],
            exclude_fields=["bin"],
            key_set=None,
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key=2,
                    ),
                    fields={},
                    distance=0.0,
                ),
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key="rec1",
                    ),
                    fields={},
                    distance=3.0,
                ),
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key=bytes("rec5", "utf-8"),
                    ),
                    fields={},
                    distance=27.0,
                ),
            ],
        ),
        # test bytes key
        vector_search_by_key_test_case(
            index_dimensions=3,
            vector_field="vector",
            limit=3,
            key=bytes("rec5", "utf-8"),
            key_namespace=DEFAULT_NAMESPACE,
            search_namespace=DEFAULT_NAMESPACE,
            include_fields=["bin"],
            exclude_fields=["bin"],
            key_set=None,
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key=bytes("rec5", "utf-8"),
                    ),
                    fields={},
                    distance=0.0,
                ),
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key=2,
                    ),
                    fields={},
                    distance=27.0,
                ),
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set="",
                        key="rec1",
                    ),
                    fields={},
                    distance=48.0,
                ),
            ],
        ),
        # # test bytearray key
        # # TODO: add a bytearray key case, bytearrays are not hashable
        # # so this is not easily added. Leaving it for now.
        # # vector_search_by_key_test_case(
        # #     index_name="field_filter",
        # #     index_dimensions=3,
        # #     vector_field="vector",
        # #     limit=3,
        # #     key=bytearray("rec1", "utf-8"),
        # #     namespace=DEFAULT_NAMESPACE,
        # #     include_fields=["bin"],
        # #     exclude_fields=["bin"],
        # #     key_set=None,
        # #     record_data={
        # #         bytearray("rec1", "utf-8"): {
        # #             "bin": 1,
        # #             "vector": [1.0, 1.0, 1.0],
        # #         },
        # #         bytearray("rec1", "utf-8"): {
        # #             "bin": 2,
        # #             "vector": [2.0, 2.0, 2.0],
        # #         },
        # #     },
        # #     expected_results=[
        # #         types.Neighbor(
        # #             key=types.Key(
        # #                 namespace=DEFAULT_NAMESPACE,
        # #                 set="",
        # #                 key=2,
        # #             ),
        # #             fields={},
        # #             distance=3.0,
        # #         ),
        # #     ],
        # # ),
        # test with set name
        vector_search_by_key_test_case(
            index_dimensions=3,
            vector_field="vector",
            limit=2,
            key="srec100",
            key_namespace=DEFAULT_NAMESPACE,
            search_namespace=DEFAULT_NAMESPACE,
            include_fields=None,
            exclude_fields=None,
            key_set=SET_NAME,
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set=SET_NAME,
                        key="srec100",
                    ),
                    fields={
                        "bin": 100,
                        "vector": [100.0] * DIMENSIONS,
                    },
                    distance=0.0,
                ),
                types.Neighbor(
                    key=types.Key(
                        namespace=DEFAULT_NAMESPACE,
                        set=SET_NAME,
                        key="srec101",
                    ),
                    fields={
                        "bin": 101,
                        "vector": [101.0] * DIMENSIONS,
                    },
                    distance=3.0,
                ),
            ],
        ),
    ],
)
async def test_vector_search_by_key(
    session_vector_client,
    session_admin_client,
    test_case,
):
    await wait_for_index(session_admin_client, DEFAULT_NAMESPACE, INDEX)

    results = await session_vector_client.vector_search_by_key(
        search_namespace=test_case.search_namespace,
        index_name=INDEX,
        key=test_case.key,
        key_namespace=test_case.key_namespace,
        vector_field=test_case.vector_field,
        limit=test_case.limit,
        key_set=test_case.key_set,
        include_fields=test_case.include_fields,
        exclude_fields=test_case.exclude_fields,
    )

    assert results == test_case.expected_results


async def test_vector_search_by_key_different_namespaces(
    session_vector_client,
    session_admin_client,
):
    
    await session_admin_client.index_create(
        namespace="index_storage",
        name="diff_ns_idx",
        vector_field="vec",
        dimensions=3,
    )

    await session_vector_client.upsert(
        namespace="test",
        key="search_by",
        record_data={
            "bin": 1,
            "vec": [1.0, 1.0, 1.0],
        },
    )

    await session_vector_client.upsert(
        namespace="index_storage",
        key="search_for",
        record_data={
            "bin": 2,
            "vec": [2.0, 2.0, 2.0],
        },
    )
    
    await wait_for_index(session_admin_client, "index_storage", "diff_ns_idx")

    results = await session_vector_client.vector_search_by_key(
        search_namespace="index_storage",
        index_name="diff_ns_idx",
        key="search_by",
        key_namespace="test",
        vector_field="vec",
        limit=1,
    )

    expected = [
        types.Neighbor(
            key=types.Key(
                namespace="index_storage",
                set="",
                key="search_for",
            ),
            fields={
                "bin": 2,
                "vec": [2.0, 2.0, 2.0],
            },
            distance=3.0,
        ),
    ]

    assert results == expected

    await session_vector_client.delete(
        namespace="test",
        key="search_by",
    )

    await session_vector_client.delete(
        namespace="index_storage",
        key="search_for",
    )

    await session_admin_client.index_drop(
        namespace="index_storage",
        name="diff_ns_idx",
    )