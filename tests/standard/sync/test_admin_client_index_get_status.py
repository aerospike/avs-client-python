import pytest

@pytest.fixture
def add_index(function_admin_client):
    function_admin_client.index_create(
        namespace="test",
        name="index_get_status_1",
        vector_field="science",
        dimensions=1024,
    )


def test_index_get_status(add_index, session_admin_client):
    result = session_admin_client.index_get_status(
        namespace="test", name="index_get_status_1"
    )
    assert result == 0
