import pytest

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
            key="aio/delete/1",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
        ),
        delete_test_case(
            namespace="test",
            key="aio/delete/2",
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
        )
    ],
)
async def test_vector_delete(session_vector_client, test_case):
    await session_vector_client.upsert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )
    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=test_case.key,
    )
    with pytest.raises(Exception) as e_info:
        result = await session_vector_client.get(
            namespace=test_case.namespace, key=test_case.key
        )    
