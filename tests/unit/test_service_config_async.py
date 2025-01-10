import pytest
from unittest.mock import patch

from aerospike_vector_search import types
from aerospike_vector_search.aio import Client

import grpc

async def test_service_config():
    # NOTE: this path is relative to the tests directory
    service_config_path = "service_configs/backoff_multiplier.json"
    with patch("grpc.aio.insecure_channel") as mock_insecure_channel:
        with open(service_config_path, "rb") as f:
            service_config_json = f.read()
            try:
                client = Client(
                    seeds=types.HostPort(host="localhost", port=8080),
                    service_config_path=service_config_path,
                )
            except Exception as e:
                pass

            mock_insecure_channel.assert_called_with(
                "localhost:8080", options=[("grpc.service_config", service_config_json)]
            )


async def test_service_config_secure():
    # NOTE: this path is relative to the tests directory
    service_config_path = "service_configs/backoff_multiplier.json"
    # mock ssl_channel_credentials so that it doesn't throw an error
    # when passed the fake root certificate
    with patch("grpc.ssl_channel_credentials") as mock_ssl_channel_credentials:
        mock_ssl_channel_credentials.return_value = "fake_ssl_credentials"
        with patch("grpc.aio.secure_channel") as mock_secure_channel:
            with open(service_config_path, "rb") as f:
                service_config_json = f.read()
                try:
                    client = Client(
                        seeds=types.HostPort(host="localhost", port=8080),
                        service_config_path=service_config_path,
                        root_certificate="trigger_secure_path",
                    )
                except Exception as e:
                    pass

                mock_secure_channel.assert_called_with(
                    "localhost:8080",
                    mock_ssl_channel_credentials.return_value,
                    options=[("grpc.service_config", service_config_json)]
                )