import pytest
from aerospike_vector_search import AVSServerError
import grpc

class exists_test_case:
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
        self.set_name = set_name
        self.record_data = record_data
        self.timeout = timeout

@pytest.mark.parametrize(
    "test_case",
    [
        exists_test_case(
            namespace="test",
            key="exists/1",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
            timeout=None
        ),
        exists_test_case(
            namespace="test",
            key="exists/2",
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
            timeout=None
        )
    ],
)
def test_vector_exists(session_vector_client, test_case):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name

    )
    result = session_vector_client.exists(
        namespace=test_case.namespace,
        key=test_case.key,
    )
    assert result is True

@pytest.mark.parametrize(
    "test_case",
    [
        exists_test_case(
            namespace="test",
            key="exists/3",
            set_name=None,
            record_data=None,
            timeout=0
        ),
    ],
)
def test_vector_exists_timeout(session_vector_client, test_case):
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):

            result = session_vector_client.exists(
                namespace=test_case.namespace,
                key=test_case.key,
                timeout=test_case.timeout
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED