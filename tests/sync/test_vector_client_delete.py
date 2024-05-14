import pytest
from aerospike_vector_search import AVSServerError

class delete_test_case:
    def __init__(
        self,
        *,
        namespace,
        key,
        record_data,
        set_name,

    ):
        self.namespace = namespace
        self.key = key
        self.set_name = set_name
        self.record_data = record_data

@pytest.mark.parametrize(
    "test_case",
    [
        delete_test_case(
            namespace="test",
            key="delete/1",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
        ),
        delete_test_case(
            namespace="test",
            key="delete/2",
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
        )
    ],
)
def test_vector_delete(session_vector_client, test_case):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )
    session_vector_client.delete(
        namespace=test_case.namespace,
        key=test_case.key,
    )
    with pytest.raises(AVSServerError) as e_info:
        result = session_vector_client.get(
            namespace=test_case.namespace, key=test_case.key
        )
    print(e_info.value.rpc_error.code())

@pytest.mark.parametrize(
    "test_case",
    [
        delete_test_case(
            namespace="test",
            key="aio/delete/3",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
        ),
    ],
)
async def test_vector_delete_without_record(session_vector_client, test_case):
    session_vector_client.delete(
        namespace=test_case.namespace,
        key=test_case.key,
    )