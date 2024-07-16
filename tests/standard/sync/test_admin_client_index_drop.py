import pytest

from aerospike_vector_search import AVSServerError
import grpc

from ...utils import index_strategy

from hypothesis import given, settings, Verbosity




@pytest.mark.parametrize("empty_test_case",[None])
@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
def test_index_drop(session_admin_client, empty_test_case, random_name):
    try:

        session_admin_client.index_create(
            namespace="test",
            name=random_name,
            vector_field="art",
            dimensions=1024,
        )

    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.ALREADY_EXISTS:
            raise se

    session_admin_client.index_drop(namespace="test", name=random_name)

    result = session_admin_client.index_list()
    result = result
    for index in result:
        assert index["id"]["name"] != random_name

@pytest.mark.parametrize("empty_test_case",[None])
@given(random_name=index_strategy())
@settings(max_examples=1, deadline=1000)
def test_index_drop_timeout(session_admin_client, empty_test_case, random_name):
    try:
        session_admin_client.index_create(
            namespace="test",
            name=random_name,
            vector_field="art",
            dimensions=1024,
        )
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.ALREADY_EXISTS:
            raise se

    with pytest.raises(AVSServerError) as e_info:
        for i in range(10): 
            session_admin_client.index_drop(namespace="test", name=random_name, timeout=0)

    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED