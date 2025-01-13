import pytest
from unittest.mock import patch

from aerospike_vector_search import Client, types

import grpc


def test_channel_no_options():
    # NOTE: this path is relative to the tests directory
    with patch("grpc.insecure_channel") as mock_insecure_channel:
        try:
            client = Client(
                seeds=types.HostPort(host="localhost", port=8080),
            )
        except Exception as e:
            pass

        mock_insecure_channel.assert_called_with(
            "localhost:8080",
            options=None
        )


def test_channel_insecure():
    # NOTE: this path is relative to the tests directory
    service_config_path = "service_configs/backoff_multiplier.json"
    with patch("grpc.insecure_channel") as mock_insecure_channel:
        with open(service_config_path, "rb") as f:
            service_config_json = f.read()
            try:
                client = Client(
                    seeds=types.HostPort(host="localhost", port=8080),
                    service_config_path=service_config_path,
                    ssl_target_name_override="test_ssl_name",
                )
            except Exception as e:
                pass

            mock_insecure_channel.assert_called_with(
                "localhost:8080",
                options=[
                    ("grpc.ssl_target_name_override", "test_ssl_name"),
                    ("grpc.service_config", service_config_json)
                ]
            )


def test_channel_secure():
    # NOTE: this path is relative to the tests directory
    service_config_path = "service_configs/backoff_multiplier.json"
    # mock ssl_channel_credentials so that it doesn't throw an error
    # when passed the fake root certificate
    with patch("grpc.ssl_channel_credentials") as mock_ssl_channel_credentials:
        mock_ssl_channel_credentials.return_value = "fake_ssl_credentials"
        with patch("grpc.secure_channel") as mock_secure_channel:
            with open(service_config_path, "rb") as f:
                service_config_json = f.read()
                try:
                    client = Client(
                        seeds=types.HostPort(host="localhost", port=8080),
                        service_config_path=service_config_path,
                        root_certificate="trigger_secure_path",
                        ssl_target_name_override="test_ssl_name",
                    )
                except Exception as e:
                    pass

                mock_secure_channel.assert_called_with(
                    "localhost:8080",
                    mock_ssl_channel_credentials.return_value,
                    options=[
                        ("grpc.ssl_target_name_override", "test_ssl_name"),
                        ("grpc.service_config", service_config_json)
                    ]
                )