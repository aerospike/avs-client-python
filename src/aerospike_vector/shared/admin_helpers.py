import asyncio
import logging
from typing import Any, Optional, Union
import time

import google.protobuf.empty_pb2
from google.protobuf.json_format import MessageToDict
import grpc

from . import helpers
from .proto_generated import index_pb2_grpc
from .proto_generated import types_pb2
from .. import types

logger = logging.getLogger(__name__)

empty = google.protobuf.empty_pb2.Empty()

def prepare_seeds(seeds) -> None:
    return helpers.prepare_seeds(seeds)

def prepare_index_create(self, namespace, name, vector_field, dimensions, vector_distance_metric, sets, index_params, index_meta_data, logger) -> None:

    logger.debug(
        "Creating index: namespace=%s, name=%s, vector_field=%s, dimensions=%d, vector_distance_metric=%s, "
        "sets=%s, index_params=%s, index_meta_data=%s",
        namespace,
        name,
        vector_field,
        dimensions,
        vector_distance_metric,
        sets,
        index_params,
        index_meta_data,
    )

    if sets and not sets.strip():
        sets = None
    if index_params != None:
        index_params = index_params._to_pb2()
    id = get_index_id(namespace, name)
    vector_distance_metric = vector_distance_metric.value

    index_stub = get_index_stub(self)

    index_create_request = types_pb2.IndexDefinition(
        id=id,
        vectorDistanceMetric=vector_distance_metric,
        setFilter=sets,
        hnswParams=index_params,
        bin=vector_field,
        dimensions=dimensions,
        labels=index_meta_data,
    )
    return (index_stub, index_create_request)

def prepare_index_drop(self, namespace, name, logger) -> None:
    
    logger.debug("Dropping index: namespace=%s, name=%s", namespace, name)

    index_stub = get_index_stub(self)
    index_drop_request = get_index_id(namespace, name)

    return (index_stub, index_drop_request)

def prepare_index_list(self, logger) -> None:

    logger.debug("Getting index list")

    index_stub = get_index_stub(self)
    index_list_request = empty

    return (index_stub, index_list_request)

def prepare_index_get(self, namespace, name, logger) -> None:

    logger.debug(
        "Getting index information: namespace=%s, name=%s", namespace, name
    )

    index_stub = get_index_stub(self)
    index_get_request = get_index_id(namespace, name)

    return (index_stub, index_get_request)

def prepare_index_get_status(self, namespace, name, logger) -> None:

    logger.debug("Getting index status: namespace=%s, name=%s", namespace, name)

    index_stub = get_index_stub(self)
    index_get_status_request = get_index_id(namespace, name)


    return (index_stub, index_get_status_request)

def respond_index_list(response) -> None:
    response_list = []
    for index in response.indices:
        response_dict = MessageToDict(index)

        # Modifying dict to adhere to PEP-8 naming
        hnsw_params_dict = response_dict.pop("hnswParams", None)

        hnsw_params_dict["ef_construction"] = hnsw_params_dict.pop(
            "efConstruction", None
        )

        batching_params_dict = hnsw_params_dict.pop("batchingParams", None)
        batching_params_dict["max_records"] = batching_params_dict.pop(
            "maxRecords", None
        )
        hnsw_params_dict["batching_params"] = batching_params_dict

        response_dict["hnsw_params"] = hnsw_params_dict
        response_list.append(response_dict)
    return response_list

def respond_index_get(response) -> None:
    response_dict = MessageToDict(response)

    # Modifying dict to adhere to PEP-8 naming
    hnsw_params_dict = response_dict.pop("hnswParams", None)

    hnsw_params_dict["ef_construction"] = hnsw_params_dict.pop(
        "efConstruction", None
    )

    batching_params_dict = hnsw_params_dict.pop("batchingParams", None)
    batching_params_dict["max_records"] = batching_params_dict.pop(
        "maxRecords", None
    )
    hnsw_params_dict["batching_params"] = batching_params_dict

    response_dict["hnsw_params"] = hnsw_params_dict
    return response_dict

def respond_index_get_status(response) -> None:
    return response.unmergedRecordCount

def get_index_stub(self):
    return index_pb2_grpc.IndexServiceStub(
        self._channelProvider.get_channel()
    )

def get_index_id(namespace, name):
    return types_pb2.IndexId(namespace=namespace, name=name)

def prepare_wait_for_index_waiting(self, namespace, name):
    return helpers.prepare_wait_for_index_waiting(self, namespace, name)


def check_timeout(start_time, timeout):
    if start_time + timeout < time.monotonic():
        raise "timed-out waiting for index creation"




