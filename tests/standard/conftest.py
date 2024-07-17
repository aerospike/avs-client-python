import pytest


def pytest_addoption(parser):
    parser.addoption("--username", action="store", default=None, help="AVS Username")
    parser.addoption("--password", action="store", default=None, help="AVS Password")
    parser.addoption("--host", action="store", default="localhost", help="AVS Host")
    parser.addoption("--port", action="store", default=5000, help="AVS Port")
    parser.addoption("--root_certificate", action="store", default=None, help="Path to root CA certificate")
    parser.addoption("--certificate_chain", action="store", default=None, help="Path to certificate chain")
    parser.addoption("--private_key", action="store", default=None, help="Path to private key")
    parser.addoption("--local_latency", action="store_true", help="Skip the test if latency is too low to effectively trigger timeout")


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
def local_latency(request):
    return request.config.getoption("--local_latency")
