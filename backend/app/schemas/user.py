from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: str | None = None
    is_online: bool = False
    is_admin: bool = False
    is_banned: bool = False
    last_seen_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSearchResult(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None
    is_online: bool = False

    model_config = {"from_attributes": True}

