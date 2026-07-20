"""视频生成管线：TTS → OSS → Seedance/海螺（不含Celery依赖）"""
import asyncio
import httpx
import json
import logging
import os
import tempfile
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings
from app.models.video_task import VideoTask
from app.models.avatar import Avatar
from app.models.template import Template
from app.services.tts_service import get_tts_service
from app.services.seedance_service import get_seedance_service, get_seedance_mini_service
from app.services.hailuo_service import get_hailuo_service
from app.services.storage_service import get_storage_service
from app.services.credit_service import refund_credits

settings = get_settings()
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # 每次用前先 ping，确保连接存活
    pool_recycle=60,          # 每60秒回收连接，避免被PolarDB杀
    pool_size=5,
    max_overflow=2,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

logger = logging.getLogger(__name__)


async def run_video_pipeline(task_id: str, duration: int = 5, provider: str = "seedance",
                              long_video: bool = False):
    """视频生成管线: TTS → OSS → Seedance/海螺（短Session避免超时）"""

    # === Phase 1: 准备阶段（短暂DB操作） ===
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        if not task:
            return {"error": "Task not found"}

        avatar = await db.get(Avatar, task.avatar_id) if task.avatar_id else None
        template = await db.get(Template, task.template_id)
        scene_prompt = task.prompt or ""
        if not scene_prompt and template and template.config:
            scene_prompt = template.config.get("seedance_prompt", "")
        image_url = task.scene_image_url or ""
        if not image_url and avatar and avatar.photo_urls:
            image_url = avatar.photo_urls.get("front", "") or ""
        voice_id = getattr(avatar, 'voice_id', '') or '' if avatar else ''
        if not voice_id:
            voice_id = 'v1_Mr/I+AnmPB/pm/1UZPa9sVnjH75LHrCKMAaJkynaE9hAzckuOo/oekN9faNyt17Mm+U='

        task.status = "processing"
        await db.commit()

    # === Phase 2: 视频生成（按provider分发） ===
    try:
        script_text = ""
        reference_video_url = ""
        async with AsyncSessionLocal() as db:
            task = await db.get(VideoTask, UUID(task_id))
            task.status = "video_generating"
            script_text = task.script_text or ""
            reference_video_url = task.reference_video_url or ""
            await db.commit()

        if provider == "hailuo":
            if long_video:
                return await _run_hailuo_long_pipeline(
                    task_id, scene_prompt, image_url, duration, script_text)
            else:
                return await _run_hailuo_pipeline(task_id, scene_prompt, image_url, duration)
        elif provider == "seedance-mini":
            if long_video:
                raise ValueError("长视频模式仅支持海螺AI引擎")
            return await _run_seedance_mini_pipeline(task_id, scene_prompt, image_url, duration,
                                                     script_text, reference_video_url)
        else:
            if long_video:
                raise ValueError("长视频模式仅支持海螺AI引擎")
            return await _run_seedance_pipeline(task_id, scene_prompt, image_url, duration,
                                                script_text, reference_video_url)

    except Exception as e:
        async with AsyncSessionLocal() as db:
            task = await db.get(VideoTask, UUID(task_id))
            task.status = "failed"
            task.error_message = str(e)
            await db.commit()
            if task.cost_credits > 0:
                await refund_credits(db, task.user_id, task.cost_credits,
                                     f"视频生成失败退款: {task_id}")
        raise


async def _run_seedance_pipeline(
    task_id: str, scene_prompt: str, image_url: str, duration: int,
    script_text: str, reference_video_url: str,
) -> dict:
    """Seedance 2.0 视频生成管线"""
    seedance = get_seedance_service()
    video_result = await seedance.generate_video(
        image_url=image_url,
        audio_url="",
        script_text=scene_prompt or script_text,
        reference_video_url=reference_video_url,
        duration=duration,
        resolution="720p",
        ratio="9:16",
    )

    seedance_task_id = video_result["task_id"]

    # 把 Seedance 任务 ID 存进 DB，方便手动追踪
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        task.tts_audio_url = f"seedance://{seedance_task_id}"
        await db.commit()

    volcanic_video_url = ""
    for i in range(240):  # 最多等20分钟
        await asyncio.sleep(5)
        status = await seedance.query_video_status(seedance_task_id)
        if status["status"] == "succeeded":
            volcanic_video_url = status.get("video_url", "")
            break
        elif status["status"] in ("failed", "expired", "cancelled"):
            raise Exception(status.get("error", f"Seedance {status['status']}"))

    if not volcanic_video_url:
        last_status = await seedance.query_video_status(seedance_task_id)
        raise Exception(f"Seedance 视频生成超时 (状态: {last_status.get('status', 'unknown')}, seedance_id: {seedance_task_id})")

    # 先存火山URL → 异步上传OSS（上传失败不影响结果）
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        task.video_url = volcanic_video_url
        task.status = "done"
        task.completed_at = datetime.utcnow()
        await db.commit()

    await _upload_to_oss(task_id, volcanic_video_url)
    return {"status": "done", "video_url": volcanic_video_url}


async def _run_seedance_mini_pipeline(
    task_id: str, scene_prompt: str, image_url: str, duration: int,
    script_text: str, reference_video_url: str,
) -> dict:
    """Seedance 2.0 Mini 视频生成管线 — 成本降低约50%"""
    seedance = get_seedance_mini_service()
    video_result = await seedance.generate_video(
        image_url=image_url,
        audio_url="",
        script_text=scene_prompt or script_text,
        reference_video_url=reference_video_url,
        duration=duration,
        resolution="720p",
        ratio="9:16",
    )

    seedance_task_id = video_result["task_id"]

    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        task.tts_audio_url = f"seedance-mini://{seedance_task_id}"
        await db.commit()

    volcanic_video_url = ""
    for i in range(240):
        await asyncio.sleep(5)
        status = await seedance.query_video_status(seedance_task_id)
        if status["status"] == "succeeded":
            volcanic_video_url = status.get("video_url", "")
            break
        elif status["status"] in ("failed", "expired", "cancelled"):
            raise Exception(status.get("error", f"Seedance Mini {status['status']}"))

    if not volcanic_video_url:
        last_status = await seedance.query_video_status(seedance_task_id)
        raise Exception(f"Seedance Mini 视频生成超时 (seedance_id: {seedance_task_id})")

    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        task.video_url = volcanic_video_url
        task.status = "done"
        task.completed_at = datetime.utcnow()
        await db.commit()

    await _upload_to_oss(task_id, volcanic_video_url)
    return {"status": "done", "video_url": volcanic_video_url}


async def _run_hailuo_pipeline(
    task_id: str, scene_prompt: str, image_url: str, duration: int,
) -> dict:
    """海螺AI 视频生成管线"""
    hailuo = get_hailuo_service()

    # 海螺的 duration 只支持 6 或 10，映射一下
    hailuo_duration = 6 if duration <= 6 else 10
    resolution = "768P"

    video_result = await hailuo.generate_video(
        prompt=scene_prompt,
        image_url=image_url,
        duration=hailuo_duration,
        resolution=resolution,
    )

    hailuo_task_id = video_result["task_id"]

    # 存海螺任务 ID 到 DB
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        task.tts_audio_url = f"hailuo://{hailuo_task_id}"
        await db.commit()

    # 轮询海螺任务状态
    file_id = ""
    for i in range(120):  # 最多等10分钟（海螺通常更快）
        await asyncio.sleep(10)  # 海螺建议10秒轮询间隔
        status = await hailuo.query_video_status(hailuo_task_id)
        if status["status"] == "Success":
            file_id = status.get("file_id", "")
            break
        elif status["status"] == "Fail":
            raise Exception(status.get("error", "Hailuo generation failed"))

    if not file_id:
        last_status = await hailuo.query_video_status(hailuo_task_id)
        raise Exception(f"海螺视频生成超时 (状态: {last_status.get('status', 'unknown')}, task_id: {hailuo_task_id})")

    # 获取下载链接
    download_url = await hailuo.get_download_url(file_id)

    # 先存下载URL → 异步上传OSS
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        task.video_url = download_url
        task.status = "done"
        task.completed_at = datetime.utcnow()
        await db.commit()

    await _upload_to_oss(task_id, download_url)
    return {"status": "done", "video_url": download_url}


async def _run_hailuo_long_pipeline(
    task_id: str, scene_prompt: str, image_url: str, duration: int, script_text: str,
) -> dict:
    """海螺AI 长视频管线: 拆段→逐段生成→ffmpeg拼接→上传OSS"""
    from app.services.script_splitter import split_script_for_long_video

    # Step 0: 拆分脚本
    segments = split_script_for_long_video(script_text)
    total = len(segments)
    logger.info(f"Long video: split script into {total} segments")

    # 初始化分镜状态
    seg_status_data = {
        "total": total, "completed": 0, "current": 0,
        "segments": [{"index": i, "status": "queued", "prompt": ""} for i in range(total)],
    }
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        task.segment_status = json.dumps(seg_status_data, ensure_ascii=False)
        await db.commit()

    hailuo = get_hailuo_service()
    segment_files = []  # list of local temp file paths
    completed_count = 0
    hailuo_duration = 6 if duration <= 6 else 10

    for i, chunk in enumerate(segments):
        # 更新当前段状态为 generating
        seg_status_data["current"] = i
        seg_status_data["segments"][i]["status"] = "generating"
        seg_status_data["segments"][i]["prompt"] = chunk[:100]
        async with AsyncSessionLocal() as db:
            task = await db.get(VideoTask, UUID(task_id))
            task.segment_status = json.dumps(seg_status_data, ensure_ascii=False)
            await db.commit()

        # 构建每段的 prompt
        segment_prompt = f"{scene_prompt} — {chunk}" if scene_prompt else chunk

        try:
            # 调用海螺生成
            video_result = await hailuo.generate_video(
                prompt=segment_prompt,
                image_url=image_url,
                duration=hailuo_duration,
                resolution="768P",
            )
            hailuo_task_id = video_result["task_id"]

            # 轮询
            file_id = ""
            for _ in range(120):
                await asyncio.sleep(10)
                status = await hailuo.query_video_status(hailuo_task_id)
                if status["status"] == "Success":
                    file_id = status.get("file_id", "")
                    break
                elif status["status"] == "Fail":
                    raise Exception(status.get("error", "Hailuo segment failed"))

            if not file_id:
                raise Exception(f"段 {i+1} 生成超时")

            # 下载到临时文件
            download_url = await hailuo.get_download_url(file_id)
            temp_path = await _download_segment_to_temp(task_id, i, download_url)
            segment_files.append(temp_path)

            # 标记完成
            seg_status_data["completed"] = i + 1
            seg_status_data["segments"][i]["status"] = "done"
            completed_count = i + 1

        except Exception as e:
            # 某段失败 — 设置为 failed，退还未生成的段
            seg_status_data["segments"][i]["status"] = "failed"
            async with AsyncSessionLocal() as db:
                task = await db.get(VideoTask, UUID(task_id))
                task.status = "failed"
                task.error_message = f"分镜 {i+1}/{total} 失败: {e}"
                task.segment_status = json.dumps(seg_status_data, ensure_ascii=False)
                await db.commit()
                remaining = total - completed_count
                if remaining > 0:
                    refund_amount = remaining * 10
                    await refund_credits(db, task.user_id, refund_amount,
                                         f"长视频分镜 {i+1} 失败退款: {task_id}")
            await _cleanup_temp_segments(segment_files)
            raise

        # 段间延迟 5s，避免限流
        if i < total - 1:
            await asyncio.sleep(5)

    # === Concatenate ===
    try:
        final_bytes = await _concat_videos_with_ffmpeg(segment_files, task_id)
    except Exception as e:
        logger.error(f"ffmpeg concat failed: {e}")
        # 拼接失败，上传第一段作为 fallback
        async with AsyncSessionLocal() as db:
            task = await db.get(VideoTask, UUID(task_id))
            task.error_message = f"视频拼接失败: {e}，仅保留第1段"
            await db.commit()
        if segment_files:
            storage = get_storage_service()
            with open(segment_files[0], "rb") as f:
                oss_url = await storage.upload_video(f"long_fallback_{task_id}.mp4", f.read())
            async with AsyncSessionLocal() as db:
                task = await db.get(VideoTask, UUID(task_id))
                task.video_url = oss_url
                task.status = "done"
                task.completed_at = datetime.utcnow()
                await db.commit()
        await _cleanup_temp_segments(segment_files)
        return {"status": "done", "video_url": oss_url if segment_files else ""}

    # === Upload final video to OSS ===
    storage = get_storage_service()
    oss_url = await storage.upload_video(f"long_{task_id[:8]}.mp4", final_bytes)

    # === Finalize ===
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        task.video_url = oss_url
        task.status = "done"
        task.completed_at = datetime.utcnow()
        task.segment_status = json.dumps(seg_status_data, ensure_ascii=False)
        await db.commit()

    await _cleanup_temp_segments(segment_files)
    return {"status": "done", "video_url": oss_url}


# --- Long Video Helpers ---

async def _download_segment_to_temp(task_id: str, index: int, url: str) -> str:
    """下载段视频到临时文件，返回本地路径"""
    tmpdir = tempfile.gettempdir()
    path = os.path.join(tmpdir, f"hailuo_{task_id[:8]}_seg{index}.mp4")
    async with httpx.AsyncClient(timeout=120, follow_redirects=True, trust_env=False) as http:
        resp = await http.get(url)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
    logger.info(f"Downloaded segment {index}: {len(resp.content)} bytes -> {path}")
    return path


async def _concat_videos_with_ffmpeg(segment_files: list[str], task_id: str) -> bytes:
    """用 ffmpeg concat demuxer 拼接多个 MP4 文件，返回最终视频 bytes"""
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    tmpdir = tempfile.gettempdir()
    concat_list = os.path.join(tmpdir, f"concat_{task_id[:8]}.txt")
    output_path = os.path.join(tmpdir, f"long_{task_id[:8]}.mp4")

    # 写 concat list
    with open(concat_list, "w", encoding="utf-8") as f:
        for seg in segment_files:
            f.write(f"file '{seg.replace(chr(92), '/')}'\n")

    # 先尝试 -c copy（无损拼接）
    cmd = [ffmpeg, "-f", "concat", "-safe", "0", "-i", concat_list,
           "-c", "copy", output_path, "-y"]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        # copy 模式失败 → 尝试重编码
        logger.warning(f"ffmpeg copy concat failed, trying re-encode...")
        cmd = [ffmpeg, "-f", "concat", "-safe", "0", "-i", concat_list,
               "-c:v", "libx264", "-c:a", "aac", output_path, "-y"]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg concat failed: {stderr.decode()[:500]}")

    with open(output_path, "rb") as f:
        result = f.read()
    logger.info(f"Concatenated {len(segment_files)} segments -> {len(result)} bytes")
    return result


async def _cleanup_temp_segments(segment_files: list[str]):
    """删除临时段文件"""
    for path in segment_files:
        try:
            os.remove(path)
        except Exception:
            pass


async def _upload_to_oss(task_id: str, source_url: str):
    """后台下载视频 → 上传OSS，成功则替换为永久URL"""
    try:
        storage = get_storage_service()
        async with httpx.AsyncClient(timeout=60, follow_redirects=True, trust_env=False) as http:
            video_resp = await http.get(source_url)
            if video_resp.status_code == 200 and len(video_resp.content) > 1000:
                oss_url = await storage.upload_video("output.mp4", video_resp.content)
                async with AsyncSessionLocal() as db:
                    task = await db.get(VideoTask, UUID(task_id))
                    task.video_url = oss_url
                    await db.commit()
                logger.info(f"Video uploaded to OSS: {oss_url}")
            else:
                logger.warning(f"Failed to download video, keeping temp URL")
    except Exception as e:
        logger.error(f"OSS upload failed (video still available via temp URL): {e}")
