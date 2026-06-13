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
