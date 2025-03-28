import pytest
from ...utils import random_int
from aerospike_vector_search import AVSServerError
import grpc


class drop_user_test_case:
    def __init__(
        self,
        *,
        username,
        password,
    ):
        self.username = username
        self.password = password


@pytest.mark.parametrize(
    "test_case",
    [
        drop_user_test_case(
            username="aio-drop-user-" + str(random_int()),
            password="tallyho",
        ),
    ],
)
async def test_drop_user(session_rbac_client, test_case):
    await session_rbac_client.add_user(
        username=test_case.username, password=test_case.password, roles=None
    )
    await session_rbac_client.drop_user(
        username=test_case.username,
    )
    with pytest.raises(AVSServerError) as e_info:
        result = await session_rbac_client.get_user(username=test_case.username)
    assert e_info.value.rpc_error.code() == grpc.StatusCode.NOT_FOUND
