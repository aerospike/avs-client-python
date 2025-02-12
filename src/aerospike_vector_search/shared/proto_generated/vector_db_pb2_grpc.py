# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import vector_db_pb2 as vector__db__pb2

GRPC_GENERATED_VERSION = '1.70.0'
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
        + f' but the generated code in vector_db_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class AboutServiceStub(object):
    """Information about the service.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Get = channel.unary_unary(
                '/aerospike.vector.AboutService/Get',
                request_serializer=vector__db__pb2.AboutRequest.SerializeToString,
                response_deserializer=vector__db__pb2.AboutResponse.FromString,
                _registered_method=True)


class AboutServiceServicer(object):
    """Information about the service.
    """

    def Get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AboutServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=vector__db__pb2.AboutRequest.FromString,
                    response_serializer=vector__db__pb2.AboutResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'aerospike.vector.AboutService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('aerospike.vector.AboutService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class AboutService(object):
    """Information about the service.
    """

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
            '/aerospike.vector.AboutService/Get',
            vector__db__pb2.AboutRequest.SerializeToString,
            vector__db__pb2.AboutResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)


class ClusterInfoServiceStub(object):
    """Vector DB cluster service.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetNodeId = channel.unary_unary(
                '/aerospike.vector.ClusterInfoService/GetNodeId',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=vector__db__pb2.NodeId.FromString,
                _registered_method=True)
        self.GetClusterId = channel.unary_unary(
                '/aerospike.vector.ClusterInfoService/GetClusterId',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=vector__db__pb2.ClusterId.FromString,
                _registered_method=True)
        self.GetClusteringState = channel.unary_unary(
                '/aerospike.vector.ClusterInfoService/GetClusteringState',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=vector__db__pb2.ClusteringState.FromString,
                _registered_method=True)
        self.GetClusterEndpoints = channel.unary_unary(
                '/aerospike.vector.ClusterInfoService/GetClusterEndpoints',
                request_serializer=vector__db__pb2.ClusterNodeEndpointsRequest.SerializeToString,
                response_deserializer=vector__db__pb2.ClusterNodeEndpoints.FromString,
                _registered_method=True)


class ClusterInfoServiceServicer(object):
    """Vector DB cluster service.
    """

    def GetNodeId(self, request, context):
        """Get the internal cluster node-Id for this server.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetClusterId(self, request, context):
        """Get current cluster-Id for the current cluster.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetClusteringState(self, request, context):
        """Get current cluster-Id for the current cluster.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetClusterEndpoints(self, request, context):
        """Get the advertised/listening endpoints for all nodes in the cluster, given a listener name.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ClusterInfoServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetNodeId': grpc.unary_unary_rpc_method_handler(
                    servicer.GetNodeId,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=vector__db__pb2.NodeId.SerializeToString,
            ),
            'GetClusterId': grpc.unary_unary_rpc_method_handler(
                    servicer.GetClusterId,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=vector__db__pb2.ClusterId.SerializeToString,
            ),
            'GetClusteringState': grpc.unary_unary_rpc_method_handler(
                    servicer.GetClusteringState,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=vector__db__pb2.ClusteringState.SerializeToString,
            ),
            'GetClusterEndpoints': grpc.unary_unary_rpc_method_handler(
                    servicer.GetClusterEndpoints,
                    request_deserializer=vector__db__pb2.ClusterNodeEndpointsRequest.FromString,
                    response_serializer=vector__db__pb2.ClusterNodeEndpoints.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'aerospike.vector.ClusterInfoService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('aerospike.vector.ClusterInfoService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ClusterInfoService(object):
    """Vector DB cluster service.
    """

    @staticmethod
    def GetNodeId(request,
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
            '/aerospike.vector.ClusterInfoService/GetNodeId',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            vector__db__pb2.NodeId.FromString,
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
    def GetClusterId(request,
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
            '/aerospike.vector.ClusterInfoService/GetClusterId',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            vector__db__pb2.ClusterId.FromString,
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
    def GetClusteringState(request,
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
            '/aerospike.vector.ClusterInfoService/GetClusteringState',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            vector__db__pb2.ClusteringState.FromString,
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
    def GetClusterEndpoints(request,
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
            '/aerospike.vector.ClusterInfoService/GetClusterEndpoints',
            vector__db__pb2.ClusterNodeEndpointsRequest.SerializeToString,
            vector__db__pb2.ClusterNodeEndpoints.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
