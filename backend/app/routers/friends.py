from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.friend_request import FriendRequest
from app.schemas.friend import (
    FriendRequestCreate,
    FriendRequestResponse,
    FriendRequestWithUser,
    FriendWithLastMessage,
    FriendshipResponse,
)
from app.services import friend_service
from app.services.user_service import get_user_by_id
from app.websocket.manager import manager

router = APIRouter(prefix="/api/v1/friends", tags=["friends"])


@router.get("", response_model=list[FriendWithLastMessage])
async def get_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await friend_service.get_friends_with_last_message(db, current_user.id)


@router.post("/requests", response_model=FriendRequestResponse, status_code=201)
async def send_request(
    body: FriendRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fr = await friend_service.send_friend_request(db, current_user.id, body.receiver_id, body.message)

    # Notify the receiver via WebSocket
    if fr.status == "accepted":
        # Auto-accepted (e.g. AI assistant) - notify sender
        await manager.send_personal(
            {"type": "friend_request_accepted", "request_id": fr.id, "friend_id": body.receiver_id},
            current_user.id,
        )
    else:
        # Normal request - notify receiver
        await manager.send_personal(
            {"type": "new_friend_request", "request_id": fr.id, "sender_name": current_user.username},
            body.receiver_id,
        )

    return FriendRequestResponse.model_validate(fr)


@router.get("/requests/pending", response_model=list[FriendRequestWithUser])
async def get_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    requests = await friend_service.get_pending_requests(db, current_user.id)
    result = []
    for fr in requests:
        sender = await get_user_by_id(db, fr.sender_id)
        result.append(
            FriendRequestWithUser(
                id=fr.id,
                sender_id=fr.sender_id,
                receiver_id=fr.receiver_id,
                status=fr.status,
                message=fr.message,
                sender=sender,
                created_at=fr.created_at,
                updated_at=fr.updated_at,
            )
        )
    return result


@router.get("/requests/sent", response_model=list[FriendRequestWithUser])
async def get_sent_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    requests = await friend_service.get_sent_requests(db, current_user.id)
    result = []
    for fr in requests:
        receiver = await get_user_by_id(db, fr.receiver_id)
        result.append(
            FriendRequestWithUser(
                id=fr.id,
                sender_id=fr.sender_id,
                receiver_id=fr.receiver_id,
                status=fr.status,
                message=fr.message,
                receiver=receiver,
                created_at=fr.created_at,
                updated_at=fr.updated_at,
            )
        )
    return result


@router.patch("/requests/{request_id}/accept", response_model=FriendRequestResponse)
async def accept_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    friendship = await friend_service.accept_friend_request(db, request_id, current_user.id)

    result = await db.execute(select(FriendRequest).where(FriendRequest.id == request_id))
    fr = result.scalar_one()

    # Notify the original sender via WebSocket that request was accepted
    await manager.send_personal(
        {"type": "friend_request_accepted", "request_id": request_id, "friend_id": current_user.id},
        fr.sender_id,
    )

    return FriendRequestResponse.model_validate(fr)


@router.patch("/requests/{request_id}/reject", response_model=FriendRequestResponse)
async def reject_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fr = await friend_service.reject_friend_request(db, request_id, current_user.id)
    return FriendRequestResponse.model_validate(fr)


@router.delete("/{friend_id}")
async def remove_friend(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await friend_service.remove_friend(db, current_user.id, friend_id)
    return {"ok": True, "detail": "Friend and all chat history deleted"}

