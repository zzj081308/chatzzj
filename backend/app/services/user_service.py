from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.friendship import Friendship


async def search_users(db: AsyncSession, current_user_id: int, query: str, limit: int = 20) -> list[User]:
    """Search users by username, excluding self and existing friends."""
    # Get friend IDs
    friend_result = await db.execute(
        select(Friendship).where(
            or_(Friendship.user_id == current_user_id, Friendship.friend_id == current_user_id)
        )
    )
    friendships = friend_result.scalars().all()
    friend_ids = set()
    for f in friendships:
        friend_ids.add(f.user_id if f.friend_id == current_user_id else f.friend_id)

    # Exclude self and existing friends from search
    exclude_ids = friend_ids | {current_user_id}

    result = await db.execute(
        select(User)
        .where(
            User.username.ilike(f"%{query}%"),
            User.id.notin_(exclude_ids),
        )
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

