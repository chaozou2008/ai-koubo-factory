"""
Seedance 2.0 API 封装 (火山引擎方舟)

API: POST /api/v3/contents/generations/tasks @ ark.cn-beijing.volces.com
模型: doubao-seedance-2-0-260128 (标准版) | doubao-seedance-2-0-mini-260615 (Mini版)
定价: 标准版 1080p ~4.7元/5秒, 720p ~2.5元/5秒 | Mini版 ~0.5元/秒 (降低约50%)
"""
import httpx
import time
from volcenginesdkarkruntime import Ark


class SeedanceService:
    """Seedance 2.0 视频生成服务 — 火山引擎方舟"""

    MODEL = "doubao-seedance-2-0-260128"
    MODEL_MINI = "doubao-seedance-2-0-mini-260615"

    def __init__(self, api_key: str = "", use_mini: bool = False):
        # bypass system proxy (HTTPS_PROXY) — 本地代理未运行会导致 Connection error
        http_client = httpx.Client(trust_env=False)
        self.client = Ark(api_key=api_key, http_client=http_client)
        self.model = self.MODEL_MINI if use_mini else self.MODEL

    async def generate_video(
        self,
        image_url: str = "",
        audio_url: str = "",
        script_text: str = "",
        reference_video_url: str = "",
        duration: int = 5,
        resolution: str = "720p",
        ratio: str = "9:16",
    ) -> dict:
        """
        生成数字人口播视频。

        Args:
            image_url: 人物参考图片 URL（可选）
            audio_url: TTS 语音 URL
            script_text: 口播文案/场景描述
            reference_video_url: 参考视频 URL（可选，用于模仿风格）
            duration: 视频时长（秒），4-15
            resolution: 480p / 720p / 1080p
            ratio: 16:9 / 9:16 / 1:1

        Returns:
            {"task_id": "xxx", "status": "queued"}
        """
        has_visual_ref = bool((image_url and image_url.startswith("http")) or (reference_video_url and reference_video_url.startswith("http")))
        content = [
            {"type": "text", "text": f"数字人口播视频，人物面对镜头说话，口型与语音同步。{script_text}"},
        ]
        if image_url and image_url.startswith("http"):
            content.append({"type": "image_url", "image_url": {"url": image_url}, "role": "reference_image"})
        if reference_video_url and reference_video_url.startswith("http"):
            content.append({"type": "video_url", "video_url": {"url": reference_video_url}, "role": "reference_video"})
        # 有视觉参考时才能传参考音频，否则 Seedance 报错
        if audio_url and has_visual_ref:
            content.append({"type": "audio_url", "audio_url": {"url": audio_url}, "role": "reference_audio"})

        resp = self.client.content_generation.tasks.create(
            model=self.model,
            content=content,
            resolution=resolution,
            ratio=ratio,
            duration=duration,
        )

        # SDK 返回 ContentGenerationTaskID，只有 id，status 需通过 get 查询
        return {
            "task_id": resp.id if hasattr(resp, 'id') else str(resp),
            "status": "queued",
        }

    async def query_video_status(self, task_id: str) -> dict:
        """
        查询视频生成状态。

        Returns:
            {"task_id": "xxx", "status": "queued|running|succeeded|failed",
             "video_url": "..." (if succeeded), "error": "..." (if failed)}
        """
        result = self.client.content_generation.tasks.get(task_id=task_id)
        status = result.status

        response = {"task_id": task_id, "status": status}

        if status == "succeeded":
            response["video_url"] = result.content.video_url
        elif status in ("failed", "expired", "cancelled"):
            response["error"] = str(result.error) if result.error else status

        return response

    async def generate_auth_qrcode(self, user_id: str) -> dict:
        """
        Seedance 高级创作权益包自带真人授权流程。
        用户需在火山引擎完成实名认证和素材授权。
        MVP 阶段返回提示信息。
        """
        return {
            "qrcode_url": "https://console.volcengine.com/ark/region:ark+cn-beijing/seedance/auth",
            "note": "请在火山引擎方舟控制台完成真人素材授权",
            "expire_seconds": 86400,
        }

    async def check_authorization(self, user_id: str) -> dict:
        """
        检查素材授权状态。
        MVP 阶段假设已授权（使用方舟私域素材库）。
        """
        return {
            "authorized": True,
            "material_id": f"volc-{user_id}",
            "character_id": f"seedance-char-{user_id}",
        }


def get_seedance_service() -> SeedanceService:
    from app.config import get_settings
    s = get_settings()
    return SeedanceService(api_key=s.VOLCENGINE_ARK_API_KEY)


def get_seedance_mini_service() -> SeedanceService:
    from app.config import get_settings
    s = get_settings()
    return SeedanceService(api_key=s.VOLCENGINE_ARK_API_KEY, use_mini=True)
