from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class AvatarCreateRequest(BaseModel):
    name: str
    photo_urls: dict


class AvatarResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    photo_urls: dict | None
    material_id: str | None
    character_id: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AvatarListResponse(BaseModel):
    items: list[AvatarResponse]
    total: int
