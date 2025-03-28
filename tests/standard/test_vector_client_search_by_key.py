from aerospike_vector_search import types
from utils import wait_for_index

import pytest

class vector_search_by_key_test_case:
    def __init__(
        self,
        *,
        index_name,
        index_dimensions,
        vector_field,
        limit,
        key,
        key_namespace,
        search_namespace,
        include_fields,
        exclude_fields,
        key_set,
        record_data,
        expected_results,
    ):
        self.index_name = index_name
        self.index_dimensions = index_dimensions
        self.vector_field = vector_field
        self.limit = limit
        self.key = key
        self.search_namespace = search_namespace
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields
        self.key_set = key_set
        self.record_data = record_data
        self.expected_results = expected_results
        self.key_namespace = key_namespace

# TODO add a teardown
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        # test string key
        vector_search_by_key_test_case(
            index_name="BSSK",
            index_dimensions=3,
            vector_field="vector",
            limit=2,
            key="rec1",
            key_namespace="test",
            search_namespace="test",
            include_fields=None,
            exclude_fields=None,
            key_set=None,
            record_data={
                "rec1": {
                    "bin": 1,
                    "vector": [1.0, 1.0, 1.0],
                },
                "rec2": {
                    "bin": 2,
                    "vector": [2.0, 2.0, 2.0],
                },
                "rec3": {
                    "bin": 3,
                    "vector": [3.0, 3.0, 3.0],
                },
            },
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace="test",
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
                        namespace="test",
                        set="",
                        key="rec2",
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
            index_name="BSIK",
            index_dimensions=3,
            vector_field="vector",
            limit=3,
            key=1,
            key_namespace="test",
            search_namespace="test",
            include_fields=["bin"],
            exclude_fields=["bin"],
            key_set=None,
            record_data={
                1: {
                    "bin": 1,
                    "vector": [1.0, 1.0, 1.0],
                },
                2: {
                    "bin": 2,
                    "vector": [2.0, 2.0, 2.0],
                },
            },
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace="test",
                        set="",
                        key=1,
                    ),
                    fields={},
                    distance=0.0,
                ),
                types.Neighbor(
                    key=types.Key(
                        namespace="test",
                        set="",
                        key=2,
                    ),
                    fields={},
                    distance=3.0,
                ),
            ],
        ),
        # test bytes key
        vector_search_by_key_test_case(
            index_name="BSBK",
            index_dimensions=3,
            vector_field="vector",
            limit=3,
            key=bytes("rec1", "utf-8"),
            key_namespace="test",
            search_namespace="test",
            include_fields=["bin"],
            exclude_fields=["bin"],
            key_set=None,
            record_data={
                bytes("rec1", "utf-8"): {
                    "bin": 1,
                    "vector": [1.0, 1.0, 1.0],
                },
                bytes("rec2", "utf-8"): {
                    "bin": 2,
                    "vector": [2.0, 2.0, 2.0],
                },
            },
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace="test",
                        set="",
                        key=bytes("rec1", "utf-8"),
                    ),
                    fields={},
                    distance=0.0,
                ),
                types.Neighbor(
                    key=types.Key(
                        namespace="test",
                        set="",
                        key=bytes("rec2", "utf-8"),
                    ),
                    fields={},
                    distance=3.0,
                ),
            ],
        ),
        # test bytearray key
        # TODO: add a bytearray key case, bytearrays are not hashable
        # so this is not easily added. Leaving it for now.
        # vector_search_by_key_test_case(
        #     index_name="field_filter",
        #     index_dimensions=3,
        #     vector_field="vector",
        #     limit=3,
        #     key=bytearray("rec1", "utf-8"),
        #     namespace="test",
        #     include_fields=["bin"],
        #     exclude_fields=["bin"],
        #     key_set=None,
        #     record_data={
        #         bytearray("rec1", "utf-8"): {
        #             "bin": 1,
        #             "vector": [1.0, 1.0, 1.0],
        #         },
        #         bytearray("rec1", "utf-8"): {
        #             "bin": 2,
        #             "vector": [2.0, 2.0, 2.0],
        #         },
        #     },
        #     expected_results=[
        #         types.Neighbor(
        #             key=types.Key(
        #                 namespace="test",
        #                 set="",
        #                 key=2,
        #             ),
        #             fields={},
        #             distance=3.0,
        #         ),
        #     ],
        # ),
        # test with set name
        vector_search_by_key_test_case(
            index_name="BSSN",
            index_dimensions=3,
            vector_field="vector",
            limit=2,
            key="rec1",
            key_namespace="test",
            search_namespace="test",
            include_fields=None,
            exclude_fields=None,
            key_set="test_set",
            record_data={
                "rec1": {
                    "bin": 1,
                    "vector": [1.0, 1.0, 1.0],
                },
                "rec2": {
                    "bin": 2,
                    "vector": [2.0, 2.0, 2.0],
                },
            },
            expected_results=[
                types.Neighbor(
                    key=types.Key(
                        namespace="test",
                        set="test_set",
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
                        namespace="test",
                        set="test_set",
                        key="rec2",
                    ),
                    fields={
                        "bin": 2,
                        "vector": [2.0, 2.0, 2.0],
                    },
                    distance=3.0,
                ),
            ],
        ),
    ],
)
def test_vector_search_by_key(
    session_vector_client,
    test_case,
):
    
    session_vector_client.index_create(
        namespace=test_case.search_namespace,
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

    for key, rec in test_case.record_data.items():
        session_vector_client.upsert(
            namespace=test_case.key_namespace,
            key=key,
            record_data=rec,
            set_name=test_case.key_set,
        )
    
    wait_for_index(
        admin_client=session_vector_client,
        namespace=test_case.search_namespace,
        index=test_case.index_name,
    )

    results = session_vector_client.vector_search_by_key(
        search_namespace=test_case.search_namespace,
        index_name=test_case.index_name,
        key=test_case.key,
        key_namespace=test_case.key_namespace,
        vector_field=test_case.vector_field,
        limit=test_case.limit,
        key_set=test_case.key_set,
        include_fields=test_case.include_fields,
        exclude_fields=test_case.exclude_fields,
    )

    assert results == test_case.expected_results

    for key in test_case.record_data:
        session_vector_client.delete(
            namespace=test_case.key_namespace,
            set_name=test_case.key_set,
            key=key,
        )

    session_vector_client.index_drop(
        namespace=test_case.search_namespace,
        name=test_case.index_name,
    )


def test_vector_search_by_key_different_namespaces(
    session_vector_client,
):
    
    session_vector_client.index_create(
        namespace="index_storage",
        name="diff_ns_idx",
        vector_field="vec",
        dimensions=3,
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

    session_vector_client.upsert(
        namespace="test",
        key="search_by",
        record_data={
            "bin": 1,
            "vec": [1.0, 1.0, 1.0],
        },
    )

    session_vector_client.upsert(
        namespace="index_storage",
        key="search_for",
        record_data={
            "bin": 2,
            "vec": [2.0, 2.0, 2.0],
        },
    )
    
    wait_for_index(
        admin_client=session_vector_client,
        namespace="index_storage",
        index="diff_ns_idx",
    )

    results = session_vector_client.vector_search_by_key(
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

    session_vector_client.delete(
        namespace="test",
        key="search_by",
    )

    session_vector_client.delete(
        namespace="index_storage",
        key="search_for",
    )

    session_vector_client.index_drop(
        namespace="index_storage",
        name="diff_ns_idx",
    )