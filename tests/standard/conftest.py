import pytest


def pytest_addoption(parser):
    parser.addoption("--username", action="store", default="admin", help="AVS Username")
    parser.addoption("--password", action="store", default="admin", help="AVS Password")
    parser.addoption("--host", action="store", default="localhost", help="AVS Host")
    parser.addoption("--port", action="store", default=5000, help="AVS Port")
    parser.addoption("--root_certificate", action="store", default=None, help="Path to root CA certificate")

@pytest.fixture(scope="module", autouse=True)
def username(request):
    return request.config.getoption("--username")

@pytest.fixture(scope="module", autouse=True)
def password(request):
    return request.config.getoption("--password")

@pytest.fixture(scope="module", autouse=True)
def root_certificate(request):
    return request.config.getoption("--root_certificate")


@pytest.fixture(scope="module", autouse=True)
def host(request):
    return request.config.getoption("--host")

@pytest.fixture(scope="module", autouse=True)
def port(request):
    return request.config.getoption("--port")

