from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, or_, delete as sa_delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.message import Message
from app.models.friendship import Friendship
from app.models.friend_request import FriendRequest

async def get_dashboard_stats(db: AsyncSession) -> dict:
    r = await db.execute(select(func.count(User.id))); tu = r.scalar()
    r = await db.execute(select(func.count(Message.id))); tm = r.scalar()
    r = await db.execute(select(func.count(User.id)).where(User.is_online == True)); ou = r.scalar()
    r = await db.execute(select(func.count(User.id)).where(User.is_banned == True)); bu = r.scalar()
    r = await db.execute(select(func.count(User.id)).where(User.is_admin == True)); au = r.scalar()
    r = await db.execute(select(func.count(Friendship.id))); tf = r.scalar()
    r = await db.execute(select(func.count(FriendRequest.id)).where(FriendRequest.status == "pending")); pr = r.scalar()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    r = await db.execute(select(func.count(Message.id)).where(Message.created_at >= cutoff)); m24 = r.scalar()
    r = await db.execute(select(func.count(User.id)).where(User.created_at >= cutoff)); nu24 = r.scalar()
    return {"total_users": tu or 0, "total_messages": tm or 0, "online_users": ou or 0,
            "banned_users": bu or 0, "admin_users": au or 0, "total_friendships": tf or 0,
            "pending_requests": pr or 0, "messages_last_24h": m24 or 0, "new_users_last_24h": nu24 or 0}

async def list_users(db: AsyncSession, page=1, page_size=20, search=None):
    q = select(User); cq = select(func.count(User.id))
    if search:
        f = User.username.ilike(f"%{search}%"); q = q.where(f); cq = cq.where(f)
    r = await db.execute(cq); total = r.scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.order_by(User.created_at.desc()).offset(offset).limit(page_size))
    return list(r.scalars().all()), total

async def set_user_ban(db, user_id, banned):
    if banned:
        from app.websocket.manager import manager
        ws = manager.active_connections.get(user_id)
        if ws:
            try: await ws.close(code=4001, reason="你已被封禁")
            except: pass
            manager.active_connections.pop(user_id, None)
    r = await db.execute(select(User).where(User.id == user_id))
    u = r.scalar_one_or_none()
    if not u: return None
    u.is_banned = banned; await db.commit(); await db.refresh(u); return u

async def set_user_admin(db, user_id, is_admin):
    r = await db.execute(select(User).where(User.id == user_id))
    u = r.scalar_one_or_none()
    if not u: return None
    u.is_admin = is_admin; await db.commit(); await db.refresh(u); return u

async def delete_user(db, user_id):
    r = await db.execute(select(User).where(User.id == user_id))
    u = r.scalar_one_or_none()
    if not u: return False
    await db.execute(sa_delete(Message).where(or_(Message.sender_id == user_id, Message.receiver_id == user_id)))
    await db.execute(sa_delete(Friendship).where(or_(Friendship.user_id == user_id, Friendship.friend_id == user_id)))
    await db.execute(sa_delete(FriendRequest).where(or_(FriendRequest.sender_id == user_id, FriendRequest.receiver_id == user_id)))
    await db.delete(u); await db.commit(); return True

async def list_messages(db, page=1, page_size=20, search=None, sender=None, receiver=None):
    cq = select(func.count(Message.id))
    if search: cq = cq.where(Message.content.ilike(f"%{search}%"))
    r = await db.execute(cq); total = r.scalar() or 0
    offset = (page - 1) * page_size
    q = """SELECT m.id, m.sender_id, m.receiver_id, m.message_type, m.content,
                  m.image_url, m.file_url, m.file_name, m.is_read, m.created_at,
                  su.username as sender_username, ru.username as receiver_username
           FROM messages m
           LEFT JOIN users su ON m.sender_id = su.id
           LEFT JOIN users ru ON m.receiver_id = ru.id"""
    params = {}
    where_conds = []
    if search:
        where_conds.append("m.content LIKE :search")
        params["search"] = f"%{search}%"
    if sender:
        where_conds.append("su.username = :sender")
        params["sender"] = sender
    if receiver:
        where_conds.append("ru.username = :receiver")
        params["receiver"] = receiver
    if where_conds:
        q += " WHERE " + " AND ".join(where_conds)
    q += " ORDER BY m.created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size; params["offset"] = offset
    r = await db.execute(text(q), params)
    msgs = []
    for row in r.all():
        msgs.append({"id": int(row.id), "sender_id": int(row.sender_id), "receiver_id": int(row.receiver_id),
                     "message_type": str(row.message_type), "content": row.content,
                     "image_url": row.image_url, "file_url": row.file_url,
                     "file_name": row.file_name, "is_read": bool(row.is_read),
                     "created_at": str(row.created_at).replace(" ", "T") if row.created_at else None,
                     "sender_username": row.sender_username, "receiver_username": row.receiver_username})
    return msgs, total

async def delete_message(db, message_id):
    r = await db.execute(select(Message).where(Message.id == message_id))
    m = r.scalar_one_or_none()
    if not m: return False
    await db.delete(m); await db.commit(); return True

async def ensure_admin_user(db, username, password):
    from app.utils.security import hash_password
    r = await db.execute(select(User).where(User.username == username))
    u = r.scalar_one_or_none()
    if u:
        if not u.is_admin: u.is_admin = True; await db.commit()
        return u
    u = User(username=username, email=f"{username}@chatzzj.admin", hashed_password=hash_password(password), is_admin=True)
    db.add(u); await db.commit(); await db.refresh(u); return u



