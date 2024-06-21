import pytest
from ...utils import index_strategy
from .aio_utils import drop_specified_index
from hypothesis import given, settings, Verbosity

@pytest.mark.parametrize("empty_test_case",[None, None])
@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
async def test_index_get_status(session_admin_client, empty_test_case, random_name):
    await session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="science",
        dimensions=1024,
    )

    result = await session_admin_client.index_get_status(
        namespace="test", name=random_name
    )
    assert result == 0
    await drop_specified_index(session_admin_client, "test", random_name)