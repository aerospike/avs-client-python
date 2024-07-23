import pytest
from ...utils import index_strategy
from .aio_utils import drop_specified_index
from hypothesis import given, settings, Verbosity

from aerospike_vector_search import types, AVSServerError
import grpc


@pytest.mark.parametrize("empty_test_case", [None, None])
@given(random_name=index_strategy())
@settings(max_examples=1, deadline=1000)
async def test_index_get_status(session_admin_client, empty_test_case, random_name):
    try:
        await session_admin_client.index_create(
            namespace="test",
            name=random_name,
            vector_field="science",
            dimensions=1024,
        )
    except Exception as e:
        pass

    result = await session_admin_client.index_get_status(
        namespace="test", name=random_name
    )
    assert result == 0
    await drop_specified_index(session_admin_client, "test", random_name)


@pytest.mark.parametrize("empty_test_case", [None, None])
@given(random_name=index_strategy())
@settings(max_examples=1, deadline=1000)
async def test_index_get_status_timeout(
    session_admin_client, empty_test_case, random_name, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    try:
        await session_admin_client.index_create(
            namespace="test",
            name=random_name,
            vector_field="science",
            dimensions=1024,
        )
    except Exception as e:
        pass

    for i in range(10):
        try:
            result = await session_admin_client.index_get_status(
                namespace="test", name=random_name, timeout=0.0001
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
