#!/usr/bin/env bash

cd "$(dirname "$0")"

# Generate the gRPC client code
python3 -m pip install grpcio-tools
python3 -m grpc_tools.protoc \
  --proto_path=. \
  --python_out=../src/aerospike_vector/private \
  --grpc_python_out=../src/aerospike_vector/private \
  *.proto

# The generated imports are not relative and fail in generated packages.
# Fix with relative imports.
find ../src/aerospike_vector/private -name "*.py" -exec sed -i -e 's/^import \(.*\)_pb2 /from . import \1_pb2 /g' {} \;
