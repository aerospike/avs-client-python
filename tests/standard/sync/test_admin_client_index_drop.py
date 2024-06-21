import pytest

from ...utils import index_strategy

from hypothesis import given, settings, Verbosity




@pytest.mark.parametrize("empty_test_case",[None])
@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
def test_index_drop(session_admin_client, empty_test_case, random_name):
    session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="art",
        dimensions=1024,
    )
    session_admin_client.index_drop(namespace="test", name=random_name)

    result = session_admin_client.index_list()
    result = result
    for index in result:
        assert index["id"]["name"] != random_name

