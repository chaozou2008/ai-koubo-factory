from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    industry: str
    thumbnail_url: str | None
    preview_video_url: str | None
    config: dict | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    items: list[TemplateResponse]
    total: int
