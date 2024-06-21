import pytest
from ...utils import index_strategy
from .sync_utils import drop_specified_index
from hypothesis import given, settings, Verbosity




@pytest.mark.parametrize("empty_test_case",[None])
@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
def test_index_get(session_admin_client, empty_test_case, random_name):
    session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="science",
        dimensions=1024,
    )
    result = session_admin_client.index_get(
        namespace="test", name=random_name
    )
    
    assert result["id"]["name"] == random_name
    assert result["id"]["namespace"] == "test"
    assert result["dimensions"] == 1024
    assert result['field'] == "science"
    assert result["hnsw_params"]["m"] == 16
    assert result["hnsw_params"]["ef_construction"] == 100
    assert result["hnsw_params"]["ef"] == 100
    assert result["hnsw_params"]["batching_params"]["max_records"] == 100000
    assert result["hnsw_params"]["batching_params"]["interval"] == 30000
    assert not result["hnsw_params"]["batching_params"]["disabled"]
    assert result["storage"]["namespace"] == "test"
    assert result["storage"]["set"] == random_name

    drop_specified_index(session_admin_client, "test", random_name)
