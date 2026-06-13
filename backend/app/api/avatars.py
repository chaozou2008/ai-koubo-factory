from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.avatar import Avatar
from app.schemas.avatar import AvatarCreateRequest, AvatarResponse, AvatarListResponse
from app.api.deps import get_current_user
from app.services.seedance_service import get_seedance_service

router = APIRouter(prefix="/api/avatars", tags=["avatars"])


@router.post("", response_model=AvatarResponse, status_code=status.HTTP_201_CREATED)
async def create_avatar(
    req: AvatarCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar = Avatar(
        user_id=current_user.id,
        name=req.name,
        photo_urls=req.photo_urls,
    )
    db.add(avatar)
    await db.flush()

    seedance = get_seedance_service()
    auth_info = await seedance.generate_auth_qrcode(str(current_user.id))
    check = await seedance.check_authorization(str(current_user.id))
    avatar.material_id = check.get("material_id")
    avatar.character_id = check.get("character_id")
    avatar.status = "active"

    await db.commit()
    return avatar


@router.get("", response_model=AvatarListResponse)
async def list_avatars(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Avatar).where(Avatar.user_id == current_user.id))
    items = result.scalars().all()
    return AvatarListResponse(items=list(items), total=len(items))


@router.get("/{avatar_id}", response_model=AvatarResponse)
async def get_avatar(
    avatar_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar = await db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="形象不存在")
    return avatar


@router.delete("/{avatar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(
    avatar_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar = await db.get(Avatar, avatar_id)
    if not avatar or avatar.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="形象不存在")
    await db.delete(avatar)
