import pytest
import random
from aerospike_vector_search import AVSServerError
from aerospike_vector_search import Client, AdminClient

import grpc

# Define module-level constants for common arguments
NAMESPACE = "test"
SET_NAME = "isidxset"
INDEX_NAME = "isidx"
DIMENSIONS = 3
VECTOR_FIELD = "vector"

@pytest.fixture(scope="module", autouse=True)
async def setup_teardown(session_vector_client: Client, session_admin_client: AdminClient):
    # Setup: Create index and upsert records
    session_admin_client.index_create(
        namespace=NAMESPACE,
        sets=SET_NAME,
        name=INDEX_NAME,
        dimensions=DIMENSIONS,
        vector_field=VECTOR_FIELD,
    )
    for i in range(10):
        session_vector_client.upsert(
            namespace=NAMESPACE,
            set_name=SET_NAME,
            key=str(i),
            record_data={VECTOR_FIELD: [float(i)] * DIMENSIONS},
        )
    session_vector_client.wait_for_index_completion(
        namespace=NAMESPACE,
        name=INDEX_NAME,
    )
    yield
    # Teardown: remove records
    for i in range(10):
        session_vector_client.delete(
            namespace=NAMESPACE,
            set_name=SET_NAME,
            key=str(i)
        )

    # Teardown: Drop index
    session_admin_client.index_drop(
        namespace=NAMESPACE,
        name=INDEX_NAME
    )

async def test_vector_is_indexed(
    session_vector_client,
):
    result = session_vector_client.is_indexed(
        namespace=NAMESPACE,
        key="0",
        index_name=INDEX_NAME,
        set_name=SET_NAME,
    )
    assert result is True


async def test_vector_is_indexed_timeout(
    session_vector_client, with_latency
):
    if not with_latency:
        pytest.skip("Server latency too low to test timeout")
    for _ in range(10):
        try:
            session_vector_client.is_indexed(
                namespace=NAMESPACE,
                key="0",
                index_name=INDEX_NAME,
                timeout=0.0001,
            )
        except AVSServerError as se:
            if se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                assert se.rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                return
    assert "In several attempts, the timeout did not happen" == "TEST FAIL"