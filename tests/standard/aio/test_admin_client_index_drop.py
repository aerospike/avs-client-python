import pytest
from aerospike_vector_search import AVSServerError
import grpc

from ...utils import random_name


from hypothesis import given, settings, Verbosity


@pytest.mark.parametrize("empty_test_case", [None, None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=2000)
async def test_index_drop(session_admin_client, empty_test_case, random_name):
    await session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="art",
        dimensions=1024,
    )
    await session_admin_client.index_drop(namespace="test", name=random_name)

    result = session_admin_client.index_list()
    result = await result
    for index in result:
        assert index["id"]["name"] != random_name


@pytest.mark.parametrize("empty_test_case", [None, None])
#@given(random_name=index_strategy())
#@settings(max_examples=1, deadline=1000)
async def test_index_drop_timeout(
    session_admin_client, empty_test_case, random_name, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    await session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="art",
        dimensions=1024,
    )
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):

            await session_admin_client.index_drop(
                namespace="test", name=random_name, timeout=0.0001
            )

    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
