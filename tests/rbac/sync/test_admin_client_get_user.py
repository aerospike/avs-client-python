import pytest
from ...utils import random_int


class get_user_test_case:
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
        get_user_test_case(
            username="aio-drop-user-" + str(random_int()),
            password="tallyho",
        ),
    ],
)
def test_get_user(session_rbac_admin_client, test_case):
    session_rbac_admin_client.add_user(
        username=test_case.username, password=test_case.password, roles=None
    )

    result = session_rbac_admin_client.get_user(username=test_case.username)

    assert result.username == test_case.username

    assert result.roles == []
