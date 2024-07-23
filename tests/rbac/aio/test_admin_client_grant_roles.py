import pytest
from ...utils import random_int


class grant_roles_test_case:
    def __init__(self, *, username, password, roles, granted_roles):
        self.username = username
        self.password = password
        self.roles = roles
        self.granted_roles = granted_roles


@pytest.mark.parametrize(
    "test_case",
    [
        grant_roles_test_case(
            username="aio-update-credentials-" + str(random_int()),
            password="yeoldpassword",
            roles=[],
            granted_roles=["admin", "read-write"],
        ),
    ],
)
async def test_grant_roles(session_rbac_admin_client, test_case):
    await session_rbac_admin_client.add_user(
        username=test_case.username, password=test_case.password, roles=test_case.roles
    )

    await session_rbac_admin_client.grant_roles(
        username=test_case.username, roles=test_case.granted_roles
    )

    result = await session_rbac_admin_client.get_user(username=test_case.username)

    assert result.username == test_case.username

    assert result.roles == test_case.granted_roles
