# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import vector_db_pb2 as vector__db__pb2


class AboutStub(object):
    """Information about the service."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Get = channel.unary_unary(
            "/aerospike.vector.About/Get",
            request_serializer=vector__db__pb2.AboutRequest.SerializeToString,
            response_deserializer=vector__db__pb2.AboutResponse.FromString,
        )


class AboutServicer(object):
    """Information about the service."""

    def Get(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_AboutServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "Get": grpc.unary_unary_rpc_method_handler(
            servicer.Get,
            request_deserializer=vector__db__pb2.AboutRequest.FromString,
            response_serializer=vector__db__pb2.AboutResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "aerospike.vector.About", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class About(object):
    """Information about the service."""

    @staticmethod
    def Get(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/aerospike.vector.About/Get",
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
        )


class ClusterInfoStub(object):
    """Vector DB cluster service."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetNodeId = channel.unary_unary(
            "/aerospike.vector.ClusterInfo/GetNodeId",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=vector__db__pb2.NodeId.FromString,
        )
        self.GetClusterId = channel.unary_unary(
            "/aerospike.vector.ClusterInfo/GetClusterId",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=vector__db__pb2.ClusterId.FromString,
        )
        self.GetClusterEndpoints = channel.unary_unary(
            "/aerospike.vector.ClusterInfo/GetClusterEndpoints",
            request_serializer=vector__db__pb2.ClusterNodeEndpointsRequest.SerializeToString,
            response_deserializer=vector__db__pb2.ClusterNodeEndpoints.FromString,
        )
        self.GetOwnedPartitions = channel.unary_unary(
            "/aerospike.vector.ClusterInfo/GetOwnedPartitions",
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=vector__db__pb2.ClusterPartitions.FromString,
        )


class ClusterInfoServicer(object):
    """Vector DB cluster service."""

    def GetNodeId(self, request, context):
        """Get the internal cluster node-Id for this server."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetClusterId(self, request, context):
        """Get current cluster-Id for the current cluster."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetClusterEndpoints(self, request, context):
        """Get the advertised/listening endpoints for all nodes in the cluster, given a listener name."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetOwnedPartitions(self, request, context):
        """Get per-node owned partition list for all nodes in the cluster."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_ClusterInfoServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetNodeId": grpc.unary_unary_rpc_method_handler(
            servicer.GetNodeId,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=vector__db__pb2.NodeId.SerializeToString,
        ),
        "GetClusterId": grpc.unary_unary_rpc_method_handler(
            servicer.GetClusterId,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=vector__db__pb2.ClusterId.SerializeToString,
        ),
        "GetClusterEndpoints": grpc.unary_unary_rpc_method_handler(
            servicer.GetClusterEndpoints,
            request_deserializer=vector__db__pb2.ClusterNodeEndpointsRequest.FromString,
            response_serializer=vector__db__pb2.ClusterNodeEndpoints.SerializeToString,
        ),
        "GetOwnedPartitions": grpc.unary_unary_rpc_method_handler(
            servicer.GetOwnedPartitions,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=vector__db__pb2.ClusterPartitions.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "aerospike.vector.ClusterInfo", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class ClusterInfo(object):
    """Vector DB cluster service."""

    @staticmethod
    def GetNodeId(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/aerospike.vector.ClusterInfo/GetNodeId",
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
        )

    @staticmethod
    def GetClusterId(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/aerospike.vector.ClusterInfo/GetClusterId",
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
        )

    @staticmethod
    def GetClusterEndpoints(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/aerospike.vector.ClusterInfo/GetClusterEndpoints",
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
        )

    @staticmethod
    def GetOwnedPartitions(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/aerospike.vector.ClusterInfo/GetOwnedPartitions",
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            vector__db__pb2.ClusterPartitions.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
