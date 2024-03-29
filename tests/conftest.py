# test_example.py

import pytest
import pytest_asyncio  # Import pytest_asyncio module

from aerospike_vector import vectordb_client, vectordb_admin, types


@pytest_asyncio.fixture
def truncated_admin_client(event_loop):
    client = vectordb_admin.VectorDbAdminClient(
        seeds=types.HostPort(
            host='localhost',
            port=5000
        )
    )

    list = event_loop.run_until_complete(client.index_list())
    for index in list:
        event_loop.run_until_complete(client.index_drop(namespace='test', name=index.id.name))

    yield client
    event_loop.run_until_complete(client.close())

@pytest_asyncio.fixture
def truncated_vector_client(event_loop):
    client = vectordb_client.VectorDbClient(
        seeds=types.HostPort(
            host='localhost',
            port=5000
        )
    )

    yield client
    event_loop.run_until_complete(client.close())