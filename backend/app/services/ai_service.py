import httpx
from sqlalchemy import select, or_, and_
from app.config import settings
from app.database import async_session
from app.models.message import Message
from app.models.user import User


async def get_ai_response(user_id: int, user_message: str) -> str | None:
    """Call LLM API and return AI response."""
    if not settings.AI_API_KEY:
        return "AI \u52a9\u624b\u6682\u672a\u914d\u7f6e API Key\uff0c\u8bf7\u8054\u7cfb\u7ba1\u7406\u5458\u3002"

    async with async_session() as db:
        ai_user = await db.execute(select(User).where(User.username == settings.AI_ASSISTANT_USERNAME))
        ai_user = ai_user.scalar_one_or_none()
        if not ai_user:
            return "AI \u52a9\u624b\u4e0d\u5b58\u5728"

        # Get last 10 messages as context
        result = await db.execute(
            select(Message)
            .where(
                or_(
                    and_(Message.sender_id == user_id, Message.receiver_id == ai_user.id),
                    and_(Message.sender_id == ai_user.id, Message.receiver_id == user_id),
                )
            )
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        history = list(reversed(result.scalars().all()))

    messages = [{"role": "system", "content": settings.AI_SYSTEM_PROMPT}]
    for msg in history:
        role = "user" if msg.sender_id == user_id else "assistant"
        messages.append({"role": role, "content": msg.content or ""})

    # Add current message
    messages.append({"role": "user", "content": user_message})

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                settings.AI_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI \u56de\u590d\u51fa\u9519: {str(e)}"

