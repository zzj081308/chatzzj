from datetime import datetime
from pydantic import BaseModel


class AppealSubmit(BaseModel):
    username: str
    password: str
    reason: str


class AppealResponse(BaseModel):
    id: int
    user_id: int
    username: str
    email: str
    reason: str
    status: str
    admin_response: str | None = None
    admin_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminAppealAction(BaseModel):
    response: str | None = None

