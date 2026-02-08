from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
import logging
import json
from pydantic import BaseModel
from src.database.session import get_session
from src.api.deps import verify_user_access
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate
from src.services.task_service import TaskService
from src.utils.validation import validate_task_title
from src.utils.logging import log_error, log_task_operation
from src.exceptions import ValidationErrorException, TaskNotFoundException, TaskAccessDeniedException

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic model for pagination response
class PaginatedTasksResponse(BaseModel):
    tasks: List[TaskRead]
    pagination: dict

@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.
    """
    # Get user_id from the verified JWT token (now verified against URL param)
    user_id = payload.get("userId") or payload.get("sub")

    try:
        # Validate task title
        is_valid, msg = validate_task_title(task_data.title)
        if not is_valid:
            raise ValidationErrorException(msg)

        # Create the task using the service
        task = TaskService.create_task(
            session=session,
            user_id=user_id,
            task_create=task_data
        )
        session.commit()
        session.refresh(task)

        # Log the task creation
        log_task_operation(
            logger=logger,
            operation="create",
            user_id=user_id,
            task_id=task.id,
            details=f"Created task: {task.title}"
        )

        return task
    except ValidationErrorException as ve:
        logger.error(f"Validation error in create_task: {ve.message}")
        raise HTTPException(status_code=ve.status_code, detail=ve.message)
    except Exception as e:
        log_error(logger, e, "create_task", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.get("/tasks", response_model=PaginatedTasksResponse)
async def get_user_tasks(
    status: str = None,
    priority: str = None,
    tag: str = None,
    sort: str = None,
    order: str = "asc",
    page: int = 0,
    limit: int = 100,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for the authenticated user with optional filtering, sorting, and pagination.
    """
    # Get user_id from the verified JWT token (now verified against URL param)
    user_id = payload.get("userId") or payload.get("sub")

    try:
        # Calculate offset from page and limit
        offset = page * limit

        # Get tasks for the user with optional filters
        tasks = TaskService.get_user_tasks(
            session=session, 
            user_id=user_id, 
            status=status, 
            priority=priority, 
            tag=tag,
            sort_field=sort,
            sort_order=order,
            offset=offset,
            limit=limit
        )
        
        # Get total count for pagination metadata
        total_count = TaskService.get_user_tasks_count(
            session=session,
            user_id=user_id,
            status=status,
            priority=priority,
            tag=tag
        )
        
        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit  # Ceiling division
        
        pagination_metadata = {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": total_pages
        }
        
        return PaginatedTasksResponse(tasks=tasks, pagination=pagination_metadata)
    except Exception as e:
        log_error(logger, e, "get_user_tasks", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to get user tasks: {str(e)}")


@router.get("/tasks/search", response_model=List[TaskRead])
async def search_tasks(
    q: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Search tasks for the authenticated user by title, description, or tags.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"GET /tasks/search - Query: '{q}' for user {user_id}")

        # Search tasks for the user
        tasks = TaskService.search_user_tasks(session=session, user_id=user_id, query_str=q)
        return tasks
    except Exception as e:
        log_error(logger, e, "search_tasks", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to search tasks: {str(e)}")


@router.get("/pending-tasks", response_model=dict)
async def get_pending_tasks_count(
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Get the count of pending tasks for the authenticated user.
    Pending tasks are tasks that are not completed.
    """
    # Get user_id from the verified JWT token (now verified against URL param)
    user_id = payload.get("userId") or payload.get("sub")

    logger.info(f"GET /pending-tasks - Request for user {user_id}")

    # Get the count of pending tasks
    pending_count = TaskService.get_pending_tasks_count(session=session, user_id=user_id)

    logger.info(f"GET /pending-tasks - Returning count: {pending_count} for user {user_id}")

    return {"pending": pending_count}

@router.get("/completed-tasks", response_model=dict)
async def get_completed_tasks_count(
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Get the count of completed tasks for the authenticated user.
    Completed tasks are tasks where completed = True.
    """
    # Get user_id from the verified JWT token (now verified against URL param)
    user_id = payload.get("userId") or payload.get("sub")

    logger.info(f"GET /completed-tasks - Request for user {user_id}")

    # Get the count of completed tasks
    completed_count = TaskService.get_completed_tasks_count(session=session, user_id=user_id)

    logger.info(f"GET /completed-tasks - Returning count: {completed_count} for user {user_id}")

    return {"completed": completed_count}


@router.get("/tasks/stats", response_model=dict)
async def get_task_stats(
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Get comprehensive task statistics for the authenticated user.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"GET /tasks/stats - Request for user {user_id}")

        # Get various task counts
        pending_count = TaskService.get_pending_tasks_count(session=session, user_id=user_id)
        completed_count = TaskService.get_completed_tasks_count(session=session, user_id=user_id)

        # Get all tasks to calculate additional stats
        all_tasks = TaskService.get_user_tasks(session=session, user_id=user_id)

        # Count by priority
        priority_counts = {"low": 0, "medium": 0, "high": 0}
        for task in all_tasks:
            if task.priority in priority_counts:
                priority_counts[task.priority] += 1

        # Count by status
        status_counts = {"active": 0, "completed": 0, "archived": 0}
        for task in all_tasks:
            if task.status in status_counts:
                status_counts[task.status] += 1

        stats = {
            "total": len(all_tasks),
            "pending": pending_count,
            "completed": completed_count,
            "by_priority": priority_counts,
            "by_status": status_counts
        }

        logger.info(f"GET /tasks/stats - Returning stats for user {user_id}: {stats}")

        return stats
    except Exception as e:
        log_error(logger, e, "get_task_stats", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to get task stats: {str(e)}")


@router.get("/tasks/{id}", response_model=TaskRead)
async def get_task(
    id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID for the authenticated user.
    """
    # Get user_id from the verified JWT token (now verified against URL param)
    user_id = payload.get("userId") or payload.get("sub")

    try:
        # Get the specific task
        task = TaskService.get_task_by_id(session=session, task_id=id, user_id=user_id)

        if not task:
            raise TaskNotFoundException(id)

        return task
    except TaskNotFoundException as tnfe:
        logger.error(f"Task not found in get_task: {tnfe.message}")
        raise HTTPException(status_code=tnfe.status_code, detail=tnfe.message)
    except Exception as e:
        log_error(logger, e, "get_task", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")


@router.put("/tasks/{id}", response_model=TaskRead)
async def update_task(
    id: str,
    task_update: TaskUpdate,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Update a specific task for the authenticated user.
    """
    # Get user_id from the verified JWT token (now verified against URL param)
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"PUT /tasks/{id} - Request for user {user_id}")

        # Validate task title if it's being updated
        if task_update.title is not None:
            is_valid, msg = validate_task_title(task_update.title)
            if not is_valid:
                raise ValidationErrorException(msg)

        # Update the task
        updated_task = TaskService.update_task(
            session=session,
            task_id=id,
            user_id=user_id,
            task_update=task_update
        )
        if updated_task:
            session.commit()
            session.refresh(updated_task)

        if not updated_task:
            logger.warning(f"PUT /tasks/{id} - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        logger.info(f"PUT /tasks/{id} - Task updated successfully for user {user_id}")

        # Log the task update
        log_task_operation(
            logger=logger,
            operation="update",
            user_id=user_id,
            task_id=updated_task.id,
            details=f"Updated task: {updated_task.title}"
        )

        return updated_task
    except ValidationErrorException as ve:
        logger.error(f"Validation error in update_task: {ve.message}")
        raise HTTPException(status_code=ve.status_code, detail=ve.message)
    except TaskNotFoundException as tnfe:
        logger.error(f"Task not found in update_task: {tnfe.message}")
        raise HTTPException(status_code=tnfe.status_code, detail=tnfe.message)
    except Exception as e:
        log_error(logger, e, "update_task", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task for the authenticated user.
    """
    # Get user_id from the verified JWT token (now verified against URL param)
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"DELETE /tasks/{id} - Request for user {user_id}")

        # Delete the task
        deleted = TaskService.delete_task(session=session, task_id=id, user_id=user_id)
        if deleted:
            session.commit()

        if not deleted:
            logger.warning(f"DELETE /tasks/{id} - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        logger.info(f"DELETE /tasks/{id} - Task deleted successfully for user {user_id}")

        # Log the task deletion
        log_task_operation(
            logger=logger,
            operation="delete",
            user_id=user_id,
            task_id=id,
            details="Task deleted"
        )

        return {"message": "Task deleted successfully"}
    except TaskNotFoundException as tnfe:
        logger.error(f"Task not found in delete_task: {tnfe.message}")
        raise HTTPException(status_code=tnfe.status_code, detail=tnfe.message)
    except Exception as e:
        log_error(logger, e, "delete_task", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


@router.patch("/tasks/{id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a task for the authenticated user.
    """
    # Get user_id from the verified JWT token (now verified against URL param)
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"PATCH /tasks/{id}/complete - Request for user {user_id}")

        # Toggle task completion
        task = TaskService.toggle_completion(session=session, task_id=id, user_id=user_id)
        if task:
            session.commit()
            session.refresh(task)

        if not task:
            logger.warning(f"PATCH /tasks/{id}/complete - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        logger.info(f"PATCH /tasks/{id}/complete - Task completion toggled successfully for user {user_id}")

        # Log the task completion toggle
        log_task_operation(
            logger=logger,
            operation="toggle_completion",
            user_id=user_id,
            task_id=task.id,
            details=f"Toggled completion status to {task.completed}"
        )

        return task
    except TaskNotFoundException as tnfe:
        logger.error(f"Task not found in toggle_task_completion: {tnfe.message}")
        raise HTTPException(status_code=tnfe.status_code, detail=tnfe.message)
    except Exception as e:
        log_error(logger, e, "toggle_task_completion", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to toggle task completion: {str(e)}")


@router.post("/tasks/{id}/complete", response_model=TaskRead)
async def complete_task(
    id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Mark a task as completed and handle recurring task logic.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"POST /tasks/{id}/complete - Request for user {user_id}")

        # Get the task to check if it's a recurring task
        task = TaskService.get_task_by_id(session=session, user_id=user_id, task_id=id)
        if not task:
            logger.warning(f"POST /tasks/{id}/complete - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        # Mark the task as completed
        completed_task = TaskService.complete_task(session=session, user_id=user_id, task_id=id)
        if completed_task:
            session.commit()
            session.refresh(completed_task)

        # Check if the task has a recurrence pattern and create the next occurrence
        if completed_task and completed_task.recurrence_pattern:
            next_task = TaskService.create_next_recurring_task(session=session, completed_task=completed_task)
            if next_task:
                session.commit()
                session.refresh(next_task)
                logger.info(f"Created next recurring task {next_task.id} for user {user_id}")

        logger.info(f"POST /tasks/{id}/complete - Task completed successfully for user {user_id}")

        # Log the task completion
        log_task_operation(
            logger=logger,
            operation="complete",
            user_id=user_id,
            task_id=completed_task.id if completed_task else id,
            details="Task completed"
        )

        return completed_task
    except TaskNotFoundException as tnfe:
        logger.error(f"Task not found in complete_task: {tnfe.message}")
        raise HTTPException(status_code=tnfe.status_code, detail=tnfe.message)
    except Exception as e:
        log_error(logger, e, "complete_task", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to complete task: {str(e)}")


@router.post("/tasks/{id}/schedule-recurrence", response_model=TaskRead)
async def schedule_recurrence(
    id: str,
    task_data: TaskUpdate,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Schedule recurrence for a task.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"POST /tasks/{id}/schedule-recurrence - Request for user {user_id}")

        # Get the task to update
        task = TaskService.get_task_by_id(session=session, user_id=user_id, task_id=id)
        if not task:
            logger.warning(f"POST /tasks/{id}/schedule-recurrence - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        # Update the task with the recurrence pattern
        updated_task = TaskService.update_task(
            session=session,
            task_id=id,
            user_id=user_id,
            task_update=task_data
        )
        if updated_task:
            session.commit()
            session.refresh(updated_task)

        if not updated_task:
            logger.warning(f"POST /tasks/{id}/schedule-recurrence - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        logger.info(f"POST /tasks/{id}/schedule-recurrence - Task updated successfully for user {user_id}")

        # Log the task update
        log_task_operation(
            logger=logger,
            operation="update_recurrence",
            user_id=user_id,
            task_id=updated_task.id,
            details="Scheduled recurrence for task"
        )

        return updated_task
    except TaskNotFoundException as tnfe:
        logger.error(f"Task not found in schedule_recurrence: {tnfe.message}")
        raise HTTPException(status_code=tnfe.status_code, detail=tnfe.message)
    except Exception as e:
        log_error(logger, e, "schedule_recurrence", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to schedule recurrence: {str(e)}")


@router.put("/tasks/{id}/update-recurrence", response_model=TaskRead)
async def update_recurrence(
    id: str,
    task_data: TaskUpdate,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Update recurrence pattern for a task.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"PUT /tasks/{id}/update-recurrence - Request for user {user_id}")

        # Get the task to update
        task = TaskService.get_task_by_id(session=session, user_id=user_id, task_id=id)
        if not task:
            logger.warning(f"PUT /tasks/{id}/update-recurrence - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        # Update the task with the recurrence pattern
        updated_task = TaskService.update_task(
            session=session,
            task_id=id,
            user_id=user_id,
            task_update=task_data
        )
        if updated_task:
            session.commit()
            session.refresh(updated_task)

        if not updated_task:
            logger.warning(f"PUT /tasks/{id}/update-recurrence - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        logger.info(f"PUT /tasks/{id}/update-recurrence - Task recurrence updated successfully for user {user_id}")

        # Log the task update
        log_task_operation(
            logger=logger,
            operation="update_recurrence",
            user_id=user_id,
            task_id=updated_task.id,
            details="Updated recurrence for task"
        )

        return updated_task
    except TaskNotFoundException as tnfe:
        logger.error(f"Task not found in update_recurrence: {tnfe.message}")
        raise HTTPException(status_code=tnfe.status_code, detail=tnfe.message)
    except Exception as e:
        log_error(logger, e, "update_recurrence", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to update recurrence: {str(e)}")


@router.delete("/tasks/{id}/cancel-recurrence", response_model=TaskRead)
async def cancel_recurrence(
    id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Cancel recurrence for a task.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"DELETE /tasks/{id}/cancel-recurrence - Request for user {user_id}")

        # Get the task to update
        task = TaskService.get_task_by_id(session=session, user_id=user_id, task_id=id)
        if not task:
            logger.warning(f"DELETE /tasks/{id}/cancel-recurrence - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        # Update the task to remove the recurrence pattern
        from src.models.task import TaskUpdate
        task_update_data = TaskUpdate(recurrence_pattern=None)

        updated_task = TaskService.update_task(
            session=session,
            task_id=id,
            user_id=user_id,
            task_update=task_update_data
        )
        if updated_task:
            session.commit()
            session.refresh(updated_task)

        if not updated_task:
            logger.warning(f"DELETE /tasks/{id}/cancel-recurrence - Task not found for user {user_id}")
            raise TaskNotFoundException(id)

        logger.info(f"DELETE /tasks/{id}/cancel-recurrence - Task recurrence cancelled successfully for user {user_id}")

        # Log the task update
        log_task_operation(
            logger=logger,
            operation="cancel_recurrence",
            user_id=user_id,
            task_id=updated_task.id,
            details="Cancelled recurrence for task"
        )

        return updated_task
    except TaskNotFoundException as tnfe:
        logger.error(f"Task not found in cancel_recurrence: {tnfe.message}")
        raise HTTPException(status_code=tnfe.status_code, detail=tnfe.message)
    except Exception as e:
        log_error(logger, e, "cancel_recurrence", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to cancel recurrence: {str(e)}")