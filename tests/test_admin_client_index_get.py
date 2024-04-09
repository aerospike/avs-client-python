import pytest

@pytest.fixture
async def add_index(function_admin_client):
    await function_admin_client.index_create(
        namespace="test",
        name="index_get_1",
        vector_bin_name="science",
        dimensions=1024,
    )


async def test_index_get(add_index, session_admin_client):
    result = await session_admin_client.index_get(
        namespace="test", name="index_get_1"
    )
    
    assert result["id"]["name"] == "index_get_1"
    assert result["id"]["namespace"] == "test"
    assert result["dimensions"] == 1024
    assert result["bin"] == "science"
    assert result["hnswParams"]["m"] == 16
    assert result["hnswParams"]["efConstruction"] == 100
    assert result["hnswParams"]["ef"] == 100
    assert result["hnswParams"]["batchingParams"]["maxRecords"] == 100000
    assert result["hnswParams"]["batchingParams"]["interval"] == 30000
    assert not result["hnswParams"]["batchingParams"]["disabled"]
    assert result["aerospikeStorage"]["namespace"] == "test"
    assert result["aerospikeStorage"]["set"] == "index_get_1"