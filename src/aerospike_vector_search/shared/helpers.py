import time
from .. import types
from .proto_generated import types_pb2
from .proto_generated import index_pb2_grpc

def prepare_seeds(seeds) -> None:

    if not seeds:
        raise Exception("at least one seed host needed")

    if isinstance(seeds, types.HostPort):
        seeds = (seeds,)

    return seeds


def prepare_wait_for_index_waiting(self, namespace, name):

    wait_interval = 5
    unmerged_record_initialized = False
    start_time = time.monotonic()
    double_check = False

    index_stub = index_pb2_grpc.IndexServiceStub(
        self._channelProvider.get_channel()
    )
    index_wait_request = types_pb2.IndexId(namespace=namespace, name=name)
    return (index_stub, wait_interval, start_time, unmerged_record_initialized, False, index_wait_request)
