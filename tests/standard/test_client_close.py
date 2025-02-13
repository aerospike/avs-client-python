import pytest
from aerospike_vector_search import types


def test_close(session_vector_client):
    session_vector_client.close()
    assert session_vector_client.closed == True


def test_use_after_close(session_vector_client):
    client = session_vector_client
    assert client.closed == False

    client.close()
    assert client.closed == True

    # When the client is closed, all public methods should be patched with
    # the _raise_closed method that raises an AVSClientErrorClosed error
    for attr_name in dir(client):
        attr = getattr(client, attr_name)
        if callable(attr) and not attr_name.startswith("_"):
            with pytest.raises(types.AVSClientErrorClosed):
                attr()
