import pytest

class get_test_case:
    def __init__(
        self,
        *,
        namespace,
        key,
        bin_names,
        set_name,
        record_data,
        expected_bins
    ):
        self.namespace = namespace
        self.key = key
        self.bin_names = bin_names
        self.set_name = set_name
        self.record_data = record_data
        self.expected_bins = expected_bins

@pytest.mark.parametrize(
    "test_case",
    [
        get_test_case(
            namespace="test",
            key="get/1",
            bin_names=['skills'],
            set_name=None,
            record_data={"skills": [i for i in range(1024)]},
            expected_bins={"skills": [i for i in range(1024)]}
        ),
        get_test_case(
            namespace="test",
            key="get/1",
            bin_names=['english'],
            set_name=None,
            record_data={"english": [float(i) for i in range(1024)]},
            expected_bins={"english": [float(i) for i in range(1024)]}
        )
    ],
)
async def test_vector_get(session_vector_client, test_case):
    await session_vector_client.put(
        namespace=test_case.namespace,
        key=test_case.key,
        record_data=test_case.record_data,
        set_name=test_case.set_name

    )
    result = await session_vector_client.get(
        namespace=test_case.namespace, key=test_case.key, bin_names=test_case.bin_names
    )
    assert result.key.namespace == test_case.namespace
    if(test_case.set_name == None):
        test_case.set_name = ""
    assert result.key.set == test_case.set_name
    assert result.key.key == test_case.key
    assert isinstance(result.key.digest, bytes)
    assert result.bins == test_case.expected_bins
