import pytest


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def register_and_login(client) -> str:
    resp = await client.post("/api/auth/register", json={"phone": "13900000001", "password": "123456"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_avatar(client):
    token = await register_and_login(client)
    resp = await client.post("/api/avatars", json={
        "name": "我的数字人",
        "photo_urls": {"front": "https://example.com/face1.jpg", "side": "https://example.com/face2.jpg"},
    }, headers=auth_header(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "我的数字人"
    assert data["status"] == "active"
    assert data["character_id"] is not None


@pytest.mark.asyncio
async def test_list_avatars(client):
    token = await register_and_login(client)
    await client.post("/api/avatars", json={"name": "形象1", "photo_urls": {}}, headers=auth_header(token))
    await client.post("/api/avatars", json={"name": "形象2", "photo_urls": {}}, headers=auth_header(token))
    resp = await client.get("/api/avatars", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_delete_avatar(client):
    token = await register_and_login(client)
    resp = await client.post("/api/avatars", json={"name": "待删除", "photo_urls": {}}, headers=auth_header(token))
    avatar_id = resp.json()["id"]
    resp = await client.delete(f"/api/avatars/{avatar_id}", headers=auth_header(token))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_cannot_access_other_user_avatar(client):
    token1 = await register_and_login(client)
    resp = await client.post("/api/avatars", json={"name": "我的", "photo_urls": {}}, headers=auth_header(token1))
    avatar_id = resp.json()["id"]
    resp2 = await client.post("/api/auth/register", json={"phone": "13900000002", "password": "123456"})
    token2 = resp2.json()["access_token"]
    resp3 = await client.get(f"/api/avatars/{avatar_id}", headers=auth_header(token2))
    assert resp3.status_code == 404
