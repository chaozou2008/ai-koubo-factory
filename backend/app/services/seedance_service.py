"""
Seedance 2.0 API 封装 (火山引擎)

MVP阶段：提供桩实现，返回模拟数据。
正式环境：对接火山引擎方舟平台API。
"""
import uuid


class SeedanceService:
    """Seedance 2.0 视频生成服务"""

    def __init__(self, access_key: str = "", secret_key: str = ""):
        self.access_key = access_key
        self.secret_key = secret_key

    async def generate_auth_qrcode(self, user_id: str) -> dict:
        """生成真人授权二维码。MVP返回模拟数据。"""
        return {
            "qrcode_url": f"https://volcengine.example.com/auth?uid={user_id}&nonce={uuid.uuid4().hex[:8]}",
            "expire_seconds": 600,
        }

    async def check_authorization(self, user_id: str) -> dict:
        """检查授权状态。MVP返回已授权。"""
        return {
            "authorized": True,
            "material_id": f"MAT-{uuid.uuid4().hex[:12]}",
            "character_id": f"CHAR-{uuid.uuid4().hex[:8]}",
        }

    async def generate_video(
        self, material_id: str, audio_url: str, template_config: dict, script_text: str
    ) -> dict:
        """调用Seedance 2.0生成视频。MVP返回模拟数据。"""
        return {
            "task_id": f"SD-{uuid.uuid4().hex[:16]}",
            "status": "processing",
        }

    async def query_video_status(self, task_id: str) -> dict:
        """查询视频生成状态。MVP返回已完成。"""
        return {
            "task_id": task_id,
            "status": "done",
            "video_url": f"https://oss.example.com/videos/{task_id}.mp4",
        }


def get_seedance_service() -> SeedanceService:
    from app.config import get_settings
    s = get_settings()
    return SeedanceService(access_key=s.VOLCENGINE_ACCESS_KEY, secret_key=s.VOLCENGINE_SECRET_KEY)
