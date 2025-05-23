import pytest
import grpc

from aerospike_vector_search import types, AVSServerError
from utils import random_name, drop_specified_index, DEFAULT_NAMESPACE

from hypothesis import given, settings, Verbosity

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
        timeout,
        mode=None,
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
        self.mode = mode


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_1",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_labels=None,
            index_storage=None,
            timeout=None,
        )
    ],
)
def test_index_create(session_vector_client, test_case, random_name):
    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass

    session_vector_client.index_create(
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

    results = session_vector_client.index_list()
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
            assert result["hnsw_params"]["batching_params"]["max_reindex_records"] == max(100000/10, 1000)
            assert result["hnsw_params"]["batching_params"]["reindex_interval"] == 30000
            assert result["storage"]["namespace"] == test_case.namespace
            assert result["storage"]["set_name"] == random_name
    assert found == True
    drop_specified_index(session_vector_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
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
            namespace=DEFAULT_NAMESPACE,
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
def test_index_create_with_dimnesions(session_vector_client, test_case, random_name):

    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass

    session_vector_client.index_create(
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

    results = session_vector_client.index_list()

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

    drop_specified_index(session_vector_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
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
            namespace=DEFAULT_NAMESPACE,
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
            namespace=DEFAULT_NAMESPACE,
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
            namespace=DEFAULT_NAMESPACE,
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
def test_index_create_with_vector_distance_metric(
    session_vector_client, test_case, random_name
):

    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass

    session_vector_client.index_create(
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
    results = session_vector_client.index_list()
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
    drop_specified_index(session_vector_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
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
            namespace=DEFAULT_NAMESPACE,
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
def test_index_create_with_sets(session_vector_client, test_case, random_name):

    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass

    session_vector_client.index_create(
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
    results = session_vector_client.index_list()
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
    drop_specified_index(session_vector_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_10",
            dimensions=1024,
            vector_distance_metric=None,
            sets="demo",
            index_params=types.HnswParams(
                m=32,
                ef_construction=200,
                ef=400,
                enable_vector_integrity_check = False,
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_11",
            dimensions=1024,
            vector_distance_metric=None,
            sets="demo",
            index_params=types.HnswParams(
                m=8, ef_construction=50, ef=25, max_mem_queue_size=16384, enable_vector_integrity_check = True,
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_20",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=types.HnswParams(
                m=8, enable_vector_integrity_check= True,
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_12",
            dimensions=1024,
            vector_distance_metric=None,
            sets="demo",
            index_params=types.HnswParams(
                batching_params=types.HnswBatchingParams(max_index_records=2000, index_interval=20000, max_reindex_records=1500, reindex_interval=70000),
                enable_vector_integrity_check= True
            ),
            index_labels=None,
            index_storage=None,
            timeout=None,
        ),
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_13",
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
def test_index_create_with_index_params(session_vector_client, test_case, random_name):
    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass
    session_vector_client.index_create(
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

    results = session_vector_client.index_list()
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
                == test_case.index_params.ef_construction  or server_defaults
            )
            assert result["hnsw_params"]["ef"] == test_case.index_params.ef or server_defaults
            if getattr(result.hnsw_params, 'max_mem_queue_size', None) is not None:
                assert (
                    result["hnsw_params"]["max_mem_queue_size"]
                    == test_case.index_params.max_mem_queue_size or server_defaults
                )

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

            assert result["hnsw_params"][
                       "enable_vector_integrity_check"] == test_case.index_params.enable_vector_integrity_check or server_defaults
            """
            if getattr(result.hnsw_params, 'index_caching_params', None) is not None:

                assert (
                    int(result["hnsw_params"]["index_caching_params"]["max_entries"])
                    == test_case.index_params.index_caching_params.max_entries
                )
                assert (
                    int(result["hnsw_params"]["index_caching_params"]["expiry"])
                    == test_case.index_params.index_caching_params.expiry
                )
            if getattr(result.hnsw_params, 'merge_params', None) is not None:
                assert (
                    result["hnsw_params"]["merge_params"]["index_parallelism"]
                    == test_case.index_params.merge_params.index_parallelism
                )
                assert (
                    result["hnsw_params"]["merge_params"]["reindex_parallelism"]
                    == test_case.index_params.merge_params.reindex_parallelism
                )
            if getattr(result.hnsw_params, 'healer_params', None) is not None:
                assert (
                    int(
                        result["hnsw_params"]["healer_params"]["max_scan_rate_per_node"]
                    )
                    == test_case.index_params.healer_params.max_scan_rate_per_node
                )
                assert (
                    int(result["hnsw_params"]["healer_params"]["max_scan_page_size"])
                    == test_case.index_params.healer_params.max_scan_page_size
                )
                assert (
                    int(result["hnsw_params"]["healer_params"]["re_index_percent"])
                    == test_case.index_params.healer_params.re_index_percent
                )
                assert (
                    result["hnsw_params"]["healer_params"]["schedule"]
                    == test_case.index_params.healer_params.schedule
                )
                assert (
                    result["hnsw_params"]["healer_params"]["parallelism"]
                    == test_case.index_params.healer_params.parallelism
                )
            """
            assert result["storage"]["namespace"] == test_case.namespace
            assert result["storage"]["set_name"] == random_name
    assert found == True
    drop_specified_index(session_vector_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_16",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_labels={"size": "large", "price": "$4.99", "currencyType": "CAN"},
            index_storage=None,
            timeout=None,
        )
    ],
)
def test_index_create_index_labels(session_vector_client, test_case, random_name):
    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass
    session_vector_client.index_create(
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

    results = session_vector_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert result["field"] == test_case.vector_field
            assert isinstance(result["field"], str)

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
    drop_specified_index(session_vector_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_17",
            dimensions=1024,
            vector_distance_metric=None,
            sets=None,
            index_params=None,
            index_labels=None,
            index_storage=types.IndexStorage(namespace=DEFAULT_NAMESPACE, set_name="foo"),
            timeout=None,
        ),
    ],
)
def test_index_create_index_storage(session_vector_client, test_case, random_name):
    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass
    session_vector_client.index_create(
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

    results = session_vector_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["id"]["namespace"] == test_case.namespace
            assert result["dimensions"] == test_case.dimensions
            assert isinstance(result["field"], str)
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


@pytest.mark.parametrize(
    "test_case, expected",
    [
        (
            index_create_test_case(
                namespace=DEFAULT_NAMESPACE,
                vector_field="standalone",
                dimensions=1024,
                vector_distance_metric=None,
                sets=None,
                index_params=None,
                index_labels=None,
                index_storage=None,
                timeout=None,
                mode=types.IndexMode.STANDALONE,
            ),
            types.IndexMode.STANDALONE,
        ),
        (
            index_create_test_case(
                namespace=DEFAULT_NAMESPACE,
                vector_field="distributed",
                dimensions=1024,
                vector_distance_metric=None,
                sets=None,
                index_params=None,
                index_labels=None,
                index_storage=None,
                timeout=None,
                mode=types.IndexMode.DISTRIBUTED,
            ),
            types.IndexMode.DISTRIBUTED,
        ),
        (
            index_create_test_case(
                namespace=DEFAULT_NAMESPACE,
                vector_field="mode_none",
                dimensions=1024,
                vector_distance_metric=None,
                sets=None,
                index_params=None,
                index_labels=None,
                index_storage=None,
                timeout=None,
                mode=None,
            ),
            types.IndexMode.DISTRIBUTED,
        )
    ],
)
def test_index_create_with_mode(
        session_vector_client, test_case, expected, random_name
):
    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass
    session_vector_client.index_create(
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
        mode=test_case.mode,
    )

    results = session_vector_client.index_list()
    found = False
    for result in results:
        if result["id"]["name"] == random_name:
            found = True
            assert result["mode"] == expected
    assert found == True
    drop_specified_index(session_vector_client, test_case.namespace, random_name)


#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        index_create_test_case(
            namespace=DEFAULT_NAMESPACE,
            vector_field="example_18",
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
def test_index_create_timeout(
    session_vector_client, test_case, random_name, with_latency
):

    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    try:
        session_vector_client.index_drop(namespace=DEFAULT_NAMESPACE, name=random_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass

    for i in range(10):
        try:
            session_vector_client.index_create(
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
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
