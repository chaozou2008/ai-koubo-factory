"""
腾讯云媒体AI (MAIS) TTS服务封装

MVP阶段：提供桩实现，返回模拟数据。
正式环境：对接腾讯云MAIS API。
"""
import httpx
import hashlib


class TencentMAIService:
    """腾讯云媒体AI TTS服务"""

    def __init__(self, secret_id: str = "", secret_key: str = "", region: str = "ap-guangzhou"):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region

    async def create_voice_clone(self, audio_url: str, voice_name: str) -> dict:
        """克隆音色：上传参考音频 → 返回音色ID。MVP返回模拟数据。"""
        return {
            "voice_id": f"VOICE-{hashlib.md5(voice_name.encode()).hexdigest()[:12]}",
            "voice_name": voice_name,
        }

    async def synthesize(self, text: str, voice_id: str, speed: float = 1.0) -> dict:
        """文本转语音：传入文本 + 音色ID → 返回音频URL。MVP返回模拟数据。"""
        return {
            "audio_url": f"https://oss.example.com/tts/{hashlib.md5(text.encode()).hexdigest()[:8]}.mp3",
            "duration_seconds": len(text) * 0.3,
            "voice_id": voice_id,
        }

    async def create_voice_and_synthesize(self, text: str, voice_name: str, audio_url: str) -> dict:
        """便捷方法：先建音色再合成"""
        voice = await self.create_voice_clone(audio_url, voice_name)
        result = await self.synthesize(text, voice["voice_id"])
        return {**result, "voice_id": voice["voice_id"]}


def get_tts_service() -> TencentMAIService:
    from app.config import get_settings
    s = get_settings()
    return TencentMAIService(
        secret_id=s.TENCENT_SECRET_ID,
        secret_key=s.TENCENT_SECRET_KEY,
        region=s.TENCENT_MAIS_REGION,
    )
