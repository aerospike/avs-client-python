import pytest
from aerospike_vector_search import Client
from aerospike_vector_search.admin import Client as AdminClient
from aerospike_vector_search import types


@pytest.fixture(scope="module", autouse=True)
def drop_all_indexes(host, port):
    with AdminClient(
        seeds=types.HostPort(host=host, port=port)

    ) as client:
        index_list = client.index_list()

        tasks = []
        for item in index_list:
            client.index_drop(namespace="test", name=item['id']['name'])



@pytest.fixture(scope="module")
def session_admin_client(host, port):
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port)
    )
    yield client
    client.close()

@pytest.fixture(scope="module")
def session_vector_client(host, port):
    client = Client(
        seeds=types.HostPort(host=host, port=port)
    )
    yield client
    client.close()

@pytest.fixture
def function_admin_client(host, port):
    client = AdminClient(
        seeds=types.HostPort(host=host, port=port)
    ) 
    yield client
    client.close()
