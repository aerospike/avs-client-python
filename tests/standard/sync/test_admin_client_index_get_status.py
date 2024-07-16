import pytest
import grpc

from ...utils import index_strategy
from .sync_utils import drop_specified_index
from hypothesis import given, settings, Verbosity

from aerospike_vector_search import AVSServerError
import grpc

@pytest.mark.parametrize("empty_test_case",[None])
@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
def test_index_get_status(session_admin_client, empty_test_case, random_name):
    session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="science",
        dimensions=1024,
    )

    result = session_admin_client.index_get_status(
        namespace="test", name=random_name
    )

    assert result == 0
    drop_specified_index(session_admin_client, "test", random_name)

@pytest.mark.parametrize("empty_test_case",[None])
@given(random_name=index_strategy())
@settings(max_examples=1, deadline=1000)
def test_index_get_status_timeout(session_admin_client, empty_test_case, random_name):


    for i in range(10):
        try:
            result = session_admin_client.index_get_status(
                namespace="test", name=random_name, timeout=0
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return

    assert 1 == 2