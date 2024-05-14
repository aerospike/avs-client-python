async def test_index_list(session_admin_client):
    result = await session_admin_client.index_list()
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

