from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class VideoCreateRequest(BaseModel):
    avatar_id: UUID
    template_id: UUID
    script_text: str


class VideoTaskResponse(BaseModel):
    id: UUID
    avatar_id: UUID
    template_id: UUID
    script_text: str
    tts_audio_url: str | None
    video_url: str | None
    status: str
    cost_credits: int
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    items: list[VideoTaskResponse]
    total: int
