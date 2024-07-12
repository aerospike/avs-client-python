import pytest
import asyncio
from aerospike_vector_search import Client
from aerospike_vector_search.admin import Client as AdminClient
from aerospike_vector_search import types

host = '0.0.0.0'
port = 10000
@pytest.fixture(scope="session", autouse=True)
def drop_all_indexes():
    with AdminClient(
        seeds=types.HostPort(host=host, port=port)
    ) as client:
        index_list = client.index_list()

        for item in index_list:
            client.index_drop(namespace="test", name=item['id']['name'])


@pytest.fixture(scope="module")
def session_admin_client():
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port)
    )
    yield client
    client.close()


@pytest.fixture(scope="module")
def session_vector_client():
    client = Client(
        seeds=types.HostPort(host=host, port=port)
    )
    yield client
    client.close()

@pytest.fixture(scope="module")
def get_host():
    return host

@pytest.fixture(scope="module")
def get_port():
    return port

@pytest.fixture
def function_admin_client():
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port)
    ) 
    yield client
    client.close()