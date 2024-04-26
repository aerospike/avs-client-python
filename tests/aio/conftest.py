import pytest
import asyncio
from aerospike_vector.aio import Client
from aerospike_vector.aio.admin import Client as AdminClient
from aerospike_vector import types

host = 'localhost'
port = 5000
@pytest.fixture(scope="session", autouse=True)
async def drop_all_indexes():
    async with AdminClient(
        seeds=types.HostPort(host=host, port=port)
    ) as client:
        index_list = await client.index_list()
        tasks = []
        for item in index_list:
            tasks.append(client.index_drop(namespace="test", name=item['id']['name']))
        await asyncio.gather(*tasks)

@pytest.fixture(scope="module")
async def session_admin_client():
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port)
    )
    yield client
    await client.close()


@pytest.fixture(scope="module")
async def session_vector_client():
    client = Client(
        seeds=types.HostPort(host=host, port=port)
    )
    yield client
    await client.close()

@pytest.fixture
async def function_admin_client():
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port)
    ) 
    yield client
    await client.close()