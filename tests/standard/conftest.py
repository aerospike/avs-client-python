import asyncio
import random
import string
import threading

from aerospike_vector_search import Client
from aerospike_vector_search.aio import Client as AsyncClient
from aerospike_vector_search import types, AVSServerError

from utils import gen_records, DEFAULT_NAMESPACE, DEFAULT_INDEX_DIMENSION, DEFAULT_VECTOR_FIELD, DEFAULT_INDEX_MODE
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
    "mode": DEFAULT_INDEX_MODE,
}

STANDALONE_INDEX_ARGS = {
    "namespace": DEFAULT_NAMESPACE,
    "vector_field": DEFAULT_VECTOR_FIELD,
    "dimensions": DEFAULT_INDEX_DIMENSION,
    "mode": types.IndexMode.STANDALONE,
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

    with Client(
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


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """
    Create an event loop that runs in a separate thread.
    The async client requires a running event loop at initialization.
    """
    loop = asyncio.new_event_loop()

    # Define the target function to run the loop
    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    # Start the event loop in a background thread
    loop_thread = threading.Thread(target=run_loop, daemon=True)
    loop_thread.start()

    yield loop

    # Stop the event loop and wait for the thread to finish
    loop.call_soon_threadsafe(loop.stop)
    loop_thread.join()
    loop.close()


async def new_wrapped_async_client(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    is_loadbalancer,
    ssl_target_name_override,
    loop
):
    return AsyncClient(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override
    )


async def new_wrapped_async_index(
    client,
    name,
    namespace,
):
    return client.index(
        name=name,
        namespace=namespace,
    )


class AsyncClientWrapper():
    def __init__(self, client, loop):
        self.client = client
        self.loop = loop
    
    def __getattr__(self, name):
        attr = getattr(self.client, name)
        if asyncio.iscoroutinefunction(attr):
            # Wrap async methods to run in the current event loop
            def sync_method(*args, **kwargs):
                return self._run_async_task(attr(*args, **kwargs))

            return sync_method
        return attr
    
    def _run_async_task(self, task):
        # Submit the coroutine to the loop and get its result
        if self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(task, self.loop)
            return future.result()
        else:
            raise RuntimeError("Event loop is not running")


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
        task = new_wrapped_async_client(
            host=host,
            port=port,
            username=username,
            password=password,
            root_certificate=root_certificate,
            certificate_chain=certificate_chain,
            private_key=private_key,
            is_loadbalancer=is_loadbalancer,
            ssl_target_name_override=ssl_target_name_override,
            loop=event_loop
        )
        client = asyncio.run_coroutine_threadsafe(task, event_loop).result()
        client = AsyncClientWrapper(client, event_loop)
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

    if not client.closed:
        client.close()


@pytest.fixture(scope="function")
def index_obj(event_loop, async_client, session_vector_client, index):
    if async_client:
        idxobj = AsyncClientWrapper(session_vector_client.index(
            name=index,
            namespace=DEFAULT_NAMESPACE,
        ), event_loop)
    else:
        idxobj = session_vector_client.index(
            name=index,
            namespace=DEFAULT_NAMESPACE,
        )

    yield idxobj


@pytest.fixture()
def index_name():
    length = random.randint(1, 15)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest.fixture(params=[DEFAULT_INDEX_ARGS])
def index(session_vector_client, index_name, request):
    args = request.param
    namespace = args.get("namespace", DEFAULT_NAMESPACE)
    vector_field = args.get("vector_field", DEFAULT_VECTOR_FIELD) 
    dimensions = args.get("dimensions", DEFAULT_INDEX_DIMENSION)
    mode = args.get("mode", DEFAULT_INDEX_MODE)
    session_vector_client.index_create(
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
        ),
        mode=mode
    )
    yield index_name
    try:
        session_vector_client.index_drop(namespace=namespace, name=index_name)
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
