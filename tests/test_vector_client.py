import pytest
import asyncio
import pytest_asyncio  # Import pytest_asyncio module
import random

@pytest_asyncio.fixture
def initializeIndex(event_loop, truncated_admin_client):
    try:
        event_loop.run_until_complete(truncated_admin_client.index_create(
            namespace='test',
            name='darth',
            vector_bin_name='chocolate',
            dimensions=1024,
            )
        )
    except:
        pass

@pytest_asyncio.fixture
def random_choice(event_loop):
    return [random.choice([True, False]) for _ in range(1024)]

@pytest.mark.asyncio
async def test_vector_put(truncated_vector_client, random_choice):
    await truncated_vector_client.put(
        namespace='test',
        key='example',
        record_data={'chocolate':  random_choice},
        set_name='demo'
    )
    await asyncio.sleep(10)
    print("FINISHED")


@pytest.mark.asyncio
async def test_vector_get(truncated_vector_client):
    result = await truncated_vector_client.get(
        namespace='test',
        key='example',
        set_name='demo',
        bin_names=['chocolate']
    )
    print(type(result))
    print(result.__dict__)  # If `result` is an object

@pytest.mark.asyncio
async def test_vector_exists(truncated_vector_client):
    result = await truncated_vector_client.exists(
        namespace='test',
        key='example',
        set_name='demo'
    )
    print(result)

@pytest.mark.asyncio
async def try_multiple_times(initializeIndex, truncated_vector_client):
    async def test_vector_is_indexed():
        result = await truncated_vector_client.is_indexed(
            namespace='test',
            key='example',
            index_name='darth',
            set_name='demo'
        )
        print(result)

    for i in range(5):
        print(f"Attempt {i+1}:")
        await test_vector_is_indexed()
        print()


@pytest.mark.asyncio
async def test_vector_vector_search(truncated_vector_client, random_choice):
    result = await truncated_vector_client.vector_search(
        namespace='test',
        index_name='darth',
        query=random_choice,
        limit=20,
        bin_names=['chocolate']
    )
    print(result)
