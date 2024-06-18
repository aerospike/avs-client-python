import pytest
from utils import random_int


class update_credentials_test_case:
    def __init__(
        self,
        *,
        username,
        old_password,
        new_password
    ):
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
async def test_update_credentials(session_rbac_admin_client, test_case):
    await session_rbac_admin_client.add_user(
        username=test_case.username,
        password=test_case.old_password,
        roles=None

    )

    await session_rbac_admin_client.update_credentials(
        username=test_case.username,
        password=test_case.new_password,
    )

    result = await session_rbac_admin_client.get_user(
        username=test_case.username
    )

    assert result.username == test_case.username

    assert result.roles == []

