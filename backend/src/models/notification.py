from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class NotificationBase(SQLModel):
    task_id: str = Field(index=True)
    user_id: str = Field(index=True)
    message: str
    scheduled_time: datetime
    sent_status: str = Field(default="pending", max_length=20)
    delivery_method: str = Field(default="push", max_length=20)


class Notification(NotificationBase, table=True):
    __tablename__ = "notifications"

    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)


# Pydantic models for API requests/responses
class NotificationCreate(NotificationBase):
    pass


class NotificationRead(NotificationBase):
    id: str
    created_at: datetime
    sent_at: Optional[datetime]