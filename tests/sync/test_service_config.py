import pytest
import time
from aerospike_vector_search import AVSServerError, types
from aerospike_vector_search import AdminClient

class service_config_parse_test_case:
    def __init__(
        self,
        *,
        max_attempts,
        initial_backoff,
        max_backoff,
        backoff_multiplier,
        retryable_status_codes,
    ):
        self.max_attempts = max_attempts
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self.retryable_status_codes = retryable_status_codes

@pytest.mark.parametrize(
    "test_case",
    [
        service_config_parse_test_case(
            max_attempts=4,
            initial_backoff=None,
            max_backoff=None,
            backoff_multiplier=None,
            retryable_status_codes=None,
        ),
        service_config_parse_test_case(
            max_attempts=None,
            initial_backoff=0.3,
            max_backoff=None,
            backoff_multiplier=None,
            retryable_status_codes=None,
        ),
        service_config_parse_test_case(
            max_attempts=None,
            initial_backoff=None,
            max_backoff=3,
            backoff_multiplier=None,
            retryable_status_codes=None,
        ),
        service_config_parse_test_case(
            max_attempts=None,
            initial_backoff=None,
            max_backoff=None,
            backoff_multiplier=1.75,
            retryable_status_codes=None,
        ),
        service_config_parse_test_case(
            max_attempts=4,
            initial_backoff=0.3,
            max_backoff=3,
            backoff_multiplier=1.75,
            retryable_status_codes=None,
        )
    ],
)
def test_admin_client_service_config_parse(get_host, get_port, test_case):
    client = AdminClient(
        seeds=types.HostPort(host=get_host, port=get_port),
        max_attempts=test_case.max_attempts,
        initial_backoff=test_case.initial_backoff,
        backoff_multiplier=test_case.backoff_multiplier,
        max_backoff=test_case.max_backoff,
        retryable_status_codes=test_case.retryable_status_codes
    )
    client.close()

class service_config_test_case:
    def __init__(
        self,
        *,
        max_attempts,
        initial_backoff,
        max_backoff,
        backoff_multiplier,
        retryable_status_codes,
        namespace,
        name,
        vector_field,
        dimensions
    ):
        self.max_attempts = max_attempts
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self.retryable_status_codes = retryable_status_codes
        self.namespace = namespace
        self.name = name
        self.vector_field = vector_field
        self.dimensions = dimensions


def calculate_expected_time(max_attempts, initial_backoff, backoff_multiplier, max_backoff, retryable_status_codes):

    current_backkoff = initial_backoff

    expected_time = 0
    for attempt in range(max_attempts-1):
        expected_time += current_backkoff
        current_backkoff *= backoff_multiplier
        current_backkoff = min(current_backkoff, max_backoff)

    return expected_time

@pytest.mark.parametrize(
    "test_case",
    [

        service_config_test_case(
            max_attempts=5,
            initial_backoff=1,
            backoff_multiplier=1,
            max_backoff=1,
            retryable_status_codes=["ALREADY_EXISTS"],
            namespace="test",
            name="service_config_index_1",
            vector_field="example_1",
            dimensions=1024
        )
    ],
)
def test_admin_client_service_config_retries(get_host, get_port, test_case):
    client = AdminClient(
        seeds=types.HostPort(host=get_host, port=get_port),
        max_attempts=test_case.max_attempts,
        initial_backoff=test_case.initial_backoff,
        backoff_multiplier=test_case.backoff_multiplier,
        max_backoff=test_case.max_backoff,
        retryable_status_codes=test_case.retryable_status_codes
    )


    client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
    )

    expected_time = calculate_expected_time(test_case.max_attempts, test_case.initial_backoff, test_case.backoff_multiplier, test_case.max_backoff, test_case.retryable_status_codes)
    start_time = time.time()

    with pytest.raises(AVSServerError) as e_info:
        client.index_create(
            namespace=test_case.namespace,
            name=test_case.name,
            vector_field=test_case.vector_field,
            dimensions=test_case.dimensions,
        )

    end_time = time.time()
    elapsed_time = end_time - start_time

    assert abs(elapsed_time - expected_time) < 1.2
    client.close()

@pytest.mark.parametrize(
    "test_case",
    [

        service_config_test_case(
            max_attempts=2,
            initial_backoff=5,
            backoff_multiplier=1,
            max_backoff=1,
            retryable_status_codes=["ALREADY_EXISTS"],
            namespace="test",
            name="service_config_index_2",
            vector_field="example_1",
            dimensions=1024
        )
    ],
)
def test_admin_client_service_config_initial_backoff(get_host, get_port, test_case):
    client = AdminClient(
        seeds=types.HostPort(host=get_host, port=get_port),
        max_attempts=test_case.max_attempts,
        initial_backoff=test_case.initial_backoff,
        backoff_multiplier=test_case.backoff_multiplier,
        max_backoff=test_case.max_backoff,
        retryable_status_codes=test_case.retryable_status_codes
    )

    
    client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
    )

    expected_time = calculate_expected_time(test_case.max_attempts, test_case.initial_backoff, test_case.backoff_multiplier, test_case.max_backoff, test_case.retryable_status_codes)
    start_time = time.time()

    with pytest.raises(AVSServerError) as e_info:
        client.index_create(
            namespace=test_case.namespace,
            name=test_case.name,
            vector_field=test_case.vector_field,
            dimensions=test_case.dimensions,
        )

    end_time = time.time()
    elapsed_time = end_time - start_time

    assert abs(elapsed_time - expected_time) < 1.2
    client.close()

@pytest.mark.parametrize(
    "test_case",
    [

        service_config_test_case(
            max_attempts=4,
            initial_backoff=1,
            backoff_multiplier=2,
            max_backoff=1,
            retryable_status_codes=["ALREADY_EXISTS"],
            namespace="test",
            name="service_config_index_3",
            vector_field="example_1",
            dimensions=1024
        ),
        service_config_test_case(
            max_attempts=5,
            initial_backoff=2,
            backoff_multiplier=2,
            max_backoff=1,
            retryable_status_codes=["ALREADY_EXISTS"],
            namespace="test",
            name="service_config_index_4",
            vector_field="example_1",
            dimensions=1024
        )
    ],
)
def test_admin_client_service_config_max_backoff(get_host, get_port, test_case):
    client = AdminClient(
        seeds=types.HostPort(host=get_host, port=get_port),
        max_attempts=test_case.max_attempts,
        initial_backoff=test_case.initial_backoff,
        backoff_multiplier=test_case.backoff_multiplier,
        max_backoff=test_case.max_backoff,
        retryable_status_codes=test_case.retryable_status_codes
    )

    
    client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
    )

    expected_time = calculate_expected_time(test_case.max_attempts, test_case.initial_backoff, test_case.backoff_multiplier, test_case.max_backoff, test_case.retryable_status_codes)
    start_time = time.time()

    with pytest.raises(AVSServerError) as e_info:
        client.index_create(
            namespace=test_case.namespace,
            name=test_case.name,
            vector_field=test_case.vector_field,
            dimensions=test_case.dimensions,
        )

    end_time = time.time()
    elapsed_time = end_time - start_time
    assert abs(elapsed_time - expected_time) < 1.2

    client.close()

@pytest.mark.parametrize(
    "test_case",
    [

        service_config_test_case(
            max_attempts=4,
            initial_backoff=1,
            backoff_multiplier=3,
            max_backoff=5,
            retryable_status_codes=["ALREADY_EXISTS"],
            namespace="test",
            name="service_config_index_5",
            vector_field="example_1",
            dimensions=1024
        )
    ],
)
def test_admin_client_service_config_backoff_multiplier(get_host, get_port, test_case):
    client = AdminClient(
        seeds=types.HostPort(host=get_host, port=get_port),
        max_attempts=test_case.max_attempts,
        initial_backoff=test_case.initial_backoff,
        backoff_multiplier=test_case.backoff_multiplier,
        max_backoff=test_case.max_backoff,
        retryable_status_codes=test_case.retryable_status_codes
    )

    
    client.index_create(
        namespace=test_case.namespace,
        name=test_case.name,
        vector_field=test_case.vector_field,
        dimensions=test_case.dimensions,
    )

    expected_time = calculate_expected_time(test_case.max_attempts, test_case.initial_backoff, test_case.backoff_multiplier, test_case.max_backoff, test_case.retryable_status_codes)
    start_time = time.time()

    with pytest.raises(AVSServerError) as e_info:
        client.index_create(
            namespace=test_case.namespace,
            name=test_case.name,
            vector_field=test_case.vector_field,
            dimensions=test_case.dimensions,
        )

    end_time = time.time()
    elapsed_time = end_time - start_time
    assert abs(elapsed_time - expected_time) < 1.2

    client.close()

@pytest.mark.parametrize(
    "test_case",
    [

        service_config_test_case(
            max_attempts=2,
            initial_backoff=5,
            backoff_multiplier=1,
            max_backoff=1,
            retryable_status_codes=["NOT_FOUND"],
            namespace="test",
            name="service_config_index_6",
            vector_field=None,
            dimensions=None
        )
    ],
)
def test_admin_client_service_config_retryable_status_codes(get_host, get_port, test_case):
    client = AdminClient(
        seeds=types.HostPort(host=get_host, port=get_port),
        max_attempts=test_case.max_attempts,
        initial_backoff=test_case.initial_backoff,
        backoff_multiplier=test_case.backoff_multiplier,
        max_backoff=test_case.max_backoff,
        retryable_status_codes=test_case.retryable_status_codes
    )

    expected_time = calculate_expected_time(test_case.max_attempts, test_case.initial_backoff, test_case.backoff_multiplier, test_case.max_backoff, test_case.retryable_status_codes)
    start_time = time.time()
    
    with pytest.raises(AVSServerError) as e_info:
        client.index_get_status(
            namespace=test_case.namespace,
            name=test_case.name,
        )

    end_time = time.time()
    elapsed_time = end_time - start_time
    assert abs(elapsed_time - expected_time) < 1.2


    client.close()