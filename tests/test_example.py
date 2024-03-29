import pytest
import asyncio
import pytest_asyncio  # Import pytest_asyncio module

import tracemalloc





#@pytest_asyncio.fixture
#def vector_client(event_loop):
#    client = vectordb_admin.VectorDbClient(
#        seeds=types.HostPort(
#            host='localhost',
#            port=5000
#        )
#    )
#    yield client
#    event_loop.run_until_complete(client.close())


@pytest.mark.asyncio
async def test_index_create(truncated_admin_client):
    await truncated_admin_client.index_create(
        namespace='test',
        name='index_create201',
        vector_bin_name='example',
        dimensions=1024,
    )
    await asyncio.sleep(1)






@pytest.mark.asyncio
async def test_index_list(truncated_admin_client):
    result = await truncated_admin_client.index_list()
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


@pytest.mark.asyncio
async def test_index_get(truncated_admin_client):
    result = await truncated_admin_client.index_get(namespace='test', name='index_create201')
    assert result['id']['name'] == "index_create201"
    assert result['id']['namespace'] == "test"
    assert result['dimensions'] == 1024
    assert result['bin'] == "example"
    assert result['hnswParams']['m'] == 16
    assert result['hnswParams']['efConstruction'] == 100
    assert result['hnswParams']['ef'] == 100
    assert result['hnswParams']['batchingParams']['maxRecords'] == 100000
    assert result['hnswParams']['batchingParams']['interval'] == 30000
    assert not result['hnswParams']['batchingParams']['disabled']
    assert result['aerospikeStorage']['namespace'] == "test"
    assert result['aerospikeStorage']['set'] == "index_create201"


@pytest.mark.asyncio
async def test_index_get_status(truncated_admin_client):
    client = truncated_admin_client
    result = await client.index_get_status(namespace='test', name='index_create201')


@pytest.mark.asyncio
async def test_index_drop(truncated_admin_client):
    client = truncated_admin_client
    res = await client.index_drop(namespace='test', name='index_create201')
    # TODO implement delete wait
    await asyncio.sleep(1)
    result = client.index_list()
    result = await result
    assert len(result) == 0
