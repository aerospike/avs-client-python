import pytest
from ...utils import random_int


class revoke_roles_test_case:
    def __init__(
        self,
        *,
        username,
        password,
        roles,
        revoked_roles
    ):
        self.username = username
        self.password = password
        self.roles = roles
        self.revoked_roles = revoked_roles

@pytest.mark.parametrize(
    "test_case",
    [
        revoke_roles_test_case(
            username="aio-revoke-roles-" + str(random_int()),
            password="yeoldpassword",
            roles=["admin", "read-write"],
            revoked_roles=[]
        ),
    ],
)
def test_revoke_roles(session_rbac_admin_client, test_case):
    session_rbac_admin_client.add_user(
        username=test_case.username,
        password=test_case.password,
        roles=test_case.roles

    )

    session_rbac_admin_client.revoke_roles(
        username=test_case.username,
        roles=test_case.roles
    )

    result = session_rbac_admin_client.get_user(
        username=test_case.username
    )

    assert result.username == test_case.username

    assert result.roles == test_case.revoked_roles

