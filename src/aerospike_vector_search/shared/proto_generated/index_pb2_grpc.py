# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import index_pb2 as index__pb2
from . import types_pb2 as types__pb2

GRPC_GENERATED_VERSION = '1.66.2'
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
        + f' but the generated code in index_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class IndexServiceStub(object):
    """Service to manage indices.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Create = channel.unary_unary(
                '/aerospike.vector.IndexService/Create',
                request_serializer=index__pb2.IndexCreateRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/aerospike.vector.IndexService/Update',
                request_serializer=index__pb2.IndexUpdateRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)
        self.Drop = channel.unary_unary(
                '/aerospike.vector.IndexService/Drop',
                request_serializer=index__pb2.IndexDropRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)
        self.List = channel.unary_unary(
                '/aerospike.vector.IndexService/List',
                request_serializer=index__pb2.IndexListRequest.SerializeToString,
                response_deserializer=types__pb2.IndexDefinitionList.FromString,
                _registered_method=True)
        self.Get = channel.unary_unary(
                '/aerospike.vector.IndexService/Get',
                request_serializer=index__pb2.IndexGetRequest.SerializeToString,
                response_deserializer=types__pb2.IndexDefinition.FromString,
                _registered_method=True)
        self.GetStatus = channel.unary_unary(
                '/aerospike.vector.IndexService/GetStatus',
                request_serializer=index__pb2.IndexStatusRequest.SerializeToString,
                response_deserializer=index__pb2.IndexStatusResponse.FromString,
                _registered_method=True)
        self.GcInvalidVertices = channel.unary_unary(
                '/aerospike.vector.IndexService/GcInvalidVertices',
                request_serializer=index__pb2.GcInvalidVerticesRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)


class IndexServiceServicer(object):
    """Service to manage indices.
    """

    def Create(self, request, context):
        """Create an index.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Update(self, request, context):
        """Create an index.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Drop(self, request, context):
        """Drop an index.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        """List available indices.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """Get the index definition.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStatus(self, request, context):
        """Query status of an index.
        NOTE: API is subject to change.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GcInvalidVertices(self, request, context):
        """Garbage collect vertices identified as invalid before cutoff timestamp.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_IndexServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=index__pb2.IndexCreateRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=index__pb2.IndexUpdateRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'Drop': grpc.unary_unary_rpc_method_handler(
                    servicer.Drop,
                    request_deserializer=index__pb2.IndexDropRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'List': grpc.unary_unary_rpc_method_handler(
                    servicer.List,
                    request_deserializer=index__pb2.IndexListRequest.FromString,
                    response_serializer=types__pb2.IndexDefinitionList.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=index__pb2.IndexGetRequest.FromString,
                    response_serializer=types__pb2.IndexDefinition.SerializeToString,
            ),
            'GetStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStatus,
                    request_deserializer=index__pb2.IndexStatusRequest.FromString,
                    response_serializer=index__pb2.IndexStatusResponse.SerializeToString,
            ),
            'GcInvalidVertices': grpc.unary_unary_rpc_method_handler(
                    servicer.GcInvalidVertices,
                    request_deserializer=index__pb2.GcInvalidVerticesRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'aerospike.vector.IndexService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('aerospike.vector.IndexService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class IndexService(object):
    """Service to manage indices.
    """

    @staticmethod
    def Create(request,
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
            '/aerospike.vector.IndexService/Create',
            index__pb2.IndexCreateRequest.SerializeToString,
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
    def Update(request,
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
            '/aerospike.vector.IndexService/Update',
            index__pb2.IndexUpdateRequest.SerializeToString,
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
    def Drop(request,
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
            '/aerospike.vector.IndexService/Drop',
            index__pb2.IndexDropRequest.SerializeToString,
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
    def List(request,
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
            '/aerospike.vector.IndexService/List',
            index__pb2.IndexListRequest.SerializeToString,
            types__pb2.IndexDefinitionList.FromString,
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
            '/aerospike.vector.IndexService/Get',
            index__pb2.IndexGetRequest.SerializeToString,
            types__pb2.IndexDefinition.FromString,
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
    def GetStatus(request,
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
            '/aerospike.vector.IndexService/GetStatus',
            index__pb2.IndexStatusRequest.SerializeToString,
            index__pb2.IndexStatusResponse.FromString,
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
    def GcInvalidVertices(request,
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
            '/aerospike.vector.IndexService/GcInvalidVertices',
            index__pb2.GcInvalidVerticesRequest.SerializeToString,
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
