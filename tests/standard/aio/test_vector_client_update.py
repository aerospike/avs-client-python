import pytest
from aerospike_vector_search import AVSServerError
from ...utils import key_strategy
from hypothesis import given, settings, Verbosity
import grpc


class update_test_case:
    def __init__(
        self,
        *,
        namespace,
        record_data,
        set_name,
        timeout,
    ):
        self.namespace = namespace
        self.record_data = record_data
        self.set_name = set_name
        self.timeout = timeout


@given(random_key=key_strategy())
@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        update_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=None,
        ),
        update_test_case(
            namespace="test",
            record_data={"english": [float(i) for i in range(1024)]},
            set_name=None,
            timeout=None,
        ),
        update_test_case(
            namespace="test",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None,
            timeout=None,
        ),
    ],
)
async def test_vector_update_with_existing_record(
    session_vector_client, test_case, random_key
):
    try:
        await session_vector_client.insert(
            namespace=test_case.namespace,
            key=random_key,
            record_data=test_case.record_data,
            set_name=test_case.set_name,
        )
    except Exception as e:
        pass
    await session_vector_client.update(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name,
    )
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
        update_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=None,
        ),
    ],
)
async def test_vector_update_without_existing_record(
    session_vector_client, test_case, random_key
):
    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )
    with pytest.raises(AVSServerError) as e_info:
        await session_vector_client.update(
            namespace=test_case.namespace,
            key=random_key,
            record_data=test_case.record_data,
            set_name=test_case.set_name,
        )


@given(random_key=key_strategy())
@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        update_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=0.0001,
        ),
    ],
)
async def test_vector_update_timeout(
    session_vector_client, test_case, random_key, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):
            await session_vector_client.update(
                namespace=test_case.namespace,
                key=random_key,
                record_data=test_case.record_data,
                set_name=test_case.set_name,
                timeout=test_case.timeout,
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
