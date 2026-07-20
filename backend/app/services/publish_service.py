"""
自动分发服务 — 通过 Playwright 浏览器自动化上传视频到各平台

依赖:
  - Playwright (已安装)
  - KrLongAI 项目的浏览器存档 (已登录状态)
  - ms-playwright 浏览器二进制文件
"""
import os
import sys
import json
import asyncio
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# KrLongAI 项目根目录
KRLONGAI_ROOT = Path("D:/05-Learning/AILearnning/KrLongAI_Simplify")

# 浏览器二进制（默认路径已在 Playwright 安装时配置好，无需额外设置）

os.environ.setdefault("UV_NO_TITLE", "1")
os.environ.pop("NODE_OPTIONS", None)
for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
    os.environ.pop(key, None)

# 各平台配置
PLATFORM_CONFIG = {
    "douyin": {
        "name": "抖音",
        "url": "https://creator.douyin.com/creator-micro/content/upload",
        "profile": KRLONGAI_ROOT / "browser_profile" / "抖音",
        "title_sel": 'input[placeholder*="标题"], [placeholder*="标题"]',
        "desc_sel": 'div[contenteditable="true"], textarea[placeholder*="简介"]',
    },
    "kuaishou": {
        "name": "快手",
        "url": "https://cp.kuaishou.com/article/publish/video",
        "profile": Path("D:/05-Learning/AILearnning/KrLongAI_Simplify/browser_profile_ks"),
        "title_sel": 'input[placeholder*="标题"], [placeholder*="标题"]',
        "desc_sel": 'div[contenteditable="true"], textarea[placeholder*="简介"]',
    },
    "xiaohongshu": {
        "name": "小红书",
        "url": "https://creator.xiaohongshu.com/publish/publish",
        "profile": Path("D:/05-Learning/AILearnning/KrLongAI_Simplify/browser_profile_xhs"),
        "title_sel": 'input[placeholder*="标题"], [placeholder*="标题"]',
        "desc_sel": 'div[contenteditable="true"], textarea[placeholder*="正文"]',
    },
    "shipinhao": {
        "name": "视频号",
        "url": "https://channels.weixin.qq.com/platform/post/create",
        "profile": Path("D:/05-Learning/AILearnning/KrLongAI_Simplify/browser_profile_shipinhao"),
        "title_sel": 'input[placeholder*="标题"], [placeholder*="描述"]',
        "desc_sel": 'div[contenteditable="true"], textarea[placeholder*="描述"]',
    },
}


def publish_sync(platform: str, video_path: str, title: str, description: str = "", cover_path: str = ""):
    """同步入口——供 Celery 或子进程调用"""
    return asyncio.run(_publish(platform, video_path, title, description, cover_path))


async def _publish(platform: str, video_path: str, title: str, description: str = "", cover_path: str = ""):
    """核心上传逻辑"""
    from playwright.async_api import async_playwright

    cfg = PLATFORM_CONFIG.get(platform)
    if not cfg:
        return {"ok": False, "msg": f"未知平台: {platform}"}

    # 确保视频文件存在
    if not os.path.exists(video_path):
        return {"ok": False, "msg": f"视频文件不存在: {video_path}"}

    profile_dir = Path(cfg["profile"])
    profile_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"[Publish] {cfg['name']}: 打开浏览器, 视频={video_path}")

    pw = await async_playwright().start()
    try:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
        )
        page = await context.new_page()
        await page.goto(cfg["url"], wait_until="domcontentloaded", timeout=30000)

        # 等待用户登录
        await asyncio.sleep(2)
        if "login" in page.url.lower() or "passport" in page.url.lower():
            logger.info(f"[Publish] {cfg['name']}: 等待登录...")
            await page.wait_for_function(
                """() => { const u = window.location.href.toLowerCase();
                    return !u.includes('login') && !u.includes('passport'); }""",
                timeout=600_000,  # 10分钟
            )
            await asyncio.sleep(2)
            await page.goto(cfg["url"], wait_until="domcontentloaded", timeout=30000)

        await asyncio.sleep(3)

        # 上传视频文件
        try:
            file_input = page.locator('input[type="file"]').first
            await file_input.set_input_files(video_path)
            logger.info(f"[Publish] {cfg['name']}: 视频文件已选择")
            await asyncio.sleep(5)
        except Exception as e:
            logger.warning(f"[Publish] {cfg['name']}: 选择视频文件失败: {e}")

        # 填写标题
        try:
            el = page.locator(cfg["title_sel"]).first
            await el.wait_for(state="visible", timeout=15000)
            await el.fill("")
            await el.fill(title)
            logger.info(f"[Publish] {cfg['name']}: 标题已填写")
        except Exception as e:
            logger.warning(f"[Publish] {cfg['name']}: 填写标题失败: {e}")

        # 填写描述
        if description.strip():
            try:
                el = page.locator(cfg["desc_sel"]).first
                await el.wait_for(state="visible", timeout=10000)
                await el.fill("")
                await el.fill(description)
                logger.info(f"[Publish] {cfg['name']}: 描述已填写")
            except Exception as e:
                logger.warning(f"[Publish] {cfg['name']}: 填写描述失败: {e}")

        # 上传封面（如果有）
        if cover_path and os.path.exists(cover_path):
            try:
                cover_abs = str(Path(cover_path).resolve())
                btns = page.locator('button, [role="button"], span, div')
                count = await btns.count()
                for i in range(count):
                    el = btns.nth(i)
                    text = await el.inner_text()
                    if "编辑封面" in text or "修改封面" in text:
                        await el.click(force=True)
                        await asyncio.sleep(3)
                        file_inputs = page.locator('input[type="file"]')
                        fc = await file_inputs.count()
                        for j in range(fc):
                            fi = file_inputs.nth(j)
                            try:
                                await fi.set_input_files(cover_abs, timeout=5000)
                                logger.info(f"[Publish] {cfg['name']}: 封面已上传")
                                # 确认按钮
                                for t in ["完成", "确定", "保存"]:
                                    try:
                                        b = page.locator(f'button:has-text("{t}"), text="{t}"').last
                                        if await b.is_visible(timeout=2000):
                                            await b.click(force=True)
                                            break
                                    except Exception:
                                        continue
                                break
                            except Exception:
                                continue
                        break
            except Exception as e:
                logger.warning(f"[Publish] {cfg['name']}: 上传封面失败: {e}")

        logger.info(f"[Publish] {cfg['name']}: 页面已准备好, 等待手动点击发布...")
        return {
            "ok": True,
            "msg": f"{cfg['name']} 发布页面已准备完毕，请在浏览器中确认并点击发布",
            "url": cfg["url"],
        }
    except Exception as e:
        logger.error(f"[Publish] {cfg['name']}: {e}")
        return {"ok": False, "msg": str(e)}
    finally:
        # 不关闭浏览器，留给用户手动发布
        pass
