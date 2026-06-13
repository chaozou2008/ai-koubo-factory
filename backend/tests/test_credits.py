import pytest


async def register_and_login(client) -> str:
    resp = await client.post("/api/auth/register", json={"phone": "13800138004", "password": "123456"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_get_balance(client):
    token = await register_and_login(client)
    resp = await client.get("/api/credits/balance", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["balance"] == 100


@pytest.mark.asyncio
async def test_get_credit_log(client):
    token = await register_and_login(client)
    resp = await client.get("/api/credits/log", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_list_plans(client):
    resp = await client.get("/api/plans")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 3
