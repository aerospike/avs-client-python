import pytest
from ...utils import random_int

async def test_add_user(session_rbac_admin_client):
    print("WE ARE IN THIS")
    await session_rbac_admin_client.add_user(
        username="admin",
        password="admin",
        roles=None

    )
    assert 1 == 1