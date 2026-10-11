from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import engine, Base
from app.database import init_db, async_session
from app.routers import auth, users, friends, messages, upload
from app.routers import admin as admin_router
from app.routers import appeal as appeal_router
from app.websocket.handlers import handle_websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()

    # Run DB migration for new columns
    from sqlalchemy import text
    _migrations = [
        "ALTER TABLE messages ADD COLUMN file_url VARCHAR(500)",
        "ALTER TABLE messages ADD COLUMN file_name VARCHAR(255)",
        "ALTER TABLE users ADD COLUMN is_ai BOOLEAN DEFAULT 0",
        "ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0",
        "ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT 0",
    ]
    for _sql in _migrations:
        try:
            async with engine.begin() as _conn:
                await _conn.execute(text(_sql))
        except Exception:
            pass  # Column already exists

    # Create AI assistant user if not exists
    if settings.AI_ASSISTANT_ENABLED:
        try:
            async with async_session() as session:
                from app.models.user import User
                from sqlalchemy import select
                result = await session.execute(select(User).where(User.username == settings.AI_ASSISTANT_USERNAME))
                ai_user = result.scalar_one_or_none()
                if not ai_user:
                    ai_user = User(
                        username=settings.AI_ASSISTANT_USERNAME,
                        email="ai@chatzzj.local",
                        hashed_password="",
                        avatar_url="/uploads/avatars/ai_assistant.png",
                        is_online=True,
                        is_ai=True,
                    )
                    session.add(ai_user)
                    await session.commit()
                    print(f"Created AI assistant user: {ai_user.username} (id={ai_user.id})")
        except Exception as e:
            print(f"Could not create AI user: {e}")

    # Create admin user on startup
    admin_username = settings.ADMIN_USERNAME
    admin_password = settings.ADMIN_PASSWORD
    if admin_username and admin_password:
        from app.services.admin_service import ensure_admin_user
        try:
            async with async_session() as session:
                await ensure_admin_user(session, admin_username, admin_password)
                print(f"Admin user ensured: {admin_username}")
        except Exception as e:
            print(f"Could not ensure admin user: {e}")


    os.makedirs(os.path.join(settings.UPLOAD_DIR, "avatars"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "chat_images"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "chat_files"), exist_ok=True)

    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# CORS - allow configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routers
app.include_router(admin_router.router)
app.include_router(appeal_router.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(messages.router)
app.include_router(upload.router)

# Ensure upload directory exists before mounting
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    import traceback
    async with async_session() as db:
        try:
            await handle_websocket(websocket, token, db)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"WebSocket error: {e}")
            traceback.print_exc()
