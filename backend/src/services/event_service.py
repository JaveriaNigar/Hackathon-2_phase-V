from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
import json
import logging

from ..models.event_log import EventLog

logger = logging.getLogger(__name__)


class EventService:
    @staticmethod
    def create_event(
        session: Session,
        event_type: str,
        payload: dict,
        source_service: str,
        correlation_id: Optional[str] = None
    ) -> EventLog:
        """Create a new event log entry"""
        import uuid

        event_log = EventLog(
            id=str(uuid.uuid4()),
            event_type=event_type,
            payload=json.dumps(payload),
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id or str(uuid.uuid4()),
            source_service=source_service
        )
        session.add(event_log)
        # session.commit() is handled by the caller
        return event_log

    @staticmethod
    def get_events_by_type(
        session: Session,
        event_type: str,
        limit: int = 100
    ) -> List[EventLog]:
        """Get events by type, ordered by timestamp descending"""
        query = select(EventLog).where(EventLog.event_type == event_type)
        query = query.order_by(EventLog.timestamp.desc()).limit(limit)
        return session.exec(query).all()

    @staticmethod
    def get_events_by_correlation_id(
        session: Session,
        correlation_id: str
    ) -> List[EventLog]:
        """Get events by correlation ID"""
        query = select(EventLog).where(EventLog.correlation_id == correlation_id)
        return session.exec(query).all()

    @staticmethod
    def get_recent_events(
        session: Session,
        hours: int = 24
    ) -> List[EventLog]:
        """Get events from the last N hours"""
        from sqlalchemy import and_, func
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = select(EventLog).where(EventLog.timestamp >= cutoff_time)
        query = query.order_by(EventLog.timestamp.desc())
        return session.exec(query).all()

    @staticmethod
    def publish_task_event(
        session: Session,
        task_id: str,
        user_id: str,
        event_action: str,  # "created", "updated", "completed", "deleted"
        additional_data: Optional[dict] = None
    ):
        """Publish a task-related event to the event log"""
        event_type = f"task.{event_action}"
        payload = {
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": event_action
        }
        
        if additional_data:
            payload.update(additional_data)

        event = EventService.create_event(
            session=session,
            event_type=event_type,
            payload=payload,
            source_service="task_service"
        )
        
        return event