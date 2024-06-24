import pytest
import asyncio
from aerospike_vector_search.aio import Client
from aerospike_vector_search.aio.admin import Client as AdminClient
from aerospike_vector_search import types

@pytest.fixture(scope="module", autouse=True)
def username(request):
    return request.config.getoption("--username")

@pytest.fixture(scope="module", autouse=True)
def password(request):
    return request.config.getoption("--password")

@pytest.fixture(scope="module", autouse=True)
def root_certificate(request):
    return request.config.getoption("--root_certificate")

@pytest.fixture(scope="module", autouse=True)
async def drop_all_indexes(username, password, root_certificate, host, port):
    async with AdminClient(
        seeds=types.HostPort(host=host, port=port), username=username, password=password, root_certificate=root_certificate,
    ) as client:
        index_list = await client.index_list()

        tasks = []
        for item in index_list:
            tasks.append(client.index_drop(namespace="test", name=item['id']['name']))

        await asyncio.gather(*tasks)

@pytest.fixture(scope="module")
async def session_rbac_admin_client(username, password, root_certificate, host, port):
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port), username=username, password=password, root_certificate=root_certificate,
    )
    yield client
    await client.close()



