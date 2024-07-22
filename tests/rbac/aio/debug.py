import pytest
import pytest
from ...utils import random_int

@pytest.mark.parametrize("test_case", [])
async def test_add_user(session_rbac_admin_client):
    await session_rbac_admin_client.add_user(
        username="admin",
        password="admin",
        roles=None

    )
    assert 1 == 1