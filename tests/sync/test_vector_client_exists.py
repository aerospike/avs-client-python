import pytest

class exists_test_case:
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
        exists_test_case(
            namespace="test",
            key="get/1",
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
        ),
        exists_test_case(
            namespace="test",
            key="get/1",
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
        )
    ],
)
def test_vector_exists(session_vector_client, test_case):
    session_vector_client.put(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name

    )
    result = session_vector_client.exists(
        namespace=test_case.namespace,
        key=test_case.key,
    )
    assert result is True
