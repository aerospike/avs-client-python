import pytest
import asyncio

from aerospike_vector_search.aio import Client
from aerospike_vector_search.aio.admin import Client as AdminClient
from aerospike_vector_search import types

host = 'connector.aerospike.com'
port = 5000


@pytest.fixture
def username(request):
    return request.config.getoption("--username")

@pytest.fixture
def password(request):
    return request.config.getoption("--password")

@pytest.fixture
def root_certificate(request):
    return request.config.getoption("--root_certificate")

@pytest.fixture(scope="module", autouse=True)
async def drop_all_indexes():
    async with AdminClient(
        seeds=types.HostPort(host=host, port=port), username="admin", password="admin", root_certificate="/home/dpelini/Documents/prox/example/tls/connector.aerospike.com.crt",
    ) as client:
        index_list = await client.index_list()

        tasks = []
        for item in index_list:
            tasks.append(client.index_drop(namespace="test", name=item['id']['name']))


        await asyncio.gather(*tasks)

@pytest.fixture(scope="module")
async def session_rbac_admin_client():
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port), username="admin", password="admin", root_certificate="/home/dpelini/Documents/prox/example/tls/connector.aerospike.com.crt",
    )
    yield client
    await client.close()




