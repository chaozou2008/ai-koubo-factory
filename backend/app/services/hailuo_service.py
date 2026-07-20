"""
海螺AI (Hailuo / MiniMax) 视频生成 API 封装

API: POST /v1/video_generation @ api.minimax.io
模型: MiniMax-Hailuo-2.3 (T2V + I2V, 1080P/6s, 768P/10s)
认证: Authorization: Bearer <api_key>
定价: ~0.067$/秒 (远低于 Seedance 的 ~2.5¥/5秒)
"""
import httpx
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://api.minimaxi.com/v1"


class HailuoService:
    """海螺AI 视频生成服务 — MiniMax 开放平台"""

    MODEL = "MiniMax-Hailuo-2.3"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=BASE_URL,
            headers=self.headers,
            timeout=30,
            trust_env=False,  # bypass system proxy
        )

    async def generate_video(
        self,
        prompt: str = "",
        image_url: str = "",
        duration: int = 6,
        resolution: str = "768P",
    ) -> dict:
        """
        创建视频生成任务（T2V 或 I2V）。

        Args:
            prompt: 画面描述文本（支持相机控制如 [推进][左摇]）
            image_url: 可选，起始帧图片 URL（有则走 I2V）
            duration: 视频时长（秒），6 或 10
            resolution: 1080P / 720P / 576P

        Returns:
            {"task_id": "xxx", "status": "queued"}
        """
        body = {
            "model": self.MODEL,
            "prompt": prompt or "数字人口播视频，人物面对镜头自然说话，画面流畅稳定",
            "duration": duration,
            "resolution": resolution,
        }
        if image_url and image_url.startswith("http"):
            body["image_url"] = image_url

        async with self._client() as http:
            resp = await http.post("/video_generation", json=body)
            resp.raise_for_status()
            data = resp.json()

        base_resp = data.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            raise Exception(f"MiniMax API error: {base_resp.get('status_msg', 'unknown')}")

        return {
            "task_id": data["task_id"],
            "status": "queued",
        }

    async def query_video_status(self, task_id: str) -> dict:
        """
        查询视频生成状态。

        Returns:
            {"task_id": "xxx", "status": "Queuing|InProgress|Success|Fail",
             "file_id": "..." (if Success), "error": "..." (if Fail)}
        """
        async with self._client() as http:
            resp = await http.get("/query/video_generation", params={"task_id": task_id})
            resp.raise_for_status()
            data = resp.json()

        status = data.get("status", "Fail")
        result = {"task_id": task_id, "status": status}

        if status == "Success":
            result["file_id"] = data.get("file_id", "")
        elif status == "Fail":
            result["error"] = data.get("base_resp", {}).get("status_msg", "Generation failed")

        return result

    async def get_download_url(self, file_id: str) -> str:
        """
        获取视频下载链接。

        Args:
            file_id: query_video_status 返回的 file_id

        Returns:
            视频下载 URL
        """
        async with self._client() as http:
            resp = await http.get("/files/retrieve", params={"file_id": file_id})
            resp.raise_for_status()
            data = resp.json()

        file_info = data.get("file", {})
        download_url = file_info.get("download_url", "")
        if not download_url:
            raise Exception(f"MiniMax: no download_url for file_id={file_id}")
        return download_url


def get_hailuo_service() -> HailuoService:
    from app.config import get_settings
    s = get_settings()
    return HailuoService(api_key=s.MINIMAX_API_KEY)
