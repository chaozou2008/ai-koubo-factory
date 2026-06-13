import pytest

VIDEO_CREDIT_COST = 10


async def register_and_login(client) -> str:
    resp = await client.post("/api/auth/register", json={"phone": "13800138000", "password": "123456"})
    return resp.json()["access_token"]


async def create_avatar(client, token: str) -> str:
    resp = await client.post("/api/avatars", json={"name": "测试形象", "photo_urls": {}},
                             headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


async def get_template_id(client) -> str:
    resp = await client.get("/api/templates")
    items = resp.json()["items"]
    return items[0]["id"] if items else None


@pytest.mark.asyncio
async def test_create_video_insufficient_credits(client):
    token = await register_and_login(client)
    avatar_id = await create_avatar(client, token)
    template_id = await get_template_id(client)
    for i in range(10):
        resp = await client.post("/api/videos", json={
            "avatar_id": avatar_id, "template_id": template_id, "script_text": f"测试文案{i}",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201
    resp = await client.post("/api/videos", json={
        "avatar_id": avatar_id, "template_id": template_id, "script_text": "超出预算",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 402


@pytest.mark.asyncio
async def test_create_video_success(client):
    token = await register_and_login(client)
    avatar_id = await create_avatar(client, token)
    template_id = await get_template_id(client)
    resp = await client.post("/api/videos", json={
        "avatar_id": avatar_id, "template_id": template_id,
        "script_text": "大家好，今天给大家推荐一款超好用的护肤品",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] in ("queued", "processing")
    assert data["cost_credits"] == VIDEO_CREDIT_COST


@pytest.mark.asyncio
async def test_list_videos(client):
    token = await register_and_login(client)
    avatar_id = await create_avatar(client, token)
    template_id = await get_template_id(client)
    await client.post("/api/videos", json={
        "avatar_id": avatar_id, "template_id": template_id, "script_text": "视频1",
    }, headers={"Authorization": f"Bearer {token}"})
    resp = await client.get("/api/videos", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1
