import pytest
from utils import random_key

from hypothesis import given, settings, Verbosity

import numpy as np

from aerospike_vector_search import AVSServerError
import grpc


class upsert_test_case:
    def __init__(self, *, namespace, record_data, set_name, timeout, key=None):
        self.namespace = namespace
        self.record_data = record_data
        self.set_name = set_name
        self.timeout = timeout
        self.key = key


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        upsert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=None,
        ),
        upsert_test_case(
            namespace="test",
            record_data={"english": [float(i) for i in range(1024)]},
            set_name=None,
            timeout=None,
        ),
        upsert_test_case(
            namespace="test",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None,
            timeout=None,
        ),
    ],
)
def test_vector_upsert_without_existing_record(
    session_vector_client, test_case, random_key
):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name,
    )

    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        upsert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=None,
        )
    ],
)
def test_vector_upsert_with_existing_record(
    session_vector_client, test_case, random_key
):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name,
    )

    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )


@pytest.mark.parametrize(
    "test_case",
    [
        upsert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=None,
            key=np.int32(31),
        ),
        upsert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=None,
            key=np.array([b"a", b"b", b"c"]),
        ),
    ],
)
def test_vector_upsert_with_numpy_key(session_vector_client, test_case):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name,
    )

    session_vector_client.delete(
        namespace=test_case.namespace,
        key=test_case.key,
    )


#@given(random_key=key_strategy())
#@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        upsert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=0.0001,
        )
    ],
)
def test_vector_upsert_timeout(
    session_vector_client, test_case, random_key, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")

    for i in range(10):
        try:
            session_vector_client.upsert(
                namespace=test_case.namespace,
                key=random_key,
                record_data=test_case.record_data,
                set_name=test_case.set_name,
                timeout=test_case.timeout,
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"
