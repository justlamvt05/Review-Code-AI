from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from modules.notifications.models import NotificationType


class NotificationResponse(BaseModel):
    id: UUID
    recipient_id: UUID
    sender_id: UUID | None
    type: NotificationType
    title: str
    message: str
    reference_id: UUID | None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnreadCountResponse(BaseModel):
    count: int
