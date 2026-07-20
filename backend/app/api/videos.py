from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.avatar import Avatar
from app.models.template import Template
from app.models.video_task import VideoTask
from app.schemas.video import VideoCreateRequest, VideoTaskResponse, VideoListResponse
from app.api.deps import get_current_user
from app.services.credit_service import deduct_credits
from app.tasks.video_tasks import generate_video_task

router = APIRouter(prefix="/api/videos", tags=["videos"])
VIDEO_CREDIT_COST = 10


@router.post("", response_model=VideoTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    req: VideoCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.avatar_id and req.avatar_id.strip():
        avatar = await db.get(Avatar, UUID(req.avatar_id))
        if not avatar or avatar.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="形象不存在")
        if avatar.status != "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="形象未就绪")

    template = await db.get(Template, req.template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="模板不存在")

    # 长视频仅支持海螺
    if req.long_video and req.provider != "hailuo":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="长视频仅支持海螺AI引擎")

    credit_cost = 30 if req.long_video else VIDEO_CREDIT_COST
    ok = await deduct_credits(db, current_user.id, credit_cost,
                              f"视频生成: {req.script_text[:20]}...")
    if not ok:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="算粒不足，请充值")

    task = VideoTask(
        user_id=current_user.id,
        avatar_id=UUID(req.avatar_id) if (req.avatar_id and req.avatar_id.strip()) else None,
        template_id=req.template_id, script_text=req.script_text,
        cost_credits=credit_cost,
        prompt=req.prompt,
        reference_video_url=req.reference_video_url,
        scene_image_url=req.scene_image_url,
        provider=req.provider,
        long_video=req.long_video,
    )
    db.add(task)
    await db.commit()
    # MVP: 异步后台生成（绕过Celery Redis问题）
    import asyncio as _asyncio
    _asyncio.create_task(_run_video_generation(task.id, req.duration, req.provider, req.long_video))
    return task


async def _run_video_generation(task_id, duration, provider="seedance", long_video=False):
    from app.services.video_pipeline import run_video_pipeline
    import logging
    try:
        await run_video_pipeline(str(task_id), duration, provider, long_video)
    except Exception as e:
        logging.error(f"Video generation failed: {e}")


@router.get("", response_model=VideoListResponse)
async def list_videos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VideoTask).where(VideoTask.user_id == current_user.id).order_by(VideoTask.created_at.desc())
    )
    items = result.scalars().all()
    return VideoListResponse(items=list(items), total=len(items))


@router.get("/{video_id}", response_model=VideoTaskResponse)
async def get_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(VideoTask, video_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频不存在")
    return task


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(VideoTask, video_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频不存在")
    await db.delete(task)
