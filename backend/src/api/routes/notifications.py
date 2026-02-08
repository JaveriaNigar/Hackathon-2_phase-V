from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
import logging
from datetime import datetime
from src.database.session import get_session
from src.api.deps import verify_user_access
from src.models.notification import Notification, NotificationCreate, NotificationRead
from src.services.notification_service import NotificationService
from src.utils.logging import log_error
from src.exceptions import ValidationErrorException, TaskNotFoundException, TaskAccessDeniedException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/notifications", response_model=List[NotificationRead])
async def get_user_notifications(
    sent_status: str = None,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Get all notifications for the authenticated user.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"GET /notifications - Request for user {user_id}")

        # Get notifications for the user with optional status filter
        notifications = NotificationService.get_user_notifications(
            session=session,
            user_id=user_id,
            sent_status=sent_status
        )
        return notifications
    except Exception as e:
        log_error(logger, e, "get_user_notifications", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to get user notifications: {str(e)}")


@router.get("/notifications/{id}", response_model=NotificationRead)
async def get_notification(
    id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Get a specific notification by ID for the authenticated user.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"GET /notifications/{id} - Request for user {user_id}")

        # Get the specific notification
        notification = NotificationService.get_notification_by_id(
            session=session,
            user_id=user_id,
            notification_id=id
        )

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        return notification
    except HTTPException:
        raise
    except Exception as e:
        log_error(logger, e, "get_notification", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to get notification: {str(e)}")


@router.put("/notifications/{id}/mark-sent", response_model=NotificationRead)
async def mark_notification_as_sent(
    id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Mark a notification as sent.
    """
    # Get user_id from the verified JWT token
    user_id = payload.get("userId") or payload.get("sub")

    try:
        logger.info(f"PUT /notifications/{id}/mark-sent - Request for user {user_id}")

        # Get the notification to verify it belongs to the user
        notification = NotificationService.get_notification_by_id(
            session=session,
            user_id=user_id,
            notification_id=id
        )

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        # Mark the notification as sent
        updated_notification = NotificationService.mark_notification_as_sent(
            session=session,
            notification_id=id
        )
        
        if updated_notification:
            session.commit()
            session.refresh(updated_notification)

        logger.info(f"PUT /notifications/{id}/mark-sent - Notification marked as sent for user {user_id}")

        return updated_notification
    except HTTPException:
        raise
    except Exception as e:
        log_error(logger, e, "mark_notification_as_sent", user_id)
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as sent: {str(e)}")