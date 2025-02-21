import time
from typing import Union, Tuple, Optional

from .. import types
from .proto_generated import types_pb2, index_pb2
from .proto_generated import index_pb2_grpc

import google.protobuf.empty_pb2


empty = google.protobuf.empty_pb2.Empty()


def _prepare_seeds(seeds: Union[types.HostPort, Tuple[types.HostPort, ...]]) -> Tuple[types.HostPort, ...]:

    if not seeds:
        raise types.AVSClientError(message="at least one seed host needed")

    if isinstance(seeds, types.HostPort):
        seeds = (seeds,)

    return seeds

def _create_index_status_request(namespace: str, name: str) -> index_pb2.IndexStatusRequest:
    index_id = types_pb2.IndexId(namespace=namespace, name=name)
    return index_pb2.IndexStatusRequest(indexId=index_id)

# TODO: In the future we should reuse service stubs
# perhaps we can wrap the client's channel provider in a service stub provider
# that caches the stubs
def _create_index_service_stub(client) -> index_pb2_grpc.IndexServiceStub:
    return index_pb2_grpc.IndexServiceStub(client._channel_provider.get_channel())

def _prepare_wait_for_index_waiting(client, namespace: str, name: str, wait_interval: int) -> (
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

# _get_index_exclusions is a helper function used in Index object search methods
# to determine which fields to exclude from the results. By default the vector field
# is excluded from the results to avoid sending large amounts of data over the network.
# Users can override this behavior by passing the vector field in the include_fields.
def _get_index_exclusions(vector_field: str, include_fields: Optional[list[str]], exclude_fields: Optional[list[str]]) -> list[str]:
        # exclude vector data from the results by default to
        # avoid sending large amounts of data over the network
        # users can override this by passing the vector field in the include_fields
        exclusions = [vector_field]

        if exclude_fields:
            exclusions.extend(exclude_fields)

        # if the user wants to include the vector field in the results
        # we need to remove it from the exclusions list
        # because exclude_fields takes priority over include_fields
        if include_fields and vector_field in include_fields:
            exclusions.remove(vector_field)
        
        return exclusions 