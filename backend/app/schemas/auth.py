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
