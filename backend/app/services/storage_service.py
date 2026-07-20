"""
阿里云 OSS 存储服务

存储结构:
  videos/{uuid}.mp4     — Seedance 生成的视频
  audio/{uuid}.wav      — TTS 合成的语音
  images/{uuid}.jpg     — 用户上传的形象照片
"""
import uuid
import oss2


class StorageService:
    """阿里云 OSS 存储"""

    def __init__(self, endpoint: str = "", bucket: str = "", access_key: str = "", secret_key: str = ""):
        self.endpoint = endpoint
        self.bucket_name = bucket
        auth = oss2.Auth(access_key, secret_key)
        # 用 oss2.Session + trust_env=False 绕过 Windows 系统代理
        sess = oss2.Session()
        sess.session.trust_env = False
        self.bucket = oss2.Bucket(auth, endpoint, bucket, session=sess)

    async def upload_file(self, file_path: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        """
        上传文件到 OSS，返回公网访问 URL。

        Args:
            file_path: 文件路径或对象名 (如 "audio/tts_output.wav")
            content: 文件内容 bytes
            content_type: MIME 类型
        Returns:
            公网 URL，如 https://aivedio-bucket.oss-cn-hangzhou.aliyuncs.com/audio/xxx.wav
        """
        self.bucket.put_object(file_path, content, headers={"Content-Type": content_type})
        return f"https://{self.bucket_name}.{self.endpoint}/{file_path}"

    async def upload_audio(self, file_name: str, content: bytes) -> str:
        """上传音频文件"""
        key = f"audio/{uuid.uuid4().hex}_{file_name}"
        return await self.upload_file(key, content, "audio/wav")

    async def upload_image(self, file_name: str, content: bytes) -> str:
        """上传图片文件"""
        key = f"images/{uuid.uuid4().hex}_{file_name}"
        return await self.upload_file(key, content, "image/jpeg")

    async def upload_video(self, file_name: str, content: bytes) -> str:
        """上传视频文件"""
        key = f"videos/{uuid.uuid4().hex}_{file_name}"
        return await self.upload_file(key, content, "video/mp4")


def get_storage_service() -> StorageService:
    from app.config import get_settings
    s = get_settings()
    return StorageService(
        endpoint=s.OSS_ENDPOINT,
        bucket=s.OSS_BUCKET,
        access_key=s.OSS_ACCESS_KEY,
        secret_key=s.OSS_SECRET_KEY,
    )
