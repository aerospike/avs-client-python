# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: index.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'index.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import types_pb2 as types__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bindex.proto\x12\x10\x61\x65rospike.vector\x1a\x1bgoogle/protobuf/empty.proto\x1a\x0btypes.proto\"}\n\x13IndexStatusResponse\x12\x1b\n\x13unmergedRecordCount\x18\x02 \x01(\x03\x12\'\n\x1findexHealerVectorRecordsIndexed\x18\x03 \x01(\x03\x12 \n\x18indexHealerVerticesValid\x18\x04 \x01(\x03\"_\n\x18GcInvalidVerticesRequest\x12*\n\x07indexId\x18\x01 \x01(\x0b\x32\x19.aerospike.vector.IndexId\x12\x17\n\x0f\x63utoffTimestamp\x18\x02 \x01(\x03\"K\n\x12IndexCreateRequest\x12\x35\n\ndefinition\x18\x01 \x01(\x0b\x32!.aerospike.vector.IndexDefinition\"\xf9\x01\n\x12IndexUpdateRequest\x12*\n\x07indexId\x18\x01 \x01(\x0b\x32\x19.aerospike.vector.IndexId\x12@\n\x06labels\x18\x02 \x03(\x0b\x32\x30.aerospike.vector.IndexUpdateRequest.LabelsEntry\x12<\n\x0fhnswIndexUpdate\x18\x03 \x01(\x0b\x32!.aerospike.vector.HnswIndexUpdateH\x00\x1a-\n\x0bLabelsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\x08\n\x06update\">\n\x10IndexDropRequest\x12*\n\x07indexId\x18\x01 \x01(\x0b\x32\x19.aerospike.vector.IndexId\"@\n\x10IndexListRequest\x12\x1a\n\rapplyDefaults\x18\x01 \x01(\x08H\x00\x88\x01\x01\x42\x10\n\x0e_applyDefaults\"k\n\x0fIndexGetRequest\x12*\n\x07indexId\x18\x01 \x01(\x0b\x32\x19.aerospike.vector.IndexId\x12\x1a\n\rapplyDefaults\x18\x02 \x01(\x08H\x00\x88\x01\x01\x42\x10\n\x0e_applyDefaults\"@\n\x12IndexStatusRequest\x12*\n\x07indexId\x18\x01 \x01(\x0b\x32\x19.aerospike.vector.IndexId2\xc3\x04\n\x0cIndexService\x12H\n\x06\x43reate\x12$.aerospike.vector.IndexCreateRequest\x1a\x16.google.protobuf.Empty\"\x00\x12H\n\x06Update\x12$.aerospike.vector.IndexUpdateRequest\x1a\x16.google.protobuf.Empty\"\x00\x12\x44\n\x04\x44rop\x12\".aerospike.vector.IndexDropRequest\x1a\x16.google.protobuf.Empty\"\x00\x12S\n\x04List\x12\".aerospike.vector.IndexListRequest\x1a%.aerospike.vector.IndexDefinitionList\"\x00\x12M\n\x03Get\x12!.aerospike.vector.IndexGetRequest\x1a!.aerospike.vector.IndexDefinition\"\x00\x12Z\n\tGetStatus\x12$.aerospike.vector.IndexStatusRequest\x1a%.aerospike.vector.IndexStatusResponse\"\x00\x12Y\n\x11GcInvalidVertices\x12*.aerospike.vector.GcInvalidVerticesRequest\x1a\x16.google.protobuf.Empty\"\x00\x42\x43\n!com.aerospike.vector.client.protoP\x01Z\x1c\x61\x65rospike.com/vector/protos/b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'index_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n!com.aerospike.vector.client.protoP\001Z\034aerospike.com/vector/protos/'
  _globals['_INDEXUPDATEREQUEST_LABELSENTRY']._loaded_options = None
  _globals['_INDEXUPDATEREQUEST_LABELSENTRY']._serialized_options = b'8\001'
  _globals['_INDEXSTATUSRESPONSE']._serialized_start=75
  _globals['_INDEXSTATUSRESPONSE']._serialized_end=200
  _globals['_GCINVALIDVERTICESREQUEST']._serialized_start=202
  _globals['_GCINVALIDVERTICESREQUEST']._serialized_end=297
  _globals['_INDEXCREATEREQUEST']._serialized_start=299
  _globals['_INDEXCREATEREQUEST']._serialized_end=374
  _globals['_INDEXUPDATEREQUEST']._serialized_start=377
  _globals['_INDEXUPDATEREQUEST']._serialized_end=626
  _globals['_INDEXUPDATEREQUEST_LABELSENTRY']._serialized_start=571
  _globals['_INDEXUPDATEREQUEST_LABELSENTRY']._serialized_end=616
  _globals['_INDEXDROPREQUEST']._serialized_start=628
  _globals['_INDEXDROPREQUEST']._serialized_end=690
  _globals['_INDEXLISTREQUEST']._serialized_start=692
  _globals['_INDEXLISTREQUEST']._serialized_end=756
  _globals['_INDEXGETREQUEST']._serialized_start=758
  _globals['_INDEXGETREQUEST']._serialized_end=865
  _globals['_INDEXSTATUSREQUEST']._serialized_start=867
  _globals['_INDEXSTATUSREQUEST']._serialized_end=931
  _globals['_INDEXSERVICE']._serialized_start=934
  _globals['_INDEXSERVICE']._serialized_end=1513
# @@protoc_insertion_point(module_scope)
