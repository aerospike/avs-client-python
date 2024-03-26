# test_example.py

import pytest

from aerospike_vector import vectordb_client, vectordb_admin, types, types_pb2


@pytest.fixture(scope='session')
def delete_indexes(admin_client):
    for index in admin_client.index_list():
        print(index)
        admin_client.index_drop(namespace='test', name=index.id.name)


@pytest.fixture(scope='session', autouse=True)
def final_cleanup(admin_client):
    for index in admin_client.index_list():
        print(index)
        admin_client.index_drop(namespace='test', name=index.id.name)



def test_index_create(admin_client):
    admin_client.index_create(
        namespace='test',
        name='index_create0',
        vector_bin_name='example',
        dimensions=1024,
    )


@pytest.mark.parametrize("sets", ['example'])
def test_index_create_with_sets(admin_client, sets):
    admin_client.index_create(
        namespace='test',
        name='index_create1',
        vector_bin_name='example',
        dimensions=1024,
        sets='demo'
    )


#def test_client():
#    proximus_client = vectordb_client.VectorDbClient(
#    types.HostPort(
#        '34.31.160.155',
#        5000,
#        False),
#    None)
#
#    print(proximus_client.exists('test', 'demo', 'yes'))
#
#    proximus_client.upsert(namespace='test', set='demo', key='yes', bins={
#        "_vectors": {
#            "features_description_vector":[0.00001, 0.00002, 0.0003],
#            "image0_vector": [0.00001, 0.00002, 0.0003],
#        },
#        "main_category": "All Beauty",
#        } 
#    )
