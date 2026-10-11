from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.friendship import Friendship
from app.config import settings
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token


async def register_user(db: AsyncSession, username: str, email: str, password: str) -> tuple[User, str, str]:
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已被注册")

    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已被注册")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    if settings.AI_ASSISTANT_ENABLED:
        try:
            result = await db.execute(select(User).where(User.username == settings.AI_ASSISTANT_USERNAME))
            ai_user = result.scalar_one_or_none()
            if ai_user:
                lower, higher = sorted([user.id, ai_user.id])
                existing = await db.execute(
                    select(Friendship).where(
                        Friendship.user_id == lower, Friendship.friend_id == higher
                    )
                )
                if not existing.scalar_one_or_none():
                    friendship = Friendship(user_id=lower, friend_id=higher)
                    db.add(friendship)
                    await db.commit()
        except Exception:
            await db.rollback()

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return user, access_token, refresh_token


async def authenticate_user(db: AsyncSession, username: str, password: str) -> tuple[User, str, str]:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你已被封禁，请联系管理员")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return user, access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token_str: str) -> tuple[str, str]:
    payload = decode_token(refresh_token_str)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return new_access_token, new_refresh_token

