from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.credit_log import CreditLog


async def deduct_credits(db: AsyncSession, user_id: UUID, amount: int, source: str) -> bool:
    """扣减算粒，余额不足返回False"""
    user = await db.get(User, user_id)
    if user.credits_balance < amount:
        return False
    user.credits_balance -= amount
    log = CreditLog(
        user_id=user_id, amount=-amount, balance=user.credits_balance,
        type="consume", source=source,
    )
    db.add(log)
    return True


async def refund_credits(db: AsyncSession, user_id: UUID, amount: int, source: str):
    """退还算粒"""
    user = await db.get(User, user_id)
    user.credits_balance += amount
    log = CreditLog(
        user_id=user_id, amount=amount, balance=user.credits_balance,
        type="refund", source=source,
    )
    db.add(log)
