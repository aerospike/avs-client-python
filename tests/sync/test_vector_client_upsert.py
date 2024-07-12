import pytest
from aerospike_vector_search import AVSServerError
import grpc

class upsert_test_case:
    def __init__(
        self,
        *,
        namespace,
        key,
        record_data,
        set_name,
        timeout,
    ):
        self.namespace = namespace
        self.key = key
        self.record_data = record_data
        self.set_name = set_name
        self.timeout = timeout


@pytest.mark.parametrize(
    "test_case",
    [
        upsert_test_case(
            namespace="test",
            key="upsert/1",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=None
        ),
        upsert_test_case(
            namespace="test",
            key="upsert/2",
            record_data={"english": [float(i) for i in range(1024)]},
            set_name=None,
            timeout=None
        ),
        upsert_test_case(
            namespace="test",
            key="upsert/3",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None,
            timeout=None
        )
    ],
)
def test_vector_upsert_without_existing_record(session_vector_client, test_case):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )

@pytest.mark.parametrize(
    "test_case",
    [
        upsert_test_case(
            namespace="test",
            key="upsert/4",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=None
        )
    ],
)
def test_vector_upsert_with_existing_record(session_vector_client, test_case):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name,
    )

@pytest.mark.parametrize(
    "test_case",
    [
        upsert_test_case(
            namespace="test",
            key="upsert/5",
            record_data={"math": [i for i in range(1024)]},
            set_name=None,
            timeout=0
        )
    ],
)
def test_vector_upsert_timeout(session_vector_client, test_case):
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):
            session_vector_client.upsert(
                namespace=test_case.namespace,
                key=test_case.key,
                record_data=test_case.record_data,
                set_name=test_case.set_name,
                timeout=test_case.timeout
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED