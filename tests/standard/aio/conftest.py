import asyncio
import pytest
import random
import string

from aerospike_vector_search.aio import Client
from aerospike_vector_search.aio.admin import Client as AdminClient
from aerospike_vector_search import types

from .aio_utils import gen_records

#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


# default test values
DEFAULT_NAMESPACE = "test"
DEFAULT_INDEX_DIMENSION = 128
DEFAULT_VECTOR_FIELD = "vector"
DEFAULT_INDEX_ARGS = {
    "namespace": DEFAULT_NAMESPACE,
    "vector_field": DEFAULT_VECTOR_FIELD,
    "dimensions": DEFAULT_INDEX_DIMENSION,
}

DEFAULT_RECORD_GENERATOR = gen_records
DEFAULT_NUM_RECORDS = 1000
DEFAULT_RECORDS_ARGS = {
    "record_generator": DEFAULT_RECORD_GENERATOR,
    "namespace": DEFAULT_NAMESPACE,
    "vector_field": DEFAULT_VECTOR_FIELD,
    "dimensions": DEFAULT_INDEX_DIMENSION,
    "num_records": DEFAULT_NUM_RECORDS,
}

@pytest.fixture(scope="module", autouse=True)
async def drop_all_indexes(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    is_loadbalancer,
):
    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    async with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
    ) as client:

        index_list = await client.index_list()
        tasks = []
        for item in index_list:
            tasks.append(asyncio.create_task(client.index_drop(namespace="test", name=item["id"]["name"])))

        await asyncio.gather(*tasks)



@pytest.fixture(scope="module")
async def session_admin_client(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    is_loadbalancer,
):
    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    client = AdminClient(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        username=username,
        password=password,
    )

    yield client
    await client.close()


@pytest.fixture(scope="module")
async def session_vector_client(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    is_loadbalancer,
):

    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    client = Client(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        username=username,
        password=password,
    )
    yield client
    await client.close()


@pytest.fixture
async def function_admin_client(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    is_loadbalancer,
):

    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    client = AdminClient(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        username=username,
        password=password,
    )
    yield client
    await client.close()


@pytest.fixture()
def index_name():
    length = random.randint(1, 15)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest.fixture(params=[DEFAULT_INDEX_ARGS])
async def index(session_admin_client, index_name, request):
    index_args = request.param
    await session_admin_client.index_create(
        name = index_name,
        **index_args,
    )
    yield index_name
    namespace = index_args.get("namespace", DEFAULT_NAMESPACE)
    await session_admin_client.index_drop(namespace=namespace, name=index_name)


@pytest.fixture(params=[DEFAULT_RECORDS_ARGS])
async def records(session_vector_client, request):
    args = request.param
    record_generator = args.get("record_generator", DEFAULT_RECORD_GENERATOR)
    namespace = args.get("namespace", DEFAULT_NAMESPACE)
    num_records = args.get("num_records", DEFAULT_NUM_RECORDS)
    vector_field = args.get("vector_field", DEFAULT_VECTOR_FIELD)
    dimensions = args.get("dimensions", DEFAULT_INDEX_DIMENSION)
    keys = []
    for key, rec in record_generator(count=num_records, vec_bin=vector_field, vec_dim=dimensions):
        await session_vector_client.upsert(namespace=namespace, key=key, record_data=rec)
        keys.append(key)
    yield len(keys)
    for key in keys:
        await session_vector_client.delete(key=key, namespace=namespace)