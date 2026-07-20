import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class VideoTask(Base):
    __tablename__ = "video_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    avatar_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("avatars.id"), nullable=True)
    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    script_text: Mapped[str] = mapped_column(Text, nullable=False)
    tts_audio_url: Mapped[str | None] = mapped_column(String(500))
    video_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    cost_credits: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    prompt: Mapped[str | None] = mapped_column(Text)
    reference_video_url: Mapped[str | None] = mapped_column(String(1000))
    scene_image_url: Mapped[str | None] = mapped_column(String(1000))
    provider: Mapped[str] = mapped_column(String(20), default="seedance")  # seedance / hailuo
    long_video: Mapped[bool] = mapped_column(default=False)  # 长视频模式（多段拼接）
    segment_status: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: 分镜进度
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user = relationship("User", back_populates="video_tasks")
    avatar = relationship("Avatar", back_populates="video_tasks")
    template = relationship("Template", back_populates="video_tasks")
