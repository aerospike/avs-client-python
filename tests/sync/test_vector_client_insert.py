import pytest
class insert_test_case:
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
        insert_test_case(
            namespace="test",
            key="insert/1",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        ),
        insert_test_case(
            namespace="test",
            key="insert/2",
            record_data={"english": [float(i) for i in range(1024)]},
            set_name=None
        ),
        insert_test_case(
            namespace="test",
            key="insert/3",
            record_data={"english": [bool(i) for i in range(1024)]},
            set_name=None
        )
    ],
)
def test_vector_insert_without_existing_record(session_vector_client, test_case):
    session_vector_client.insert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )

@pytest.mark.parametrize(
    "test_case",
    [
        insert_test_case(
            namespace="test",
            key="insert/4",
            record_data={"math": [i for i in range(1024)]},
            set_name=None
        )
    ],
)
def test_vector_insert_with_existing_record(session_vector_client, test_case):
    session_vector_client.insert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name
    )
    with pytest.raises(Exception) as e_info:
        session_vector_client.insert(
            namespace=test_case.namespace,
            key=test_case.key,
            record_data=test_case.record_data,
            set_name=test_case.set_name
        )