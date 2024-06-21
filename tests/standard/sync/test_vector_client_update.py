import pytest
from aerospike_vector_search import AVSServerError
from ...utils import key_strategy
from hypothesis import given, settings, Verbosity

class update_test_case:
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
        update_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        ),
        update_test_case(
            namespace="test",
            record_data={"english": [float(i) for i in range(1024)]},
            set_name=None
        ),
        update_test_case(
            namespace="test",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None
        )
    ],
)
def test_vector_update_with_existing_record(session_vector_client, test_case, random_key):
    session_vector_client.insert(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )
    session_vector_client.update(
        namespace=test_case.namespace,
        key=random_key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )

@given(random_key=key_strategy())
@settings(max_examples=5, deadline=1000)
@pytest.mark.parametrize(
    "test_case",
    [
        update_test_case(
            namespace="test",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        )
    ],
)
def test_vector_update_without_existing_record(session_vector_client, test_case, random_key):
    with pytest.raises(AVSServerError) as e_info:
        session_vector_client.update(
            namespace=test_case.namespace,
            key=random_key,
            record_data=test_case.record_data,
            set_name=test_case.set_name
        )
    