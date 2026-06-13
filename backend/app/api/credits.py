from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
