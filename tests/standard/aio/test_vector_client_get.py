import pytest
import grpc

from aerospike_vector_search import AVSServerError
from utils import DEFAULT_NAMESPACE, random_key

from hypothesis import given, settings, Verbosity


class get_test_case:
    def __init__(
        self,
        *,
        namespace,
        include_fields,
        exclude_fields,
        set_name,
        expected_fields,
        timeout,
    ):
        self.namespace = namespace
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields
        self.set_name = set_name
        self.expected_fields = expected_fields
        self.timeout = timeout


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "record,test_case",
    [
        (
            {"record_generator": lambda count, vec_bin, vec_dim: (yield ("key1", {"skills": 1024}))},
            get_test_case(
                namespace=DEFAULT_NAMESPACE,
                include_fields=["skills"],
                exclude_fields = None,
                set_name=None,
                expected_fields={"skills": 1024},
                timeout=None,
            ),
        ),
        (
            {"record_generator": lambda count, vec_bin, vec_dim: (yield ("key1", {"english": [float(i) for i in range(1024)]}))},
            get_test_case(
                namespace=DEFAULT_NAMESPACE,
                include_fields=["english"],
                exclude_fields = None,
                set_name=None,
                expected_fields={"english": [float(i) for i in range(1024)]},
                timeout=None,
            ),
        ),
        (   
            {"record_generator": lambda count, vec_bin, vec_dim: (yield ("key1", {"english": 1, "spanish": 2}))},
            get_test_case(
                namespace=DEFAULT_NAMESPACE,
                include_fields=["english"],
                exclude_fields = None,
                set_name=None,
                expected_fields={"english": 1},
                timeout=None,
            ),
        ),
        (
            {"record_generator": lambda count, vec_bin, vec_dim: (yield ("key1", {"english": 1, "spanish": 2}))},
            get_test_case(
                namespace=DEFAULT_NAMESPACE,
                include_fields=None,
                exclude_fields=["spanish"],
                set_name=None,
                expected_fields={"english": 1},
                timeout=None,
            ),
        ),
        (
            {"record_generator": lambda count, vec_bin, vec_dim: (yield ("key1", {"english": 1, "spanish": 2}))},
            get_test_case(
                namespace=DEFAULT_NAMESPACE,
                include_fields=["spanish"],
                exclude_fields=["spanish"],
                set_name=None,
                expected_fields={},
                timeout=None,
            ),
        ),
        (
            {"record_generator": lambda count, vec_bin, vec_dim: (yield ("key1", {"english": 1, "spanish": 2}))},
            get_test_case(
                namespace=DEFAULT_NAMESPACE,
                include_fields=[],
                exclude_fields=None,
                set_name=None,
                expected_fields={},
                timeout=None,
            ),
        ),
        (
            {"record_generator": lambda count, vec_bin, vec_dim: (yield ("key1", {"english": 1, "spanish": 2}))},
            get_test_case(
                namespace=DEFAULT_NAMESPACE,
                include_fields=None,
                exclude_fields=[],
                set_name=None,
                expected_fields={"english": 1, "spanish": 2},
                timeout=None,
            ),
        ),
    ],
    indirect=["record"],
)
async def test_vector_get(session_vector_client, test_case, record):
    result = await session_vector_client.get(
        namespace=test_case.namespace,
        key=record,
        include_fields=test_case.include_fields,
        exclude_fields=test_case.exclude_fields,
    )
    assert result.key.namespace == test_case.namespace
    if test_case.set_name == None:
        test_case.set_name = ""
    assert result.key.set == test_case.set_name
    assert result.key.key == record

    assert result.fields == test_case.expected_fields


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        get_test_case(
            namespace="test",
            include_fields=["skills"],
            exclude_fields = None,
            set_name=None,
            expected_fields=None,
            timeout=0.0001,
        ),
    ],
)
async def test_vector_get_timeout(
    session_vector_client, test_case, random_key, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):
            result = await session_vector_client.get(
                namespace=test_case.namespace,
                key=random_key,
                include_fields=test_case.include_fields,
                exclude_fields=test_case.exclude_fields,
                timeout=test_case.timeout,
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
