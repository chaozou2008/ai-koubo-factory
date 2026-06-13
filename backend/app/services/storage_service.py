"""存储服务：MVP阶段返回模拟URL"""
import uuid


class StorageService:
    def __init__(self, endpoint: str = "", bucket: str = "", access_key: str = "", secret_key: str = ""):
        self.endpoint = endpoint
        self.bucket = bucket

    async def upload_file(self, file_path: str, content: bytes, content_type: str) -> str:
        ext = file_path.split(".")[-1]
        key = f"videos/{uuid.uuid4().hex}.{ext}"
        return f"https://{self.bucket}.{self.endpoint}/{key}"


def get_storage_service() -> StorageService:
    from app.config import get_settings
    s = get_settings()
    return StorageService(endpoint=s.OSS_ENDPOINT, bucket=s.OSS_BUCKET,
                          access_key=s.OSS_ACCESS_KEY, secret_key=s.OSS_SECRET_KEY)
