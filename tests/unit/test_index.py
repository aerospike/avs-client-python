import pytest
from unittest.mock import MagicMock

from aerospike_vector_search import Client, Index, types


def test_index_vector_search():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    query = [0.0] * 10
    search_params = types.HnswSearchParams(
        ef=10,
    )

    index.vector_search(
        query=query,
        limit=10,
        search_params=search_params,
        include_fields=["test_field"],
        exclude_fields=["test_field"],
        timeout=1000,
    )

    mock_client.vector_search.assert_called_once_with(
        index_name="test_index",
        namespace="test_namespace",
        query=query,
        limit=10,
        search_params=search_params,
        include_fields=["test_field"],
        # remember that the index should exclude its vector field by default
        # so expect it to be present in the exclude_fields list
        exclude_fields=["test_vector_field", "test_field"],
        timeout=1000,
    )


def test_index_vector_search_no_params():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    query = [0.0] * 10

    index.vector_search(
        query=query,
    )

    mock_client.vector_search.assert_called_once_with(
        index_name="test_index",
        namespace="test_namespace",
        query=query,
        limit=10,
        search_params=None,
        include_fields=None,
        exclude_fields=["test_vector_field"],
        timeout=None,
    )


def test_index_vector_search_by_key():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    key = "test_key"
    search_params = types.HnswSearchParams(
        ef=10,
    )

    index.vector_search_by_key(
        key=key,
        namespace="test_input_namespace",
        vector_field="test_input_vector_field",
        limit=10,
        set_name="test_input_set_name",
        search_params=search_params,
        include_fields=["test_field"],
        exclude_fields=["test_field"],
        timeout=1000,
    )

    mock_client.vector_search_by_key.assert_called_once_with(
        search_namespace="test_namespace",
        index_name="test_index",
        key=key,
        key_namespace="test_input_namespace",
        vector_field="test_input_vector_field",
        limit=10,
        key_set="test_input_set_name",
        search_params=search_params,
        include_fields=["test_field"],
        # remember that the index should exclude its vector field by default
        # so expect it to be present in the exclude_fields list
        exclude_fields=["test_vector_field", "test_field"],
        timeout=1000,
    )


def test_index_vector_search_by_key_no_params():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    key = "test_key"
    index.vector_search_by_key(
        key=key,
    )

    mock_client.vector_search_by_key.assert_called_once_with(
        search_namespace="test_namespace",
        index_name="test_index",
        key=key,
        key_namespace="test_namespace",
        vector_field="test_vector_field",
        limit=10,
        key_set=None,
        search_params=None,
        include_fields=None,
        exclude_fields=["test_vector_field"],
        timeout=None,
    )


def test_index_is_indexed():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    key = "test_key"
    index.is_indexed(
        key=key,
        set_name="test_input_set_name",
        timeout=1000,
    )

    mock_client.is_indexed.assert_called_once_with(
        namespace="test_namespace",
        key=key,
        index_name="test_index",
        index_namespace="test_namespace",
        set_name="test_input_set_name",
        timeout=1000,
    )


def test_index_is_indexed_no_params():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    key = "test_key"
    index.is_indexed(
        key=key,
    )

    mock_client.is_indexed.assert_called_once_with(
        namespace="test_namespace",
        key=key,
        index_name="test_index",
        index_namespace="test_namespace",
        set_name="test_sets",
        timeout=None,
    )


def test_index_get_percent_unmerged():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.get_percent_unmerged(
        timeout=1000,
    )

    mock_client.index_get_percent_unmerged.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        timeout=1000,
    )


def test_index_get_percent_unmerged_no_params():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.get_percent_unmerged()

    mock_client.index_get_percent_unmerged.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        timeout=None,
    )


def test_index_update():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    updates = types.HnswIndexUpdate(
        enable_vector_integrity_check=True,
    )

    index.update(
        timeout=1000,
        hnsw_update_params=updates,
        labels={"test": "label"},
    )

    mock_client.index_update.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        index_labels={"test": "label"},
        hnsw_update_params=updates,
        timeout=1000,
    )


def test_index_update_no_params():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.update()

    mock_client.index_update.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        index_labels=None,
        hnsw_update_params=None,
        timeout=None,
    )


def test_index_get():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.get(
        apply_defaults=False,
        timeout=1000,
    )

    mock_client.index_get.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        apply_defaults=False,
        timeout=1000,
    )


def test_index_get_no_params():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.get()

    mock_client.index_get.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        apply_defaults=True,
        timeout=None,
    )


def test_index_status():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.status(
        timeout=1000,
    )

    mock_client.index_get_status.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        timeout=1000,
    )


def test_index_status_no_params():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.status()

    mock_client.index_get_status.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        timeout=None,
    )


def test_index_drop():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.drop(
        timeout=1000,
    )

    mock_client.index_drop.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        timeout=1000,
    )


def test_index_drop_no_params():
    mock_client = MagicMock(spec=Client)
    index = Index(
        client=mock_client,
        name="test_index",
        namespace="test_namespace",
        vector_field="test_vector_field",
        dimensions=10,
        vector_distance_metric=types.VectorDistanceMetric.SQUARED_EUCLIDEAN,
        sets="test_sets",
    )

    index.drop()

    mock_client.index_drop.assert_called_once_with(
        namespace="test_namespace",
        name="test_index",
        timeout=None,
    )