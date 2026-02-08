from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import json


class EventLogBase(SQLModel):
    event_type: str = Field(max_length=100)
    payload: str  # Store as JSON string
    correlation_id: Optional[str] = Field(default=None, max_length=100)
    source_service: str = Field(max_length=100)


class EventLog(EventLogBase, table=True):
    __tablename__ = "event_logs"

    id: str = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Pydantic models for API requests/responses
class EventLogCreate(EventLogBase):
    pass


class EventLogRead(EventLogBase):
    id: str
    timestamp: datetime
    
    def dict(self, *args, **kwargs):
        # Override dict to parse JSON payload
        data = super().dict(*args, **kwargs)
        try:
            data['payload'] = json.loads(data['payload']) if data['payload'] else {}
        except (json.JSONDecodeError, TypeError):
            data['payload'] = {}
        return data