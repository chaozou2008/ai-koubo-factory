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
