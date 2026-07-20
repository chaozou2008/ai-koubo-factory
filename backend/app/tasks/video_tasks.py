import asyncio
import time
from datetime import datetime
from uuid import UUID
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings
from app.models.video_task import VideoTask
from app.models.avatar import Avatar
from app.models.template import Template
from app.services.tts_service import get_tts_service
from app.services.seedance_service import get_seedance_service
from app.services.storage_service import get_storage_service
from app.services.credit_service import refund_credits

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_video_task(self, task_id: str, duration: int = 5):
    return asyncio.run(_generate_video(task_id, duration))


async def _generate_video(task_id: str, duration: int = 5):
    """视频生成管线: TTS → OSS → Seedance"""
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        if not task:
            return {"error": "Task not found"}

        try:
            # Step 1: TTS 语音合成
            task.status = "processing"
            await db.commit()

            tts = get_tts_service()
            storage = get_storage_service()
            seedance = get_seedance_service()

            # 获取 Avatar 信息
            avatar = await db.get(Avatar, task.avatar_id)

            # 使用 VoiceId 合成，没有的话用默认克隆音色
            voice_id = getattr(avatar, 'voice_id', '') or '' if avatar else ''
            if not voice_id:
                # 使用预设的默认音色（首次测试时克隆的女声）
                voice_id = 'v1_Mr/I+AnmPB/pm/1UZPa9sVnjH75LHrCKMAaJkynaE9hAzckuOo/oekN9faNyt17Mm+U='
            tts_result = await tts.synthesize(text=task.script_text, voice_id=voice_id)

            # Step 2: 上传音频到 OSS
            audio_url = await storage.upload_audio(
                "tts_output.wav", tts_result["audio_data"]
            )
            task.tts_audio_url = audio_url
            task.status = "tts_done"
            await db.commit()

            # Step 3: 获取形象图片 URL + 提示词
            image_url = ""
            scene_prompt = task.prompt or ""

            if avatar and avatar.photo_urls:
                image_url = avatar.photo_urls.get("front", "") or list(avatar.photo_urls.values())[0] if avatar.photo_urls else ""

            # 从模板获取默认场景提示词
            if not scene_prompt:
                template = await db.get(Template, task.template_id)
                if template and template.config:
                    scene_prompt = template.config.get("seedance_prompt", "")

            # Step 4: Seedance 视频生成
            task.status = "video_generating"
            await db.commit()

            video_result = await seedance.generate_video(
                image_url=image_url,
                audio_url=audio_url,
                script_text=scene_prompt or task.script_text,
                reference_video_url=task.reference_video_url or "",
                duration=duration,
                resolution="720p",
                ratio="9:16",
            )

            # Step 5: 轮询 Seedance 状态
            seedance_task_id = video_result["task_id"]
            for i in range(60):  # 最多等5分钟
                await asyncio.sleep(5)
                status = await seedance.query_video_status(seedance_task_id)
                if status["status"] == "succeeded":
                    task.video_url = status.get("video_url", "")
                    task.status = "done"
                    task.completed_at = datetime.utcnow()
                    await db.commit()
                    return {"status": "done", "video_url": task.video_url}
                elif status["status"] in ("failed", "expired", "cancelled"):
                    raise Exception(status.get("error", f"Seedance task {status['status']}"))

            raise Exception("Seedance 视频生成超时")

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            await db.commit()
            if task.cost_credits > 0:
                await refund_credits(db, task.user_id, task.cost_credits,
                                     f"视频生成失败退款: {task_id}")
            raise
