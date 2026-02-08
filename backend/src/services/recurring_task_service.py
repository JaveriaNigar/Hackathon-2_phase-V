"""
Recurring Task Service
Handles the creation of new task occurrences when recurring tasks are completed.
This service would typically run as a separate microservice in a production environment.
For this implementation, it's integrated into the main application.
"""

from sqlmodel import Session
from typing import List
import logging
from datetime import datetime
from ..database.session import get_session
from ..models.task import Task
from ..models.event_log import EventLog
from .task_service import TaskService
from .event_service import EventService

logger = logging.getLogger(__name__)


class RecurringTaskService:
    
    @staticmethod
    def handle_completed_task_event(session: Session, task_id: str, user_id: str):
        """
        Handle a task completion event and create the next occurrence if it's a recurring task.
        """
        # Get the completed task
        completed_task = TaskService.get_task_by_id(session, user_id, task_id)
        
        if not completed_task:
            logger.error(f"Could not find task {task_id} for user {user_id}")
            return None
            
        # Check if the task has a recurrence pattern
        if not completed_task.recurrence_pattern:
            logger.debug(f"Task {task_id} is not a recurring task, skipping next occurrence creation")
            return None
            
        # Create the next occurrence of the recurring task
        next_task = TaskService.create_next_recurring_task(session, completed_task)
        
        if next_task:
            session.commit()
            logger.info(f"Created next occurrence of recurring task: {next_task.id} for user {user_id}")
            
            # Publish event for the new task creation
            EventService.publish_task_event(
                session=session,
                task_id=next_task.id,
                user_id=user_id,
                event_action="created",
                additional_data={
                    "title": next_task.title,
                    "priority": next_task.priority,
                    "is_recurring": True,
                    "parent_task_id": completed_task.id
                }
            )
            
            return next_task
        else:
            logger.info(f"Task {task_id} was recurring but no next occurrence was created (possibly reached end condition)")
            return None
    
    @staticmethod
    def process_recurring_task_creation(completed_task: Task):
        """
        Process the creation of the next occurrence for a completed recurring task.
        This method would typically be called when a task completion event is received.
        """
        with get_session() as session:
            return RecurringTaskService.handle_completed_task_event(
                session, 
                completed_task.id, 
                completed_task.user_id
            )


# In a real event-driven system, this service would subscribe to task completion events
# and automatically trigger the creation of the next occurrence.
# For this implementation, the logic is integrated into the task completion endpoint.