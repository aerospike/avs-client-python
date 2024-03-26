# test_example.py

import pytest

from aerospike_vector import vectordb_client, vectordb_admin, types

@pytest.fixture(scope='session')
def admin_client():
    proximus_admin_client = vectordb_admin.VectorDbAdminClient(
        seeds=types.HostPort(
            host='localhost',
            port=5000
        )
    )
    yield proximus_admin_client
    proximus_admin_client.close()

@pytest.fixture
def client():
    proximus_client = vectordb_client.VectorDbClient(
        seeds=types.HostPort(
            host='localhost',
            port=5000
        )
    )
    yield proximus_client
    proximus_client.close()