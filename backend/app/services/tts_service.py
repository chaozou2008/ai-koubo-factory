"""
腾讯云媒体处理 (MPS) SyncDubbing API 封装

API: SyncDubbing @ mps.tencentcloudapi.com
定价:
  - 音色克隆: 25元/音色 (一次性)
  - 语音合成: 0.5元/分钟
  - 后付费日结
"""
import hashlib
import hmac
import json
import time
import base64
from datetime import datetime
import httpx


class TencentMAIService:
    """腾讯云媒体AI TTS服务 — SyncDubbing API"""

    SERVICE = "mps"
    VERSION = "2019-06-12"
    ACTION = "SyncDubbing"

    def __init__(self, secret_id: str = "", secret_key: str = "", region: str = "ap-guangzhou"):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.endpoint = "mps.tencentcloudapi.com"

    def _sign(self, method: str, payload: str, timestamp: int) -> dict:
        """Tencent Cloud API v3 TC3-HMAC-SHA256 签名"""
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
        canonical_headers = f"content-type:application/json\nhost:{self.endpoint}\n"
        signed_headers = "content-type;host"
        hashed_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        canonical_request = f"{method}\n/\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
        credential_scope = f"{date}/{self.SERVICE}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = f"TC3-HMAC-SHA256\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"

        def _sign_hmac(key: bytes, data: str) -> bytes:
            return hmac.new(key, data.encode("utf-8"), hashlib.sha256).digest()

        secret_date = _sign_hmac(("TC3" + self.secret_key).encode("utf-8"), date)
        secret_service = _sign_hmac(secret_date, self.SERVICE)
        secret_signing = _sign_hmac(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        authorization = (
            f"TC3-HMAC-SHA256 "
            f"Credential={self.secret_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        return {
            "Authorization": authorization,
            "Content-Type": "application/json",
            "Host": self.endpoint,
            "X-TC-Action": self.ACTION,
            "X-TC-Version": self.VERSION,
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Region": self.region,
        }

    async def _call_api(self, params: dict) -> dict:
        payload = json.dumps(params)
        timestamp = int(time.time())
        headers = self._sign("POST", payload, timestamp)
        # bypass system proxy (HTTPS_PROXY) — 本地代理未运行会导致 Connection error
        async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
            resp = await client.post(f"https://{self.endpoint}", content=payload, headers=headers)
            data = resp.json()
        if "Response" not in data:
            raise Exception(f"腾讯云TTS API错误: {data}")
        response = data["Response"]
        if response.get("ErrorCode") != 0 and response.get("ErrorCode") is not None:
            raise Exception(f"腾讯云TTS API错误: {response.get('Msg', 'Unknown')}")
        return response

    async def create_voice_clone(self, audio_url: str, voice_name: str) -> dict:
        """克隆音色：上传参考音频 URL → 返回音色ID。费用: 25元/音色"""
        result = await self._call_api({
            "AudioUrl": audio_url, "Text": voice_name, "AudioLang": "zh", "TextLang": "zh",
        })
        return {"voice_id": result.get("VoiceId", ""), "voice_name": voice_name}

    async def create_voice_clone_from_data(self, audio_data_b64: str, voice_name: str) -> dict:
        """克隆音色：发送 base64 编码的音频 → 返回音色ID。费用: 25元/音色"""
        result = await self._call_api({
            "AudioData": audio_data_b64, "Text": voice_name, "AudioLang": "zh", "TextLang": "zh",
        })
        return {"voice_id": result.get("VoiceId", ""), "voice_name": voice_name}

    async def synthesize(self, text: str, voice_id: str, speed: float = 1.0) -> dict:
        """
        文本转语音。费用: 0.5元/分钟
        返回: {"audio_data": bytes (wav), "audio_url": str (24h valid), "voice_id": str}
        """
        result = await self._call_api({"Text": text, "VoiceId": voice_id, "TextLang": "zh"})
        audio_b64 = result.get("AudioData", "")
        audio_bytes = base64.b64decode(audio_b64) if audio_b64 else b""
        return {
            "audio_data": audio_bytes,
            "audio_url": result.get("AudioUrl", ""),
            "duration_seconds": len(text) * 0.3,
            "voice_id": voice_id,
        }

    async def synthesize_with_clone(self, text: str, audio_data_b64: str) -> dict:
        """
        首次使用：克隆 + 合成（一次API调用完成）。
        费用: 25元/音色 + 0.5元/分钟
        返回: {"audio_data": bytes, "voice_id": str}
        """
        result = await self._call_api({
            "AudioData": audio_data_b64, "Text": text, "AudioLang": "zh", "TextLang": "zh",
        })
        audio_b64 = result.get("AudioData", "")
        return {
            "audio_data": base64.b64decode(audio_b64) if audio_b64 else b"",
            "voice_id": result.get("VoiceId", ""),
        }


def get_tts_service() -> TencentMAIService:
    from app.config import get_settings
    s = get_settings()
    return TencentMAIService(
        secret_id=s.TENCENT_SECRET_ID,
        secret_key=s.TENCENT_SECRET_KEY,
        region=s.TENCENT_MAIS_REGION,
    )
