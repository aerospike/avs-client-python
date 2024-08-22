import pytest
import asyncio
from aerospike_vector_search.aio import Client
from aerospike_vector_search.aio.admin import Client as AdminClient
from aerospike_vector_search import types

#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


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
