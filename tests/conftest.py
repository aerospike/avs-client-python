import pytest
import asyncio
from aerospike_vector import vectordb_client, vectordb_admin, types


@pytest.fixture(scope="session", autouse=True)
async def drop_all_indexes():
    client = vectordb_admin.VectorDbAdminClient(
        seeds=types.HostPort(host="localhost", port=5000)
    )
    list = await client.index_list()
    tasks = []
    for item in list:
        tasks.append(client.index_drop(namespace="test", name=item.id.name))
    await asyncio.gather(*tasks)
    try:
        await client.index_create(
            namespace="test",
            name="vec",
            vector_bin_name="chocolate",
            dimensions=1024,
            sets="demo",
        )
    except Exception as e:
        print(e)
        pass
    await client.close()


@pytest.fixture(scope="session")
async def truncated_admin_client():
    client = vectordb_admin.VectorDbAdminClient(
        seeds=types.HostPort(host="localhost", port=5000)
    )
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def truncated_vector_client():
    client = vectordb_client.VectorDbClient(
        seeds=types.HostPort(host="localhost", port=5000)
    )
    yield client
    await client.close()
