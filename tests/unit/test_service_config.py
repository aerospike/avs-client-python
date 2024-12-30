import pytest
from unittest.mock import patch

from aerospike_vector_search import AdminClient, types

import grpc

def test_service_config():
    service_config_path = "../service_configs/backoff_multiplier.json"
    with patch("grpc.insecure_channel") as mock_insecure_channel:
        with open(service_config_path, "rb") as f:
            service_config_json = f.read()
            try:
                client = AdminClient(
                    seeds=types.HostPort(host="localhost", port=8080),
                    service_config_path=service_config_path,
                )
            except Exception as e:
                pass

            mock_insecure_channel.assert_called_with(
                "localhost:8080", options=[("grpc.service_config", service_config_json)]
            )