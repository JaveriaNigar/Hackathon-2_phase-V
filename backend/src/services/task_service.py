from typing import List, Optional
from sqlmodel import Session, select, func
from ..models.task import Task, TaskBase, TaskCreate
from ..models.event_log import EventLog
from .event_service import EventService
import json
import functools
import time


class TaskService:
    # Simple in-memory cache for frequently accessed data
    _cache = {}
    CACHE_TTL = 300  # 5 minutes TTL for cached items

    @classmethod
    def _get_from_cache(cls, key):
        """Retrieve item from cache if it exists and hasn't expired"""
        if key in cls._cache:
            value, timestamp = cls._cache[key]
            if time.time() - timestamp < cls.CACHE_TTL:
                return value
            else:
                # Remove expired item
                del cls._cache[key]
        return None

    @classmethod
    def _set_in_cache(cls, key, value):
        """Store item in cache with timestamp"""
        cls._cache[key] = (value, time.time())

    @classmethod
    def _invalidate_cache_for_user(cls, user_id):
        """Invalidate all cached data for a specific user"""
        keys_to_remove = []
        for key in cls._cache:
            if key.startswith(f"user_{user_id}_"):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del cls._cache[key]
    @staticmethod
    def create_task(session: Session, user_id: str, task_create: TaskCreate) -> Task:
        """Create a new task for a user"""
        import uuid

        # Generate the ID first
        task_id = str(uuid.uuid4()).replace('-', '')[:32]

        # Process tags - convert list to JSON string if provided
        tags_json = None
        if task_create.tags:
            tags_json = json.dumps(task_create.tags)

        # Process recurrence pattern - convert dict to JSON string if provided
        recurrence_pattern_json = None
        if task_create.recurrence_pattern:
            recurrence_pattern_json = json.dumps(task_create.recurrence_pattern)

        # Create task with all the fields that are known to exist in the database
        # The due_date and priority fields may not exist in the current database schema
        task_data = {
            'id': task_id,
            'user_id': user_id,
            'title': task_create.title,
            'description': task_create.description,
            'completed': False,  # Default to not completed
            'due_date': task_create.due_date,
            'priority': task_create.priority or "medium",  # Use default if not provided
            'status': task_create.status or "active",  # Use default if not provided
            'tags': tags_json,
            'recurrence_pattern': recurrence_pattern_json,
            'next_occurrence': task_create.next_occurrence
        }

        task = Task(**task_data)
        session.add(task)
        
        # Invalidate cache for this user's tasks
        TaskService._invalidate_cache_for_user(user_id)
        
        # Publish event for task creation
        EventService.publish_task_event(
            session=session,
            task_id=task_id,
            user_id=user_id,
            event_action="created",
            additional_data={
                "title": task_create.title,
                "priority": task_create.priority,
                "has_recurrence": bool(task_create.recurrence_pattern)
            }
        )
        
        # session.commit() is now handled by the caller
        return task

    @staticmethod
    def get_user_tasks(session: Session, user_id: str, status: Optional[str] = None, priority: Optional[str] = None, tag: Optional[str] = None, sort_field: Optional[str] = None, sort_order: Optional[str] = "asc", offset: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks for a user, optionally filtered by status, priority, or tag, with optional sorting and pagination"""
        # Create a cache key based on the parameters
        cache_key = f"user_{user_id}_tasks_{status}_{priority}_{tag}_{sort_field}_{sort_order}_{offset}_{limit}"
        
        # Try to get from cache first
        cached_result = TaskService._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        query = select(Task).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)
        if tag:
            # Filter tasks that have the specified tag in their tags JSON array
            query = query.where(Task.tags.like(f'%"{tag}"%'))

        # Apply sorting if specified
        if sort_field:
            # Map string field names to actual model attributes
            if sort_field == "due_date":
                sort_attr = Task.due_date
            elif sort_field == "priority":
                sort_attr = Task.priority
            elif sort_field == "created_at":
                sort_attr = Task.created_at
            elif sort_field == "title":
                sort_attr = Task.title
            elif sort_field == "status":
                sort_attr = Task.status
            else:
                # Default to id if invalid sort field
                sort_attr = Task.id

            # Apply sort direction
            if sort_order.lower() == "desc":
                query = query.order_by(sort_attr.desc())
            else:
                query = query.order_by(sort_attr.asc())

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = session.exec(query).all()
        
        # Cache the result
        TaskService._set_in_cache(cache_key, result)
        
        return result

    @staticmethod
    def get_user_tasks_count(session: Session, user_id: str, status: Optional[str] = None, priority: Optional[str] = None, tag: Optional[str] = None) -> int:
        """Get the count of tasks for a user with optional filters"""
        query = select(func.count(Task.id)).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)
        if tag:
            # Filter tasks that have the specified tag in their tags JSON array
            query = query.where(Task.tags.like(f'%"{tag}"%'))

        return session.exec(query).one()

    @staticmethod
    def get_task_by_id(session: Session, user_id: str, task_id: str) -> Optional[Task]:
        """Get a specific task by ID for a user"""
        # Create a cache key based on the parameters
        cache_key = f"user_{user_id}_task_{task_id}"
        
        # Try to get from cache first
        cached_result = TaskService._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        query = select(Task).where(Task.user_id == user_id, Task.id == task_id)
        task = session.exec(query).first()
        
        # Cache the result if found
        if task:
            TaskService._set_in_cache(cache_key, task)
        
        return task

    @staticmethod
    def delete_task(session: Session, user_id: str, task_id: str) -> bool:
        """Delete a specific task for a user"""
        task = TaskService.get_task_by_id(session, user_id, task_id)
        if not task:
            return False

        session.delete(task)
        
        # Invalidate cache for this user's tasks
        TaskService._invalidate_cache_for_user(user_id)
        
        # session.commit() is now handled by the caller
        return True

    @staticmethod
    def complete_task(session: Session, user_id: str, task_id: str) -> Optional[Task]:
        """Mark a task as completed"""
        task = TaskService.get_task_by_id(session, user_id, task_id)
        if not task:
            return None

        task.completed = True
        task.updated_at = func.now()
        session.add(task)
        
        # Invalidate cache for this user's tasks
        TaskService._invalidate_cache_for_user(user_id)
        
        # Publish event for task completion
        EventService.publish_task_event(
            session=session,
            task_id=task_id,
            user_id=user_id,
            event_action="completed",
            additional_data={
                "title": task.title,
                "was_recurring": bool(task.recurrence_pattern)
            }
        )
        
        # session.commit() is now handled by the caller
        return task

    @staticmethod
    def toggle_completion(session: Session, task_id: str, user_id: str) -> Optional[Task]:
        """Toggle the completion status of a task"""
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(query).first()

        if not task:
            return None

        task.completed = not task.completed
        task.updated_at = func.now()
        session.add(task)
        # session.commit() is now handled by the caller
        return task

    @staticmethod
    def update_task(session: Session, task_id: str, user_id: str, task_update) -> Optional[Task]:
        """Update a specific task for a user"""
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(query).first()

        if not task:
            return None

        # Store original values for the event
        original_title = task.title
        original_priority = task.priority
        original_tags = task.tags
        original_recurrence = task.recurrence_pattern

        # Update task attributes with values from task_update
        # Convert the Pydantic model to a dictionary
        update_data = task_update.model_dump(exclude_unset=True)
        
        # Handle tags - convert list to JSON string if provided
        if 'tags' in update_data and update_data['tags'] is not None:
            task.tags = json.dumps(update_data['tags'])
            del update_data['tags']  # Remove from update_data to avoid direct assignment
        
        # Handle recurrence_pattern - convert dict to JSON string if provided
        if 'recurrence_pattern' in update_data and update_data['recurrence_pattern'] is not None:
            task.recurrence_pattern = json.dumps(update_data['recurrence_pattern'])
            del update_data['recurrence_pattern']  # Remove from update_data to avoid direct assignment
        
        # Update other attributes
        for key, value in update_data.items():
            setattr(task, key, value)

        task.updated_at = func.now()
        session.add(task)
        
        # Invalidate cache for this specific task
        TaskService._invalidate_cache_for_user(user_id)
        
        # Publish event for task update
        EventService.publish_task_event(
            session=session,
            task_id=task_id,
            user_id=user_id,
            event_action="updated",
            additional_data={
                "original_title": original_title,
                "original_priority": original_priority,
                "updated_fields": list(update_data.keys()),
                "has_recurrence": bool(task.recurrence_pattern)
            }
        )
        
        # session.commit() is now handled by the caller
        return task

    @staticmethod
    def get_pending_tasks_count(session: Session, user_id: str) -> int:
        """Get the count of pending tasks for a user"""
        query = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.completed == False
        )
        return session.exec(query).one()

    @staticmethod
    def get_completed_tasks_count(session: Session, user_id: str) -> int:
        """Get the count of completed tasks for a user"""
        query = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.completed == True
        )
        return session.exec(query).one()

    @staticmethod
    def search_user_tasks(session: Session, user_id: str, query_str: str) -> List[Task]:
        """Search tasks for a user by title, description, or tags (case-insensitive)"""
        from sqlalchemy import or_
        
        statement = select(Task).where(
            Task.user_id == user_id,
            or_(
                Task.title.ilike(f"%{query_str}%"),
                Task.description.ilike(f"%{query_str}%"),
                Task.tags.like(f'%"{query_str}"%')  # Search for tags that match the query
            )
        )
        return session.exec(statement).all()

    @staticmethod
    def resolve_task(session: Session, user_id: str, identifier: str):
        """
        Resolve a task by ID or Title.
        Returns (task, status) where status is 'FOUND', 'AMBIGUOUS', or 'NOT_FOUND'.
        """
        if not identifier:
            return None, "NOT_FOUND"

        # Normalization: Trim whitespace and strip surrounding quotes/brackets
        identifier = identifier.strip().strip('"').strip("'").strip('[]').strip('()').strip('{}').strip()

        if not identifier:
            return None, "NOT_FOUND"
        # IDs are 32 chars long (without hyphens) in this project
        if len(identifier) >= 30:
            task = TaskService.get_task_by_id(session, user_id, identifier)
            if task:
                return task, "FOUND"

        # 2. Try Exact Title match
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.title.ilike(identifier)
        )
        exact_matches = session.exec(statement).all()
        if len(exact_matches) == 1:
            return exact_matches[0], "FOUND"
        elif len(exact_matches) > 1:
            return None, "AMBIGUOUS"

        # 3. Try Partial Title match
        statement = select(Task).where(
            Task.user_id == user_id,
            Task.title.ilike(f"%{identifier}%")
        )
        partial_matches = session.exec(statement).all()
        if len(partial_matches) == 1:
            return partial_matches[0], "FOUND"
        elif len(partial_matches) > 1:
            return None, "AMBIGUOUS"

        return None, "NOT_FOUND"

    @staticmethod
    def create_next_recurring_task(session: Session, completed_task: Task) -> Optional[Task]:
        """
        Creates the next occurrence of a recurring task based on the recurrence pattern.
        """
        import uuid
        from datetime import datetime, timedelta
        import json

        # Check if the task has a recurrence pattern
        if not completed_task.recurrence_pattern:
            return None

        # Parse the recurrence pattern
        try:
            pattern = json.loads(completed_task.recurrence_pattern)
        except (json.JSONDecodeError, TypeError):
            return None

        # Determine the next occurrence date based on the pattern
        current_due_date = completed_task.due_date or datetime.utcnow()
        next_due_date = None

        recurrence_type = pattern.get('type')
        interval = pattern.get('interval', 1)

        if recurrence_type == 'daily':
            next_due_date = current_due_date + timedelta(days=interval)
        elif recurrence_type == 'weekly':
            next_due_date = current_due_date + timedelta(weeks=interval)
        elif recurrence_type == 'monthly':
            # Simple monthly calculation (adding ~30 days)
            next_due_date = current_due_date + timedelta(days=30 * interval)
        elif recurrence_type == 'yearly':
            # Simple yearly calculation (adding 365 days)
            next_due_date = current_due_date + timedelta(days=365 * interval)
        else:
            # Unsupported recurrence type
            return None

        # Check if the recurrence should end
        end_condition = pattern.get('end_condition')
        if end_condition:
            end_type = end_condition.get('type')
            end_value = end_condition.get('value')

            if end_type == 'after_n_occurrences':
                # This would require tracking the number of occurrences
                # For simplicity, we'll skip this check in this implementation
                pass
            elif end_type == 'on_date':
                end_date = datetime.fromisoformat(end_value.replace('Z', '+00:00'))
                if next_due_date > end_date:
                    return None

        # Create a new task with the same properties as the completed task
        new_task_id = str(uuid.uuid4()).replace('-', '')[:32]

        # Process tags - convert from stored JSON string back to list then to JSON string for new task
        tags_json = completed_task.tags

        # Process recurrence pattern - reuse the same pattern for the new task
        recurrence_pattern_json = completed_task.recurrence_pattern

        new_task_data = {
            'id': new_task_id,
            'user_id': completed_task.user_id,
            'title': completed_task.title,
            'description': completed_task.description,
            'completed': False,  # New task is not completed
            'due_date': next_due_date,
            'priority': completed_task.priority,
            'status': 'active',
            'tags': tags_json,
            'recurrence_pattern': recurrence_pattern_json,
            'next_occurrence': None  # Will be calculated when this new task is completed
        }

        new_task = Task(**new_task_data)
        session.add(new_task)
        
        # Publish event for recurring task creation
        EventService.publish_task_event(
            session=session,
            task_id=new_task_id,
            user_id=completed_task.user_id,
            event_action="created",
            additional_data={
                "title": completed_task.title,
                "priority": completed_task.priority,
                "is_recurring": True,
                "parent_task_id": completed_task.id
            }
        )
        
        # session.commit() is now handled by the caller
        return new_task