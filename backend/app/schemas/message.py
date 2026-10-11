from datetime import datetime
from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message_type: str
    content: str | None = None
    image_url: str | None = None
    file_url: str | None = None
    file_name: str | None = None
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageHistoryResponse(BaseModel):
    messages: list[MessageResponse]
    has_more: bool
    next_cursor: int | None = None

