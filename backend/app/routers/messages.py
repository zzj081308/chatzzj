from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.message import MessageResponse, MessageHistoryResponse
from app.services import message_service, friend_service
from app.websocket.manager import manager

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])


class SendMessageBody(BaseModel):
    file_url: str | None = None
    file_name: str | None = None
    receiver_id: int
    message_type: str = "text"
    content: str | None = None
    image_url: str | None = None
    client_msg_id: str | None = None


@router.get("/{friend_id}", response_model=MessageHistoryResponse)
async def get_messages(
    friend_id: int,
    cursor: int | None = Query(None, description="Message ID cursor for pagination"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify friendship
    are_friends = await friend_service.check_are_friends(db, current_user.id, friend_id)
    if not are_friends:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="You are not friends with this user")

    result = await message_service.get_conversation(db, current_user.id, friend_id, cursor, limit)
    return MessageHistoryResponse(
        messages=[MessageResponse.model_validate(m) for m in result["messages"]],
        has_more=result["has_more"],
        next_cursor=result["next_cursor"],
    )


@router.delete("/{friend_id}")
async def delete_messages(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all messages between current user and a friend."""
    are_friends = await friend_service.check_are_friends(db, current_user.id, friend_id)
    if not are_friends:
        raise HTTPException(status_code=403, detail="You are not friends with this user")

    deleted_count = await message_service.delete_conversation(db, current_user.id, friend_id)
    return {"ok": True, "deleted_count": deleted_count}


@router.post("/send", response_model=MessageResponse, status_code=201)
async def send_message(
    body: SendMessageBody,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify friendship
    are_friends = await friend_service.check_are_friends(db, current_user.id, body.receiver_id)
    if not are_friends:
        raise HTTPException(status_code=403, detail="You are not friends with this user")

    # Validate
    if body.message_type == "text" and not body.content:
        raise HTTPException(status_code=400, detail="Text message content is required")

    # Save message
    msg = await message_service.save_message(
        db,
        sender_id=current_user.id,
        receiver_id=body.receiver_id,
        message_type=body.message_type,
        file_url=body.file_url,
        file_name=body.file_name,
        content=body.content,
        image_url=body.image_url,
    )

    # Deliver to receiver via WebSocket if online
    await manager.send_personal(
        {
            "type": "new_message",
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "message_type": msg.message_type,
            "content": msg.content,
            "file_url": msg.file_url,
            "file_name": msg.file_name,
            "image_url": msg.image_url,
            "is_read": False,
            "created_at": msg.created_at.isoformat(),
        },
        body.receiver_id,
    )

    return MessageResponse.model_validate(msg)


