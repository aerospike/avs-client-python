import pytest
from aerospike_vector_search import AVSServerError

class update_test_case:
    def __init__(
        self,
        *,
        namespace,
        key,
        record_data,
        set_name
    ):
        self.namespace = namespace
        self.key = key
        self.record_data = record_data
        self.set_name = set_name


@pytest.mark.parametrize(
    "test_case",
    [
        update_test_case(
            namespace="test",
            key="aio/update/1",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        ),
        update_test_case(
            namespace="test",
            key="aio/update/2",
            record_data={"english": [float(i) for i in range(1024)]},
            set_name=None
        ),
        update_test_case(
            namespace="test",
            key="aio/update/3",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None
        )
    ],
)
async def test_vector_update_with_existing_record(session_vector_client, test_case):
    await session_vector_client.insert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )
    await session_vector_client.update(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )

@pytest.mark.parametrize(
    "test_case",
    [
        update_test_case(
            namespace="test",
            key="aio/update/4",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        )
    ],
)
async def test_vector_update_without_existing_record(session_vector_client, test_case):
    with pytest.raises(AVSServerError) as e_info:
        await session_vector_client.update(
            namespace=test_case.namespace,
            key=test_case.key,
            record_data=test_case.record_data,
            set_name=test_case.set_name
        )