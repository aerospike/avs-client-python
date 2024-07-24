import pytest

from aerospike_vector_search import AVSServerError
import grpc

from ...utils import random_name


from hypothesis import given, settings, Verbosity


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
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


@pytest.mark.parametrize("empty_test_case", [None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
def test_index_drop_timeout(
    session_admin_client, empty_test_case, random_name, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

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

    for i in range(10):
        try:
            session_admin_client.index_drop(
                namespace="test", name=random_name, timeout=0.0001
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
