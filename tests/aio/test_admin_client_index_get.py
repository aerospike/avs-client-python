import pytest
from aerospike_vector_search import AVSServerError
import grpc

@pytest.fixture
async def add_index(function_admin_client):
    await function_admin_client.index_create(
        namespace="test",
        name="index_get_1",
        vector_field="science",
        dimensions=1024,
    )


async def test_index_get(add_index, session_admin_client):
    result = await session_admin_client.index_get(
        namespace="test", name="index_get_1"
    )
    
    assert result["id"]["name"] == "index_get_1"
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
    assert result["storage"]["set"] == "index_get_1"

async def test_index_get_timeout(session_admin_client):
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10): 
            result = await session_admin_client.index_get(
                namespace="test", name="index_get_1", timeout=0
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
