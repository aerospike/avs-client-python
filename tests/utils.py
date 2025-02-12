import random
import time
import string

from aerospike_vector_search import types
import hypothesis.strategies as st
from hypothesis import given
import pytest


# default test values
DEFAULT_NAMESPACE = "test"
DEFAULT_INDEX_DIMENSION = 128
DEFAULT_VECTOR_FIELD = "vector"
DEFAULT_INDEX_MODE = types.IndexMode.DISTRIBUTED


def random_int():
    return str(random.randint(0, 50_000))


allowed_chars = (
    list(string.ascii_lowercase)  # a-z
    + list(string.ascii_uppercase)  # A-Z
    + list(string.digits)  # 0-9
    + ["_", "-"]  # _, -, $
)

allowed_chars = (
    list(string.ascii_lowercase)  # a-z
    + list(string.ascii_uppercase)  # A-Z
    + list(string.digits)  # 0-9
    + ["_", "-"]  # _, -, $
)


@pytest.fixture
def random_name():
    while True:
        size = random.randint(1, 63)
        key = ''.join(random.choices(allowed_chars, k=size))
        if key not in ["null"]:
            return key

@pytest.fixture
def random_key():
    while True:
        size = random.randint(1, 100_000)
        key = ''.join(random.choices(allowed_chars, k=size))
        if key not in ["0", "1", "null"]:
            return key


def drop_specified_index(admin_client, namespace, name):
    admin_client.index_drop(namespace=namespace, name=name)


def gen_records(count: int, vec_bin: str, vec_dim: int):
    num = 0
    while num < count:
        key_and_rec = (
            num,
            { "id": num, vec_bin: [float(num)] * vec_dim}
        )
        yield key_and_rec
        num += 1


def wait_for_index(admin_client, namespace: str, index: str):
    
    verticies = 0
    unmerged_recs = 0
    
    while verticies == 0 or unmerged_recs > 0:
        status = admin_client.index_get_status(
            namespace=namespace,
            name=index,
        )

        verticies = status.index_healer_vertices_valid
        unmerged_recs = status.unmerged_record_count

        # print(verticies)
        # print(unmerged_recs)
        time.sleep(0.5)


"""
def key_strategy():
    return st.text(alphabet=allowed_chars, min_size=1, max_size=100_000).filter(
        lambda ns: ns not in ["0", "1", "null"]
    )


def bin_strategy():
    return st.text(alphabet=allowed_chars, min_size=1, max_size=15).filter(
        lambda ns: ns not in ["0", "1", "null"]
    )


def index_strategy():
    return st.text(alphabet=allowed_chars, min_size=1, max_size=63).filter(
        lambda ns: ns not in ["null"]
    )



TODO: Implement Hypothesis
# Define the allowed characters



# Define the Hypothesis strategy for generating valid bin name strings (up to 15 bytes)
bin_name_strategy = st.text(
    alphabet=allowed_chars, min_size=1, max_size=15
).filter(lambda bn: bn != 'null')



def set_strategy():
    return st.text(
        alphabet=allowed_chars, min_size=1, max_size=63
    ).filter(lambda ns: ns != 'null')

def index_strategy
():
    return st.text(
        alphabet=allowed_chars, min_size=1, max_size=15
    ).filter(lambda ns: ns != 'null')




# Define strategies for generating test data using valid strings
namespace_strategy = valid_string_strategy
key_strategy = valid_string_strategy
record_data_strategy = st.dictionaries(
    keys=valid_string_strategy,
    values=st.lists(st.integers() | st.floats() | st.booleans(), min_size=1, max_size=1024)
)
set_name_strategy = st.none() | valid_string_strategy

"""
