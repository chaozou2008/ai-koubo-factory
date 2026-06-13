from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
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


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


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
        password_hash=hash_password(req.password),
        company_name=req.company_name,
    )
    db.add(user)
    await db.flush()

    # 新用户赠送100算粒
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
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="手机号或密码错误")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
