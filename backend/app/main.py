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

from app.api.auth import router as auth_router
from app.api.avatars import router as avatars_router
app.include_router(auth_router)
app.include_router(avatars_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
