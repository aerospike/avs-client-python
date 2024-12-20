import pytest
import time

import os
import json

from aerospike_vector_search import AVSServerError, types
from aerospike_vector_search.aio import AdminClient


class service_config_parse_test_case:
    def __init__(self, *, service_config_path):
        self.service_config_path = service_config_path


@pytest.mark.parametrize(
    "test_case",
    [
        service_config_parse_test_case(
            service_config_path="service_configs/master.json"
        ),
    ],
)
async def test_admin_client_service_config_parse(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    test_case,
):

    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    async with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        service_config_path=test_case.service_config_path,
    ) as client:
        pass


class service_config_test_case:
    def __init__(
        self, *, service_config_path, namespace, name, vector_field, dimensions
    ):

        script_dir = os.path.dirname(os.path.abspath(__file__))

        self.service_config_path = os.path.abspath(
            os.path.join(script_dir, "..", "..", service_config_path)
        )

        with open(self.service_config_path, "rb") as f:
            self.service_config = json.load(f)

        self.max_attempts = self.service_config["methodConfig"][0]["retryPolicy"][
            "maxAttempts"
        ]
        self.initial_backoff = int(
            self.service_config["methodConfig"][0]["retryPolicy"]["initialBackoff"][:-1]
        )
        self.max_backoff = int(
            self.service_config["methodConfig"][0]["retryPolicy"]["maxBackoff"][:-1]
        )
        self.backoff_multiplier = self.service_config["methodConfig"][0]["retryPolicy"][
            "backoffMultiplier"
        ]
        self.retryable_status_codes = self.service_config["methodConfig"][0][
            "retryPolicy"
        ]["retryableStatusCodes"]
        self.namespace = namespace
        self.name = name
        self.vector_field = vector_field
        self.dimensions = dimensions


def calculate_expected_time(
    max_attempts,
    initial_backoff,
    backoff_multiplier,
    max_backoff,
    retryable_status_codes,
):

    current_backkoff = initial_backoff

    expected_time = 0
    for attempt in range(max_attempts - 1):
        expected_time += current_backkoff
        current_backkoff *= backoff_multiplier
        current_backkoff = min(current_backkoff, max_backoff)

    return expected_time


@pytest.mark.parametrize(
    "test_case",
    [
        service_config_test_case(
            service_config_path="service_configs/retries.json",
            namespace="test",
            name="service_config_index_1",
            vector_field="example_1",
            dimensions=1024,
        )
    ],
)
async def test_admin_client_service_config_retries(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    test_case,
):

    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    async with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        service_config_path=test_case.service_config_path,
    ) as client:
        try:
            await client.index_create(
                namespace=test_case.namespace,
                name=test_case.name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
            )
        except:
            pass
        expected_time = calculate_expected_time(
            test_case.max_attempts,
            test_case.initial_backoff,
            test_case.backoff_multiplier,
            test_case.max_backoff,
            test_case.retryable_status_codes,
        )
        start_time = time.time()

        with pytest.raises(AVSServerError) as e_info:
            await client.index_create(
                namespace=test_case.namespace,
                name=test_case.name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
            )

        end_time = time.time()
        elapsed_time = end_time - start_time

        assert abs(elapsed_time - expected_time) < 1.5


@pytest.mark.parametrize(
    "test_case",
    [
        service_config_test_case(
            service_config_path="service_configs/initial_backoff.json",
            namespace="test",
            name="service_config_index_2",
            vector_field="example_1",
            dimensions=1024,
        )
    ],
)
async def test_admin_client_service_config_initial_backoff(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    test_case,
):

    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    async with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        service_config_path=test_case.service_config_path,
    ) as client:

        try:
            await client.index_create(
                namespace=test_case.namespace,
                name=test_case.name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
            )
        except:
            pass

        expected_time = calculate_expected_time(
            test_case.max_attempts,
            test_case.initial_backoff,
            test_case.backoff_multiplier,
            test_case.max_backoff,
            test_case.retryable_status_codes,
        )
        start_time = time.time()

        with pytest.raises(AVSServerError) as e_info:
            await client.index_create(
                namespace=test_case.namespace,
                name=test_case.name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
            )

        end_time = time.time()
        elapsed_time = end_time - start_time

    assert abs(elapsed_time - expected_time) < 1.5


@pytest.mark.parametrize(
    "test_case",
    [
        service_config_test_case(
            service_config_path="service_configs/max_backoff.json",
            namespace="test",
            name="service_config_index_3",
            vector_field="example_1",
            dimensions=1024,
        ),
        service_config_test_case(
            service_config_path="service_configs/max_backoff_lower_than_initial.json",
            namespace="test",
            name="service_config_index_4",
            vector_field="example_1",
            dimensions=1024,
        ),
    ],
)
async def test_admin_client_service_config_max_backoff(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    test_case,
):

    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    async with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        service_config_path=test_case.service_config_path,
    ) as client:

        try:
            await client.index_create(
                namespace=test_case.namespace,
                name=test_case.name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
            )
        except:
            pass
        expected_time = calculate_expected_time(
            test_case.max_attempts,
            test_case.initial_backoff,
            test_case.backoff_multiplier,
            test_case.max_backoff,
            test_case.retryable_status_codes,
        )
        start_time = time.time()

        with pytest.raises(AVSServerError) as e_info:
            await client.index_create(
                namespace=test_case.namespace,
                name=test_case.name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
            )

        end_time = time.time()
        elapsed_time = end_time - start_time
        assert abs(elapsed_time - expected_time) < 1.5


@pytest.mark.parametrize(
    "test_case",
    [
        service_config_test_case(
            service_config_path="service_configs/backoff_multiplier.json",
            namespace="test",
            name="service_config_index_5",
            vector_field="example_1",
            dimensions=1024,
        )
    ],
)
async def test_admin_client_service_config_backoff_multiplier(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    test_case,
):

    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    async with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        service_config_path=test_case.service_config_path,
    ) as client:

        try:

            await client.index_create(
                namespace=test_case.namespace,
                name=test_case.name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
            )
        except:
            pass

        expected_time = calculate_expected_time(
            test_case.max_attempts,
            test_case.initial_backoff,
            test_case.backoff_multiplier,
            test_case.max_backoff,
            test_case.retryable_status_codes,
        )
        start_time = time.time()

        with pytest.raises(AVSServerError) as e_info:
            await client.index_create(
                namespace=test_case.namespace,
                name=test_case.name,
                vector_field=test_case.vector_field,
                dimensions=test_case.dimensions,
            )

        end_time = time.time()
        elapsed_time = end_time - start_time
        assert abs(elapsed_time - expected_time) < 1.5


@pytest.mark.parametrize(
    "test_case",
    [
        service_config_test_case(
            service_config_path="service_configs/retryable_status_codes.json",
            namespace="test",
            name="service_config_index_6",
            vector_field=None,
            dimensions=None,
        )
    ],
)
async def test_admin_client_service_config_retryable_status_codes(
    host,
    port,
    username,
    password,
    root_certificate,
    certificate_chain,
    private_key,
    ssl_target_name_override,
    test_case,
):

    if root_certificate:
        with open(root_certificate, "rb") as f:
            root_certificate = f.read()

    if certificate_chain:
        with open(certificate_chain, "rb") as f:
            certificate_chain = f.read()
    if private_key:
        with open(private_key, "rb") as f:
            private_key = f.read()

    async with AdminClient(
        seeds=types.HostPort(host=host, port=port),
        username=username,
        password=password,
        root_certificate=root_certificate,
        certificate_chain=certificate_chain,
        private_key=private_key,
        ssl_target_name_override=ssl_target_name_override,
        service_config_path=test_case.service_config_path,
    ) as client:

        expected_time = calculate_expected_time(
            test_case.max_attempts,
            test_case.initial_backoff,
            test_case.backoff_multiplier,
            test_case.max_backoff,
            test_case.retryable_status_codes,
        )
        start_time = time.time()

        with pytest.raises(AVSServerError) as e_info:
            await client.index_get_status(
                namespace=test_case.namespace,
                name=test_case.name,
            )

        end_time = time.time()
        elapsed_time = end_time - start_time
        assert abs(elapsed_time - expected_time) < 2
