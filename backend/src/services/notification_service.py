from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from ..models.notification import Notification
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def create_notification(
        session: Session,
        task_id: str,
        user_id: str,
        message: str,
        scheduled_time: datetime,
        delivery_method: str = "push"
    ) -> Notification:
        """Create a new notification"""
        import uuid

        notification = Notification(
            id=str(uuid.uuid4()),
            task_id=task_id,
            user_id=user_id,
            message=message,
            scheduled_time=scheduled_time,
            sent_status="pending",
            delivery_method=delivery_method
        )
        session.add(notification)
        # session.commit() is handled by the caller
        return notification

    @staticmethod
    def get_user_notifications(
        session: Session,
        user_id: str,
        sent_status: Optional[str] = None
    ) -> List[Notification]:
        """Get all notifications for a user, optionally filtered by status"""
        query = select(Notification).where(Notification.user_id == user_id)

        if sent_status:
            query = query.where(Notification.sent_status == sent_status)

        query = query.order_by(Notification.scheduled_time.desc())
        return session.exec(query).all()

    @staticmethod
    def get_notification_by_id(
        session: Session,
        user_id: str,
        notification_id: str
    ) -> Optional[Notification]:
        """Get a specific notification by ID for a user"""
        query = select(Notification).where(
            Notification.user_id == user_id,
            Notification.id == notification_id
        )
        return session.exec(query).first()

    @staticmethod
    def update_notification_status(
        session: Session,
        notification_id: str,
        new_status: str,
        sent_at: Optional[datetime] = None
    ) -> Optional[Notification]:
        """Update the status of a notification"""
        query = select(Notification).where(Notification.id == notification_id)
        notification = session.exec(query).first()

        if not notification:
            return None

        notification.sent_status = new_status
        if sent_at:
            notification.sent_at = sent_at

        session.add(notification)
        # session.commit() is handled by the caller
        return notification

    @staticmethod
    def get_scheduled_notifications(
        session: Session,
        current_time: datetime
    ) -> List[Notification]:
        """Get all pending notifications that are scheduled before the current time"""
        query = select(Notification).where(
            Notification.sent_status == "pending",
            Notification.scheduled_time <= current_time
        )
        return session.exec(query).all()

    @staticmethod
    def mark_notification_as_sent(
        session: Session,
        notification_id: str
    ) -> Optional[Notification]:
        """Mark a notification as sent"""
        query = select(Notification).where(Notification.id == notification_id)
        notification = session.exec(query).first()

        if not notification:
            return None

        notification.sent_status = "sent"
        notification.sent_at = datetime.utcnow()

        session.add(notification)
        # session.commit() is handled by the caller
        return notification