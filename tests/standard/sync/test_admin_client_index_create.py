import pytest
from aerospike_vector_search import types
from ...utils import index_strategy
from .sync_utils import drop_specified_index
from hypothesis import given, settings, Verbosity

class index_create_test_case:
    def __init__(
        self,
        *,
        namespace,
        vector_field,
        dimensions,
        vector_distance_metric,
        sets,
        index_params,
        index_meta_data,
    ):
        self.namespace = namespace
        self.vector_field = vector_field
        self.dimensions = dimensions
        if vector_distance_metric == None:
            self.vector_distance_metric = types.VectorDistanceMetric.SQUARED_EUCLIDEAN
        else:
            self.vector_distance_metric = vector_distance_metric
        self.sets = sets
        self.index_params = index_params
        self.index_meta_data = index_meta_data

@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_1",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_meta_data=None,
        )
    ],
)
def test_index_create(session_admin_client, test_case, random_name):
    if test_case == None:
        return
    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_meta_data=test_case.index_meta_data,
    )
    results = session_admin_client.index_list()
    found = False
    for result in results:
        if result['id']['name'] == random_name:
            found = True
            assert result['id']['namespace'] == test_case.namespace
            assert result['dimensions'] == test_case.dimensions
            assert result['field'] == test_case.vector_field
            assert result['hnsw_params']['m'] == 16
            assert result['hnsw_params']['ef_construction'] == 100
            assert result['hnsw_params']['ef'] == 100
            assert result['hnsw_params']['batching_params']['max_records'] == 100000
            assert result['hnsw_params']['batching_params']['interval'] == 30000
            assert result['hnsw_params']['batching_params']['disabled'] == False
            assert result['storage']['namespace'] == test_case.namespace
            assert result['storage']['set'] == random_name
    assert found == True
    drop_specified_index(session_admin_client, test_case.namespace, random_name)


@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_2",
            dimensions=495,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_meta_data=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_3",
            dimensions=2048,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_meta_data=None,
        ),
    ],
)
def test_index_create_with_dimnesions(session_admin_client, test_case, random_name):
    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_meta_data=test_case.index_meta_data,
    )


    results = session_admin_client.index_list()

    found = False
    for result in results:

        if result['id']['name'] == random_name:
            found = True
            assert result['id']['namespace'] == test_case.namespace
            assert result['dimensions'] == test_case.dimensions
            assert result['field'] == test_case.vector_field
            assert result['hnsw_params']['m'] == 16
            assert result['hnsw_params']['ef_construction'] == 100
            assert result['hnsw_params']['ef'] == 100
            assert result['hnsw_params']['batching_params']['max_records'] == 100000
            assert result['hnsw_params']['batching_params']['interval'] == 30000
            assert result['hnsw_params']['batching_params']['disabled'] == False
            assert result['storage']['namespace'] == test_case.namespace
            assert result['storage']['set'] == random_name
    assert found == True

    drop_specified_index(session_admin_client, test_case.namespace, random_name)



@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_4",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.COSINE,
            sets=None,
            index_params=None,
            index_meta_data=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_5",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.DOT_PRODUCT,
            sets=None,
            index_params=None,
            index_meta_data=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_6",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.MANHATTAN,
            sets=None,
            index_params=None,
            index_meta_data=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_7",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.HAMMING,
            sets=None,
            index_params=None,
            index_meta_data=None,
        ),
    ],
)
def test_index_create_with_vector_distance_metric(
    session_admin_client, test_case, random_name
):


    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_meta_data=test_case.index_meta_data,
    )
    results = session_admin_client.index_list()
    found = False
    for result in results:
        if result['id']['name'] == random_name:
            found = True
            assert result['id']['namespace'] == test_case.namespace
            assert result['dimensions'] == test_case.dimensions
            assert result['field'] == test_case.vector_field
            assert result['hnsw_params']['m'] == 16
            assert result['hnsw_params']['ef_construction'] == 100
            assert result['hnsw_params']['ef'] == 100
            assert result['hnsw_params']['batching_params']['max_records'] == 100000
            assert result['hnsw_params']['batching_params']['interval'] == 30000
            assert result['hnsw_params']['batching_params']['disabled'] == False
            assert result['storage']['namespace'] == test_case.namespace
            assert result['storage']['set'] == random_name
    assert found == True
    drop_specified_index(session_admin_client, test_case.namespace, random_name)


@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_8",
            dimensions=1024,
            vector_distance_metric=None,
            sets="Demo",
            index_params=None,
            index_meta_data=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_9",
            dimensions=1024,
            vector_distance_metric=None,
            sets="Cheese",
            index_params=None,
            index_meta_data=None,
        ),
    ],
)
def test_index_create_with_sets(session_admin_client, test_case, random_name):

    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_meta_data=test_case.index_meta_data,
    )
    results = session_admin_client.index_list()
    found = False
    for result in results:
        if result['id']['name'] == random_name:
            found = True
            assert result['id']['namespace'] == test_case.namespace
            assert result['dimensions'] == test_case.dimensions
            assert result['field'] == test_case.vector_field
            assert result['hnsw_params']['m'] == 16
            assert result['hnsw_params']['ef_construction'] == 100
            assert result['hnsw_params']['ef'] == 100
            assert result['hnsw_params']['batching_params']['max_records'] == 100000
            assert result['hnsw_params']['batching_params']['interval'] == 30000
            assert result['hnsw_params']['batching_params']['disabled'] == False
            assert result['storage']['namespace'] == test_case.namespace
            assert result['storage']['set'] == random_name
    assert found == True
    drop_specified_index(session_admin_client, test_case.namespace, random_name)


@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_10",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                m=32,
                ef_construction=200,
                ef=400,
            ),
            index_meta_data=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_11",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                m=8,
                ef_construction=50,
                ef=25,
            ),
            index_meta_data=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_12",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                batching_params=types.HnswBatchingParams(
                    max_records=500, interval=500, disabled=True
                )
            ),
            index_meta_data=None,
        ),
    ],
)
def test_index_create_with_index_params(session_admin_client, test_case, random_name):
    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_meta_data=test_case.index_meta_data,
    )
    results = session_admin_client.index_list()
    found = False
    for result in results:
        if result['id']['name'] == random_name:
            found = True
            assert result['id']['namespace'] == test_case.namespace
            assert result['dimensions'] == test_case.dimensions
            assert result['field'] == test_case.vector_field
            assert result['hnsw_params']['m'] == test_case.index_params.m
            assert result['hnsw_params']['ef_construction'] == test_case.index_params.ef_construction
            assert result['hnsw_params']['ef'] == test_case.index_params.ef
            assert result['hnsw_params']['batching_params']['max_records'] == test_case.index_params.batching_params.max_records
            assert result['hnsw_params']['batching_params']['interval'] == test_case.index_params.batching_params.interval
            assert result['hnsw_params']['batching_params']['disabled'] == test_case.index_params.batching_params.disabled
            assert result['storage']['namespace'] == test_case.namespace
            assert result['storage']['set'] == random_name
    assert found == True
    drop_specified_index(session_admin_client, test_case.namespace, random_name)


@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_13",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_meta_data={"size": "large", "price": "$4.99", "currencyType": "CAN"},
        )
    ],
)
def test_index_create_index_meta_data(session_admin_client, test_case, random_name):
    if test_case == None:
        return
    session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_meta_data=test_case.index_meta_data,
    )
    results = session_admin_client.index_list()
    found = False
    for result in results:
        if result['id']['name'] == random_name:
            found = True
            assert result['id']['namespace'] == test_case.namespace
            assert result['dimensions'] == test_case.dimensions
            assert result['field'] == test_case.vector_field
            assert result['hnsw_params']['m'] == 16
            assert result['hnsw_params']['ef_construction'] == 100
            assert result['hnsw_params']['ef'] == 100
            assert result['hnsw_params']['batching_params']['max_records'] == 100000
            assert result['hnsw_params']['batching_params']['interval'] == 30000
            assert result['hnsw_params']['batching_params']['disabled'] == False
            assert result['storage']['namespace'] == test_case.namespace
            assert result['storage']['set'] == random_name
    assert found == True
    drop_specified_index(session_admin_client, test_case.namespace, random_name)
