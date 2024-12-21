import pytest
from aerospike_vector_search import AVSServerError
import grpc

from utils import DEFAULT_NAMESPACE


from hypothesis import given, settings, Verbosity


@pytest.mark.parametrize("empty_test_case", [None, None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=2000)
async def test_index_drop(session_admin_client, empty_test_case, index):
    await session_admin_client.index_drop(namespace=DEFAULT_NAMESPACE, name=index)

    result = session_admin_client.index_list()
    result = await result
    for index in result:
        assert index["id"]["name"] != index


@pytest.mark.parametrize("empty_test_case", [None, None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
async def test_index_drop_timeout(
    session_admin_client, empty_test_case, index, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):

            await session_admin_client.index_drop(
                namespace=DEFAULT_NAMESPACE, name=index, timeout=0.0001
            )

    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
