import pytest
from aerospike_vector_search import AVSServerError
import grpc

class get_test_case:
    def __init__(
        self,
        *,
        namespace,
        key,
        field_names,
        set_name,
        record_data,
        expected_fields,
        timeout,
    ):
        self.namespace = namespace
        self.key = key
        self.field_names = field_names
        self.set_name = set_name
        self.record_data = record_data
        self.expected_fields = expected_fields
        self.timeout = timeout

@pytest.mark.parametrize(
    "test_case",
    [
        get_test_case(
            namespace="test",
            key="aio/get/1",
            field_names=['skills'],
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
            expected_fields={"skills": [i for i in range(1024)]},
            timeout=None
        ),
        get_test_case(
            namespace="test",
            key="aio/get/2",
            field_names=['english'],
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
            expected_fields={"english": [float(i) for i in range(1024)]},
            timeout=None
        )
    ],
)
async def test_vector_get(session_vector_client, test_case):
    await session_vector_client.upsert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name

    )
    result = await session_vector_client.get(
        namespace=test_case.namespace, key=test_case.key, field_names=test_case.field_names
    )
    assert result.key.namespace == test_case.namespace
    if(test_case.set_name == None):
        test_case.set_name = ""
    assert result.key.set == test_case.set_name
    assert result.key.key == test_case.key

    assert result.fields == test_case.expected_fields

@pytest.mark.parametrize(
    "test_case",
    [
        get_test_case(
            namespace="test",
            key="aio/get/3",
            field_names=['skills'],
            set_name=None,
            record_data=None,
            expected_fields=None,
            timeout=0
        ),    ],
)
async def test_vector_get_timeout(session_vector_client, test_case):
    with pytest.raises(AVSServerError) as e_info:
        for i in range(10):
            result = await session_vector_client.get(
                namespace=test_case.namespace, key=test_case.key, field_names=test_case.field_names, timeout=test_case.timeout
            )
    assert e_info.value.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED