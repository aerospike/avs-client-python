import pytest
import asyncio
from aerospike_vector_search.aio import Client
from aerospike_vector_search.aio.admin import Client as AdminClient
from aerospike_vector_search import types

@pytest.fixture(scope="module", autouse=True)
def private_key(request):
    return request.config.getoption("--private_key")

@pytest.fixture(scope="module", autouse=True)
def certificate_chain(request):
    return request.config.getoption("--certificate_chain")

@pytest.fixture(scope="module", autouse=True)
def root_certificate(request):
    return request.config.getoption("--root_certificate")

@pytest.fixture(scope="module", autouse=True)
def username(request):
    return request.config.getoption("--username")

@pytest.fixture(scope="module", autouse=True)
def password(request):
    return request.config.getoption("--password")

@pytest.fixture(scope="module", autouse=True)
async def drop_all_indexes(host, port, username, password, root_certificate, certificate_chain, private_key):
    async with AdminClient(
        seeds=types.HostPort(host=host, port=port), username=username, password=password, root_certificate=root_certificate, certificate_chain=certificate_chain, private_key=private_key

    ) as client:
        index_list = await client.index_list()

        tasks = []
        for item in index_list:
            tasks.append(client.index_drop(namespace="test", name=item['id']['name']))


        await asyncio.gather(*tasks)


@pytest.fixture(scope="module")
async def session_admin_client(host, port, username, password, root_certificate, certificate_chain, private_key):
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port), root_certificate=root_certificate, certificate_chain=certificate_chain, private_key=private_key, username=username, password=password
    )
    yield client
    await client.close()

@pytest.fixture(scope="module")
async def session_vector_client(host, port, username, password, root_certificate, certificate_chain, private_key):
    client = Client(
        seeds=types.HostPort(host=host, port=port), root_certificate=root_certificate, certificate_chain=certificate_chain, private_key=private_key, username=username, password=password
    )
    yield client
    await client.close()

@pytest.fixture
async def function_admin_client(host, port, username, password, root_certificate, certificate_chain, private_key):
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port), root_certificate=root_certificate, certificate_chain=certificate_chain, private_key=private_key, username=username, password=password
    ) 
    yield client
    await client.close()
