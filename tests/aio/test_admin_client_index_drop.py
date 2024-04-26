import pytest

@pytest.fixture
async def add_index(function_admin_client):
    await function_admin_client.index_create(
        namespace="test",
        name="index_drop_1",
        vector_field="art",
        dimensions=1024,
    )

async def test_index_drop(add_index, session_admin_client):
    await session_admin_client.index_drop(namespace="test", name="index_drop_1")

    result = session_admin_client.index_list()
    result = await result
    for index in result:
        assert index["id"]["name"] != "index_drop_1"
