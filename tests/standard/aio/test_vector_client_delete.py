import pytest
from aerospike_vector_search import AVSServerError
from utils import DEFAULT_NAMESPACE

from hypothesis import given, settings, Verbosity
import grpc


class delete_test_case:
    def __init__(
        self,
        *,
        namespace,
        set_name,
        timeout,
    ):
        self.namespace = namespace
        self.set_name = set_name
        self.timeout = timeout


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        delete_test_case(
            namespace=DEFAULT_NAMESPACE,
            set_name=None,
            timeout=None,
        ),
        delete_test_case(
            namespace=DEFAULT_NAMESPACE,
            set_name=None,
            timeout=None,
        ),
    ],
)
async def test_vector_delete(session_vector_client, test_case, record):
    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=record,
        set_name=test_case.set_name,
        timeout=test_case.timeout,
    )
    with pytest.raises(AVSServerError) as e_info:
        result = await session_vector_client.get(
            namespace=test_case.namespace, key=record
        )


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        delete_test_case(
            namespace=DEFAULT_NAMESPACE,
            set_name=None,
            timeout=None,
        ),
    ],
)
async def test_vector_delete_without_record(
    session_vector_client, test_case, record
):
    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=record,
    )


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        delete_test_case(
            namespace=DEFAULT_NAMESPACE,
            set_name=None,
            timeout=0.0001,
        ),
    ],
)
async def test_vector_delete_timeout(
    session_vector_client, test_case, record, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):

            await session_vector_client.delete(
                namespace=test_case.namespace, key=record, timeout=test_case.timeout
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
