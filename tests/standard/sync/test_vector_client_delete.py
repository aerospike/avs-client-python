import pytest

import grpc

from aerospike_vector_search import AVSServerError
from utils import random_key, DEFAULT_NAMESPACE

from hypothesis import given, settings, Verbosity


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
def test_vector_delete(session_vector_client, test_case, record):
    session_vector_client.delete(
        namespace=test_case.namespace,
        key=record,
    )
    with pytest.raises(AVSServerError) as e_info:
        result = session_vector_client.get(
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
def test_vector_delete_without_record(session_vector_client, test_case, random_key):
    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        delete_test_case(
            namespace=DEFAULT_NAMESPACE,
            set_name=None,
            timeout=0.0001,
        ),
    ],
)
def test_vector_delete_timeout(
    session_vector_client, test_case, record, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):
        try:
            session_vector_client.delete(
                namespace=test_case.namespace, key=record, timeout=test_case.timeout
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
