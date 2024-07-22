import pytest
import grpc

from ...utils import key_strategy
from hypothesis import given, settings, Verbosity
from aerospike_vector_search import types, AVSServerError

class exists_test_case:
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
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        exists_test_case(
            namespace="test",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
            timeout=None
        ),
        exists_test_case(
            namespace="test",
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
            timeout=None
        )
    ],
)
def test_vector_exists(session_vector_client, test_case, random_key):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name,
        timeout=None

    )
    result = session_vector_client.exists(
        namespace=test_case.namespace,
        key=random_key,
    )
    assert result is True
    
    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )

@given(random_key=key_strategy())
@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        exists_test_case(
            namespace="test",
            set_name=None,
            record_data=None,
            timeout=0.0001
        ),
    ],
)
def test_vector_exists_timeout(session_vector_client, test_case, random_key, with_latency):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")    

    for i in range(10):
        try:
            result = session_vector_client.exists(
                namespace=test_case.namespace,
                key=random_key,
                timeout=test_case.timeout
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return

    assert "In several attempts, the timeout did not happen" == "TEST FAIL"