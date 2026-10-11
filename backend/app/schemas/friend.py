from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserSearchResult


class FriendRequestCreate(BaseModel):
    receiver_id: int
    message: str | None = None


class FriendRequestResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FriendRequestWithUser(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    message: str | None = None
    sender: UserSearchResult | None = None
    receiver: UserSearchResult | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FriendWithLastMessage(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None
    is_online: bool = False
    is_ai: bool = False
    last_message: str | None = None
    last_message_time: datetime | None = None
    unread_count: int = 0

    model_config = {"from_attributes": True}


class FriendshipResponse(BaseModel):
    id: int
    user_id: int
    friend_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

