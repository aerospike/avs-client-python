import pytest
from aerospike_vector import types


class index_create_test_case:
    def __init__(
        self,
        *,
        namespace,
        name,
        vector_bin_name,
        dimensions,
        vector_distance_metric,
        sets,
        index_params,
        labels,
    ):
        self.namespace = namespace
        self.name = name
        self.vector_bin_name = vector_bin_name
        self.dimensions = dimensions
        if vector_distance_metric == None:
            self.vector_distance_metric = types.VectorDistanceMetric.SQUARED_EUCLIDEAN
        else:
            self.vector_distance_metric = vector_distance_metric
        self.sets = sets
        self.index_params = index_params
        self.labels = labels


@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            name="index_1",
            vector_bin_name="example_1",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            labels=None,
        )
    ],
)
async def test_index_create(session_admin_client, test_case):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_bin_name=test_case.vector_bin_name,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        labels=test_case.labels,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result.id.name == test_case.name:
            found = True
            assert result.id.namespace == test_case.namespace
            assert result.dimensions == test_case.dimensions
            assert result.bin == test_case.vector_bin_name
            assert result.hnswParams.m == 16
            assert result.hnswParams.efConstruction == 100
            assert result.hnswParams.ef == 100
            assert result.hnswParams.batchingParams.maxRecords == 100000
            assert result.hnswParams.batchingParams.interval == 30000
            assert result.hnswParams.batchingParams.disabled == False
            assert result.aerospikeStorage.namespace == test_case.namespace
            assert result.aerospikeStorage.set == test_case.name
    assert found == True

@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            name="index_2",
            vector_bin_name="example_2",
            dimensions=495,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            labels=None,
        ),
        index_create_test_case(
            namespace="test",
            name="index_3",
            vector_bin_name="example_3",
            dimensions=2048,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            labels=None,
        ),
    ],
)
async def test_index_create_with_dimnesions(session_admin_client, test_case):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_bin_name=test_case.vector_bin_name,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        labels=test_case.labels,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result.id.name == test_case.name:
            found = True
            assert result.id.namespace == test_case.namespace
            assert result.dimensions == test_case.dimensions
            assert result.bin == test_case.vector_bin_name
            assert result.hnswParams.m == 16
            assert result.hnswParams.efConstruction == 100
            assert result.hnswParams.ef == 100
            assert result.hnswParams.batchingParams.maxRecords == 100000
            assert result.hnswParams.batchingParams.interval == 30000
            assert result.hnswParams.batchingParams.disabled == False
            assert result.aerospikeStorage.namespace == test_case.namespace
            assert result.aerospikeStorage.set == test_case.name
    assert found == True

@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            name="index_4",
            vector_bin_name="example_4",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.COSINE,
            sets=None,
            index_params=None,
            labels=None,
        ),
        index_create_test_case(
            namespace="test",
            name="index_5",
            vector_bin_name="example_5",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.DOT_PRODUCT,
            sets=None,
            index_params=None,
            labels=None,
        ),
        index_create_test_case(
            namespace="test",
            name="index_6",
            vector_bin_name="example_6",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.MANHATTAN,
            sets=None,
            index_params=None,
            labels=None,
        ),
        index_create_test_case(
            namespace="test",
            name="index_7",
            vector_bin_name="example_7",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.HAMMING,
            sets=None,
            index_params=None,
            labels=None,
        ),
    ],
)
async def test_index_create_with_vector_distance_metric(
    session_admin_client, test_case
):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_bin_name=test_case.vector_bin_name,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        labels=test_case.labels,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result.id.name == test_case.name:
            found = True
            assert result.id.namespace == test_case.namespace
            assert result.dimensions == test_case.dimensions
            assert result.bin == test_case.vector_bin_name
            assert result.hnswParams.m == 16
            assert result.hnswParams.efConstruction == 100
            assert result.hnswParams.ef == 100
            assert result.hnswParams.batchingParams.maxRecords == 100000
            assert result.hnswParams.batchingParams.interval == 30000
            assert result.hnswParams.batchingParams.disabled == False
            assert result.aerospikeStorage.namespace == test_case.namespace
            assert result.aerospikeStorage.set == test_case.name
    assert found == True

@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            name="index_8",
            vector_bin_name="example_8",
            dimensions=1024,
            vector_distance_metric=None,
            sets="Demo",
            index_params=None,
            labels=None,
        ),
        index_create_test_case(
            namespace="test",
            name="index_9",
            vector_bin_name="example_9",
            dimensions=1024,
            vector_distance_metric=None,
            sets="Cheese",
            index_params=None,
            labels=None,
        ),
    ],
)
async def test_index_create_with_sets(session_admin_client, test_case):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_bin_name=test_case.vector_bin_name,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        labels=test_case.labels,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result.id.name == test_case.name:
            found = True
            assert result.id.namespace == test_case.namespace
            assert result.dimensions == test_case.dimensions
            assert result.bin == test_case.vector_bin_name
            assert result.hnswParams.m == 16
            assert result.hnswParams.efConstruction == 100
            assert result.hnswParams.ef == 100
            assert result.hnswParams.batchingParams.maxRecords == 100000
            assert result.hnswParams.batchingParams.interval == 30000
            assert result.hnswParams.batchingParams.disabled == False
            assert result.aerospikeStorage.namespace == test_case.namespace
            assert result.aerospikeStorage.set == test_case.name
    assert found == True

@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            name="index_10",
            vector_bin_name="example_10",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                m=32,
                ef_construction=200,
                ef=400,
            ),
            labels=None,
        ),
        index_create_test_case(
            namespace="test",
            name="index_11",
            vector_bin_name="example_11",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                m=8,
                ef_construction=50,
                ef=25,
            ),
            labels=None,
        ),
        index_create_test_case(
            namespace="test",
            name="index_12",
            vector_bin_name="example_12",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                batching_params=types.HnswBatchingParams(
                    max_records=500, interval=500, disabled=True
                )
            ),
            labels=None,
        ),
    ],
)
async def test_index_create_with_index_params(session_admin_client, test_case):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_bin_name=test_case.vector_bin_name,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        labels=test_case.labels,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result.id.name == test_case.name:
            found = True
            assert result.id.namespace == test_case.namespace
            assert result.dimensions == test_case.dimensions
            assert result.bin == test_case.vector_bin_name
            assert result.hnswParams.m == test_case.index_params.m
            assert result.hnswParams.efConstruction == test_case.index_params.ef_construction
            assert result.hnswParams.ef == test_case.index_params.ef
            assert result.hnswParams.batchingParams.maxRecords == test_case.index_params.batching_params.max_records
            assert result.hnswParams.batchingParams.interval == test_case.index_params.batching_params.interval
            assert result.hnswParams.batchingParams.disabled == test_case.index_params.batching_params.disabled
            assert result.aerospikeStorage.namespace == test_case.namespace
            assert result.aerospikeStorage.set == test_case.name
    assert found == True

@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            name="index_13",
            vector_bin_name="example_13",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            labels={"size": "large", "price": "$4.99", "currencyType": "CAN"},
        ),
    ],
)
async def test_index_create_labels(session_admin_client, test_case):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_bin_name=test_case.vector_bin_name,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        labels=test_case.labels,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result.id.name == test_case.name:
            found = True
            assert result.id.namespace == test_case.namespace
            assert result.dimensions == test_case.dimensions
            assert result.bin == test_case.vector_bin_name
            assert result.hnswParams.m == 16
            assert result.hnswParams.efConstruction == 100
            assert result.hnswParams.ef == 100
            assert result.hnswParams.batchingParams.maxRecords == 100000
            assert result.hnswParams.batchingParams.interval == 30000
            assert result.hnswParams.batchingParams.disabled == False
            assert result.aerospikeStorage.namespace == test_case.namespace
            assert result.aerospikeStorage.set == test_case.name
    assert found == True