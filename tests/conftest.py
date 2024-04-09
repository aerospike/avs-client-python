import pytest
import asyncio
from aerospike_vector import vectordb_client, vectordb_admin, types


host = 'localhost'
port = 5000
@pytest.fixture(scope="session", autouse=True)
async def drop_all_indexes():
    async with vectordb_admin.VectorDbAdminClient(
        seeds=types.HostPort(host=host, port=port)
    ) as client:
        index_list = await client.index_list()
        tasks = []
        for item in index_list:
            tasks.append(client.index_drop(namespace="test", name=item.id.name))
        await asyncio.gather(*tasks)


@pytest.fixture(scope="session")
async def session_admin_client():
    client = vectordb_admin.VectorDbAdminClient(
        seeds=types.HostPort(host=host, port=port)
    )
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def session_vector_client():
    client = vectordb_client.VectorDbClient(
        seeds=types.HostPort(host=host, port=port)
    )
    yield client
    await client.close()

@pytest.fixture
async def function_admin_client():
    client = vectordb_admin.VectorDbAdminClient(
        seeds=types.HostPort(host=host, port=port)
    ) 
    yield client
    await client.close()