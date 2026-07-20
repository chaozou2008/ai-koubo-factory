from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发模式放开，生产环境改为具体域名
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.auth import router as auth_router
from app.api.avatars import router as avatars_router
from app.api.templates import router as templates_router
from app.api.videos import router as videos_router
from app.api.plans import router as plans_router
from app.api.credits import router as credits_router
from app.api.publish import router as publish_router
app.include_router(auth_router)
app.include_router(avatars_router)
app.include_router(templates_router)
app.include_router(videos_router)
app.include_router(plans_router)
app.include_router(credits_router)
app.include_router(publish_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
