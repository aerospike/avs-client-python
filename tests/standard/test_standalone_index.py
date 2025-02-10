import time

import pytest
from utils import DEFAULT_NAMESPACE, DEFAULT_INDEX_DIMENSION, DEFAULT_VECTOR_FIELD

import aerospike_vector_search as avs

@pytest.mark.parametrize(
    "index",
    [
        {
            "mode": avs.types.IndexMode.STANDALONE,
        },
    ],
    indirect=True,
)
def test_standalone_index(session_vector_client, index_obj):
    # TODO: when the client is able to tell if the cluster
    # has a node with the standalone indexer role
    # we should skip this test if there is no standalone indexer node
    
    c = session_vector_client

    index_def = index_obj.get()
    assert index_def.mode == avs.types.IndexMode.STANDALONE

    status = index_obj.status()
    assert status.index_readiness == avs.types.IndexReadiness.NOT_READY

    # we have written no records, so the index should be stuck in the creating state
    assert status.standalone_metrics.state == avs.types.StandaloneIndexState.CREATING

    records = [{"id": i, DEFAULT_VECTOR_FIELD: [float(i)] * DEFAULT_INDEX_DIMENSION} for i in range(10)]
    for record in records:
        c.upsert(
            namespace=DEFAULT_NAMESPACE,
            key=record["id"],
            record_data=record,
        )

    # wait for the index to process the records and transition to the UPDATING state
    max_retries = 1000
    while status.index_readiness != avs.types.IndexReadiness.READY:
        if max_retries <= 0:
            pytest.fail("standalone index did not transition to READY state, maybe no node in the cluster has the standalone indexer role")

        time.sleep(0.5)
        status = index_obj.status()
        max_retries -= 1

    # at this point, the index mode should switch to DISTRIBUTED
    index_def = index_obj.get()
    assert index_def.mode == avs.types.IndexMode.DISTRIBUTED

    status = index_obj.status()
    assert status.index_readiness == avs.types.IndexReadiness.READY

    # test that the index is searchable

    neighbors = index_obj.vector_search(
        query=[0.0] * DEFAULT_INDEX_DIMENSION,
        limit=3,
    )

    for record in records:
        c.delete(
            namespace=DEFAULT_NAMESPACE,
            key=record["id"],
        )

    assert len(neighbors) == 3


def test_standalone_index_update(session_vector_client, index_obj):
    c = session_vector_client

    index_def = index_obj.get()
    # by default the index fixture creates a distributed index
    assert index_def.mode == avs.types.IndexMode.DISTRIBUTED

    # update the index to standalone mode and verify using the index
    index_obj.update(mode=avs.types.IndexMode.STANDALONE)

    time.sleep(0.5)
    index_def = index_obj.get()
    assert index_def.mode == avs.types.IndexMode.STANDALONE

    # update the index back to distributed mode and verify using the client
    c.index_update(
        namespace=DEFAULT_NAMESPACE,
        name=index_obj._name,
        mode=avs.types.IndexMode.DISTRIBUTED,
    )

    time.sleep(0.5)
    index_def = index_obj.get()
    assert index_def.mode == avs.types.IndexMode.DISTRIBUTED



    

    
