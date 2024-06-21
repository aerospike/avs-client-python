import pytest
from aerospike_vector_search import AVSServerError
from ...utils import key_strategy
from hypothesis import given, settings, Verbosity

class delete_test_case:
    def __init__(
        self,
        *,
        namespace,
        record_data,
        set_name,

    ):
        self.namespace = namespace
        self.set_name = set_name
        self.record_data = record_data


@given(random_key=key_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        delete_test_case(
            namespace="test",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
        ),
        delete_test_case(
            namespace="test",
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
        )
    ],
)
async def test_vector_delete(session_vector_client, test_case, random_key):
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
    with pytest.raises(AVSServerError) as e_info:
        result = await session_vector_client.get(
            namespace=test_case.namespace, key=random_key
        )    
@given(random_key=key_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        None,
        delete_test_case(
            namespace="test",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
        ),
    ],
)
async def test_vector_delete_without_record(session_vector_client, test_case, random_key):
    await session_vector_client.delete(
        namespace=test_case.namespace,
        key=random_key,
    )