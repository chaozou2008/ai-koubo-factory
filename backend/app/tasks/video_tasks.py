import asyncio
from datetime import datetime
from uuid import UUID
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings
from app.models.video_task import VideoTask
from app.services.tts_service import get_tts_service
from app.services.seedance_service import get_seedance_service
from app.services.storage_service import get_storage_service
from app.services.credit_service import refund_credits

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_video_task(self, task_id: str):
    return asyncio.run(_generate_video(task_id))


async def _generate_video(task_id: str):
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        if not task:
            return {"error": "Task not found"}

        try:
            task.status = "processing"

            tts = get_tts_service()
            tts_result = await tts.synthesize(text=task.script_text, voice_id=f"VOICE-{task.avatar_id}")
            task.tts_audio_url = tts_result["audio_url"]
            task.status = "tts_done"

            seedance = get_seedance_service()
            video_result = await seedance.generate_video(
                material_id="", audio_url=task.tts_audio_url,
                template_config={}, script_text=task.script_text,
            )
            status = await seedance.query_video_status(video_result["task_id"])

            task.video_url = status["video_url"]
            task.status = "done"
            task.completed_at = datetime.utcnow()
            await db.commit()
            return {"status": "done", "video_url": task.video_url}

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            await db.commit()
            if task.cost_credits > 0:
                await refund_credits(db, task.user_id, task.cost_credits,
                                     f"视频生成失败退款: {task_id}")
            raise
