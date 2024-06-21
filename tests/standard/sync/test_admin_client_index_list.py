import pytest

from ...utils import index_strategy
from .sync_utils import drop_specified_index
from hypothesis import given, settings, Verbosity

@pytest.mark.parametrize("empty_test_case",[None])
@given(random_name=index_strategy())
@settings(max_examples=5, deadline=1000)
def test_index_list(session_admin_client, empty_test_case, random_name):
    session_admin_client.index_create(
        namespace="test",
        name=random_name,
        vector_field="science",
        dimensions=1024,
    )
    result = session_admin_client.index_list()
    assert len(result) > 0
    for index in result:
        assert isinstance(index['id']['name'], str)
        assert isinstance(index['id']['namespace'], str)
        assert isinstance(index['dimensions'], int)
        assert isinstance(index['field'], str)
        assert isinstance(index['hnsw_params']['m'], int)
        assert isinstance(index['hnsw_params']['ef_construction'], int)
        assert isinstance(index['hnsw_params']['ef'], int)
        assert isinstance(index['hnsw_params']['batching_params']['max_records'], int)
        assert isinstance(index['hnsw_params']['batching_params']['interval'], int)
        assert isinstance(index['hnsw_params']['batching_params']['disabled'], bool)
        assert isinstance(index['storage']['namespace'], str)
        assert isinstance(index['storage']['set'], str)
    drop_specified_index(session_admin_client, "test", random_name)
