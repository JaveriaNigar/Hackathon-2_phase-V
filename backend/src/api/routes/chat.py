from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from ...agents.todo_agent import TodoAgent
from ...tools.task_tools import TaskTools
from ...api.deps import verify_user_access
from ...database.session import get_session
from ...utils.validation import validate_task_title
from ...utils.logging import log_agent_interaction, log_error
from ...exceptions import ValidationErrorException, DatabaseOperationException
from sqlmodel import Session, select, desc
import logging
import os

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: List[ToolCall] = []


class ConversationRead(BaseModel):
    id: UUID
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MessageRead(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime


# Removed local get_db to use src.database.session.get_session


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Main chat endpoint that processes natural language and returns AI response
    along with any tool calls that need to be executed.
    """
    try:
        # Validate input
        if not request.message or not request.message.strip():
            raise ValidationErrorException("Message cannot be empty")

        # Get database URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise HTTPException(status_code=500, detail="DATABASE_URL not configured")

        if request.conversation_id:
            try:
                conv_uuid = UUID(request.conversation_id)
            except ValueError:
                # Handle non-UUID temp IDs
                conv_uuid = None
        else:
            conv_uuid = None

        from ...models.conversation import Conversation
        from ...models.message import Message as DBMessage

        # Ensure conversation exists or create one if requested/needed
        if conv_uuid:
            conversation = session.get(Conversation, conv_uuid)
            if not conversation or conversation.user_id != user_id:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            conv_uuid = conversation.id

        # Initialize the agent
        agent = TodoAgent(database_url=database_url)

        # Save user message
        user_msg = DBMessage(
            user_id=user_id,
            conversation_id=conv_uuid,
            role="user",
            content=request.message
        )
        session.add(user_msg)
        session.commit()

        # Process the user message with the agent
        result = agent.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=str(conv_uuid)
        )

        # Update conversation title if new and agent provided one
        if not conversation.title and result.get("chat_title"):
            conversation.title = result.get("chat_title")
            session.add(conversation)
            session.commit()

        # EXECUTE TOOLS - Using TaskService directly to avoid circular dependency and HTTP overhead
        from ...services.task_service import TaskService
        from ...models.task import TaskCreate, TaskUpdate

        execution_errors = []
        action_performed = False

        for tool_call in result.get("tool_calls", []):
            name = tool_call.get("name")
            args = tool_call.get("arguments", {})

            try:
                if name == "add_task":
                    title = args.get("title")
                    is_valid, msg = validate_task_title(title) if title else (False, "Task title is required")
                    if not is_valid:
                        execution_errors.append(f"add_task failed: {msg}")
                        continue

                    task_create_data = TaskCreate(
                        title=title,
                        description=args.get("description", ""),
                        priority=args.get("priority", "medium"),
                        due_date=args.get("due_date"),
                        tags=args.get("tags", []),
                        recurrence_pattern=args.get("recurrence_pattern")
                    )
                    
                    TaskService.create_task(session=session, user_id=user_id, task_create=task_create_data)
                    logger.info(f"Successfully created task via service: {title}")
                    action_performed = True

                elif name in ["delete_task", "complete_task", "update_task"]:
                    # These tools all need identifier resolution (ID or Title)
                    identifier = args.get("task_id") or args.get("title") or args.get("old_title")
                    if not identifier:
                        execution_errors.append(f"{name} failed: Task ID or title is required")
                        continue

                    task, status = TaskService.resolve_task(session, user_id, identifier)
                    if status != "FOUND":
                        execution_errors.append(f"{name} failed: Task '{identifier}' not found ({status})")
                        continue

                    if name == "delete_task":
                        TaskService.delete_task(session=session, user_id=user_id, task_id=task.id)
                        logger.info(f"Successfully deleted task: {task.id}")
                        action_performed = True

                    elif name == "complete_task":
                        completed_task = TaskService.complete_task(session=session, user_id=user_id, task_id=task.id)
                        if completed_task:
                            # Handle recurring tasks logic as in tasks.py
                            if completed_task.recurrence_pattern:
                                TaskService.create_next_recurring_task(session=session, completed_task=completed_task)
                            logger.info(f"Successfully completed task: {task.id}")
                            action_performed = True

                    elif name == "update_task":
                        new_title = args.get("new_title") or args.get("title")
                        if new_title and new_title != task.title:
                            is_valid, msg = validate_task_title(new_title)
                            if not is_valid:
                                execution_errors.append(f"update_task failed: {msg}")
                                continue
                        
                        task_update_data = TaskUpdate(
                            title=new_title,
                            description=args.get("description"),
                            completed=args.get("completed"),
                            priority=args.get("priority"),
                            due_date=args.get("due_date"),
                            tags=args.get("tags")
                        )
                        TaskService.update_task(session=session, task_id=task.id, user_id=user_id, task_update=task_update_data)
                        logger.info(f"Successfully updated task: {task.id}")
                        action_performed = True

                elif name == "list_tasks":
                    # Tool call logic for the UI signal
                    logger.info(f"list_tasks requested for user {user_id}")
                    action_performed = True

                elif name == "search_tasks":
                    query = args.get("q") or args.get("query")
                    status = args.get("status")
                    priority = args.get("priority")

                    # At least one parameter should be provided
                    if not query and not status and not priority:
                        execution_errors.append("search_tasks failed: At least one parameter (query, status, or priority) is required")
                        continue

                    # Search tasks using the service
                    if query and not status and not priority:
                        # Use keyword search if only query is provided
                        tasks = TaskService.search_user_tasks(
                            session=session,
                            user_id=user_id,
                            query_str=query
                        )
                    else:
                        # Use get_user_tasks with filters if status or priority are provided
                        tasks = TaskService.get_user_tasks(
                            session=session,
                            user_id=user_id,
                            status=status,
                            priority=priority
                        )
                        
                        # If query is also provided, further filter the results
                        if query:
                            query_lower = query.lower()
                            tasks = [t for t in tasks if query_lower in t.title.lower() or (t.description and query_lower in t.description.lower())]

                    logger.info(f"Searched with query='{query}', status='{status}', priority='{priority}' and found {len(tasks)} tasks for user {user_id}")
                    action_performed = True

                elif name == "sort_tasks":
                    field = args.get("field", "created_at")  # Default sort field
                    order = args.get("order", "asc")  # Default sort order
                    
                    # Validate sort field and order
                    valid_fields = ["title", "created_at", "updated_at", "due_date", "priority", "status"]
                    if field not in valid_fields:
                        field = "created_at"  # fallback to default
                    
                    if order not in ["asc", "desc"]:
                        order = "asc"  # fallback to default

                    # Get sorted tasks using the service
                    tasks = TaskService.get_user_tasks(
                        session=session,
                        user_id=user_id,
                        sort_field=field,
                        sort_order=order
                    )
                    logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}, sorted by {field} in {order} order")
                    action_performed = True

                logger.info(f"Successfully processed tool call: {name}")
            except Exception as tool_err:
                error_msg = f"Error executing {name}: {str(tool_err)}"
                logger.error(error_msg)
                execution_errors.append(error_msg)

        # CENTRALIZED COMMIT - Avoid double commits/conflicts
        if action_performed:
            session.commit()
            session.flush() # Ensure all changes are flushed to DB before message saving
        # Update response text if there were errors
        final_response_text = result.get("response", "I processed your request.")
        if execution_errors:
            final_response_text += "\n\n(Note: Some actions encountered errors: " + "; ".join(execution_errors) + ")"

        # Save assistant response AFTER tools are executed
        assistant_msg = DBMessage(
            user_id=user_id,
            conversation_id=conv_uuid,
            role="assistant",
            content=final_response_text
        )
        session.add(assistant_msg)
        session.commit()

        # Log the agent interaction
        log_agent_interaction(
            logger=logger,
            user_id=user_id,
            conversation_id=str(conv_uuid),
            input_text=request.message,
            response_text=final_response_text,
            tools_used=[tc.get("name") for tc in result.get("tool_calls", [])]
        )

        # Format the response
        response = ChatResponse(
            conversation_id=str(conv_uuid),
            response=final_response_text,
            tool_calls=result.get("tool_calls", [])
        )

        return response
    except ValidationErrorException as ve:
        logger.error(f"Validation error in chat endpoint: {ve.message}")
        raise HTTPException(status_code=ve.status_code, detail=ve.message)
    except HTTPException:
        raise
    except Exception as e:
        log_error(logger, e, "chat_endpoint", user_id)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.get("/conversations", response_model=List[ConversationRead])
async def list_conversations(
    user_id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    from ...models.conversation import Conversation
    
    statement = select(Conversation).where(Conversation.user_id == user_id).order_by(desc(Conversation.updated_at))
    results = session.exec(statement).all()
    return results


@router.post("/conversations", response_model=ConversationRead)
async def create_conversation(
    user_id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    from ...models.conversation import Conversation
    
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageRead])
async def list_conversation_messages(
    user_id: str,
    conversation_id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    from ...models.message import Message as DBMessage
    
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    statement = select(DBMessage).where(
        DBMessage.user_id == user_id,
        DBMessage.conversation_id == conv_uuid
    ).order_by(DBMessage.created_at)
    
    results = session.exec(statement).all()
    return results


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str,
    payload: dict = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    from ...models.conversation import Conversation
    from ...models.message import Message as DBMessage
    
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    # Use explicit join or check to ensure user owns it
    conversation = session.get(Conversation, conv_uuid)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete all messages first (if no cascade)
    statement = select(DBMessage).where(DBMessage.conversation_id == conv_uuid)
    messages = session.exec(statement).all()
    for msg in messages:
        session.delete(msg)

    session.delete(conversation)
    session.commit()
    
    return {"success": True, "message": "Conversation deleted"}

# Note: Task management endpoints...