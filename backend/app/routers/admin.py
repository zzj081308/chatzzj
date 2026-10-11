from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User
from app.config import settings
from app.schemas.admin import (
    AdminDashboard, AdminUserResponse, AdminMessageResponse,
    AdminSettingsResponse, AdminSettingsUpdate,
    AdminMessageListResponse, AdminUserListResponse,
)
from app.services import admin_service

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboard)
async def dashboard(db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    stats = await admin_service.get_dashboard_stats(db)
    stats["ai_enabled"] = settings.AI_ASSISTANT_ENABLED
    return stats


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sender: str | None = Query(None),
    receiver: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    users, total = await admin_service.list_users(db, page, page_size, search)
    return AdminUserListResponse(
        users=[AdminUserResponse.model_validate(u) for u in users],
        total=total, page=page, page_size=page_size,
    )


@router.patch("/users/{user_id}/ban", response_model=AdminUserResponse)
async def ban_user(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    if user_id == admin.id:
        raise HTTPException(400, detail="Cannot ban yourself")
    user = await admin_service.set_user_ban(db, user_id, True)
    if not user: raise HTTPException(404, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.patch("/users/{user_id}/unban", response_model=AdminUserResponse)
async def unban_user(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = await admin_service.set_user_ban(db, user_id, False)
    if not user: raise HTTPException(404, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.patch("/users/{user_id}/toggle-admin", response_model=AdminUserResponse)
async def toggle_admin(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = await admin_service.set_user_admin(db, user_id, True)
    if not user: raise HTTPException(404, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    if user_id == admin.id:
        raise HTTPException(400, detail="Cannot delete yourself")
    ok = await admin_service.delete_user(db, user_id)
    if not ok: raise HTTPException(404, detail="User not found")
    return {"ok": True, "detail": "User and all related data deleted"}


@router.get("/messages", response_model=AdminMessageListResponse)
async def list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sender: str | None = Query(None),
    receiver: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    messages, total = await admin_service.list_messages(db, page, page_size, search, sender, receiver)
    return AdminMessageListResponse(
        messages=[AdminMessageResponse(**m) for m in messages],
        total=total, page=page, page_size=page_size,
    )


@router.delete("/messages/{message_id}")
async def delete_message(message_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    ok = await admin_service.delete_message(db, message_id)
    if not ok: raise HTTPException(404, detail="Message not found")
    return {"ok": True, "detail": "Message deleted"}


@router.get("/settings", response_model=AdminSettingsResponse)
async def get_settings(admin: User = Depends(get_current_admin)):
    return AdminSettingsResponse(
        ai_assistant_enabled=settings.AI_ASSISTANT_ENABLED,
        ai_assistant_username=settings.AI_ASSISTANT_USERNAME,
        ai_model=settings.AI_MODEL,
        ai_system_prompt=settings.AI_SYSTEM_PROMPT,
        app_name=settings.APP_NAME,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        max_upload_size=settings.MAX_UPLOAD_SIZE,
        max_file_size=settings.MAX_FILE_SIZE,
    )


@router.patch("/settings", response_model=AdminSettingsResponse)
async def update_settings(body: AdminSettingsUpdate, admin: User = Depends(get_current_admin)):
    if body.ai_assistant_enabled is not None: settings.AI_ASSISTANT_ENABLED = body.ai_assistant_enabled
    if body.ai_system_prompt is not None: settings.AI_SYSTEM_PROMPT = body.ai_system_prompt
    if body.ai_model is not None: settings.AI_MODEL = body.ai_model
    if body.app_name is not None: settings.APP_NAME = body.app_name
    return AdminSettingsResponse(
        ai_assistant_enabled=settings.AI_ASSISTANT_ENABLED,
        ai_assistant_username=settings.AI_ASSISTANT_USERNAME,
        ai_model=settings.AI_MODEL,
        ai_system_prompt=settings.AI_SYSTEM_PROMPT,
        app_name=settings.APP_NAME,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        max_upload_size=settings.MAX_UPLOAD_SIZE,
        max_file_size=settings.MAX_FILE_SIZE,
    )



