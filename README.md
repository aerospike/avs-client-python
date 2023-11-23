# Aerospike Proximus Vector Client Python
Python client for Aerospike Proximus VectorDB

## Prerequisites
 - Python 3.8 or higher
 - pip version 9.0.1 or higher

## Using the client from your application using pip
To resolve the client packages using pip, add the following to $HOME/.pip/pip.conf

```ini
[global]
extra-index-url=https://<jfrog-username>:<jfrog-access-token>@aerospike.jfrog.io/artifactory/api/pypi/ecosystem-python-dev-local/simple 
```

### Install the aerospike_vector using pip
```shell
python3 -m pip install aerospike_proximus
```
Or 

You can add the package name `aerospike_proximus` to your application's `requirements.txt` and install all dependencies using
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

### Publish to PyPI repository
Make sure [pyproject.toml](pyproject.toml) has the correct version.

Create or update `$HOME/.pypirc` with following contents

```ini
[distutils]
index-servers = ecosystem-python-dev-local
[ecosystem-python-dev-local]
repository: https://aerospike.jfrog.io/artifactory/api/pypi/ecosystem-python-dev-local
username: <jfrog-username>
password: <jfrog-access-token>
```

### Upload the packages to the repository
```shell
python3 -m pip install twine
python3 -m twine upload --repository ecosystem-python-dev-local dist/*
```

## Examples

See [examples](https://github.com/aerospike/proximus-examples) for working samples.
