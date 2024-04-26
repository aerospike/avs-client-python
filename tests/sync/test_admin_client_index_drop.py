import pytest

@pytest.fixture
def add_index(function_admin_client):
    function_admin_client.index_create(
        namespace="test",
        name="index_drop_1",
        vector_field="art",
        dimensions=1024,
    )

def test_index_drop(add_index, session_admin_client):
    session_admin_client.index_drop(namespace="test", name="index_drop_1")

    result = session_admin_client.index_list()
    result = result
    for index in result:
        assert index["id"]["name"] != "index_drop_1"
