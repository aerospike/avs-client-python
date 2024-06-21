import pytest
from aerospike_vector_search import AVSServerError
from ...utils import key_strategy
from hypothesis import given, settings, Verbosity

from hypothesis import given, settings

class insert_test_case:
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
        insert_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        ),
        insert_test_case(
            namespace="test",
            record_data={"homeSkills": [float(i) for i in range(1024)]},
            set_name=None
        ),
        insert_test_case(
            namespace="test",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None
        )
    ],
)
def test_vector_insert_without_existing_record(session_vector_client, test_case, random_key):
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
            set_name=None
        )
    ],
)
def test_vector_insert_with_existing_record(session_vector_client, test_case, random_key):
    session_vector_client.insert(
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