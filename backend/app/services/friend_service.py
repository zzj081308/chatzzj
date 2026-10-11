from sqlalchemy import select, or_, and_, func, delete as sa_delete, case, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.models.friendship import Friendship
from app.models.friend_request import FriendRequest
from app.models.message import Message


async def send_friend_request(
    db: AsyncSession, sender_id: int, receiver_id: int, message: str | None = None
) -> FriendRequest:
    if sender_id == receiver_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot send friend request to yourself")

    result = await db.execute(select(User).where(User.id == receiver_id))
    receiver_user = result.scalar_one_or_none()
    if not receiver_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    lower_id, higher_id = (sender_id, receiver_id) if sender_id < receiver_id else (receiver_id, sender_id)
    result = await db.execute(
        select(Friendship).where(
            and_(Friendship.user_id == lower_id, Friendship.friend_id == higher_id)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already friends")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already friends")

    result = await db.execute(
        select(FriendRequest).where(
            and_(
                FriendRequest.sender_id == sender_id,
                FriendRequest.receiver_id == receiver_id,
                FriendRequest.status == "pending",
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already sent")

    result = await db.execute(
        select(FriendRequest).where(
            and_(
                FriendRequest.sender_id == receiver_id,
                FriendRequest.receiver_id == sender_id,
                FriendRequest.status == "pending",
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This user has already sent you a friend request")

    friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id, message=message)
    db.add(friend_request)
    await db.commit()
    await db.refresh(friend_request)
    return friend_request

    result = await db.execute(
        select(FriendRequest).where(
            and_(
                FriendRequest.sender_id == sender_id,
                FriendRequest.receiver_id == receiver_id,
                FriendRequest.status == "pending",
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already sent")

    result = await db.execute(
        select(FriendRequest).where(
            and_(
                FriendRequest.sender_id == receiver_id,
                FriendRequest.receiver_id == sender_id,
                FriendRequest.status == "pending",
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This user has already sent you a friend request")

    friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id, message=message)
    db.add(friend_request)
    await db.commit()
    await db.refresh(friend_request)
    return friend_request

async def accept_friend_request(db: AsyncSession, request_id: int, current_user_id: int) -> Friendship:
    result = await db.execute(select(FriendRequest).where(FriendRequest.id == request_id))
    friend_request = result.scalar_one_or_none()
    if not friend_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    if friend_request.receiver_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your request to accept")
    if friend_request.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is no longer pending")

    friend_request.status = "accepted"
    friend_request.updated_at = func.now()

    # Create friendship with canonical ordering (lower_id, higher_id)
    lower_id, higher_id = (
        (friend_request.sender_id, friend_request.receiver_id)
        if friend_request.sender_id < friend_request.receiver_id
        else (friend_request.receiver_id, friend_request.sender_id)
    )
    friendship = Friendship(user_id=lower_id, friend_id=higher_id)
    db.add(friendship)

    await db.commit()
    await db.refresh(friendship)
    return friendship


async def reject_friend_request(db: AsyncSession, request_id: int, current_user_id: int) -> FriendRequest:
    result = await db.execute(select(FriendRequest).where(FriendRequest.id == request_id))
    friend_request = result.scalar_one_or_none()
    if not friend_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    if friend_request.receiver_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your request to reject")
    if friend_request.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is no longer pending")

    friend_request.status = "rejected"
    friend_request.updated_at = func.now()
    await db.commit()
    await db.refresh(friend_request)
    return friend_request


async def get_friends_with_last_message(db: AsyncSession, user_id: int) -> list[dict]:
    """Get all friends with last message preview and unread count (optimized: 4 queries total)."""
    # 1. Get all friendships
    result = await db.execute(
        select(Friendship).where(
            or_(Friendship.user_id == user_id, Friendship.friend_id == user_id)
        )
    )
    friendships = result.scalars().all()
    if not friendships:
        return []

    friend_ids = [
        f.user_id if f.friend_id == user_id else f.friend_id
        for f in friendships
    ]

    # 2. Get all friend user info in one query
    friend_result = await db.execute(select(User).where(User.id.in_(friend_ids)))
    friends_by_id = {u.id: u for u in friend_result.scalars().all()}

    # 3. Get last message for each friend using a single query
    last_msg_subq = (
        select(
            Message.id,
            Message.sender_id,
            Message.receiver_id,
            Message.content,
            Message.created_at,
            Message.message_type,
            Message.image_url,
            Message.is_read,
            func.row_number().over(
                partition_by=case(
                    (Message.sender_id < Message.receiver_id, func.concat(Message.sender_id, '_', Message.receiver_id)),
                    else_=func.concat(Message.receiver_id, '_', Message.sender_id),
                ),
                order_by=Message.created_at.desc(),
            ).label('rn'),
        ).where(
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id.in_(friend_ids)),
                and_(Message.sender_id.in_(friend_ids), Message.receiver_id == user_id),
            )
        ).subquery()
    )
    last_msg_result = await db.execute(
        select(last_msg_subq).where(last_msg_subq.c.rn == 1)
    )
    # Map friend_id -> last message (Row objects with sender_id, receiver_id, content, created_at)
    last_msgs = {}
    for row in last_msg_result.all():
        fid = row.sender_id if row.receiver_id == user_id else row.receiver_id
        last_msgs[fid] = row

    # 4. Get unread counts in one query
    unread_result = await db.execute(
        select(
            Message.sender_id,
            func.count(Message.id).label('cnt'),
        ).where(
            and_(
                Message.sender_id.in_(friend_ids),
                Message.receiver_id == user_id,
                Message.is_read == False,
            )
        ).group_by(Message.sender_id)
    )
    unread_counts = {row.sender_id: row.cnt for row in unread_result.all()}

    # Build result
    friends_data = []
    for fid in friend_ids:
        friend = friends_by_id.get(fid)
        if not friend:
            continue
        last_msg = last_msgs.get(fid)
        friends_data.append({
            "id": friend.id,
            "username": friend.username,
            "avatar_url": friend.avatar_url,
            "is_online": True if friend.is_ai else friend.is_online,
            "is_ai": friend.is_ai,
            "last_message": last_msg.content if last_msg else None,
            "last_message_time": last_msg.created_at if last_msg else None,
            "unread_count": unread_counts.get(fid, 0),
        })

    # Sort by last message time descending (handle None safely)
    from datetime import datetime
    default_dt = datetime.min
    friends_data.sort(
        key=lambda x: x["last_message_time"] if x["last_message_time"] is not None else default_dt,
        reverse=True,
    )
    return friends_data


async def get_pending_requests(db: AsyncSession, user_id: int) -> list[FriendRequest]:
    result = await db.execute(
        select(FriendRequest)
        .where(
            and_(FriendRequest.receiver_id == user_id, FriendRequest.status == "pending")
        )
        .order_by(FriendRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def get_sent_requests(db: AsyncSession, user_id: int) -> list[FriendRequest]:
    result = await db.execute(
        select(FriendRequest)
        .where(
            and_(FriendRequest.sender_id == user_id, FriendRequest.status == "pending")
        )
        .order_by(FriendRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def remove_friend(db: AsyncSession, user_id: int, friend_id: int) -> None:
    """Remove friendship and delete all messages between the two users."""
    lower_id, higher_id = (user_id, friend_id) if user_id < friend_id else (friend_id, user_id)
    result = await db.execute(
        select(Friendship).where(
            and_(Friendship.user_id == lower_id, Friendship.friend_id == higher_id)
        )
    )
    friendship = result.scalar_one_or_none()
    if not friendship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")
    await db.delete(friendship)

    # Delete all messages between the two users
    await db.execute(
        sa_delete(Message).where(
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id == friend_id),
                and_(Message.sender_id == friend_id, Message.receiver_id == user_id),
            )
        )
    )

    await db.commit()


async def check_are_friends(db: AsyncSession, user_id: int, other_id: int) -> bool:
    lower_id, higher_id = (user_id, other_id) if user_id < other_id else (other_id, user_id)
    result = await db.execute(
        select(Friendship).where(
            and_(Friendship.user_id == lower_id, Friendship.friend_id == higher_id)
        )
    )
    return result.scalar_one_or_none() is not None

