# AI口播工厂 — MVP实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零构建AI数字人口播视频生成SaaS平台MVP——面向国内小商家的Web应用，支持创建虚拟数字人形象、选模板、输入文案、自动生成口播视频。

**Architecture:** Vue 3 + Element Plus 前端，Python FastAPI 后端REST API，PostgreSQL持久化，Celery + Redis异步任务处理视频生成，Seedance 2.0 API生成视频画面，腾讯云MAIS合成语音。

**Tech Stack:** Vue 3, Element Plus, Vite, TypeScript, Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery, Seedance 2.0 API, 腾讯云MAIS, OSS/COS

---

## 文件结构规划

```
FengVedio/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI入口，注册路由
│   │   ├── config.py                # 配置管理（环境变量）
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── __init__.py          # 导入所有模型
│   │   │   ├── user.py              # User模型
│   │   │   ├── avatar.py            # Avatar模型
│   │   │   ├── template.py          # Template模型
│   │   │   ├── video_task.py        # VideoTask模型
│   │   │   ├── plan.py              # Plan模型
│   │   │   ├── subscription.py      # Subscription模型
│   │   │   └── credit_log.py        # CreditLog模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # 登录/注册请求响应
│   │   │   ├── avatar.py            # 形象相关schema
│   │   │   ├── template.py          # 模板相关schema
│   │   │   ├── video.py             # 视频任务schema
│   │   │   ├── plan.py              # 套餐schema
│   │   │   └── credit.py            # 算粒schema
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # /api/auth/*
│   │   │   ├── avatars.py           # /api/avatars/*
│   │   │   ├── templates.py         # /api/templates/*
│   │   │   ├── videos.py            # /api/videos/*
│   │   │   ├── plans.py             # /api/plans/*
│   │   │   ├── credits.py           # /api/credits/*
│   │   │   └── deps.py              # 公共依赖(get_db, get_current_user)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── tts_service.py       # 腾讯云MAIS TTS封装
│   │   │   ├── seedance_service.py  # Seedance 2.0 API封装
│   │   │   ├── credit_service.py    # 算粒扣减/退还
│   │   │   └── storage_service.py   # OSS/COS上传下载
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── celery_app.py        # Celery实例配置
│   │       └── video_tasks.py       # 视频生成异步任务
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_avatars.py
│       ├── test_videos.py
│       └── test_credits.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── api/
│   │   │   ├── client.ts            # axios实例+拦截器
│   │   │   ├── auth.ts
│   │   │   ├── avatars.ts
│   │   │   ├── templates.ts
│   │   │   ├── videos.ts
│   │   │   ├── plans.ts
│   │   │   └── credits.ts
│   │   ├── stores/
│   │   │   └── user.ts              # Pinia用户状态
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── AvatarCreate.vue
│   │   │   ├── AvatarList.vue
│   │   │   ├── VideoCreate.vue
│   │   │   ├── VideoList.vue
│   │   │   ├── VideoDetail.vue
│   │   │   ├── PlanList.vue
│   │   │   └── CreditLog.vue
│   │   ├── components/
│   │   │   ├── AppLayout.vue
│   │   │   └── CreditBadge.vue
│   │   └── styles/
│   │       └── global.css
│   └── public/
└── docs/
    └── superpowers/
        ├── specs/
        │   └── 2026-06-13-ai-koubo-factory-design.md
        └── plans/
            └── (this file)
```

---

### Task 1: 项目脚手架搭建

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `frontend/` (via Vite)

- [ ] **Step 1: 创建后端目录 + requirements.txt**

```bash
mkdir -p backend/app/models backend/app/schemas backend/app/api backend/app/services backend/app/tasks backend/tests
```

`backend/requirements.txt`:
```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
asyncpg==0.30.0
psycopg2-binary==2.9.10
alembic==1.14.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.19
pydantic==2.10.4
pydantic-settings==2.7.1
redis==5.2.1
celery[redis]==5.4.0
httpx==0.28.1
tencentcloud-sdk-python==3.0.1298
oss2==2.19.1
pytest==8.3.4
pytest-asyncio==0.25.0
httpx==0.28.1
```

- [ ] **Step 2: 编写配置管理 `backend/app/config.py`**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "AI口播工厂"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/koubo_factory"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/koubo_factory"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-me-in-production-please"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Tencent Cloud MAIS (TTS)
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""
    TENCENT_MAIS_REGION: str = "ap-guangzhou"

    # Volcengine Seedance
    VOLCENGINE_ACCESS_KEY: str = ""
    VOLCENGINE_SECRET_KEY: str = ""

    # OSS/COS
    OSS_ENDPOINT: str = ""
    OSS_BUCKET: str = ""
    OSS_ACCESS_KEY: str = ""
    OSS_SECRET_KEY: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 3: 编写数据库连接 `backend/app/database.py`**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 4: 编写FastAPI入口 `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
```

- [ ] **Step 5: 创建前端脚手架**

```bash
cd frontend
npm create vite@latest . -- --template vue-ts
npm install
npm install element-plus @element-plus/icons-vue vue-router@4 pinia axios
```

- [ ] **Step 6: 启动验证**

```bash
# 终端1: 后端
cd backend && uvicorn app.main:app --reload --port 8000
# 终端2: 前端
cd frontend && npm run dev
```

验证: `curl http://localhost:8000/api/health` 返回 `{"status":"ok","app":"AI口播工厂"}`

- [ ] **Step 7: Commit**

```bash
git init
git add -A && git commit -m "feat: project scaffolding - FastAPI backend + Vue 3 frontend"
```

---

### Task 2: 数据库模型 + Alembic迁移

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/avatar.py`
- Create: `backend/app/models/template.py`
- Create: `backend/app/models/video_task.py`
- Create: `backend/app/models/plan.py`
- Create: `backend/app/models/subscription.py`
- Create: `backend/app/models/credit_log.py`
- Create: `backend/alembic.ini`

- [ ] **Step 1: 创建 User 模型 `backend/app/models/user.py`**

```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(50))
    credits_balance: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    avatars = relationship("Avatar", back_populates="user")
    video_tasks = relationship("VideoTask", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    credit_logs = relationship("CreditLog", back_populates="user")
```

- [ ] **Step 2: 创建剩余6个模型**

`backend/app/models/avatar.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Avatar(Base):
    __tablename__ = "avatars"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    photo_urls: Mapped[dict | None] = mapped_column(JSONB)
    material_id: Mapped[str | None] = mapped_column(String(100))
    character_id: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="avatars")
    video_tasks = relationship("VideoTask", back_populates="avatar")
```

`backend/app/models/template.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str] = mapped_column(String(50), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    preview_video_url: Mapped[str | None] = mapped_column(String(500))
    config: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    video_tasks = relationship("VideoTask", back_populates="template")
```

`backend/app/models/video_task.py`:
```python
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
    avatar_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("avatars.id"), nullable=False)
    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    script_text: Mapped[str] = mapped_column(Text, nullable=False)
    tts_audio_url: Mapped[str | None] = mapped_column(String(500))
    video_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    cost_credits: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user = relationship("User", back_populates="video_tasks")
    avatar = relationship("Avatar", back_populates="video_tasks")
    template = relationship("Template", back_populates="video_tasks")
```

`backend/app/models/plan.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    monthly_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    credits_per_month: Mapped[int] = mapped_column(Integer, nullable=False)
    features: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subscriptions = relationship("Subscription", back_populates="plan")
```

`backend/app/models/subscription.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")

    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
```

`backend/app/models/credit_log.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class CreditLog(Base):
    __tablename__ = "credit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="credit_logs")
```

`backend/app/models/__init__.py`:
```python
from app.models.user import User
from app.models.avatar import Avatar
from app.models.template import Template
from app.models.video_task import VideoTask
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.credit_log import CreditLog
from app.database import Base

__all__ = ["User", "Avatar", "Template", "VideoTask", "Plan", "Subscription", "CreditLog", "Base"]
```

- [ ] **Step 3: 配置Alembic**

```bash
cd backend && pip install alembic && alembic init alembic
```

编辑 `backend/alembic.ini`，找到 `sqlalchemy.url` 行替换为:
```
sqlalchemy.url = postgresql+psycopg2://postgres:postgres@localhost:5432/koubo_factory
```

编辑 `backend/alembic/env.py`，在 `target_metadata = None` 之前添加:
```python
from app.database import Base
from app.models import User, Avatar, Template, VideoTask, Plan, Subscription, CreditLog
target_metadata = Base.metadata
```

- [ ] **Step 4: 创建数据库 + 跑迁移**

```bash
createdb koubo_factory  # 或 psql -c "CREATE DATABASE koubo_factory;"
cd backend && alembic revision --autogenerate -m "init_all_models"
alembic upgrade head
```

- [ ] **Step 5: 验证**

```bash
cd backend && python -c "from app.database import engine; from app.models import Base; print('Models OK')"
```

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: database models + alembic migration"
```

---

### Task 3: 用户认证系统 (注册 + 登录 + JWT)

**Files:**
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/auth.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`
- Modify: `backend/app/main.py` (注册auth路由)

- [ ] **Step 1: 创建认证Schema `backend/app/schemas/auth.py`**

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class RegisterRequest(BaseModel):
    phone: str = Field(min_length=11, max_length=20, pattern=r"^1[3-9]\d{9}$")
    password: str = Field(min_length=6, max_length=50)
    company_name: str | None = None


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    phone: str
    company_name: str | None
    credits_balance: int
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 创建公共依赖 `backend/app/api/deps.py`**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from app.database import get_db
from app.config import get_settings
from app.models.user import User
from uuid import UUID

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    settings = get_settings()
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await db.get(User, UUID(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
```

- [ ] **Step 3: 创建认证API `backend/app/api/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from uuid import UUID

from app.database import get_db
from app.config import get_settings
from app.models.user import User
from app.models.credit_log import CreditLog
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.SECRET_KEY,
        algorithm="HS256",
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == req.phone))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="手机号已注册")

    user = User(
        phone=req.phone,
        password_hash=pwd_context.hash(req.password),
        company_name=req.company_name,
    )
    db.add(user)
    await db.flush()

    # 新用户赠送100算粒体验
    log = CreditLog(user_id=user.id, amount=100, balance=100, type="charge", source="新用户注册赠送")
    user.credits_balance = 100
    db.add(log)

    await db.commit()
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == req.phone))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="手机号或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

- [ ] **Step 4: 注册路由到 `backend/app/main.py`**

在 `app/main.py` 的 `app = FastAPI(...)` 之后，`return app` 之前添加:
```python
from app.api.auth import router as auth_router
app.include_router(auth_router)
```

- [ ] **Step 5: 编写测试 `backend/tests/conftest.py`**

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.database import Base, get_db
from app.models import User, Avatar, Template, VideoTask, Plan, Subscription, CreditLog

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/koubo_factory_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

- [ ] **Step 6: 编写认证测试 `backend/tests/test_auth.py`**

```python
import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/api/auth/register", json={
        "phone": "13800138000",
        "password": "123456",
        "company_name": "测试公司",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_phone(client):
    await client.post("/api/auth/register", json={"phone": "13800138000", "password": "123456"})
    resp = await client.post("/api/auth/register", json={"phone": "13800138000", "password": "654321"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/auth/register", json={"phone": "13800138001", "password": "123456"})
    resp = await client.post("/api/auth/login", json={"phone": "13800138001", "password": "123456"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={"phone": "13800138002", "password": "123456"})
    resp = await client.post("/api/auth/login", json={"phone": "13800138002", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client):
    resp = await client.post("/api/auth/register", json={"phone": "13800138003", "password": "123456"})
    token = resp.json()["access_token"]
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["phone"] == "13800138003"
    assert resp.json()["credits_balance"] == 100


@pytest.mark.asyncio
async def test_unauthorized(client):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 403
```

- [ ] **Step 7: 运行测试**

```bash
createdb koubo_factory_test
cd backend && pip install -r requirements.txt
pytest tests/test_auth.py -v
```

预期: 6 passed

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "feat: user auth - register/login/JWT with tests"
```

---

### Task 4: 数字人形象模块 (Avatar CRUD + 火山引擎授权)

**Files:**
- Create: `backend/app/schemas/avatar.py`
- Create: `backend/app/api/avatars.py`
- Create: `backend/app/services/seedance_service.py`
- Create: `backend/tests/test_avatars.py`
- Modify: `backend/app/main.py` (注册avatars路由)

- [ ] **Step 1: 创建Avatar Schema `backend/app/schemas/avatar.py`**

```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class AvatarCreateRequest(BaseModel):
    name: str
    photo_urls: dict


class AvatarResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    photo_urls: dict | None
    material_id: str | None
    character_id: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AvatarListResponse(BaseModel):
    items: list[AvatarResponse]
    total: int
```

- [ ] **Step 2: 创建Seedance服务桩 `backend/app/services/seedance_service.py`**

```python
"""
Seedance 2.0 API 封装 (火山引擎)

MVP阶段：提供桩实现，返回模拟数据。
正式环境：对接火山引擎方舟平台API。
"""
import uuid


class SeedanceService:
    """Seedance 2.0 视频生成服务"""

    def __init__(self, access_key: str = "", secret_key: str = ""):
        self.access_key = access_key
        self.secret_key = secret_key

    async def generate_auth_qrcode(self, user_id: str) -> dict:
        """
        生成真人授权二维码。
        MVP阶段返回模拟数据，正式环境调用火山引擎API。
        """
        return {
            "qrcode_url": f"https://volcengine.example.com/auth?uid={user_id}&nonce={uuid.uuid4().hex[:8]}",
            "expire_seconds": 600,
        }

    async def check_authorization(self, user_id: str) -> dict:
        """检查授权状态。MVP返回已授权。"""
        return {
            "authorized": True,
            "material_id": f"MAT-{uuid.uuid4().hex[:12]}",
            "character_id": f"CHAR-{uuid.uuid4().hex[:8]}",
        }

    async def generate_video(
        self,
        material_id: str,
        audio_url: str,
        template_config: dict,
        script_text: str,
    ) -> dict:
        """
        调用Seedance 2.0生成视频。
        MVP阶段返回模拟数据。
        """
        return {
            "task_id": f"SD-{uuid.uuid4().hex[:16]}",
            "status": "processing",
        }

    async def query_video_status(self, task_id: str) -> dict:
        """查询视频生成状态。MVP返回已完成。"""
        return {
            "task_id": task_id,
            "status": "done",
            "video_url": f"https://oss.example.com/videos/{task_id}.mp4",
        }


def get_seedance_service() -> SeedanceService:
    from app.config import get_settings
    s = get_settings()
    return SeedanceService(access_key=s.VOLCENGINE_ACCESS_KEY, secret_key=s.VOLCENGINE_SECRET_KEY)
```

- [ ] **Step 3: 创建Avatar API `backend/app/api/avatars.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.avatar import Avatar
from app.schemas.avatar import AvatarCreateRequest, AvatarResponse, AvatarListResponse
from app.api.deps import get_current_user
from app.services.seedance_service import get_seedance_service

router = APIRouter(prefix="/api/avatars", tags=["avatars"])


@router.post("", response_model=AvatarResponse, status_code=status.HTTP_201_CREATED)
async def create_avatar(
    req: AvatarCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar = Avatar(
        user_id=current_user.id,
        name=req.name,
        photo_urls=req.photo_urls,
    )
    db.add(avatar)
    await db.flush()

    seedance = get_seedance_service()
    auth_info = await seedance.generate_auth_qrcode(str(current_user.id))
    # MVP: 直接标记为已授权；正式环境需用户扫码后回调更新
    check = await seedance.check_authorization(str(current_user.id))
    avatar.material_id = check.get("material_id")
    avatar.character_id = check.get("character_id")
    avatar.status = "active"

    await db.commit()
    return avatar


@router.get("", response_model=AvatarListResponse)
async def list_avatars(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Avatar).where(Avatar.user_id == current_user.id))
    items = result.scalars().all()
    return AvatarListResponse(items=list(items), total=len(items))


@router.get("/{avatar_id}", response_model=AvatarResponse)
async def get_avatar(
    avatar_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar = await db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="形象不存在")
    return avatar


@router.delete("/{avatar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(
    avatar_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar = await db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="形象不存在")
    await db.delete(avatar)
```

- [ ] **Step 4: 注册路由到 `main.py`**

```python
from app.api.avatars import router as avatars_router
app.include_router(avatars_router)
```

- [ ] **Step 5: 编写测试 `backend/tests/test_avatars.py`**

```python
import pytest


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def register_and_login(client) -> str:
    resp = await client.post("/api/auth/register", json={"phone": "13900000001", "password": "123456"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_avatar(client):
    token = await register_and_login(client)
    resp = await client.post("/api/avatars", json={
        "name": "我的数字人",
        "photo_urls": {"front": "https://example.com/face1.jpg", "side": "https://example.com/face2.jpg"},
    }, headers=auth_header(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "我的数字人"
    assert data["status"] == "active"
    assert data["character_id"] is not None


@pytest.mark.asyncio
async def test_list_avatars(client):
    token = await register_and_login(client)
    await client.post("/api/avatars", json={"name": "形象1", "photo_urls": {}}, headers=auth_header(token))
    await client.post("/api/avatars", json={"name": "形象2", "photo_urls": {}}, headers=auth_header(token))
    resp = await client.get("/api/avatars", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_delete_avatar(client):
    token = await register_and_login(client)
    resp = await client.post("/api/avatars", json={"name": "待删除", "photo_urls": {}}, headers=auth_header(token))
    avatar_id = resp.json()["id"]
    resp = await client.delete(f"/api/avatars/{avatar_id}", headers=auth_header(token))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_cannot_access_other_user_avatar(client):
    token1 = await register_and_login(client)
    resp = await client.post("/api/avatars", json={"name": "我的", "photo_urls": {}}, headers=auth_header(token1))
    avatar_id = resp.json()["id"]

    resp2 = await client.post("/api/auth/register", json={"phone": "13900000002", "password": "123456"})
    token2 = resp2.json()["access_token"]

    resp3 = await client.get(f"/api/avatars/{avatar_id}", headers=auth_header(token2))
    assert resp3.status_code == 404
```

- [ ] **Step 6: 运行测试**

```bash
cd backend && pytest tests/test_avatars.py -v
```

预期: 4 passed

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: avatar CRUD + seedance service stub"
```

---

### Task 5: 行业模板模块 (Template读取 + 种子数据)

**Files:**
- Create: `backend/app/schemas/template.py`
- Create: `backend/app/api/templates.py`
- Modify: `backend/app/main.py` (注册templates路由)

- [ ] **Step 1: 创建Template Schema `backend/app/schemas/template.py`**

```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    industry: str
    thumbnail_url: str | None
    preview_video_url: str | None
    config: dict | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    items: list[TemplateResponse]
    total: int
```

- [ ] **Step 2: 创建Template API `backend/app/api/templates.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models.template import Template
from app.schemas.template import TemplateResponse, TemplateListResponse

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    industry: str | None = Query(None, description="按行业筛选"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Template).where(Template.status == "active")
    if industry:
        stmt = stmt.where(Template.industry == industry)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return TemplateListResponse(items=list(items), total=len(items))


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    template = await db.get(Template, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")
    return template
```

- [ ] **Step 3: 创建种子数据脚本 `backend/seed_templates.py`**

```python
"""运行一次：python seed_templates.py 插入美容行业模板"""
import asyncio
from app.database import async_session
from app.models.template import Template

TEMPLATES = [
    {
        "name": "美容推荐-产品介绍",
        "industry": "美容美发",
        "config": {
            "scene": "indoor_bright",
            "camera": "medium_shot",
            "duration_range": [15, 30],
            "style": "professional_beauty",
            "resolution": "1080p",
            "aspect_ratio": "9:16",
        },
    },
    {
        "name": "美容教程-护肤步骤",
        "industry": "美容美发",
        "config": {
            "scene": "studio_setup",
            "camera": "close_up",
            "duration_range": [30, 60],
            "style": "tutorial",
            "resolution": "1080p",
            "aspect_ratio": "9:16",
        },
    },
    {
        "name": "美容活动-促销推广",
        "industry": "美容美发",
        "config": {
            "scene": "shop_environment",
            "camera": "medium_shot",
            "duration_range": [15, 30],
            "style": "promotional",
            "resolution": "1080p",
            "aspect_ratio": "9:16",
        },
    },
]


async def seed():
    async with async_session() as db:
        for t in TEMPLATES:
            template = Template(**t)
            db.add(template)
        await db.commit()
        print(f"Seeded {len(TEMPLATES)} templates.")


if __name__ == "__main__":
    asyncio.run(seed())
```

- [ ] **Step 4: 注册路由 + 跑种子数据**

```python
# 在 main.py 添加:
from app.api.templates import router as templates_router
app.include_router(templates_router)
```

```bash
cd backend && python seed_templates.py
```

- [ ] **Step 5: 验证**

```bash
curl http://localhost:8000/api/templates?industry=美容美发
```

预期: 返回3个美容模板。

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: template module with beauty industry seed data"
```

---

### Task 6: TTS服务集成 (腾讯云MAIS)

**Files:**
- Create: `backend/app/services/tts_service.py`
- Create: `backend/tests/test_tts.py`

- [ ] **Step 1: 创建TTS服务 `backend/app/services/tts_service.py`**

```python
"""
腾讯云媒体AI (MAIS) TTS服务封装

发音人克隆:
1. 上传参考音频 → 获得音色ID（一次性，25元/音色）
2. 调用配音接口 → 传入音色ID + 文本 → 获得音频URL

API参考: https://cloud.tencent.com/document/product/...
"""
import httpx
import hashlib
import hmac
import time
from datetime import datetime


class TencentMAIService:
    """腾讯云媒体AI TTS服务"""

    def __init__(self, secret_id: str = "", secret_key: str = "", region: str = "ap-guangzhou"):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.base_url = "https://mais.tencentcloudapi.com"

    async def create_voice_clone(self, audio_url: str, voice_name: str) -> dict:
        """
        克隆音色：上传参考音频 → 返回音色ID。
        MVP阶段返回模拟数据。
        """
        # 正式环境: POST / CreateVoiceClone
        return {
            "voice_id": f"VOICE-{hashlib.md5(voice_name.encode()).hexdigest()[:12]}",
            "voice_name": voice_name,
        }

    async def synthesize(self, text: str, voice_id: str, speed: float = 1.0) -> dict:
        """
        文本转语音：传入文本 + 音色ID → 返回音频URL。
        MVP阶段返回模拟数据。
        """
        # 正式环境: POST / SynthesizeSpeech
        return {
            "audio_url": f"https://oss.example.com/tts/{hashlib.md5(text.encode()).hexdigest()[:8]}.mp3",
            "duration_seconds": len(text) * 0.3,
            "voice_id": voice_id,
        }

    async def create_voice_and_synthesize(self, text: str, voice_name: str, audio_url: str) -> dict:
        """便捷方法：先建音色再合成（首次创建数字人时使用）"""
        voice = await self.create_voice_clone(audio_url, voice_name)
        result = await self.synthesize(text, voice["voice_id"])
        return {**result, "voice_id": voice["voice_id"]}


def get_tts_service() -> TencentMAIService:
    from app.config import get_settings
    s = get_settings()
    return TencentMAIService(
        secret_id=s.TENCENT_SECRET_ID,
        secret_key=s.TENCENT_SECRET_KEY,
        region=s.TENCENT_MAIS_REGION,
    )
```

- [ ] **Step 2: 编写TTS单元测试 `backend/tests/test_tts.py`**

```python
from app.services.tts_service import TencentMAIService


def test_tts_service_creates_voice():
    svc = TencentMAIService()
    result = await svc.create_voice_clone(
        audio_url="https://example.com/reference.mp3",
        voice_name="test_voice",
    )
    assert "voice_id" in result
    assert result["voice_name"] == "test_voice"


def test_tts_service_synthesizes():
    svc = TencentMAIService()
    result = await svc.synthesize(
        text="大家好，欢迎来到我的直播间",
        voice_id="VOICE-test123",
    )
    assert "audio_url" in result
    assert result["duration_seconds"] > 0
```

- [ ] **Step 3: 运行测试**

```bash
cd backend && pytest tests/test_tts.py -v
```

预期: 2 passed

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: TTS service - Tencent MAIS integration stub"
```

---

### Task 7: 视频生成核心 (Celery异步任务 + API编排)

**Files:**
- Create: `backend/app/tasks/celery_app.py`
- Create: `backend/app/tasks/video_tasks.py`
- Create: `backend/app/services/credit_service.py`
- Create: `backend/app/services/storage_service.py`
- Create: `backend/app/schemas/video.py`
- Create: `backend/app/api/videos.py`
- Modify: `backend/app/main.py` (注册videos路由)

- [ ] **Step 1: 创建Celery配置 `backend/app/tasks/celery_app.py`**

```python
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "koubo_factory",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
```

- [ ] **Step 2: 创建算粒服务 `backend/app/services/credit_service.py`**

```python
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.credit_log import CreditLog


async def deduct_credits(db: AsyncSession, user_id: UUID, amount: int, source: str) -> bool:
    """扣减算粒，余额不足返回False"""
    user = await db.get(User, user_id)
    if user.credits_balance < amount:
        return False

    user.credits_balance -= amount
    log = CreditLog(
        user_id=user_id,
        amount=-amount,
        balance=user.credits_balance,
        type="consume",
        source=source,
    )
    db.add(log)
    return True


async def refund_credits(db: AsyncSession, user_id: UUID, amount: int, source: str):
    """退还算粒"""
    user = await db.get(User, user_id)
    user.credits_balance += amount
    log = CreditLog(
        user_id=user_id,
        amount=amount,
        balance=user.credits_balance,
        type="refund",
        source=source,
    )
    db.add(log)
```

- [ ] **Step 3: 创建存储服务 `backend/app/services/storage_service.py`**

```python
"""存储服务：MVP阶段返回模拟URL"""
import uuid


class StorageService:
    def __init__(self, endpoint: str = "", bucket: str = "", access_key: str = "", secret_key: str = ""):
        self.endpoint = endpoint
        self.bucket = bucket

    async def upload_file(self, file_path: str, content: bytes, content_type: str) -> str:
        """上传文件到OSS/COS，返回访问URL"""
        ext = file_path.split(".")[-1]
        key = f"videos/{uuid.uuid4().hex}.{ext}"
        return f"https://{self.bucket}.{self.endpoint}/{key}"


def get_storage_service() -> StorageService:
    from app.config import get_settings
    s = get_settings()
    return StorageService(endpoint=s.OSS_ENDPOINT, bucket=s.OSS_BUCKET,
                          access_key=s.OSS_ACCESS_KEY, secret_key=s.OSS_SECRET_KEY)
```

- [ ] **Step 4: 创建视频生成异步任务 `backend/app/tasks/video_tasks.py`**

```python
import asyncio
from uuid import UUID
from celery import shared_task
from sqlalchemy import select
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
    """视频生成异步任务：TTS → Seedance → 存储"""
    return asyncio.run(_generate_video(task_id, self.request.id))


async def _generate_video(task_id: str, celery_task_id: str):
    async with AsyncSessionLocal() as db:
        task = await db.get(VideoTask, UUID(task_id))
        if not task:
            return {"error": "Task not found"}

        try:
            # Step 1: 更新状态 → processing
            task.status = "processing"

            # Step 2: TTS合成语音
            tts = get_tts_service()
            tts_result = await tts.synthesize(
                text=task.script_text,
                voice_id=f"VOICE-{task.avatar_id}",  # 正式环境使用avatar绑定的voice_id
            )
            task.tts_audio_url = tts_result["audio_url"]
            task.status = "tts_done"

            # Step 3: Seedance视频生成
            seedance = get_seedance_service()
            video_result = await seedance.generate_video(
                material_id="",     # 从avatar获取
                audio_url=task.tts_audio_url,
                template_config={},  # 从template获取
                script_text=task.script_text,
            )

            # Step 4: 轮询Seedance状态（MVP直接模拟完成）
            status = await seedance.query_video_status(video_result["task_id"])

            # Step 5: 上传到OSS
            storage = get_storage_service()
            video_url = status["video_url"]

            task.video_url = video_url
            task.status = "done"
            task.completed_at = __import__("datetime").datetime.utcnow()

            await db.commit()
            return {"status": "done", "video_url": video_url}

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            await db.commit()

            # 退款
            if task.cost_credits > 0:
                await refund_credits(db, task.user_id, task.cost_credits,
                                     f"视频生成失败退款: {task_id}")

            raise
```

- [ ] **Step 5: 创建Video Schema `backend/app/schemas/video.py`**

```python
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
```

- [ ] **Step 6: 创建Videos API `backend/app/api/videos.py`**

```python
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

VIDEO_CREDIT_COST = 10  # 每条视频消耗10算粒


@router.post("", response_model=VideoTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    req: VideoCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 校验avatar归属
    avatar = await db.get(Avatar, req.avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="形象不存在")
    if avatar.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="形象未就绪")

    # 校验template存在
    template = await db.get(Template, req.template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="模板不存在")

    # 扣减算粒
    ok = await deduct_credits(db, current_user.id, VIDEO_CREDIT_COST, f"视频生成: {req.script_text[:20]}...")
    if not ok:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="算粒不足，请充值")

    # 创建任务
    task = VideoTask(
        user_id=current_user.id,
        avatar_id=req.avatar_id,
        template_id=req.template_id,
        script_text=req.script_text,
        cost_credits=VIDEO_CREDIT_COST,
    )
    db.add(task)
    await db.commit()

    # 投递Celery异步任务
    generate_video_task.delay(str(task.id))

    return task


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
```

- [ ] **Step 7: 注册路由到 `main.py`**

```python
from app.api.videos import router as videos_router
app.include_router(videos_router)
```

- [ ] **Step 8: 编写测试 `backend/tests/test_videos.py`**

```python
import pytest

VIDEO_CREDIT_COST = 10


async def register_and_login(client) -> str:
    resp = await client.post("/api/auth/register", json={"phone": "13800138000", "password": "123456"})
    return resp.json()["access_token"]


async def create_avatar(client, token: str) -> str:
    resp = await client.post("/api/avatars", json={"name": "测试形象", "photo_urls": {}},
                             headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


async def get_template_id(client) -> str:
    resp = await client.get("/api/templates")
    items = resp.json()["items"]
    return items[0]["id"] if items else None


@pytest.mark.asyncio
async def test_create_video_insufficient_credits(client):
    token = await register_and_login(client)
    avatar_id = await create_avatar(client, token)
    template_id = await get_template_id(client)

    # 100 credits, cost is 10 per video. Make 11 requests to drain.
    for i in range(10):
        resp = await client.post("/api/videos", json={
            "avatar_id": avatar_id,
            "template_id": template_id,
            "script_text": f"测试文案{i}",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201, f"Request {i} failed: {resp.text}"

    # 第11次应该失败（余额不足）
    resp = await client.post("/api/videos", json={
        "avatar_id": avatar_id,
        "template_id": template_id,
        "script_text": "超出预算的文案",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 402


@pytest.mark.asyncio
async def test_create_video_success(client):
    token = await register_and_login(client)
    avatar_id = await create_avatar(client, token)
    template_id = await get_template_id(client)

    resp = await client.post("/api/videos", json={
        "avatar_id": avatar_id,
        "template_id": template_id,
        "script_text": "大家好，今天给大家推荐一款超好用的护肤品",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] in ("queued", "processing")
    assert data["cost_credits"] == VIDEO_CREDIT_COST


@pytest.mark.asyncio
async def test_list_videos(client):
    token = await register_and_login(client)
    avatar_id = await create_avatar(client, token)
    template_id = await get_template_id(client)
    await client.post("/api/videos", json={
        "avatar_id": avatar_id,
        "template_id": template_id,
        "script_text": "视频1",
    }, headers={"Authorization": f"Bearer {token}"})

    resp = await client.get("/api/videos", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1
```

- [ ] **Step 9: 运行测试**

```bash
cd backend && pytest tests/test_videos.py -v
```

预期: 3 passed

- [ ] **Step 10: Commit**

```bash
git add -A && git commit -m "feat: video generation - celery async pipeline + credits deduction"
```

---

### Task 8: 会员套餐 + 算粒查询

**Files:**
- Create: `backend/app/schemas/plan.py`
- Create: `backend/app/schemas/credit.py`
- Create: `backend/app/api/plans.py`
- Create: `backend/app/api/credits.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_credits.py`

- [ ] **Step 1: 创建Schema `backend/app/schemas/plan.py`**

```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class PlanResponse(BaseModel):
    id: UUID
    name: str
    monthly_price: float
    credits_per_month: int
    features: dict | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PlanListResponse(BaseModel):
    items: list[PlanResponse]
    total: int
```

`backend/app/schemas/credit.py`:
```python
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class CreditLogResponse(BaseModel):
    id: UUID
    amount: int
    balance: int
    type: str
    source: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class CreditBalanceResponse(BaseModel):
    balance: int


class CreditLogListResponse(BaseModel):
    items: list[CreditLogResponse]
    total: int
```

- [ ] **Step 2: 创建Plans API `backend/app/api/plans.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.plan import Plan
from app.schemas.plan import PlanResponse, PlanListResponse

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("", response_model=PlanListResponse)
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan).where(Plan.status == "active"))
    items = result.scalars().all()
    return PlanListResponse(items=list(items), total=len(items))
```

- [ ] **Step 3: 创建Credits API `backend/app/api/credits.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import func as sqlfunc

from app.database import get_db
from app.models.user import User
from app.models.credit_log import CreditLog
from app.schemas.credit import CreditBalanceResponse, CreditLogResponse, CreditLogListResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/credits", tags=["credits"])


@router.get("/balance", response_model=CreditBalanceResponse)
async def get_balance(current_user: User = Depends(get_current_user)):
    return CreditBalanceResponse(balance=current_user.credits_balance)


@router.get("/log", response_model=CreditLogListResponse)
async def get_credit_log(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CreditLog)
        .where(CreditLog.user_id == current_user.id)
        .order_by(CreditLog.created_at.desc())
        .limit(50)
    )
    items = result.scalars().all()
    return CreditLogListResponse(items=list(items), total=len(items))
```

- [ ] **Step 4: 注册路由 + 创建套餐种子数据**

在 `main.py`:
```python
from app.api.plans import router as plans_router
from app.api.credits import router as credits_router
app.include_router(plans_router)
app.include_router(credits_router)
```

更新 `backend/seed_templates.py` 末尾添加套餐种子:

```python
async def seed_plans():
    from app.models.plan import Plan
    plans = [
        Plan(name="基础版", monthly_price=99.00, credits_per_month=300,
             features={"avatars": 1, "video_length": 30, "resolution": "720p"}),
        Plan(name="专业版", monthly_price=299.00, credits_per_month=1000,
             features={"avatars": 3, "video_length": 60, "resolution": "1080p"}),
        Plan(name="企业版", monthly_price=999.00, credits_per_month=5000,
             features={"avatars": 10, "video_length": 120, "resolution": "1080p", "priority_support": True}),
    ]
    async with async_session() as db:
        for p in plans:
            db.add(p)
        await db.commit()
    print(f"Seeded {len(plans)} plans.")
```

- [ ] **Step 5: 编写测试 `backend/tests/test_credits.py`**

```python
import pytest


async def register_and_login(client) -> str:
    resp = await client.post("/api/auth/register", json={"phone": "13800138004", "password": "123456"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_get_balance(client):
    token = await register_and_login(client)
    resp = await client.get("/api/credits/balance", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["balance"] == 100  # 注册赠送


@pytest.mark.asyncio
async def test_get_credit_log(client):
    token = await register_and_login(client)
    resp = await client.get("/api/credits/log", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1  # 至少有一条注册赠送记录


@pytest.mark.asyncio
async def test_list_plans(client):
    resp = await client.get("/api/plans")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 3
```

- [ ] **Step 6: 运行测试**

```bash
cd backend && python seed_templates.py  # 确保套餐数据已插入
pytest tests/test_credits.py -v
```

预期: 3 passed

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat: plans + credits API with seed data"
```

---

### Task 9: Vue前端 — 路由 + 布局 + Axios客户端

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/stores/user.ts`
- Create: `frontend/src/components/AppLayout.vue`
- Create: `frontend/src/components/CreditBadge.vue`
- Modify: `frontend/src/main.ts`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: 配置main.ts `frontend/src/main.ts`**

```typescript
import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import App from "./App.vue";
import router from "./router";
import "./styles/global.css";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(ElementPlus);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}
app.mount("#app");
```

- [ ] **Step 2: 创建axios客户端 `frontend/src/api/client.ts`**

```typescript
import axios from "axios";
import { ElMessage } from "element-plus";

const client = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 30000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg =
      error.response?.data?.detail || error.message || "请求失败";
    if (error.response?.status === 402) {
      ElMessage.error("算粒不足，请充值后再试");
    } else if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    } else {
      ElMessage.error(msg);
    }
    return Promise.reject(error);
  }
);

export default client;
```

- [ ] **Step 3: 创建用户Store `frontend/src/stores/user.ts`**

```typescript
import { defineStore } from "pinia";
import { ref } from "vue";
import client from "../api/client";

export const useUserStore = defineStore("user", () => {
  const user = ref<any>(null);
  const balance = ref(0);
  const isLoggedIn = ref(false);

  async function fetchMe() {
    try {
      const resp = await client.get("/api/auth/me");
      user.value = resp.data;
      balance.value = resp.data.credits_balance;
      isLoggedIn.value = true;
    } catch {
      isLoggedIn.value = false;
    }
  }

  async function fetchBalance() {
    const resp = await client.get("/api/credits/balance");
    balance.value = resp.data.balance;
  }

  function logout() {
    localStorage.removeItem("token");
    user.value = null;
    isLoggedIn.value = false;
  }

  return { user, balance, isLoggedIn, fetchMe, fetchBalance, logout };
});
```

- [ ] **Step 4: 创建路由 `frontend/src/router/index.ts`**

```typescript
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "Login",
      component: () => import("../views/Login.vue"),
      meta: { guest: true },
    },
    {
      path: "/register",
      name: "Register",
      component: () => import("../views/Register.vue"),
      meta: { guest: true },
    },
    {
      path: "/",
      name: "Dashboard",
      component: () => import("../views/Dashboard.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/avatars",
      name: "AvatarList",
      component: () => import("../views/AvatarList.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/avatars/create",
      name: "AvatarCreate",
      component: () => import("../views/AvatarCreate.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/videos/create",
      name: "VideoCreate",
      component: () => import("../views/VideoCreate.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/videos",
      name: "VideoList",
      component: () => import("../views/VideoList.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/videos/:id",
      name: "VideoDetail",
      component: () => import("../views/VideoDetail.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/plans",
      name: "PlanList",
      component: () => import("../views/PlanList.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/credits",
      name: "CreditLog",
      component: () => import("../views/CreditLog.vue"),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else if (to.meta.guest && token) {
    next("/");
  } else {
    next();
  }
});

export default router;
```

- [ ] **Step 5: 创建布局组件 `frontend/src/components/AppLayout.vue`**

```vue
<template>
  <el-container class="app-layout">
    <el-header class="app-header">
      <div class="header-left">
        <h2 @click="$router.push('/')" style="cursor: pointer">AI口播工厂</h2>
      </div>
      <div class="header-right">
        <CreditBadge />
        <el-dropdown trigger="click">
          <el-button type="text" style="color: #333">
            {{ userStore.user?.phone }} <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/credits')">算粒明细</el-dropdown-item>
              <el-dropdown-item @click="$router.push('/plans')">升级套餐</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="app-aside">
        <el-menu router :default-active="$route.path" background-color="#fafafa">
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>工作台</span>
          </el-menu-item>
          <el-menu-item index="/avatars">
            <el-icon><UserFilled /></el-icon>
            <span>我的形象</span>
          </el-menu-item>
          <el-menu-item index="/videos">
            <el-icon><VideoCamera /></el-icon>
            <span>视频管理</span>
          </el-menu-item>
          <el-menu-item index="/plans">
            <el-icon><Goods /></el-icon>
            <span>套餐中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="app-main">
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import CreditBadge from "./CreditBadge.vue";

const router = useRouter();
const userStore = useUserStore();

onMounted(() => userStore.fetchMe());

function handleLogout() {
  userStore.logout();
  router.push("/login");
}
</script>

<style scoped>
.app-layout { height: 100vh; }
.app-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e5e5e5; }
.header-right { display: flex; align-items: center; gap: 16px; }
.app-aside { border-right: 1px solid #e5e5e5; padding-top: 16px; }
.app-main { background: #f5f5f5; padding: 24px; }
</style>
```

- [ ] **Step 6: 创建算粒徽章 `frontend/src/components/CreditBadge.vue`**

```vue
<template>
  <el-tag type="warning" @click="$router.push('/credits')" style="cursor: pointer">
    算粒: {{ userStore.balance }}
  </el-tag>
</template>

<script setup lang="ts">
import { useUserStore } from "../stores/user";
const userStore = useUserStore();
</script>
```

- [ ] **Step 7: 创建 `frontend/src/styles/global.css`**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Microsoft YaHei", sans-serif; }
```

- [ ] **Step 8: 更新App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 9: 验证前端启动**

```bash
cd frontend && npm run dev
```

浏览器打开 `http://localhost:5173`，应看到空页面（路由需要视图组件）。

- [ ] **Step 10: Commit**

```bash
git add -A && git commit -m "feat: frontend scaffold - router, axios, pinia, layout"
```

---

### Task 10: Vue前端 — 登录注册 + 工作台

**Files:**
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/Register.vue`
- Create: `frontend/src/views/Dashboard.vue`

- [ ] **Step 1: Auth API `frontend/src/api/auth.ts`**

```typescript
import client from "./client";

export function login(phone: string, password: string) {
  return client.post("/api/auth/login", { phone, password });
}

export function register(phone: string, password: string, company_name?: string) {
  return client.post("/api/auth/register", { phone, password, company_name });
}
```

- [ ] **Step 2: 登录页 `frontend/src/views/Login.vue`**

```vue
<template>
  <div class="auth-container">
    <el-card class="auth-card" shadow="always">
      <h1 style="text-align: center; margin-bottom: 24px">AI口播工厂</h1>
      <el-form :model="form" label-position="top">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" block @click="handleLogin">登录</el-button>
      </el-form>
      <p style="text-align: center; margin-top: 16px">
        还没有账号？<el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
      </p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { login } from "../api/auth";
import { useUserStore } from "../stores/user";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const form = ref({ phone: "", password: "" });

async function handleLogin() {
  loading.value = true;
  try {
    const resp = await login(form.value.phone, form.value.password);
    localStorage.setItem("token", resp.data.access_token);
    await userStore.fetchMe();
    ElMessage.success("登录成功");
    router.push("/");
  } catch {
    // interceptor handles error message
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
.auth-card { width: 400px; }
</style>
```

- [ ] **Step 3: 注册页 `frontend/src/views/Register.vue`**

```vue
<template>
  <div class="auth-container">
    <el-card class="auth-card" shadow="always">
      <h1 style="text-align: center; margin-bottom: 24px">注册账号</h1>
      <el-form :model="form" label-position="top">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="公司名称（选填）">
          <el-input v-model="form.company_name" placeholder="您的公司或店铺名称" />
        </el-form-item>
        <el-button type="primary" :loading="loading" block @click="handleRegister">注册</el-button>
      </el-form>
      <p style="text-align: center; margin-top: 16px">
        已有账号？<el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
      </p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { register } from "../api/auth";
import { useUserStore } from "../stores/user";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const form = ref({ phone: "", password: "", company_name: "" });

async function handleRegister() {
  loading.value = true;
  try {
    const resp = await register(form.value.phone, form.value.password, form.value.company_name || undefined);
    localStorage.setItem("token", resp.data.access_token);
    await userStore.fetchMe();
    ElMessage.success("注册成功，已赠送100算粒");
    router.push("/");
  } catch {
    // interceptor handles error message
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
.auth-card { width: 400px; }
</style>
```

- [ ] **Step 4: 工作台 `frontend/src/views/Dashboard.vue`**

```vue
<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">工作台</h2>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="hover" @click="$router.push('/avatars/create')" class="quick-card">
          <el-icon :size="48" color="#409EFF"><UserFilled /></el-icon>
          <h3>创建数字人</h3>
          <p>上传照片，打造您的专属AI形象</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" @click="$router.push('/videos/create')" class="quick-card">
          <el-icon :size="48" color="#67C23A"><VideoCamera /></el-icon>
          <h3>生成视频</h3>
          <p>选模板、写文案、一键生成口播视频</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" @click="$router.push('/plans')" class="quick-card">
          <el-icon :size="48" color="#E6A23C"><Goods /></el-icon>
          <h3>升级套餐</h3>
          <p>更多算粒、更多形象、更多模板</p>
        </el-card>
      </el-col>
    </el-row>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from "../components/AppLayout.vue";
</script>

<style scoped>
.quick-card { text-align: center; cursor: pointer; padding: 24px; transition: transform 0.2s; }
.quick-card:hover { transform: translateY(-4px); }
.quick-card h3 { margin: 12px 0 8px; }
.quick-card p { color: #999; font-size: 13px; }
</style>
```

- [ ] **Step 5: 验证**

```bash
cd frontend && npm run dev
```

浏览器: `http://localhost:5173/login` → 注册 → 登录 → 看到工作台。

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: login, register, dashboard views"
```

---

### Task 11: Vue前端 — 数字人形象管理

**Files:**
- Create: `frontend/src/api/avatars.ts`
- Create: `frontend/src/views/AvatarCreate.vue`
- Create: `frontend/src/views/AvatarList.vue`

- [ ] **Step 1: Avatars API `frontend/src/api/avatars.ts`**

```typescript
import client from "./client";

export function createAvatar(name: string, photoUrls: Record<string, string>) {
  return client.post("/api/avatars", { name, photo_urls: photoUrls });
}

export function getAvatars() {
  return client.get("/api/avatars");
}

export function deleteAvatar(id: string) {
  return client.delete(`/api/avatars/${id}`);
}
```

- [ ] **Step 2: 创建形象页 `frontend/src/views/AvatarCreate.vue`**

```vue
<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">创建数字人形象</h2>
    <el-card style="max-width: 600px">
      <el-form :model="form" label-position="top">
        <el-form-item label="形象名称">
          <el-input v-model="form.name" placeholder="例如：我的AI主播" />
        </el-form-item>
        <el-form-item label="正面照片URL">
          <el-input v-model="form.front_url" placeholder="输入图片URL" />
        </el-form-item>
        <el-form-item label="侧面照片URL（可选）">
          <el-input v-model="form.side_url" placeholder="输入图片URL" />
        </el-form-item>
        <el-alert
          title="创建形象后，系统将生成授权二维码，需要真人扫码授权后方可使用。MVP版本自动完成授权。"
          type="info"
          :closable="false"
          style="margin-bottom: 16px"
        />
        <el-button type="primary" :loading="loading" @click="handleCreate">创建形象</el-button>
      </el-form>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { createAvatar } from "../api/avatars";
import AppLayout from "../components/AppLayout.vue";

const router = useRouter();
const loading = ref(false);
const form = ref({ name: "", front_url: "", side_url: "" });

async function handleCreate() {
  if (!form.value.name) {
    ElMessage.warning("请输入形象名称");
    return;
  }
  loading.value = true;
  try {
    const photoUrls: Record<string, string> = { front: form.value.front_url };
    if (form.value.side_url) photoUrls.side = form.value.side_url;
    await createAvatar(form.value.name, photoUrls);
    ElMessage.success("数字人形象创建成功");
    router.push("/avatars");
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false;
  }
}
</script>
```

- [ ] **Step 3: 形象列表页 `frontend/src/views/AvatarList.vue`**

```vue
<template>
  <AppLayout>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2>我的形象</h2>
      <el-button type="primary" @click="$router.push('/avatars/create')">创建形象</el-button>
    </div>
    <el-table :data="avatars" v-loading="loading" empty-text="还没有数字人形象，点击右上角创建">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'warning'">
            {{ row.status === 'active' ? '已就绪' : row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleDateString() }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getAvatars, deleteAvatar } from "../api/avatars";
import AppLayout from "../components/AppLayout.vue";

const avatars = ref<any[]>([]);
const loading = ref(false);

async function fetchAvatars() {
  loading.value = true;
  try {
    const resp = await getAvatars();
    avatars.value = resp.data.items;
  } finally {
    loading.value = false;
  }
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm("确定删除该形象吗？", "确认", { type: "warning" });
    await deleteAvatar(id);
    ElMessage.success("已删除");
    fetchAvatars();
  } catch {
    // cancelled
  }
}

onMounted(fetchAvatars);
</script>
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: avatar create + list views"
```

---

### Task 12: Vue前端 — 视频生成 + 视频管理

**Files:**
- Create: `frontend/src/api/videos.ts`
- Create: `frontend/src/api/templates.ts`
- Create: `frontend/src/views/VideoCreate.vue`
- Create: `frontend/src/views/VideoList.vue`
- Create: `frontend/src/views/VideoDetail.vue`

- [ ] **Step 1: APIs `frontend/src/api/videos.ts` + `frontend/src/api/templates.ts`**

```typescript
// frontend/src/api/videos.ts
import client from "./client";

export function createVideo(avatarId: string, templateId: string, scriptText: string) {
  return client.post("/api/videos", { avatar_id: avatarId, template_id: templateId, script_text: scriptText });
}

export function getVideos() {
  return client.get("/api/videos");
}

export function getVideo(id: string) {
  return client.get(`/api/videos/${id}`);
}

export function deleteVideo(id: string) {
  return client.delete(`/api/videos/${id}`);
}
```

```typescript
// frontend/src/api/templates.ts
import client from "./client";

export function getTemplates(industry?: string) {
  return client.get("/api/templates", { params: { industry } });
}
```

- [ ] **Step 2: 视频生成页 `frontend/src/views/VideoCreate.vue`**

```vue
<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">生成口播视频</h2>
    <el-card style="max-width: 700px">
      <el-form :model="form" label-position="top">
        <el-form-item label="选择数字人形象">
          <el-select v-model="form.avatar_id" placeholder="请选择" style="width: 100%">
            <el-option v-for="a in avatars" :key="a.id" :label="a.name" :value="a.id"
              :disabled="a.status !== 'active'" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择模板">
          <el-select v-model="form.template_id" placeholder="请选择" style="width: 100%" @change="onTemplateChange">
            <el-option v-for="t in templates" :key="t.id" :label="`${t.name} (${t.industry})`" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="口播文案">
          <el-input v-model="form.script_text" type="textarea" :rows="6" placeholder="输入您的口播文案...&#10;&#10;例如：大家好，我是XX美容的专属顾问，今天给大家推荐一款..." />
        </el-form-item>
        <el-alert title="每条视频消耗 10 算粒" type="warning" :closable="false" style="margin-bottom: 16px" />
        <el-button type="primary" :loading="loading" size="large" @click="handleCreate">
          生成视频 (消耗10算粒)
        </el-button>
      </el-form>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getAvatars } from "../api/avatars";
import { getTemplates } from "../api/templates";
import { createVideo } from "../api/videos";
import { useUserStore } from "../stores/user";
import AppLayout from "../components/AppLayout.vue";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const avatars = ref<any[]>([]);
const templates = ref<any[]>([]);
const form = ref({ avatar_id: "", template_id: "", script_text: "" });

onMounted(async () => {
  const [aRes, tRes] = await Promise.all([getAvatars(), getTemplates()]);
  avatars.value = aRes.data.items;
  templates.value = tRes.data.items;
});

function onTemplateChange() {
  // could pre-fill script based on template
}

async function handleCreate() {
  if (!form.value.avatar_id || !form.value.template_id || !form.value.script_text) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  loading.value = true;
  try {
    const resp = await createVideo(form.value.avatar_id, form.value.template_id, form.value.script_text);
    await userStore.fetchBalance();
    ElMessage.success("视频生成任务已提交");
    router.push(`/videos/${resp.data.id}`);
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false;
  }
}
</script>
```

- [ ] **Step 3: 视频列表页 `frontend/src/views/VideoList.vue`**

```vue
<template>
  <AppLayout>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2>视频管理</h2>
      <el-button type="primary" @click="$router.push('/videos/create')">
        <el-icon><Plus /></el-icon> 生成视频
      </el-button>
    </div>
    <el-table :data="videos" v-loading="loading" empty-text="还没有生成视频">
      <el-table-column prop="script_text" label="文案" :show-overflow-tooltip="true">
        <template #default="{ row }">{{ row.script_text.slice(0, 50) }}{{ row.script_text.length > 50 ? '...' : '' }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="cost_credits" label="消耗算粒" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="$router.push(`/videos/${row.id}`)">详情</el-button>
          <el-button v-if="row.status === 'done'" size="small" text type="success" @click="download(row)">下载</el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getVideos, deleteVideo } from "../api/videos";
import AppLayout from "../components/AppLayout.vue";

const videos = ref<any[]>([]);
const loading = ref(false);

function statusType(status: string) {
  const map: Record<string, string> = { done: "success", failed: "danger", processing: "warning", queued: "info", tts_done: "warning" };
  return map[status] || "info";
}
function statusText(status: string) {
  const map: Record<string, string> = { done: "已完成", failed: "失败", processing: "生成中", queued: "排队中", tts_done: "语音完成" };
  return map[status] || status;
}
function download(row: any) {
  if (row.video_url) window.open(row.video_url);
}

async function fetchVideos() {
  loading.value = true;
  try { const resp = await getVideos(); videos.value = resp.data.items; }
  finally { loading.value = false; }
}

async function handleDelete(id: string) {
  try {
    await ElMessageBox.confirm("确定删除该视频吗？", "确认", { type: "warning" });
    await deleteVideo(id);
    ElMessage.success("已删除");
    fetchVideos();
  } catch { /* cancelled */ }
}

onMounted(fetchVideos);
</script>
```

- [ ] **Step 4: 视频详情页 `frontend/src/views/VideoDetail.vue`**

```vue
<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">视频详情</h2>
    <el-card v-loading="loading" style="max-width: 700px">
      <el-descriptions :column="2" border v-if="video">
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(video.status)">{{ statusText(video.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="消耗算粒">{{ video.cost_credits }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ new Date(video.created_at).toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">
          {{ video.completed_at ? new Date(video.completed_at).toLocaleString() : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="文案" :span="2">{{ video.script_text }}</el-descriptions-item>
        <el-descriptions-item v-if="video.error_message" label="错误信息" :span="2">
          <el-text type="danger">{{ video.error_message }}</el-text>
        </el-descriptions-item>
      </el-descriptions>
      <div style="margin-top: 24px" v-if="video">
        <el-button v-if="video.video_url" type="success" size="large" @click="window.open(video.video_url)">
          下载视频
        </el-button>
        <el-button @click="refresh" :loading="loading">刷新状态</el-button>
      </div>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { getVideo } from "../api/videos";
import AppLayout from "../components/AppLayout.vue";

const route = useRoute();
const video = ref<any>(null);
const loading = ref(false);

function statusType(s: string) {
  const map: Record<string, string> = { done: "success", failed: "danger", processing: "warning", queued: "info" };
  return map[s] || "info";
}
function statusText(s: string) {
  const map: Record<string, string> = { done: "已完成", failed: "失败", processing: "生成中", queued: "排队中" };
  return map[s] || s;
}

async function refresh() {
  loading.value = true;
  try { video.value = (await getVideo(route.params.id as string)).data; }
  finally { loading.value = false; }
}

onMounted(refresh);
</script>
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: video create, list, detail views"
```

---

### Task 13: Vue前端 — 套餐 + 算粒 + App.vue注册

**Files:**
- Create: `frontend/src/api/plans.ts`
- Create: `frontend/src/api/credits.ts`
- Create: `frontend/src/views/PlanList.vue`
- Create: `frontend/src/views/CreditLog.vue`

- [ ] **Step 1: APIs**

```typescript
// frontend/src/api/plans.ts
import client from "./client";
export function getPlans() { return client.get("/api/plans"); }
```

```typescript
// frontend/src/api/credits.ts
import client from "./client";
export function getCreditLog() { return client.get("/api/credits/log"); }
```

- [ ] **Step 2: 套餐页 `frontend/src/views/PlanList.vue`**

```vue
<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">套餐中心</h2>
    <el-row :gutter="16">
      <el-col :span="8" v-for="plan in plans" :key="plan.id">
        <el-card shadow="hover" class="plan-card">
          <h3>{{ plan.name }}</h3>
          <div class="plan-price">¥{{ plan.monthly_price }}<span>/月</span></div>
          <el-divider />
          <p>每月 {{ plan.credits_per_month }} 算粒</p>
          <p v-if="plan.features">可创建 {{ plan.features.avatars }} 个形象</p>
          <p v-if="plan.features">最高 {{ plan.features.resolution }} 分辨率</p>
          <el-button type="primary" style="margin-top: 16px" block>订阅 (即将上线)</el-button>
        </el-card>
      </el-col>
    </el-row>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getPlans } from "../api/plans";
import AppLayout from "../components/AppLayout.vue";

const plans = ref<any[]>([]);

onMounted(async () => {
  const resp = await getPlans();
  plans.value = resp.data.items;
});
</script>

<style scoped>
.plan-card { text-align: center; padding: 16px; }
.plan-price { font-size: 32px; font-weight: bold; color: #409EFF; margin: 12px 0; }
.plan-price span { font-size: 14px; font-weight: normal; color: #999; }
</style>
```

- [ ] **Step 3: 算粒明细页 `frontend/src/views/CreditLog.vue`**

```vue
<template>
  <AppLayout>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2>算粒明细</h2>
      <el-tag type="warning" size="large">当前余额: {{ userStore.balance }}</el-tag>
    </div>
    <el-table :data="logs" v-loading="loading" empty-text="暂无记录">
      <el-table-column prop="type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.type === 'charge' ? 'success' : row.type === 'refund' ? 'info' : 'warning'">
            {{ row.type === 'charge' ? '充值' : row.type === 'refund' ? '退款' : '消耗' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="数量" width="120">
        <template #default="{ row }">
          <span :style="{ color: row.amount > 0 ? '#67C23A' : '#F56C6C' }">
            {{ row.amount > 0 ? '+' : '' }}{{ row.amount }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="balance" label="余额" width="100" />
      <el-table-column prop="source" label="来源" />
      <el-table-column prop="created_at" label="时间" width="180">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
      </el-table-column>
    </el-table>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getCreditLog } from "../api/credits";
import { useUserStore } from "../stores/user";
import AppLayout from "../components/AppLayout.vue";

const userStore = useUserStore();
const logs = ref<any[]>([]);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    const resp = await getCreditLog();
    logs.value = resp.data.items;
    await userStore.fetchBalance();
  } finally { loading.value = false; }
});
</script>
```

- [ ] **Step 4: 验证所有前端页面**

```bash
cd frontend && npm run dev
```

完整流程: 注册 → 登录 → 工作台 → 创建形象 → 形象列表 → 生成视频 → 视频列表 → 视频详情 → 套餐中心 → 算粒明细

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: plans + credit log views, frontend complete"
```

---

### Task 14: 端到端验证

- [ ] **Step 1: 确保所有服务运行**

```bash
# 确保 PostgreSQL + Redis 运行中
# 终端1: Celery worker
cd backend && celery -A app.tasks.celery_app worker -l info -P solo
# 终端2: FastAPI
cd backend && uvicorn app.main:app --reload --port 8000
# 终端3: Vite
cd frontend && npm run dev
```

- [ ] **Step 2: E2E验证脚本**

```bash
# 1. 健康检查
curl http://localhost:8000/api/health

# 2. 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000000","password":"123456","company_name":"测试美容店"}'

# 3. 登录 + 保存token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000000","password":"123456"}' | jq -r '.access_token')

# 4. 查询模板
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/templates | jq '.total'

# 5. 创建形象
AVATAR_ID=$(curl -s -X POST http://localhost:8000/api/avatars \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试形象","photo_urls":{"front":"http://example.com/face.jpg"}}' | jq -r '.id')

# 6. 创建视频任务
TEMPLATE_ID=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/templates | jq -r '.items[0].id')
curl -s -X POST http://localhost:8000/api/videos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"avatar_id\":\"$AVATAR_ID\",\"template_id\":\"$TEMPLATE_ID\",\"script_text\":\"大家好，欢迎光临我们的店铺\"}" | jq '.'

# 7. 查询算粒余额
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/credits/balance | jq '.'

# 8. 查询视频列表
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/videos | jq '.total'
```

验证: 所有API返回正常，无错误。

- [ ] **Step 3: 跑全部后端测试**

```bash
cd backend && pytest tests/ -v
```

预期: 12+ tests passed

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: e2e verification + all backend tests passing"
```

---

## 完成检查清单

- [ ] 用户可注册/登录
- [ ] 用户可创建数字人形象（MVP自动授权）
- [ ] 用户可查看行业模板（美容行业3个模板）
- [ ] 用户可提交视频生成任务（消耗算粒）
- [ ] 算粒不足时提示402
- [ ] 视频任务异步处理（Celery）
- [ ] 用户可查看视频列表/详情/下载
- [ ] 用户可查看套餐
- [ ] 用户可查看算粒流水
- [ ] 全部后端测试通过
- [ ] 前后端联调正常

---

> 📌 **依赖集成完成时需替换的桩代码:**
> - `seedance_service.py`: 替换为火山引擎方舟平台真实API调用
> - `tts_service.py`: 替换为腾讯云MAIS真实API调用
> - `storage_service.py`: 替换为OSS/COS SDK真实上传
> - `Video.vue` 的download: 点击后触发OSS下载
