import pytest
from aerospike_vector_search import AVSServerError
import grpc

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

def test_index_get_status_timeout(session_admin_client):
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):
            result = session_admin_client.index_get_status(
                namespace="test", name="index_get_status_1", timeout=0
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
