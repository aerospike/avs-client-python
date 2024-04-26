def init_tend(self) -> None:
    end_tend = False
    if self._is_loadbalancer:
        # Skip tend if we are behind a load-balancer
        end_tend = True

    if self._closed:
        end_tend = True

    # TODO: Worry about thread safety
    temp_endpoints: dict[int, vector_db_pb2.ServerEndpointList] = {}

    update_endpoints = False
    channels = self._seedChannels + [
        x.channel for x in self._nodeChannels.values()
    ]
    return (temp_endpoints, update_endpoints, channels, end_tend)


def check_cluster_id(self, new_cluster_id) -> None:
    if new_cluster_id == self._clusterId:
        return False

    self._clusterId = new_cluster_id

    return True

def update_temp_endpoints(response, temp_endpoints):
    endpoints = response.endpoints
    if len(endpoints) > len(temp_endpoints):
        return endpoints
    else:
        return temp_endpoints


def check_for_new_endpoints(self, node, newEndpoints):

    channel_endpoints = self._nodeChannels.get(node)
    add_new_channel = True

    if channel_endpoints:
        # We have this node. Check if the endpoints changed.
        if channel_endpoints.endpoints == newEndpoints:
            # Nothing to be done for this node
            add_new_channel = False
        else:
            add_new_channel = True

    return (channel_endpoints, add_new_channel)

