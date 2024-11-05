import time
from .. import types
from .proto_generated import types_pb2, index_pb2
from .proto_generated import index_pb2_grpc
from typing import Union, Tuple, Optional


def _prepare_seeds(seeds: Union[types.HostPort, Tuple[types.HostPort, ...]]) -> Tuple[types.HostPort, ...]:

    if not seeds:
        raise types.AVSClientError(message="at least one seed host needed")

    if isinstance(seeds, types.HostPort):
        seeds = (seeds,)

    return tuple(seeds)


def _prepare_wait_for_index_waiting(client, namespace: str, name: str, wait_interval: Optional[int]) -> (
        Tuple)[index_pb2_grpc.IndexServiceStub, int, float, bool, int, index_pb2.IndexGetRequest]:

    unmerged_record_initialized = False
    start_time = time.monotonic()
    consecutive_index_validations = 0

    index_stub = index_pb2_grpc.IndexServiceStub(client._channel_provider.get_channel())
    index_id = types_pb2.IndexId(namespace=namespace, name=name)
    index_wait_request = index_pb2.IndexGetRequest(indexId=index_id)
    return (
        index_stub,
        wait_interval,
        start_time,
        unmerged_record_initialized,
        consecutive_index_validations,
        index_wait_request,
    )


def _get_credentials(username: str, password: str) -> Optional[types_pb2.Credentials]:
    if not username:
        return None
    return types_pb2.Credentials(
        username=username,
        passwordCredentials=types_pb2.PasswordCredentials(password=password),
    )
