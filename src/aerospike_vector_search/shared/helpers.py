import time
from .. import types
from .proto_generated import types_pb2
from .proto_generated import index_pb2_grpc


def _prepare_seeds(seeds) -> None:

    if not seeds:
        raise Exception("at least one seed host needed")

    if isinstance(seeds, types.HostPort):
        seeds = (seeds,)

    return seeds


def _prepare_wait_for_index_waiting(namespace, name, wait_interval):

    unmerged_record_initialized = False
    start_time = time.monotonic()
    consecutive_index_validations = 0

    index_stub = index_pb2_grpc.IndexServiceStub(self._channel_provider.get_channel())
    index_wait_request = types_pb2.IndexId(namespace=namespace, name=name)
    return (
        index_stub,
        wait_interval,
        start_time,
        unmerged_record_initialized,
        consecutive_index_validations,
        index_wait_request,
    )

def _get_credentials(username, password):
    return types_pb2.Credentials(username=username, passwordCredentials=types_pb2.PasswordCredentials(password=password))