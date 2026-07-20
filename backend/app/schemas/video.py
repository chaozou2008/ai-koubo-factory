from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class VideoCreateRequest(BaseModel):
    avatar_id: str | None = None  # 空字符串或UUID字符串，AI脱口秀模式不需要
    template_id: UUID
    script_text: str
    prompt: str | None = None
    reference_video_url: str | None = None
    scene_image_url: str | None = None  # 餐饮等场景：店铺/产品照片URL
    provider: str = Field(default="seedance")  # seedance / hailuo
    long_video: bool = Field(default=False)  # 长视频模式（多段拼接，仅hailuo）
    duration: int = Field(default=5, ge=4, le=15)  # 4-15秒


class VideoTaskResponse(BaseModel):
    id: UUID
    avatar_id: UUID | None = None
    template_id: UUID
    script_text: str
    prompt: str | None = None
    tts_audio_url: str | None
    video_url: str | None
    status: str
    cost_credits: int
    error_message: str | None
    provider: str
    long_video: bool
    segment_status: str | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    items: list[VideoTaskResponse]
    total: int
