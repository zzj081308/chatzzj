from datetime import datetime
from pydantic import BaseModel

class AdminDashboard(BaseModel):
    total_users: int = 0
    total_messages: int = 0
    online_users: int = 0
    banned_users: int = 0
    admin_users: int = 0
    total_friendships: int = 0
    pending_requests: int = 0
    pending_appeals: int = 0
    ai_enabled: bool = True
    messages_last_24h: int = 0
    new_users_last_24h: int = 0

class AdminUserResponse(BaseModel):
    id: int; username: str; email: str
    avatar_url: str | None = None
    is_online: bool = False; is_ai: bool = False
    is_admin: bool = False; is_banned: bool = False
    last_seen_at: datetime | None = None; created_at: datetime
    model_config = {"from_attributes": True}

class AdminMessageResponse(BaseModel):
    id: int; sender_id: int; receiver_id: int
    message_type: str; content: str | None = None
    image_url: str | None = None; file_url: str | None = None
    file_name: str | None = None; is_read: bool = False
    created_at: datetime
    sender_username: str | None = None; receiver_username: str | None = None
    model_config = {"from_attributes": True}

class AdminSettingsResponse(BaseModel):
    ai_assistant_enabled: bool; ai_assistant_username: str
    ai_model: str; ai_system_prompt: str; app_name: str
    access_token_expire_minutes: int; refresh_token_expire_days: int
    max_upload_size: int; max_file_size: int

class AdminSettingsUpdate(BaseModel):
    ai_assistant_enabled: bool | None = None
    ai_system_prompt: str | None = None
    ai_model: str | None = None
    app_name: str | None = None

class AdminMessageListResponse(BaseModel):
    messages: list[AdminMessageResponse]; total: int; page: int; page_size: int

class AdminUserListResponse(BaseModel):
    users: list[AdminUserResponse]; total: int; page: int; page_size: int

