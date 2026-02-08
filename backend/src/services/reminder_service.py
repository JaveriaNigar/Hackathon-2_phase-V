import logging
import asyncio
from datetime import datetime, timedelta
from sqlmodel import Session, select, and_
from ..database.session import engine
from ..models.task import Task
from ..models.notification import Notification
from .notification_service import NotificationService

logger = logging.getLogger(__name__)

class ReminderService:
    @staticmethod
    def process_task_reminders(session: Session):
        """
        Check for tasks that are nearing their due date and create notifications.
        We'll look for tasks due in the next 1 hour that don't have a notification yet.
        """
        now = datetime.utcnow()
        one_hour_later = now + timedelta(hours=1)
        
        # 1. Find tasks due up to one hour from now that are not completed
        # This includes tasks that are already past due but haven't been notified
        query = select(Task).where(
            and_(
                Task.due_date != None,
                Task.due_date <= one_hour_later,
                Task.completed == False
            )
        )
        tasks_due_soon = session.exec(query).all()
        
        if tasks_due_soon:
            logger.info(f"Found {len(tasks_due_soon)} tasks due soon")
        
        for task in tasks_due_soon:
            # 2. Check if a notification already exists for this task and this due date
            # We use scheduled_time to match the due_date of the task
            existing_notif_query = select(Notification).where(
                and_(
                    Notification.task_id == task.id,
                    Notification.scheduled_time == task.due_date
                )
            )
            existing_notif = session.exec(existing_notif_query).first()
            
            if not existing_notif:
                # 3. Create a notification
                # Calculate how much time is left
                time_diff = task.due_date - now
                minutes_left = int(time_diff.total_seconds() / 60)
                
                if minutes_left <= 0:
                    message = f"Reminder: Task '{task.title}' is due NOW!"
                else:
                    message = f"Reminder: Task '{task.title}' is due in {minutes_left} minutes!"
                
                NotificationService.create_notification(
                    session=session,
                    task_id=task.id,
                    user_id=task.user_id,
                    message=message,
                    scheduled_time=task.due_date
                )
                logger.info(f"Created reminder for task {task.id}")
        
        # Note: NotificationService.create_notification doesn't commit, 
        # so we commit here
        session.commit()

    @staticmethod
    def process_pending_notifications(session: Session):
        """
        Check for pending notifications that should be 'sent' and mark them as sent.
        For this app, 'sending' might just mean updating the status so the frontend shows them.
        """
        now = datetime.utcnow()
        pending_notifs = NotificationService.get_scheduled_notifications(session, now)
        
        if pending_notifs:
            logger.info(f"Processing {len(pending_notifs)} pending notifications")
            
        for notif in pending_notifs:
            NotificationService.mark_notification_as_sent(session, notif.id)
            logger.info(f"Marked notification {notif.id} as sent")
            
        session.commit()

    @staticmethod
    async def start_reminder_worker():
        """
        Background worker that periodically checks for task reminders and processes notifications.
        """
        logger.info("Starting reminder background worker...")
        while True:
            try:
                # Use a fresh session for each iteration
                with Session(engine) as session:
                    # 1. Create reminders for upcoming tasks
                    ReminderService.process_task_reminders(session)
                    
                    # 2. Process (send) pending notifications
                    ReminderService.process_pending_notifications(session)
                    
            except Exception as e:
                logger.error(f"Error in reminder worker: {e}")
            
            # Wait for 1 minute before checking again
            await asyncio.sleep(60)
