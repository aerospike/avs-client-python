import pytest
from aerospike_vector_search import AVSServerError
from ...utils import key_strategy
from hypothesis import given, settings, Verbosity
import grpc


class delete_test_case:
    def __init__(
        self,
        *,
        namespace,
        record_data,
        set_name,
        timeout,
    ):
        self.namespace = namespace
        self.set_name = set_name
        self.record_data = record_data
        self.timeout = timeout


@given(random_key=key_strategy())
@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        delete_test_case(
            namespace="test",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
            timeout=None,
        ),
        delete_test_case(
            namespace="test",
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
            timeout=None,
        ),
    ],
)
async def test_vector_delete(session_vector_client, test_case, random_key):
    await session_vector_client.upsert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name,
    )
    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )
    with pytest.raises(AVSServerError) as e_info:
        result = await session_vector_client.get(
            namespace=test_case.namespace, key=random_key
        )


@given(random_key=key_strategy())
@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        delete_test_case(
            namespace="test",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
            timeout=None,
        ),
    ],
)
async def test_vector_delete_without_record(
    session_vector_client, test_case, random_key
):
    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )


@given(random_key=key_strategy())
@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        delete_test_case(
            namespace="test",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
            timeout=0.0001,
        ),
    ],
)
async def test_vector_delete_timeout(
    session_vector_client, test_case, random_key, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):

            await session_vector_client.delete(
                namespace=test_case.namespace, key=random_key, timeout=test_case.timeout
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
