from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Friendship(Base):
    __tablename__ = "friendships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uq_friendship_pair"),
        CheckConstraint("user_id < friend_id", name="ck_user_less_than_friend"),
    )

