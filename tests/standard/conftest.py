import asyncio
import random
import string

from aerospike_vector_search import Client
from aerospike_vector_search.aio import Client as AsyncClient
from aerospike_vector_search.admin import Client as AdminClient
from aerospike_vector_search.aio.admin import Client as AsyncAdminClient
from aerospike_vector_search import types, AVSServerError

from utils import gen_records, DEFAULT_NAMESPACE, DEFAULT_INDEX_DIMENSION, DEFAULT_VECTOR_FIELD
import grpc
import pytest

##########################################
###### GLOBALS
##########################################

# default test values
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


##########################################
###### FIXTURES
##########################################

@pytest.fixture(scope="module", autouse=True)
def drop_all_indexes(
    username,
    password,
    root_certificate,
    host,
    port,
    certificate_chain,
    private_key,
    is_loadbalancer,
    ssl_target_name_override,
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

    with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
    ) as client:
        index_list = client.index_list()

        tasks = []
        for item in index_list:
            client.index_drop(namespace="test", name=item["id"]["name"])


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the test session.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    #HACK the async client schedules tasks in its init function so we need
    # to run the event loop to allow the tasks to be scheduled
    yield loop
    loop.close()


class AsyncClientWrapper():
    def __init__(self, client):
        self.client = client
    
    def __getattr__(self, name):
        attr = getattr(self.client, name)
        if asyncio.iscoroutinefunction(attr):
            # Wrap async methods to run in the current event loop
            def sync_method(*args, **kwargs):
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(attr(*args, **kwargs))

            return sync_method
        return attr


async def new_wrapped_async_client(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    is_loadbalancer,
    ssl_target_name_override
):
    client = AsyncClient(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override
    )
    return AsyncClientWrapper(client)


async def new_wrapped_async_admin_client(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    is_loadbalancer,
    ssl_target_name_override
):
    client = AsyncAdminClient(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override
    )
    return AsyncClientWrapper(client)


@pytest.fixture(scope="module")
def session_admin_client(
    username,
    password,
    root_certificate,
    host,
    port,
    certificate_chain,
    private_key,
    is_loadbalancer,
    ssl_target_name_override,
    async_client,
    event_loop,
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

    if async_client:
        loop = asyncio.get_event_loop()
        client = loop.run_until_complete(new_wrapped_async_admin_client(
            host=host,
            port=port,
            username=username,
            password=password,
            root_certificate=root_certificate,
            certificate_chain=certificate_chain,
            private_key=private_key,
            is_loadbalancer=is_loadbalancer,
            ssl_target_name_override=ssl_target_name_override
        ))
    else:
        client = AdminClient(
            seeds=types.HostPort(host=host, port=port),
            is_loadbalancer=is_loadbalancer,
            username=username,
            password=password,
            root_certificate=root_certificate,
            certificate_chain=certificate_chain,
            private_key=private_key,
            ssl_target_name_override=ssl_target_name_override
        )

    yield client
    client.close()


@pytest.fixture(scope="module")
def session_vector_client(
    username,
    password,
    root_certificate,
    host,
    port,
    certificate_chain,
    private_key,
    is_loadbalancer,
    ssl_target_name_override,
    async_client,
    event_loop,
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

    if async_client:
        loop = asyncio.get_event_loop()
        client = loop.run_until_complete(new_wrapped_async_client(
            host=host,
            port=port,
            username=username,
            password=password,
            root_certificate=root_certificate,
            certificate_chain=certificate_chain,
            private_key=private_key,
            is_loadbalancer=is_loadbalancer,
            ssl_target_name_override=ssl_target_name_override
        ))
    else:
        client = Client(
            seeds=types.HostPort(host=host, port=port),
            is_loadbalancer=is_loadbalancer,
            username=username,
            password=password,
            root_certificate=root_certificate,
            certificate_chain=certificate_chain,
            private_key=private_key,
            ssl_target_name_override=ssl_target_name_override
        )

    yield client
    client.close()


@pytest.fixture()
def index_name():
    length = random.randint(1, 15)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest.fixture(params=[DEFAULT_INDEX_ARGS])
def index(session_admin_client, index_name, request):
    args = request.param
    namespace = args.get("namespace", DEFAULT_NAMESPACE)
    vector_field = args.get("vector_field", DEFAULT_VECTOR_FIELD) 
    dimensions = args.get("dimensions", DEFAULT_INDEX_DIMENSION)
    session_admin_client.index_create(
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
        session_admin_client.index_drop(namespace=namespace, name=index_name)
    except AVSServerError as se:
        if se.rpc_error.code() != grpc.StatusCode.NOT_FOUND:
            pass
        else:
            raise


@pytest.fixture(params=[DEFAULT_RECORDS_ARGS])
def records(session_vector_client, request):
    args = request.param
    record_generator = args.get("record_generator", DEFAULT_RECORD_GENERATOR)
    namespace = args.get("namespace", DEFAULT_NAMESPACE)
    num_records = args.get("num_records", DEFAULT_NUM_RECORDS)
    vector_field = args.get("vector_field", DEFAULT_VECTOR_FIELD)
    dimensions = args.get("dimensions", DEFAULT_INDEX_DIMENSION)
    set_name = args.get("set_name", None)
    keys = []
    for key, rec in record_generator(count=num_records, vec_bin=vector_field, vec_dim=dimensions):
        session_vector_client.upsert(
            namespace=namespace,
            key=key,
            record_data=rec,
            set_name=set_name,
        )
        keys.append(key)
    yield keys
    for key in keys:
        session_vector_client.delete(key=key, namespace=namespace)


@pytest.fixture(params=[DEFAULT_RECORDS_ARGS])
def record(session_vector_client, request):
    args = request.param
    record_generator = args.get("record_generator", DEFAULT_RECORD_GENERATOR)
    namespace = args.get("namespace", DEFAULT_NAMESPACE)
    vector_field = args.get("vector_field", DEFAULT_VECTOR_FIELD)
    dimensions = args.get("dimensions", DEFAULT_INDEX_DIMENSION)
    set_name = args.get("set_name", None)
    key, rec = next(record_generator(count=1, vec_bin=vector_field, vec_dim=dimensions))
    session_vector_client.upsert(
        namespace=namespace,
        key=key,
        record_data=rec,
        set_name=set_name,
    )
    yield key
    session_vector_client.delete(key=key, namespace=namespace)


##########################################
###### SUITE FLAGS
##########################################

def pytest_addoption(parser):
    parser.addoption("--username", action="store", default=None, help="AVS Username")
    parser.addoption("--password", action="store", default=None, help="AVS Password")
    parser.addoption("--host", action="store", default="localhost", help="AVS Host")
    parser.addoption("--port", action="store", default=5000, help="AVS Port")
    parser.addoption(
        "--root_certificate",
        action="store",
        default=None,
        help="Path the root certificate",
    )
    parser.addoption(
        "--certificate_chain",
        action="store",
        default=None,
        help="Path to certificate chain",
    )
    parser.addoption(
        "--private_key", action="store", default=None, help="Path to private key"
    )
    parser.addoption(
        "--ssl_target_name_override", action="store", default=None, help="ssl target name override"
    )
    parser.addoption(
        "--is_loadbalancer",
        action="store_true",
        help="Enable to use load balancer tending logic",
    )
    parser.addoption(
        "--with_latency",
        action="store_true",
        help="Skip the test if latency is too low to effectively trigger timeout",
    )
    parser.addoption(
        "--extensive_vector_search",
        action="store_true",
        help="Run extensive vector search testing",
    )
    parser.addoption(
        "--async",
        action="store_true",
        help="Run tests using the async client",
    )
    parser.addoption(
        "--sync",
        action="store_true",
        help="Run tests using the sync client",
    )


@pytest.fixture(scope="module", autouse=True)
def async_client(request):
    return request.config.getoption("--async")


@pytest.fixture(scope="module", autouse=True)
def sync_client(request):
    return request.config.getoption("--sync")


@pytest.fixture(scope="module", autouse=True)
def username(request):
    return request.config.getoption("--username")


@pytest.fixture(scope="module", autouse=True)
def password(request):
    return request.config.getoption("--password")


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
def ssl_target_name_override(request):
    return request.config.getoption("--ssl_target_name_override")

@pytest.fixture(scope="module", autouse=True)
def host(request):
    return request.config.getoption("--host")


@pytest.fixture(scope="module", autouse=True)
def port(request):
    return request.config.getoption("--port")


@pytest.fixture(scope="module", autouse=True)
def is_loadbalancer(request):
    return request.config.getoption("--is_loadbalancer")


@pytest.fixture(scope="module", autouse=True)
def with_latency(request):
    return request.config.getoption("--with_latency")


@pytest.fixture(scope="module", autouse=True)
def extensive_vector_search(request):
    return request.config.getoption("--extensive_vector_search")
