import pytest
from ...utils import random_int


class add_user_test_case:
    def __init__(
        self,
        *,
        username,
        password,
        roles,
    ):
        self.username = username
        self.password = password
        self.roles = roles


@pytest.mark.parametrize(
    "test_case",
    [
        add_user_test_case(
            username="aio-add-user-" + str(random_int()),
            password="alphanumeric",
            roles=None,
        ),
    ],
)
async def test_add_user(session_rbac_admin_client, test_case):
    await session_rbac_admin_client.add_user(
        username=test_case.username, password=test_case.password, roles=test_case.roles
    )

    result = await session_rbac_admin_client.get_user(username=test_case.username)

    assert result.username == test_case.username

    assert result.roles == []


@pytest.mark.parametrize(
    "test_case",
    [
        add_user_test_case(
            username="aio-add-user-" + str(random_int()),
            password="eu123#$%",
            roles=["admin"],
        ),
        add_user_test_case(
            username="aio-add-user-" + str(random_int()),
            password="radical",
            roles=["read-write"],
        ),
        add_user_test_case(
            username="aio-add-user-" + str(random_int()),
            password="marshall",
            roles=["admin", "read-write"],
        ),
    ],
)
async def test_add_user_with_roles(session_rbac_admin_client, test_case):
    await session_rbac_admin_client.add_user(
        username=test_case.username, password=test_case.password, roles=test_case.roles
    )

    result = await session_rbac_admin_client.get_user(username=test_case.username)

    assert result.username == test_case.username

    assert result.roles == test_case.roles
