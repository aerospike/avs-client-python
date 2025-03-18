# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import transact_pb2 as transact__pb2
from . import types_pb2 as types__pb2

GRPC_GENERATED_VERSION = '1.71.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in transact_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TransactServiceStub(object):
    """Record transaction services.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Put = channel.unary_unary(
                '/aerospike.vector.TransactService/Put',
                request_serializer=transact__pb2.PutRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)
        self.Get = channel.unary_unary(
                '/aerospike.vector.TransactService/Get',
                request_serializer=transact__pb2.GetRequest.SerializeToString,
                response_deserializer=types__pb2.Record.FromString,
                _registered_method=True)
        self.Delete = channel.unary_unary(
                '/aerospike.vector.TransactService/Delete',
                request_serializer=transact__pb2.DeleteRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)
        self.Exists = channel.unary_unary(
                '/aerospike.vector.TransactService/Exists',
                request_serializer=transact__pb2.ExistsRequest.SerializeToString,
                response_deserializer=types__pb2.Boolean.FromString,
                _registered_method=True)
        self.IsIndexed = channel.unary_unary(
                '/aerospike.vector.TransactService/IsIndexed',
                request_serializer=transact__pb2.IsIndexedRequest.SerializeToString,
                response_deserializer=types__pb2.Boolean.FromString,
                _registered_method=True)
        self.VectorSearch = channel.unary_stream(
                '/aerospike.vector.TransactService/VectorSearch',
                request_serializer=transact__pb2.VectorSearchRequest.SerializeToString,
                response_deserializer=types__pb2.Neighbor.FromString,
                _registered_method=True)


class TransactServiceServicer(object):
    """Record transaction services.
    """

    def Put(self, request, context):
        """Update/insert records.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """Get a record.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Delete a record.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Exists(self, request, context):
        """Check if a record exists.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def IsIndexed(self, request, context):
        """Check is a record is indexed.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def VectorSearch(self, request, context):
        """Perform a vector nearest neighbor search.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TransactServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=transact__pb2.PutRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=transact__pb2.GetRequest.FromString,
                    response_serializer=types__pb2.Record.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=transact__pb2.DeleteRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'Exists': grpc.unary_unary_rpc_method_handler(
                    servicer.Exists,
                    request_deserializer=transact__pb2.ExistsRequest.FromString,
                    response_serializer=types__pb2.Boolean.SerializeToString,
            ),
            'IsIndexed': grpc.unary_unary_rpc_method_handler(
                    servicer.IsIndexed,
                    request_deserializer=transact__pb2.IsIndexedRequest.FromString,
                    response_serializer=types__pb2.Boolean.SerializeToString,
            ),
            'VectorSearch': grpc.unary_stream_rpc_method_handler(
                    servicer.VectorSearch,
                    request_deserializer=transact__pb2.VectorSearchRequest.FromString,
                    response_serializer=types__pb2.Neighbor.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'aerospike.vector.TransactService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('aerospike.vector.TransactService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TransactService(object):
    """Record transaction services.
    """

    @staticmethod
    def Put(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aerospike.vector.TransactService/Put',
            transact__pb2.PutRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aerospike.vector.TransactService/Get',
            transact__pb2.GetRequest.SerializeToString,
            types__pb2.Record.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aerospike.vector.TransactService/Delete',
            transact__pb2.DeleteRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Exists(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aerospike.vector.TransactService/Exists',
            transact__pb2.ExistsRequest.SerializeToString,
            types__pb2.Boolean.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def IsIndexed(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/aerospike.vector.TransactService/IsIndexed',
            transact__pb2.IsIndexedRequest.SerializeToString,
            types__pb2.Boolean.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def VectorSearch(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/aerospike.vector.TransactService/VectorSearch',
            transact__pb2.VectorSearchRequest.SerializeToString,
            types__pb2.Neighbor.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
