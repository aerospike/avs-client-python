import pytest
from ...utils import random_int


class update_credentials_test_case:
    def __init__(self, *, username, old_password, new_password):
        self.username = username
        self.old_password = old_password
        self.new_password = new_password


@pytest.mark.parametrize(
    "test_case",
    [
        update_credentials_test_case(
            username="aio-update-credentials-" + str(random_int()),
            old_password="yeoldpassword",
            new_password="newpass",
        ),
    ],
)
def test_update_credentials(session_rbac_client, test_case):
    session_rbac_client.add_user(
        username=test_case.username, password=test_case.old_password, roles=None
    )

    session_rbac_client.update_credentials(
        username=test_case.username,
        password=test_case.new_password,
    )

    result = session_rbac_client.get_user(username=test_case.username)

    assert result.username == test_case.username

    assert result.roles == []
