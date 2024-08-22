import pytest

from aerospike_vector_search import Client
from aerospike_vector_search.admin import Client as AdminClient
from aerospike_vector_search import types


@pytest.fixture(scope="module", autouse=True)
def drop_all_indexes(
    username,
    password,
    root_certificate,
    host,
    port,
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

    with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        is_loadbalancer=is_loadbalancer,
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_overridessl_target_name_override,
    ) as client:
        index_list = client.index_list()

        tasks = []
        for item in index_list:
            client.index_drop(namespace="test", name=item["id"]["name"])


@pytest.fixture(scope="module")
def session_rbac_admin_client(
    username,
    password,
    root_certificate,
    host,
    port,
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
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_overridessl_target_name_override,
    )
    yield client
    client.close()
