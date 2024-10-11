import pytest
from aerospike_vector_search import types


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
            index_name="basic_search",
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
            index_name="field_filter",
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
            index_name="field_filter",
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
            index_name="basic_search",
            index_dimensions=3,
            vector_field="vector",
            limit=1,
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
    session_admin_client,
    test_case,
):
    
    session_admin_client.index_create(
        namespace=test_case.search_namespace,
        name=test_case.index_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.index_dimensions,
    )

    for key, rec in test_case.record_data.items():
        session_vector_client.upsert(
            namespace=test_case.key_namespace,
            key=key,
            record_data=rec,
            key_set=test_case.key_set,
        )
    
    session_vector_client.wait_for_index_completion(
        namespace=test_case.search_namespace,
        name=test_case.index_name,
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
            key=key,
        )

    session_admin_client.index_drop(
        namespace=test_case.search_namespace,
        name=test_case.index_name,
    )
