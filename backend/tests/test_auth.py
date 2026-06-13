import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/api/auth/register", json={
        "phone": "13800138000",
        "password": "123456",
        "company_name": "测试公司",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_phone(client):
    await client.post("/api/auth/register", json={"phone": "13800138000", "password": "123456"})
    resp = await client.post("/api/auth/register", json={"phone": "13800138000", "password": "654321"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/auth/register", json={"phone": "13800138001", "password": "123456"})
    resp = await client.post("/api/auth/login", json={"phone": "13800138001", "password": "123456"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={"phone": "13800138002", "password": "123456"})
    resp = await client.post("/api/auth/login", json={"phone": "13800138002", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client):
    resp = await client.post("/api/auth/register", json={"phone": "13800138003", "password": "123456"})
    token = resp.json()["access_token"]
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["phone"] == "13800138003"
    assert resp.json()["credits_balance"] == 100


@pytest.mark.asyncio
async def test_unauthorized(client):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 403
