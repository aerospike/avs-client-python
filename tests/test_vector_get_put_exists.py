async def test_vector_put(truncated_vector_client):
    await truncated_vector_client.put(
        namespace="test",
        key="example",
        record_data={"chocolate": [0 for i in range(1024)]},
    )


async def test_vector_get(truncated_vector_client):
    result = await truncated_vector_client.get(
        namespace="test", key="example", bin_names=["chocolate"]
    )
    assert result.key.namespace == "test"
    assert result.key.set == "demo"
    assert result.key.key == "example"
    assert isinstance(result.key.digest, bytes)
    assert result.bins["chocolate"] == [0 for i in range(1024)]


async def test_vector_exists(truncated_vector_client):
    result = await truncated_vector_client.exists(
        namespace="test",
        key="example",
    )
    assert result is True
