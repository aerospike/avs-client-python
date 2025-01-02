# Aerospike Vector Search Client Python
Python client for the Aerospike Vector Search Database

## Prerequisites
 - Python 3.9 or higher
 - pip version 9.0.1 or higher
 - Aerospike Vector Search DB and Aerospike clusters running.

### Install the aerospike_vector_search using pip
```shell
python3 -m pip install aerospike-vector-search
```
Or 

You can add the package name `aerospike-vector-search` to your application's `requirements.txt` and install all dependencies using
```shell
python3 -m pip install -r requirements.txt
```

## Installing from Artifactory/Jfrog
The Aerospike Vector Search client is also available on our own Artifactory repository.
To resolve the Artifactory client packages, pip install with the following command.

```shell
pip install aerospike-vector-search -i https://<jfrog-username>:<jfrog-access-token>@aerospike.jfrog.io/artifactory/api/pypi/ecosystem-python-dev-local/simple 
```

**Note**
This project makes use of the warnings module to communicate deprecations and upcoming changes.
Run your project with the `-Wd` Python flag or the `PYTHONWARNINGS=default` environment variable to display relevant warnings.

## Building the client
### Setup the Python Virtual Environment
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

See [examples](https://github.com/aerospike/aerospike-vector) for sample projects.
