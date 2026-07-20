# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI口播工厂 (AI Koubo Factory) — a SaaS platform for generating AI digital-human talking-head videos. Target users are small Chinese merchants (beauty shops, clothing stores, etc.) who need short promotional videos for Douyin/WeChat Channels.

## Development Commands

### Backend (Python/FastAPI)

```bash
cd backend
venv\Scripts\activate                       # Activate Windows venv
uvicorn app.main:app --reload --port 8000   # Start API server
celery -A app.tasks.celery_app worker -l info -P solo --without-mingle --without-gossip  # Start Celery worker
pytest                                       # Run tests
```

### Frontend (Vue 3/TypeScript)

```bash
cd frontend
npm run dev      # Start dev server at localhost:5173
npm run build    # Type-check + production build
npm run preview  # Preview production build
```

### Key URLs

| URL | Purpose |
|-----|---------|
| `https://ai-koubo-factory.vercel.app` | 生产环境前端 |
| `http://localhost:5173` | 本地开发前端 |
| `http://localhost:8000/docs` | Swagger API docs (auto-generated) |
| `http://localhost:8000/api/health` | Health check |

### Login / Test Account

注册登录方式：手机号 + 密码，新用户赠送 100 算粒。

| 手机号 | 密码 | 算粒 |
|--------|------|:--:|
| 15600000001 | 123456 | 1000 |

## Architecture

### High-Level Flow

```
Vue 3 + Element Plus (frontend)
       │ REST (axios, JWT Bearer)
       ▼
FastAPI (backend) ──── PostgreSQL (PolarDB Supabase, async via SQLAlchemy)
       │                Redis (Upstash, Celery broker)
       ├── Celery Worker (async video generation)
       ├── Tencent Cloud MPS SyncDubbing API (TTS + voice cloning)
       ├── Volcengine Seedance 2.0 via Ark SDK (AI video generation)
       └── Alibaba Cloud OSS (audio/video/image storage)
```

### Backend Structure (`backend/app/`)

- **`main.py`** — FastAPI app creation, CORS middleware, router registration
- **`config.py`** — Pydantic Settings reading from `.env` (singleton via `@lru_cache`)
- **`database.py`** — SQLAlchemy async engine, session factory, `Base` declarative base, `get_db` dependency
- **`models/`** — SQLAlchemy ORM models: `User`, `Avatar`, `Template`, `VideoTask`, `Plan`, `Subscription`, `CreditLog`
- **`schemas/`** — Pydantic request/response models
- **`api/`** — FastAPI routers: `auth`, `avatars`, `templates`, `videos`, `plans`, `credits`, `publish`
- **`api/deps.py`** — `get_current_user` dependency: extracts JWT from `Authorization: Bearer` header, looks up user by UUID
- **`services/`** — Business logic singletons, each with a `get_*_service()` factory that reads config:
  - `tts_service.py` — Tencent Cloud MPS SyncDubbing (TC3-HMAC-SHA256 signing, voice cloning 25¥/voice, TTS 0.5¥/min)
  - `seedance_service.py` — Volcengine Ark SDK, model `doubao-seedance-2-0-260128` (~2.5¥/5s at 720p)
  - `storage_service.py` — Alibaba Cloud OSS (oss2 SDK), uploads to `audio/`, `video/`, `images/` prefixes
  - `credit_service.py` — Deduct/refund credits with atomic balance checks
  - `publish_service.py` — Playwright browser automation to upload videos to Douyin/Kuaishou/Xiaohongshu/Shipinhao
  - `video_pipeline.py` — The actual video generation pipeline (TTS→OSS→Seedance), used directly (not via Celery in current MVP due to Redis connectivity issues)
- **`tasks/`** — Celery app definition and `video_tasks.py` (Celery version of pipeline, currently bypassed)

### Frontend Structure (`frontend/src/`)

- **`main.ts`** — App bootstrap: Vue 3 + Pinia + Vue Router + Element Plus (with all icons globally registered)
- **`router/index.ts`** — Routes with `meta.requiresAuth` guard; redirects `/` to `/videos/create`; guest routes redirect to `/` when logged in
- **`api/client.ts`** — Axios instance with `baseURL: http://localhost:8000`, JWT interceptor, 401 auto-redirect to `/login`, 402 "insufficient credits" message
- **`stores/user.ts`** — Pinia store: user profile, credits balance, `fetchMe()`, `logout()`
- **`components/AppLayout.vue`** — Sidebar nav layout (生成视频 / 我的形象 / 视频管理 / 套餐中心) + header with credit badge and user dropdown
- **`views/`** — Page components: `Login`, `Register`, `Dashboard`, `AvatarList`, `AvatarCreate`, `VideoCreate`, `VideoList`, `VideoDetail`, `PlanList`, `CreditLog`

### Data Model Relationships

```
User 1──N Avatar (digital human avatars)
User 1──N VideoTask (generation jobs)
User 1──1 Subscription N──1 Plan
User 1──N CreditLog (credit transaction history)
VideoTask N──1 Avatar (optional, AI脱口秀 mode doesn't need one)
VideoTask N──1 Template (industry/scene template)
```

### Video Generation Pipeline (critical path)

1. User submits POST `/api/videos` → deducts 10 credits → creates `VideoTask(status=queued)`
2. Pipeline runs as `asyncio.create_task()` (not Celery in current MVP):
   - Sets `status=processing`
   - Optionally calls TTS for audio (currently skipped; Seedance gets scene prompt directly)
   - Calls Seedance `generate_video()` with image/audio/prompt
   - Polls `query_video_status()` every 5s for up to 7.5 minutes
   - On success: downloads video from Volcengine → uploads to OSS → sets `status=done`
   - On failure: sets `status=failed`, refunds credits via `refund_credits()`
3. Frontend polls `GET /api/videos/:id` to get status updates

### Auth Flow

- Phone + password registration (bcrypt hashed) → JWT token (HS256, 7-day expiry)
- New users get 100 free credits on registration
- All protected endpoints use `Depends(get_current_user)` which decodes JWT `sub` claim as user UUID

### Credit System

- Internal currency called "算粒" (credits)
- Types: `charge` (充值), `consume` (消耗), `refund` (退款)
- Video generation costs 10 credits per task
- Refund on generation failure; 402 HTTP status if insufficient balance

## Important Implementation Notes

- **No Celery in MVP**: The video pipeline currently runs via `asyncio.create_task()` in the FastAPI process due to Redis connectivity issues with Upstash. The Celery worker and `video_tasks.py` exist but are bypassed. See `_run_video_generation()` in `api/videos.py` — it calls `video_pipeline.run_video_pipeline()` directly.
- **Proxy avoidance**: All HTTP clients explicitly set `trust_env=False` because the dev machine has stale proxy env vars that would break connections.
- **Proxy env cleanup**: `config.py` removes HTTP_PROXY/HTTPS_PROXY env vars on import.
- **Database sessions**: The pipeline creates its own `AsyncSessionLocal` factory (short-lived sessions) to avoid PolarDB connection timeout issues. The `pool_recycle=60` setting is critical for PolarDB compatibility.
- **API base URL**: Hardcoded to `http://localhost:8000` in `frontend/src/api/client.ts`. No environment variable abstraction yet.
- **Publish service**: References hardcoded paths to `D:/05-Learning/AILearnning/KrLongAI_Simplify/` for Playwright browser profiles with pre-saved login sessions.
- **Seedance SDK note**: Uses `volcenginesdkarkruntime.Ark` (not the standard OpenAI-compatible client). The SDK's `tasks.create` returns a task object where status must be polled via `tasks.get`.
- **TTS voice fallback**: A hardcoded default voice ID is used when no avatar voice is available (line 50 of `video_pipeline.py`).
