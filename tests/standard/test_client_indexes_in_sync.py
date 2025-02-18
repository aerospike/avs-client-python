import pytest
import grpc
import time

from aerospike_vector_search import Client, types, AVSServerError
from aerospike_vector_search.aio import Client as AioClient
from utils import DEFAULT_NAMESPACE, DEFAULT_INDEX_DIMENSION, DEFAULT_VECTOR_FIELD, wait_for_index


def test_index(session_vector_client, index):
    client = session_vector_client
    # long timeout just in case test environment is very slow
    client.indexes_in_sync(timeout=9999)
