import pytest
from ...utils import key_strategy
from hypothesis import given, settings, Verbosity

class upsert_test_case:
    def __init__(
        self,
        *,
        namespace,
        record_data,
        set_name
    ):
        self.namespace = namespace
        self.record_data = record_data
        self.set_name = set_name

@given(random_key=key_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        upsert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        ),
        upsert_test_case(
            namespace="test",
            record_data={"english": [float(i) for i in range(1024)]},
            set_name=None
        ),
        upsert_test_case(
            namespace="test",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None
        )
    ],
)
async def test_vector_upsert_without_existing_record(session_vector_client, test_case, random_key):
    await session_vector_client.upsert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )

    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )
    
@given(random_key=key_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        upsert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        )
    ],
)
async def test_vector_upsert_with_existing_record(session_vector_client, test_case, random_key):
    await session_vector_client.upsert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )

    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )