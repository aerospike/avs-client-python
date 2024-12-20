import asyncio
import pytest
import random
import string
import grpc

from aerospike_vector_search.aio import Client
from aerospike_vector_search.aio.admin import Client as AdminClient
from aerospike_vector_search import types, AVSServerError

from .aio_utils import gen_records
import utils

#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


# default test values
DEFAULT_NAMESPACE = utils.DEFAULT_NAMESPACE
DEFAULT_INDEX_DIMENSION = utils.DEFAULT_INDEX_DIMENSION
DEFAULT_VECTOR_FIELD = utils.DEFAULT_VECTOR_FIELD
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
    args = request.param
    namespace = args.get("namespace", DEFAULT_NAMESPACE)
    vector_field = args.get("vector_field", DEFAULT_VECTOR_FIELD) 
    dimensions = args.get("dimensions", DEFAULT_INDEX_DIMENSION)
    await session_admin_client.index_create(
        name = index_name,
        namespace = namespace,
        vector_field = vector_field,
        dimensions = dimensions,
        index_params=types.HnswParams(
            batching_params=types.HnswBatchingParams(
                # 10_000 is the minimum value, in order for the tests to run as
                # fast as possible we set it to the minimum value so records are indexed
                # quickly
                index_interval=10_000,
            ),
            healer_params=types.HnswHealerParams(
                # run the healer every second
                # for fast indexing
                schedule="* * * * * ?"
            )
        )
    )
    yield index_name
    try:
        await session_admin_client.index_drop(namespace=namespace, name=index_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass
        else:
            raise


@pytest.fixture(params=[DEFAULT_RECORDS_ARGS])
async def records(session_vector_client, request):
    args = request.param
    record_generator = args.get("record_generator", DEFAULT_RECORD_GENERATOR)
    namespace = args.get("namespace", DEFAULT_NAMESPACE)
    num_records = args.get("num_records", DEFAULT_NUM_RECORDS)
    vector_field = args.get("vector_field", DEFAULT_VECTOR_FIELD)
    dimensions = args.get("dimensions", DEFAULT_INDEX_DIMENSION)
    set_name = args.get("set_name", None)
    keys = []
    for key, rec in record_generator(count=num_records, vec_bin=vector_field, vec_dim=dimensions):
        await session_vector_client.upsert(
            namespace=namespace,
            key=key,
            record_data=rec,
            set_name=set_name,
        )
        keys.append(key)
    yield keys
    for key in keys:
        await session_vector_client.delete(key=key, namespace=namespace)


@pytest.fixture(params=[DEFAULT_RECORDS_ARGS])
async def record(session_vector_client, request):
    args = request.param
    record_generator = args.get("record_generator", DEFAULT_RECORD_GENERATOR)
    namespace = args.get("namespace", DEFAULT_NAMESPACE)
    vector_field = args.get("vector_field", DEFAULT_VECTOR_FIELD)
    dimensions = args.get("dimensions", DEFAULT_INDEX_DIMENSION)
    set_name = args.get("set_name", None)
    key, rec = next(record_generator(count=1, vec_bin=vector_field, vec_dim=dimensions))
    await session_vector_client.upsert(
        namespace=namespace,
        key=key,
        record_data=rec,
        set_name=set_name,
    )
    yield key
    await session_vector_client.delete(key=key, namespace=namespace)