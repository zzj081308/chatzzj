from sqlalchemy import select, and_, or_, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message


async def save_message(
    db: AsyncSession,
    sender_id: int,
    receiver_id: int,
    message_type: str = "text",
    content: str | None = None,
    file_url: str | None = None,
    file_name: str | None = None,
    image_url: str | None = None,
) -> Message:
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message_type=message_type,
        content=content,
        file_url=file_url,
        file_name=file_name,
        image_url=image_url,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_conversation(
    db: AsyncSession, user_id: int, friend_id: int, cursor: int | None = None, limit: int = 50
) -> dict:
    """Get paginated conversation between two users. Cursor-based, newest first."""
    base_conditions = [
        or_(
            and_(Message.sender_id == user_id, Message.receiver_id == friend_id),
            and_(Message.sender_id == friend_id, Message.receiver_id == user_id),
        )
    ]

    if cursor:
        base_conditions.append(Message.id < cursor)

    query = (
        select(Message)
        .where(and_(*base_conditions))
        .order_by(Message.created_at.desc())
        .limit(limit + 1)  # Fetch one extra to check if there are more
    )

    result = await db.execute(query)
    messages = list(result.scalars().all())

    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]

    next_cursor = messages[-1].id if has_more else None

    return {
        "messages": messages,
        "has_more": has_more,
        "next_cursor": next_cursor,
    }


async def delete_conversation(db: AsyncSession, user_id: int, friend_id: int) -> int:
    """Delete all messages between two users. Returns count of deleted messages."""
    result = await db.execute(
        delete(Message).where(
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id == friend_id),
                and_(Message.sender_id == friend_id, Message.receiver_id == user_id),
            )
        )
    )
    await db.commit()
    return result.rowcount


async def mark_messages_as_read(db: AsyncSession, sender_id: int, receiver_id: int, up_to_message_id: int) -> None:
    """Mark all unread messages from sender to receiver as read, up to a given message ID."""
    await db.execute(
        update(Message)
        .where(
            and_(
                Message.sender_id == sender_id,
                Message.receiver_id == receiver_id,
                Message.is_read == False,
                Message.id <= up_to_message_id,
            )
        )
        .values(is_read=True)
    )
    await db.commit()

