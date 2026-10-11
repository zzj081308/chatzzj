import json

from fastapi import WebSocket, WebSocketDisconnect

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

from app.dependencies import get_current_user_ws

from app.websocket.manager import manager

from app.services.message_service import save_message, mark_messages_as_read

from app.services.friend_service import check_are_friends, get_friends_with_last_message





async def handle_websocket(websocket: WebSocket, token: str, db: AsyncSession):

    """Main WebSocket handler for chat connections."""

    # Authenticate

    user = await get_current_user_ws(token, db)

    if not user:

        await websocket.close(code=4001, reason="Invalid token")

        return



    user_id = user.id



    # Connect

    await manager.connect(websocket, user_id, db)



    # Get friend IDs for broadcasting online status

    friends_data = await get_friends_with_last_message(db, user_id)

    friend_ids = [f["id"] for f in friends_data]



    # Broadcast online status to friends

    await manager.broadcast_to_friends(

        user_id, friend_ids,

        {"type": "friend_online", "user_id": user_id, "is_online": True}

    )



    # Send current online friends to the connecting user

    online_friends = manager.get_online_friend_ids(friend_ids)

    await manager.send_personal(

        {"type": "online_friends", "user_ids": online_friends},

        user_id,

    )



    try:

        while True:
            # Check if user is still active (not banned)
            # Force fresh read from DB to bypass identity map cache
            from sqlalchemy import select
            from app.models.user import User
            r = await db.execute(
                select(User).where(User.id == user_id).execution_options(populate_existing=True)
            )
            cu = r.scalar_one_or_none()
            if cu and cu.is_banned:
                await websocket.close(code=4001, reason="账号已被封禁")
                break

            raw = await websocket.receive_text()

            data = json.loads(raw)

            msg_type = data.get("type", "")



            if msg_type == "chat_message":

                await handle_chat_message(user_id, data, db)

            elif msg_type == "typing":

                await handle_typing(user_id, data)

            elif msg_type == "read_receipt":

                await handle_read_receipt(user_id, data, db)

            elif msg_type == "ping":

                await manager.send_personal({"type": "pong"}, user_id)

            else:

                await manager.send_personal(

                    {"type": "error", "code": "unknown_type", "detail": f"Unknown message type: {msg_type}"},

                    user_id,

                )



    except WebSocketDisconnect:

        pass

    finally:

        await manager.disconnect(user_id, db)

        # Broadcast offline to friends

        await manager.broadcast_to_friends(

            user_id, friend_ids,

            {"type": "friend_offline", "user_id": user_id, "is_online": False}

        )





async def handle_chat_message(sender_id: int, data: dict, db: AsyncSession):
    # Force fresh read from DB to bypass identity map cache
    from sqlalchemy import select
    from app.models.user import User
    result = await db.execute(
        select(User).where(User.id == sender_id).execution_options(populate_existing=True)
    )
    sender = result.scalar_one_or_none()
    if sender and sender.is_banned:
        await manager.send_personal(
            {"type": "error", "code": "banned", "detail": "你的账号已被封禁，无法发送消息"},
            sender_id,
        )
        return

    """Process an incoming chat message."""

    receiver_id = data.get("receiver_id")

    message_type = data.get("message_type", "text")

    content = data.get("content")

    file_url = data.get("file_url")

    file_name = data.get("file_name")

    image_url = data.get("image_url")

    client_msg_id = data.get("client_msg_id")



    if not receiver_id:

        await manager.send_personal(

            {"type": "error", "code": "missing_field", "detail": "receiver_id is required"},

            sender_id,

        )

        return



    # Verify friendship

    are_friends = await check_are_friends(db, sender_id, receiver_id)

    if not are_friends:

        await manager.send_personal(

            {"type": "error", "code": "not_friends", "detail": "You are not friends with this user"},

            sender_id,

        )

        return



    # Check if receiver is AI assistant

    if message_type == "text" and content:

        from sqlalchemy import select

        from app.models.user import User

        receiver_user = await db.execute(select(User).where(User.id == receiver_id))

        receiver_user = receiver_user.scalar_one_or_none()

        if receiver_user and receiver_user.is_ai:

            # Save user message

            message = await save_message(

                db, sender_id=sender_id, receiver_id=receiver_id,

                message_type="text", content=content,

            )

            # ACK to sender

            await manager.send_personal(

                {"type": "message_sent", "client_msg_id": client_msg_id,

                 "server_id": message.id, "created_at": message.created_at.isoformat()},

                sender_id,

            )

            # Get AI response

            from app.services.ai_service import get_ai_response

            ai_reply = await get_ai_response(sender_id, content)

            if ai_reply:

                ai_msg = await save_message(

                    db, sender_id=receiver_id, receiver_id=sender_id,

                    message_type="text", content=ai_reply,

                )

                await manager.send_personal(

                    {"type": "new_message", "id": ai_msg.id,

                     "sender_id": receiver_id, "receiver_id": sender_id,

                     "message_type": "text", "content": ai_reply,

                     "image_url": None, "file_url": None, "file_name": None,

                     "is_read": False, "created_at": ai_msg.created_at.isoformat()},

                    sender_id,

                )

            return



    # Validate message content

    if message_type == "text" and not content:

        await manager.send_personal(

            {"type": "error", "code": "empty_content", "detail": "Text message content is required"},

            sender_id,

        )

        return





    if message_type == "file" and not file_url:

        await manager.send_personal(

            {"type": "error", "code": "empty_file", "detail": "File URL is required for file messages"},

            sender_id,

        )

        return



    if message_type == "image" and not image_url:

        await manager.send_personal(

            {"type": "error", "code": "empty_image", "detail": "Image URL is required for image messages"},

            sender_id,

        )

        return



    # Save message to database

    message = await save_message(

        db,

        sender_id=sender_id,

        receiver_id=receiver_id,

        message_type=message_type,

        content=content,

        file_url=file_url,

        file_name=file_name,

        image_url=image_url,

    )



    # ACK to sender

    await manager.send_personal(

        {

            "type": "message_sent",

            "client_msg_id": client_msg_id,

            "server_id": message.id,

            "created_at": message.created_at.isoformat(),

        },

        sender_id,

    )



    # Deliver to receiver (if online)

    await manager.send_personal(

        {

            "type": "new_message",

            "id": message.id,

            "sender_id": sender_id,

            "receiver_id": receiver_id,

            "message_type": message_type,

            "content": content,

            "file_url": file_url,

            "file_name": file_name,

            "image_url": image_url,

            "is_read": False,

            "created_at": message.created_at.isoformat(),

        },

        receiver_id,

    )





async def handle_typing(user_id: int, data: dict):

    """Relay typing indicator."""

    receiver_id = data.get("receiver_id")

    is_typing = data.get("is_typing", False)

    if receiver_id:

        await manager.send_personal(

            {"type": "typing", "sender_id": user_id, "is_typing": is_typing},

            receiver_id,

        )





async def handle_read_receipt(user_id: int, data: dict, db: AsyncSession):

    """Mark messages as read and notify sender."""

    sender_id = data.get("sender_id")

    last_read_message_id = data.get("last_read_message_id")

    if sender_id and last_read_message_id:

        await mark_messages_as_read(db, sender_id, user_id, last_read_message_id)

        await manager.send_personal(

            {

                "type": "read_receipt",

                "reader_id": user_id,

                "last_read_message_id": last_read_message_id,

            },

            sender_id,

        )



