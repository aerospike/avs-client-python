import pytest
from aerospike_vector_search import AVSServerError
import grpc

from ...utils import key_strategy
from hypothesis import given, settings, Verbosity

from hypothesis import given, settings

class insert_test_case:
    def __init__(
        self,
        *,
        namespace,
        record_data,
        set_name,
        ignore_mem_queue_full,
        timeout
    ):
        self.namespace = namespace
        self.record_data = record_data
        self.set_name = set_name
        self.ignore_mem_queue_full = ignore_mem_queue_full
        self.timeout = timeout

@given(random_key=key_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        insert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            ignore_mem_queue_full=None,
            timeout=None
        ),
        insert_test_case(
            namespace="test",
            record_data={"homeSkills": [float(i) for i in range(1024)]},
            set_name=None,
            ignore_mem_queue_full=None,
            timeout=None
        ),
        insert_test_case(
            namespace="test",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None,
            ignore_mem_queue_full=None,
            timeout=None
        )
    ],
)
def test_vector_insert_without_existing_record(session_vector_client, test_case, random_key):
    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )
    
    session_vector_client.insert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )

    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )

@given(random_key=key_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        insert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            ignore_mem_queue_full=None,
            timeout=None
        )
    ],
)
def test_vector_insert_with_existing_record(session_vector_client, test_case, random_key):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )   
    with pytest.raises(AVSServerError) as e_info:
        session_vector_client.insert(
            namespace=test_case.namespace,
            key=random_key,
            record_data=test_case.record_data,
            set_name=test_case.set_name
        )
    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )

@given(random_key=key_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        insert_test_case(
            namespace="test",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None,
            ignore_mem_queue_full=True,
            timeout=None
        )
    ],
)
def test_vector_insert_without_existing_record_ignore_mem_queue_full(session_vector_client, test_case, random_key):
    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )
    
    session_vector_client.insert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name,
        ignore_mem_queue_full=test_case.ignore_mem_queue_full
    )

    session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )


@given(random_key=key_strategy())
@settings(max_examples=1, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        insert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            ignore_mem_queue_full=None,
            timeout=0.0001
        )
    ],
)
def test_vector_insert_timeout(session_vector_client, test_case, random_key, with_latency):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")    

    for i in range(10):
        try:
            session_vector_client.insert(
                namespace=test_case.namespace,
                key=random_key,
                record_data=test_case.record_data,
                set_name=test_case.set_name,
                timeout=test_case.timeout
            )
        except AVSServerError as e:
            if e.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert e.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"