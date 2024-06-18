import pytest

class get_test_case:
    def __init__(
        self,
        *,
        namespace,
        key,
        field_names,
        set_name,
        record_data,
        expected_fields
    ):
        self.namespace = namespace
        self.key = key
        self.field_names = field_names
        self.set_name = set_name
        self.record_data = record_data
        self.expected_fields = expected_fields

@pytest.mark.parametrize(
    "test_case",
    [
        get_test_case(
            namespace="test",
            key="get/1",
            field_names=['skills'],
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
            expected_fields={"skills": [i for i in range(1024)]}
        ),
        get_test_case(
            namespace="test",
            key="get/2",
            field_names=['english'],
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
            expected_fields={"english": [float(i) for i in range(1024)]}
        )
    ],
)
def test_vector_get(session_vector_client, test_case):
    session_vector_client.upsert(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name

    )
    result = session_vector_client.get(
        namespace=test_case.namespace, key=test_case.key, field_names=test_case.field_names
    )
    assert result.key.namespace == test_case.namespace
    if(test_case.set_name == None):
        test_case.set_name = ""
    assert result.key.set == test_case.set_name
    assert result.key.key == test_case.key

    assert result.fields == test_case.expected_fields

