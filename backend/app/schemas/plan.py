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
