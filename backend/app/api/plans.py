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
