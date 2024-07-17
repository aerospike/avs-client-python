import random 
import hypothesis.strategies as st
from hypothesis import given
import string

def random_int():
    return str(random.randint(0, 50_000))

allowed_chars = (
    list(string.ascii_lowercase) +  # a-z
    list(string.ascii_uppercase) +  # A-Z
    list(string.digits) +           # 0-9
    ['_', '-']                 # _, -, $
)

def key_strategy():
    return st.text(
        alphabet=allowed_chars, min_size=1, max_size=100_000
    ).filter(lambda ns: ns not in ['0', '1', 'null'])

def bin_strategy():
    return st.text(
        alphabet=allowed_chars, min_size=1, max_size=15
    ).filter(lambda ns: ns not in ['0', '1', 'null'])

def index_strategy():
    return st.text(
        alphabet=allowed_chars, min_size=1, max_size=63
    ).filter(lambda ns: ns not in ['null'])

"""
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