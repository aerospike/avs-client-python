import pytest
from ...utils import random_int


class list_roles_test_case:
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
        list_roles_test_case(
            username="aio-list-roles-" + str(random_int()),
            password="yeoldpassword",
            roles=["admin", "read-write"],
        ),
    ],
)
def test_list_roles(session_rbac_client, test_case):
    session_rbac_client.add_user(
        username=test_case.username, password=test_case.password, roles=test_case.roles
    )

    result = session_rbac_client.list_roles()
    for role in result:
        assert role.id in test_case.roles
