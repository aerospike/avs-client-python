import pytest
from aerospike_vector_search import types, AVSServerError
import grpc

from ...utils import random_name

from .aio_utils import drop_specified_index
from hypothesis import given, settings, Verbosity, Phase

server_defaults = {
    "m": 16,
    "ef_construction": 100,
    "ef": 100,
    "batching_params": {
        "max_index_records": 10000,
        "index_interval": 10000,
    }
}

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
        index_labels,
        index_storage,
        timeout
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
        self.index_labels = index_labels
        self.index_storage = index_storage
        self.timeout = timeout


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000, phases=(Phase.generate,))
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
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
    ],
)
async def test_index_create(session_admin_client, test_case, random_name):
    if test_case == None:
        return
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_labels=test_case.index_labels,
        index_storage=test_case.index_storage,
        timeout=test_case.timeout,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert result["field"] == test_case.vector_field
            assert result["hnsw_params"]["m"] == 16
            assert result["hnsw_params"]["ef_construction"] == 100
            assert result["hnsw_params"]["ef"] == 100
            assert result["hnsw_params"]["batching_params"]["max_index_records"] == 100000
            assert result["hnsw_params"]["batching_params"]["index_interval"] == 30000
            assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == max(100000 / 10, 1000)
            assert result["hnsw_params"]["batching_params"]["reindex_interval"] == 30000
            assert result["storage"]["namespace"] == test_case.namespace
            assert result["storage"]["set_name"] == random_name
    assert found == True
    await drop_specified_index(session_admin_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000, phases=(Phase.generate,))
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
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_3",
            dimensions=2048,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
    ],
)
async def test_index_create_with_dimnesions(
    session_admin_client, test_case, random_name
):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_labels=test_case.index_labels,
        index_storage=test_case.index_storage,
        timeout=test_case.timeout,
    )

    results = await session_admin_client.index_list()

    found = False
    for result in results:

        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert result["field"] == test_case.vector_field
            assert result["hnsw_params"]["m"] == 16
            assert result["hnsw_params"]["ef_construction"] == 100
            assert result["hnsw_params"]["ef"] == 100
            assert result["hnsw_params"]["batching_params"]["max_index_records"] == 100000
            assert result["hnsw_params"]["batching_params"]["index_interval"] == 30000
            assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == max(100000 / 10, 1000)
            assert result["hnsw_params"]["batching_params"]["reindex_interval"] == 30000
            assert result["storage"]["namespace"] == test_case.namespace
            assert result["storage"]["set_name"] == random_name
    assert found == True

    await drop_specified_index(session_admin_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000, phases=(Phase.generate,))
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
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_5",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.DOT_PRODUCT,
            sets=None,
            index_params=None,
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_6",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.MANHATTAN,
            sets=None,
            index_params=None,
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_7",
            dimensions=1024,
            vector_distance_metric=types.VectorDistanceMetric.HAMMING,
            sets=None,
            index_params=None,
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
    ],
)
async def test_index_create_with_vector_distance_metric(
    session_admin_client, test_case, random_name
):

    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_labels=test_case.index_labels,
        index_storage=test_case.index_storage,
        timeout=test_case.timeout,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert result["field"] == test_case.vector_field
            assert result["hnsw_params"]["m"] == 16
            assert result["hnsw_params"]["ef_construction"] == 100
            assert result["hnsw_params"]["ef"] == 100
            assert result["hnsw_params"]["batching_params"]["max_index_records"] == 100000
            assert result["hnsw_params"]["batching_params"]["index_interval"] == 30000
            assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == max(100000 / 10, 1000)
            assert result["hnsw_params"]["batching_params"]["reindex_interval"] == 30000
            assert result["storage"]["namespace"] == test_case.namespace
            assert result["storage"]["set_name"] == random_name
    assert found == True
    await drop_specified_index(session_admin_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000, phases=(Phase.generate,))
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
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_9",
            dimensions=1024,
            vector_distance_metric=None,
            sets="Cheese",
            index_params=None,
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
    ],
)
async def test_index_create_with_sets(session_admin_client, test_case, random_name):

    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_labels=test_case.index_labels,
        index_storage=test_case.index_storage,
        timeout=test_case.timeout,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert result["field"] == test_case.vector_field
            assert result["hnsw_params"]["m"] == 16
            assert result["hnsw_params"]["ef_construction"] == 100
            assert result["hnsw_params"]["ef"] == 100
            assert result["hnsw_params"]["batching_params"]["max_index_records"] == 100000
            assert result["hnsw_params"]["batching_params"]["index_interval"] == 30000
            assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == max(100000 / 10, 1000)
            assert result["hnsw_params"]["batching_params"]["reindex_interval"] == 30000
            assert result["storage"]["namespace"] == test_case.namespace
            assert result["storage"]["set_name"] == random_name
    assert found == True
    await drop_specified_index(session_admin_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000, phases=(Phase.generate,))
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
                enable_vector_integrity_check= False,
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
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
                enable_vector_integrity_check= True
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_12",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                m=8,
                enable_vector_integrity_check= True,
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_13",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                batching_params=types.HnswBatchingParams(max_index_records=2000, index_interval=20000, max_reindex_records=1500, reindex_interval=70000),
                enable_vector_integrity_check= True
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace="test",
            vector_field="example_20",
            dimensions=1024,
            vector_distance_metric=None,
            sets="demo",
            index_params=types.HnswParams(
                index_caching_params=types.HnswCachingParams(max_entries=10, expiry=3000),
                healer_params=types.HnswHealerParams(
                    max_scan_rate_per_node=80,
                    max_scan_page_size=40,
                    re_index_percent=50,
                    schedule="* 0/5 * ? * * *",
                    parallelism=4,
                ),
                merge_params=types.HnswIndexMergeParams(
                    index_parallelism=10,
                    reindex_parallelism=3
                ),
                enable_vector_integrity_check= True
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
    ],
)
async def test_index_create_with_index_params(
    session_admin_client, test_case, random_name
):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_labels=test_case.index_labels,
        index_storage=test_case.index_storage,
        timeout=test_case.timeout,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert result["field"] == test_case.vector_field
            assert result["hnsw_params"]["m"] == test_case.index_params.m or server_defaults
            assert (
                result["hnsw_params"]["ef_construction"]
                == test_case.index_params.ef_construction or server_defaults
            )
            assert result["hnsw_params"]["ef"] == test_case.index_params.ef or server_defaults
            assert result["hnsw_params"][
                       "enable_vector_integrity_check"] == test_case.index_params.enable_vector_integrity_check
            assert (
                    result["hnsw_params"]["batching_params"]["max_index_records"]
                    == test_case.index_params.batching_params.max_index_records or server_defaults
            )
            assert (
                    result["hnsw_params"]["batching_params"]["index_interval"]
                    == test_case.index_params.batching_params.index_interval or server_defaults
            )
            assert (
                   result["hnsw_params"]["batching_params"]["max_reindex_records"]
                   == test_case.index_params.batching_params.max_reindex_records or server_defaults
            )

            assert (
                   result["hnsw_params"]["batching_params"]["reindex_interval"]
                   == test_case.index_params.batching_params.reindex_interval or server_defaults
            )

            assert result["storage"]["namespace"] == test_case.namespace
            assert result["storage"]["set_name"] == random_name
    assert found == True
    await drop_specified_index(session_admin_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000, phases=(Phase.generate,))
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_14",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_labels={"size": "large", "price": "$4.99", "currencyType": "CAN"},
            index_storage=None,
            timeout=None,
        ),
    ],
)
async def test_index_create_index_labels(session_admin_client, test_case, random_name):
    if test_case == None:
        return
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_labels=test_case.index_labels,
        index_storage=test_case.index_storage,
        timeout=test_case.timeout,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert result["field"] == test_case.vector_field
            assert result["hnsw_params"]["m"] == 16
            assert result["hnsw_params"]["ef_construction"] == 100
            assert result["hnsw_params"]["ef"] == 100
            assert result["hnsw_params"]["batching_params"]["max_index_records"] == 100000
            assert result["hnsw_params"]["batching_params"]["index_interval"] == 30000
            assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == max(100000 / 10, 1000)
            assert result["hnsw_params"]["batching_params"]["reindex_interval"] == 30000
            assert result["storage"]["namespace"] == test_case.namespace
            assert result["storage"]["set_name"] == random_name
    assert found == True
    await drop_specified_index(session_admin_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000, phases=(Phase.generate,))
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_15",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_labels=None,
            index_storage=types.IndexStorage(namespace="test", set_name="foo"),
            timeout=None,
        ),
    ],
)
async def test_index_create_index_storage(session_admin_client, test_case, random_name):
    await session_admin_client.index_create(
        namespace=test_case.namespace,
        name=random_name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
        vector_distance_metric=test_case.vector_distance_metric,
        sets=test_case.sets,
        index_params=test_case.index_params,
        index_labels=test_case.index_labels,
        index_storage=test_case.index_storage,
        timeout=test_case.timeout,
    )
    results = await session_admin_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert result["field"] == test_case.vector_field
            assert result["hnsw_params"]["m"] == 16
            assert result["hnsw_params"]["ef_construction"] == 100
            assert result["hnsw_params"]["ef"] == 100
            assert result["hnsw_params"]["batching_params"]["max_index_records"] == 100000
            assert result["hnsw_params"]["batching_params"]["index_interval"] == 30000
            assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == max(100000 / 10, 1000)
            assert result["hnsw_params"]["batching_params"]["reindex_interval"] == 30000
            assert result["storage"]["namespace"] == test_case.index_storage.namespace
            assert result["storage"]["set_name"] == test_case.index_storage.set_name
    assert found == True


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000, phases=(Phase.generate,))
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace="test",
            vector_field="example_16",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_labels=None,
            index_storage=None,
            timeout=0.0001,
        ),
    ],
)
async def test_index_create_timeout(
    session_admin_client, test_case, random_name, with_latency
):

    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):

            await session_admin_client.index_create(
                namespace=test_case.namespace,
                name=random_name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
                vector_distance_metric=test_case.vector_distance_metric,
                sets=test_case.sets,
                index_params=test_case.index_params,
                index_labels=test_case.index_labels,
                index_storage=test_case.index_storage,
                timeout=test_case.timeout,
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
