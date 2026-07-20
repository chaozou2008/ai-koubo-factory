"""
分发API — 视频一键上传到抖音/快手/小红书/视频号
"""
import asyncio
import time
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.video_task import VideoTask
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/publish", tags=["publish"])

# 后台任务追踪
_running_tasks: dict = {}


class PublishRequest(BaseModel):
    task_id: str
    platform: str  # douyin / kuaishou / xiaohongshu / shipinhao
    title: str = ""
    description: str = ""


class PublishResponse(BaseModel):
    ok: bool
    msg: str


@router.post("", response_model=PublishResponse)
async def publish_video(
    req: PublishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    自动打开浏览器，将视频上传到指定平台。
    需要先在浏览器中登录对应平台账号。
    """
    task = await db.get(VideoTask, UUID(req.task_id))
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="视频不存在")
    if not task.video_url:
        raise HTTPException(status_code=400, detail="视频尚未生成完毕")

    if req.platform not in ("douyin", "kuaishou", "xiaohongshu", "shipinhao"):
        raise HTTPException(status_code=400, detail=f"不支持的平台: {req.platform}")

    # 检查是否有正在运行的任务
    task_key = f"{current_user.id}-{req.platform}"
    if task_key in _running_tasks:
        return PublishResponse(ok=False, msg=f"已有一个 {req.platform} 上传任务在运行中")

    # 从 OSS 下载视频到本地临时目录
    video_path = await _download_video(task.video_url)
    if not video_path:
        raise HTTPException(status_code=500, detail="下载视频失败")

    # 异步执行上传
    title = req.title or task.script_text or task.prompt or "AI口播视频"
    _running_tasks[task_key] = True

    try:
        from app.services.publish_service import publish_sync

        # 在子进程中运行以避免阻塞
        import concurrent.futures
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool, publish_sync, req.platform, video_path, title, req.description
            )
        return PublishResponse(**result)
    except Exception as e:
        logger.error(f"Publish error: {e}")
        return PublishResponse(ok=False, msg=str(e))
    finally:
        _running_tasks.pop(task_key, None)


async def _download_video(url: str) -> str | None:
    """从 OSS 下载视频到本地临时目录"""
    import httpx
    tmp = Path("D:/01-Workspace/AIWorkspace/FengVedio/backend/tmp")
    tmp.mkdir(exist_ok=True)
    fpath = tmp / f"video_{int(time.time())}.mp4"
    try:
        async with httpx.AsyncClient(timeout=120, trust_env=False) as client:
            resp = await client.get(url)
            if resp.status_code == 200 and len(resp.content) > 1000:
                fpath.write_bytes(resp.content)
                logger.info(f"Downloaded video to {fpath} ({len(resp.content)} bytes)")
                return str(fpath.resolve())
    except Exception as e:
        logger.error(f"Download failed: {e}")
    return None
