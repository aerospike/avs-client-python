# Aerospike Vector Search Client Python
Python client for Aerospike Vector Search Database

## Prerequisites
 - Python 3.9 or higher
 - pip version 9.0.1 or higher
 - Aerospike Vector Search DB and Aerospike clusters running.


## Using the client from your application using pip
To resolve the client packages using pip, add the following to $HOME/.pip/pip.conf

```ini
[global]
extra-index-url=https://<jfrog-username>:<jfrog-access-token>@aerospike.jfrog.io/artifactory/api/pypi/ecosystem-python-dev-local/simple 
```

### Install the aerospike_vector_search using pip
```shell
python3 -m pip install aerospike-vector-search
```
Or 

You can add the package name `aerospike-vector-search` to your application's `requirements.txt` and install all dependencies using
```shell
python3 -m pip install -r requirements.txt
```

## Building the client
### Setup build Python Virtual Environment
This is the recommended mode for building the python client.

```shell
# Create virtual environment to isolate dependencies.
python3 -m venv .venv
source .venv/bin/activate
```

### Install requirements
```shell
python3 -m pip install -vvv  -r requirements.txt
```

### Generate gRPC client code
```shell
# Generate the gRPC client code
./proto/codegen.sh
```

### Build the package
```shell
python3 -m pip install build
python3 -m build
```

## Examples

See [examples](https://github.com/aerospike/proximus-examples) for working samples.
