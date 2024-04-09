async def test_index_list(session_admin_client):
    result = await session_admin_client.index_list()
    assert len(result) > 0
    for index in result:
        assert isinstance(index.id.name, str)
        assert isinstance(index.id.namespace, str)
        assert isinstance(index.dimensions, int)
        assert isinstance(index.bin, str)
        assert isinstance(index.hnswParams.m, int)
        assert isinstance(index.hnswParams.efConstruction, int)
        assert isinstance(index.hnswParams.ef, int)
        assert isinstance(index.hnswParams.batchingParams.maxRecords, int)
        assert isinstance(index.hnswParams.batchingParams.interval, int)
        assert isinstance(index.hnswParams.batchingParams.disabled, bool)
        assert isinstance(index.aerospikeStorage.namespace, str)
        assert isinstance(index.aerospikeStorage.set, str)
