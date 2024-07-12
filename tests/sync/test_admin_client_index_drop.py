import pytest
from aerospike_vector_search import AVSServerError
import grpc
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

def test_index_drop_timeout(add_index, session_admin_client):
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):
            session_admin_client.index_drop(namespace="test", name="index_drop_1", timeout=0)

    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
    
