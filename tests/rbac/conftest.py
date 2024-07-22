import pytest


def pytest_addoption(parser):
    parser.addoption("--username", action="store", default="admin", help="AVS Username")
    parser.addoption("--password", action="store", default="admin", help="AVS Password")
    parser.addoption("--host", action="store", default="localhost", help="AVS Host")
    parser.addoption("--port", action="store", default=5000, help="AVS Port")
    parser.addoption("--root_certificate", action="store", default=None, help="Path to root CA certificate")
    parser.addoption("--certificate_chain", action="store", default=None, help="Path to certificate chain")
    parser.addoption("--private_key", action="store", default=None, help="Path to private key")
    parser.addoption("--is_loadbalancer", action="store_true", help="Enable to use load balancer tending logic")


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
def host(request):
    return request.config.getoption("--host")

@pytest.fixture(scope="module", autouse=True)
def port(request):
    return request.config.getoption("--port")

@pytest.fixture(scope="module", autouse=True)
def is_loadbalancer(request):
    return request.config.getoption("--is_loadbalancer")