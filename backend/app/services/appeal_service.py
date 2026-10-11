from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.appeal import Appeal
from app.services.auth_service import authenticate_user




async def check_account(db: AsyncSession, username: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="账号不存在")
    from app.utils.security import verify_password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="密码错误")
    if user.is_banned:
        return {"banned": True, "username": user.username}
    return {"banned": False, "message": "账号状态正常"}

async def submit_appeal(db: AsyncSession, username: str, password: str, reason: str) -> Appeal:
    from app.utils.security import verify_password
    try:
        user, _, _ = await authenticate_user(db, username, password)
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN and "封禁" in e.detail:
            pass  # Correct - user is banned
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账号或密码错误")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_banned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="账号状态正常，无需申诉")

    appeal = Appeal(user_id=user.id, username=user.username, email=user.email, reason=reason)
    db.add(appeal)
    await db.commit()
    await db.refresh(appeal)
    return appeal


async def get_user_appeals(db: AsyncSession, user_id: int) -> list[Appeal]:
    result = await db.execute(
        select(Appeal).where(Appeal.user_id == user_id).order_by(Appeal.created_at.desc())
    )
    return list(result.scalars().all())


async def get_all_appeals(db: AsyncSession, status_filter: str | None = None) -> list[Appeal]:
    query = select(Appeal).order_by(Appeal.created_at.desc())
    if status_filter:
        query = query.where(Appeal.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def approve_appeal(db: AsyncSession, appeal_id: int, admin_id: int) -> Appeal:
    result = await db.execute(select(Appeal).where(Appeal.id == appeal_id))
    appeal = result.scalar_one_or_none()
    if not appeal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申诉不存在")

    appeal.status = "resolved"
    appeal.admin_id = admin_id
    await db.commit()

    result = await db.execute(select(User).where(User.id == appeal.user_id))
    user = result.scalar_one_or_none()
    if user:
        user.is_banned = False
        await db.commit()

    await db.refresh(appeal)
    return appeal


async def reject_appeal(db: AsyncSession, appeal_id: int, admin_id: int, response_text: str) -> Appeal:
    result = await db.execute(select(Appeal).where(Appeal.id == appeal_id))
    appeal = result.scalar_one_or_none()
    if not appeal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申诉不存在")

    appeal.status = "rejected"
    appeal.admin_id = admin_id
    appeal.admin_response = response_text
    await db.commit()
    await db.refresh(appeal)
    return appeal

