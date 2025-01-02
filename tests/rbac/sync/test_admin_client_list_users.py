import pytest
from ...utils import random_int


class list_users_test_case:
    def __init__(self, *, username, password):
        self.username = username
        self.password = password


@pytest.mark.parametrize(
    "test_case",
    [
        list_users_test_case(
            username="aio-list-user-" + str(random_int()),
            password="sample",
        ),
    ],
)
def test_list_users(session_rbac_admin_client, test_case):
    session_rbac_admin_client.add_user(
        username=test_case.username, password=test_case.password, roles=None
    )

    result = session_rbac_admin_client.list_users()
    user_found = False
    for user in result:
        if user.username == test_case.username:
            assert user.roles == []
            user_found = True

    assert user_found
