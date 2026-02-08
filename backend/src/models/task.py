from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = Field(default=None, index=True)  # Added index for performance
    priority: Optional[str] = Field(default="medium", max_length=20, index=True)  # Changed default to "medium", added index
    status: Optional[str] = Field(default="active", max_length=20, index=True)  # Added status field with index
    tags: Optional[str] = Field(default=None, max_length=1000, index=True)  # Store tags as JSON string with index
    recurrence_pattern: Optional[str] = Field(default=None, max_length=1000)  # Store recurrence pattern as JSON string
    next_occurrence: Optional[datetime] = Field(default=None)  # For recurring tasks


def generate_task_id():
    import uuid
    return str(uuid.uuid4()).replace('-', '')[:32]


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=generate_task_id, primary_key=True, sa_column_kwargs={"default": None})
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


import json
from pydantic import field_validator, computed_field
from typing import Union

# Pydantic models for API requests/responses
class TaskCreate(TaskBase):
    tags: Optional[List[str]] = None  # Accept tags as list, store as JSON string
    recurrence_pattern: Optional[Union[Dict[str, Any], str]] = None  # Accept recurrence pattern as dict or JSON string, store as JSON string


class TaskRead(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[str]] = None  # Return tags as list
    recurrence_pattern: Optional[Dict[str, Any]] = None  # Return recurrence pattern as dict

    @field_validator('recurrence_pattern', mode='before')
    @classmethod
    def parse_recurrence_pattern(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (TypeError, ValueError):
                return None
        return v

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (TypeError, ValueError):
                return []
        return v


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None  # Accept tags as list, store as JSON string
    recurrence_pattern: Optional[Union[Dict[str, Any], str]] = None  # Accept recurrence pattern as dict or JSON string, store as JSON string

