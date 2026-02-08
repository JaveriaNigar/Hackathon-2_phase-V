import os
import re
from typing import Dict, Any, List
from google.generativeai import configure, GenerativeModel
from ..tools.task_tools import TaskTools
from dotenv import load_dotenv

# Load environment variables explicitly from backend/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=env_path, override=True)

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
configure(api_key=api_key)

class TodoAgent:
    def __init__(self, database_url: str):
        self.task_tools = TaskTools(database_url)
        self.model, self.model_name = self._initialize_model()
        self.system_prompt = """
        You are a friendly personal assistant who helps users manage their tasks.
        Your responses should sound like a real person talking, not like a robot or system.
        
        MANDATORY BEHAVIOR:

        1. NATURAL CONVERSATION (CRITICAL)
        - Talk like a real person, not a computer system
        - Keep responses short and friendly
        - Never use technical terms like "database", "record", "entity", "operation", etc.
        - Never tell users about backend processes or system functions
        - Use casual, friendly language
        - Be helpful and encouraging
        - Use emojis occasionally to be warm and friendly

        2. SMART ORCHESTRATION (CRITICAL)
        - **"high priority" / "low priority"** → Use `search_tasks(priority="high/low")`.
        - **"due today" / "today"** → Use `search_tasks(query="due today")`.
        - **"pending" / "incomplete" / "khatam nahi hua"** → Use `list_tasks(status="pending")`.
        - **"completed" / "done" / "khatam ho gaya"** → Use `list_tasks(status="completed")`.
        - **"latest" / "recent" / "naya"** → Use `sort_tasks(field="created_at", order="desc")`.
        - **"urgent"** → Use `search_tasks(priority="high")` and mention deadlines.
        - **"alphabetical" / "A to Z"** → Use `sort_tasks(field="title", order="asc")`.
        - **"due date"** → Use `sort_tasks(field="due_date", order="asc")`.

        3. RESPONSE STYLE
        - Instead of "Task has been successfully created", say "Done! I've added your task."
        - Instead of "No records found in database", say "I couldn't find any tasks yet."
        - Instead of "Operation completed", say "All set!"
        - Instead of "Processing your request", say "Sure thing!"
        - Sound like a helpful friend, not a computer program
        
        4. TASK ACCESS & MANAGEMENT
        - You can **add**, **update**, **delete**, **mark complete**, **list**, **search**, and **sort** tasks
        - Always act on user requests immediately when possible
        - Never say things like "request processed" or "action completed"
        - Say things like "Got it!" or "Done!" instead

        5. FOCUS ON ACTIONS, NOT QUESTIONS
        - If the user asks for a filter or sort, USE THE TOOL. Don't just list what's in context if a specific filter is asked.

        6. FRIENDLY CHAT
        - Respond in **natural, conversational tone** (Roman Urdu or English)
        - Example: "Sure! Here are your high priority tasks. 🙂"

        7. LISTING TASKS
        - When you call a tool like `list_tasks`, `search_tasks`, or `sort_tasks`, you must **summarize the result in your text response** for the user.
        - NEVER show UUIDs. Just use titles.

        8. TOOL USAGE
        - add_task(title)
        - delete_task(task_id)
        - complete_task(task_id)
        - update_task(task_id, title)
        - list_tasks(status: "all"|"pending"|"completed")
        - search_tasks(query: string, status: string, priority: string)
        - sort_tasks(field: "due_date"|"created_at"|"priority"|"title", order: "asc"|"desc")

    EXAMPLES:
    User: "show high priority tasks"
    Tool call: search_tasks(priority="high")
    Agent: "Here are your high priority tasks: [titles from result] 🙂"

    User: "tasks due today"
    Tool call: search_tasks(query="due today")
    Agent: "These are due today: [titles]"

    User: "show pending tasks"
    Tool call: list_tasks(status="pending")
    Agent: "Here are your pending tasks: [titles]"

    User: "sort by latest"
    Tool call: sort_tasks(field="created_at", order="desc")
    Agent: "Sorted by newest for you! 🙂"

    User: "urgent tasks dikhao"
    Tool call: search_tasks(priority="high")
    Agent: "These are your urgent tasks: [titles]"
    """

    def _get_best_model(self) -> str:
        # Prioritized list of models to try
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-2.5-flash',
            'gemini-2.0-flash-lite',
            'gemini-1.5-flash'
        ]
        return models_to_try[0]
        
    def _initialize_model(self):
        """Try to initialize a working model from a list of candidates."""
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-2.5-flash',
            'gemini-1.5-flash',
            'gemini-pro'
        ]
        
        for model_name in models_to_try:
            try:
                model = GenerativeModel(model_name)
                # Test with a lightweight call
                model.count_tokens("test")
                return model, model_name
            except Exception as e:
                # print(f"DEBUG: Failed to init {model_name}: {e}")
                continue
        
        # Fallback to a default if all fail
        return GenerativeModel('gemini-2.0-flash'), 'gemini-2.0-flash'

    def process_message(self, user_id: str, message: str, conversation_id: str = None) -> Dict[str, Any]:
        import re  # Import at the beginning of the function

        try:
            # Detect simple greetings early to skip AI/DB ONLY IF no task verbs are present
            greetings = [r'^hi$', r'^hello$', r'^hey$', r'^asalam\s*o\s*alaikum$', r'^aoa$', r'^salam$']
            task_verbs = ['add', 'create', 'delete', 'remove', 'update', 'edit', 'complete', 'finish', 'list', 'show']

            message_clean = message.lower().strip().replace('?', '').replace('!', '').replace('.', '')
            has_task_verb = any(verb in message_clean for verb in task_verbs)
            is_pure_greeting = any(re.match(g, message_clean) for g in greetings)

            if is_pure_greeting and not has_task_verb:
                return {
                    "response": "Hi 🙂 How can I help you?",
                    "tool_calls": [],
                    "conversation_id": conversation_id
                }

            # Fetch current tasks to provide context
            try:
                tasks_result = self.task_tools.list_tasks(user_id)
                tasks_context = "No tasks currently."
                tasks_context_clean = "No tasks currently." # For user display
                
                if tasks_result.get("success") and tasks_result.get("tasks"):
                    tasks_list = tasks_result["tasks"]
                    # Format tasks for the AI to understand, but keeping ID internal only
                    # The AI needs ID to perform actions.
                    tasks_context = "\n".join([f"- ID: {t['id']} | Title: {t['title']} | Completed: {t['completed']}" for t in tasks_list])
                    
                    # Clean format for user display (Hidden IDs)
                    tasks_context_clean = "\n".join([f"- {t['title']} ({'Completed' if t['completed'] else 'Pending'})" for t in tasks_list])
            except:
                tasks_context = "Could not fetch tasks."
                tasks_context_clean = "Could not fetch tasks."

            prompt = f"""
            {self.system_prompt}

            USER MESSAGE: "{message}"

            ### USER'S CURRENT TASKS:
            {tasks_context_clean}

            ### CORE INSTRUCTIONS:
            1. Respond naturally to greetings, casual chat, and task-related messages.
            2. Be friendly, concise, and helpful. Use simple, human-like language (English or Roman Urdu).
            3. **CRITICAL: NEVER SHOW TASK IDs TO THE USER.**
               - When listing tasks, only show the **Title** and **Status** (Pending/Completed).
               - Example: "1. Buy Milk (Pending)"
               - Do NOT output the UUIDs like 'b87587...'.

            4. Use the available tool functions (expressed as intents) ONLY when the user intends to manage tasks.
            5. **Available Tools**:
               - `list_tasks(status: "all" | "pending" | "completed")`
               - `add_task(title: string)`
               - `complete_task(task_id: string)`
               - `delete_task(task_id: string)`
               - `update_task(task_id: string, title: string)`
               - `search_tasks(query: string, status: string, priority: string)`
               - `sort_tasks(field: "due_date" | "created_at" | "priority" | "title" | "status", order: "asc" | "desc")`

            6. **OUTPUT FORMAT**: ALWAYS return a VALID JSON object. No markdown, no extra text.
               {{
                 "response": "Your natural language response here.",
                 "tool_calls": [
                    {{ "name": "tool_name", "arguments": {{ "arg1": "val1" }} }}
                 ],
                 "chat_title": "A short 3-5 word title for this chat based on user intent (e.g. 'Shopping List', 'Fixing Bug')"
               }}
            """

            try:
                response = self.model.generate_content(prompt)
                raw_text = response.text.strip()
            except Exception as e:
                # Log the error appropriately
                import logging
                logging.error(f"Gemini generation error: {e}")

                # Better fallback handling for task-related messages
                # Parse the message to determine intent when AI fails
                message_lower = message.lower().strip()

                # Define fallback responses and tool calls based on message content
                fallback_response = "Hi 🙂 How can I help you?"
                fallback_tool_calls = []

                def clean_fallback_title(title):
                    if not title: return ""
                    # Remove common filler prefixes iteratively
                    prev_title = ""
                    while title != prev_title:
                        prev_title = title
                        title = re.sub(r'^(?:to|my|a|the|task|tasks|called|named|as|is|with|label)\s+', '', title, flags=re.IGNORECASE).strip()
                    return title.strip('"').strip("'").strip().strip('"').strip("'")

                if "add" in message_lower or "create" in message_lower:
                    match = re.search(r'(?:add|create).*?(?:task|:|called|named)\s+(.+)', message_lower, re.IGNORECASE)
                    if match:
                        task_title = clean_fallback_title(match.group(1))
                        fallback_response = f"Added task: {task_title}"
                        fallback_tool_calls = [{
                            "name": "add_task",
                            "arguments": {
                                "title": task_title,
                                "user_id": user_id
                            }
                        }]
                    else:
                        # If we can't extract title, ask for clarification
                        fallback_response = "I'd like to help you add a task. Could you please specify the task title?"

                elif re.search(r'\b(?:upd|edi|cha|ren)', message_lower):
                    # Try to capture various ways users might express editing tasks:
                    # "change X to Y", "rename X to Y", "update X to Y", "edit X to Y", "change X Y", "edit X Y"
                    match = re.search(r'(?:upd|edi|cha|ren).*?(?:task|:|called|named)?\s+(.+?)\s+(?:to|as|with)\s+(.+)', message_lower, re.IGNORECASE) or \
                           re.search(r'(?:upd|edi|cha|ren)\s+(.+?)\s+(?:to|as|with)\s+(.+)', message_lower, re.IGNORECASE) or \
                           re.search(r'(?:upd|edi|cha|ren).*?(?:task|:|called|named)?\s+(.+?)\s+(?!to|as|with)(\w+.*)', message_lower, re.IGNORECASE) or \
                           re.search(r'(?:upd|edi|cha|ren)\s+(.+?)\s+(?!to|as|with)(\w+.*)', message_lower, re.IGNORECASE)

                    if match:
                        task_identifier = clean_fallback_title(match.group(1))
                        new_title = clean_fallback_title(match.group(2))

                        from ..services.task_service import TaskService
                        from sqlmodel import Session
                        from ..database.session import engine
                        db = Session(engine)
                        try:
                            task, status = TaskService.resolve_task(db, user_id, task_identifier)
                            if status == "FOUND":
                                fallback_response = f"Theek hai, task '{task.title}' ko '{new_title}' kar diya hai. 🙂"
                                fallback_tool_calls = [{
                                    "name": "update_task",
                                    "arguments": {
                                        "task_id": task.id,
                                        "title": new_title,
                                        "user_id": user_id
                                    }
                                }]
                            elif status == "AMBIGUOUS":
                                fallback_response = f"Mujhe multiple tasks mile hain '{task_identifier}' matching. Kisko update karun?"
                            else:
                                fallback_response = f"Mujhe '{task_identifier}' naam ka koi task nahi mila jise update kar sakun."
                        finally:
                            db.close()
                    else:
                        # If we detect intent but match fails (e.g. "Edit task market" without "to...")
                        fallback_response = "Aap kis task ko badalna chahte hain aur uska naya naam kya hoga? (e.g. 'Change milk to buy milk') 🙂"

                elif re.search(r'\b(?:del|rem)', message_lower):
                    match = re.search(r'(?:del|rem).*?(?:task|:|called|named)?\s+(.+)', message_lower, re.IGNORECASE) or \
                            re.search(r'(?:del|rem)\s+(?:task\s+)?(.+)', message_lower, re.IGNORECASE)

                    if match:
                        task_identifier = clean_fallback_title(match.group(1))
                        from ..services.task_service import TaskService
                        from sqlmodel import Session
                        from ..database.session import engine
                        
                        db = Session(engine)
                        try:
                            task, status = TaskService.resolve_task(db, user_id, task_identifier)
                            
                            if status == "FOUND":
                                fallback_response = f"Theek hai, task '{task.title}' delete kar diya hai. 🙂"
                                fallback_tool_calls = [{
                                    "name": "delete_task",
                                    "arguments": {
                                        "task_id": task.id,
                                        "user_id": user_id
                                    }
                                }]
                            elif status == "AMBIGUOUS":
                                fallback_response = f"Mujhe multiple tasks mile hain '{task_identifier}' ke naam se. Aap please specify karenge?"
                            else:
                                fallback_response = f"Maaf kijiyega, mujhe '{task_identifier}' naam ka koi task nahi mila."
                        finally:
                            db.close()
                    else:
                        fallback_response = "Aap konsa task delete karna chahte hain? 🙂"

                elif re.search(r'\b(?:comp|fin|don|mark.*?c|mark.*?d|as\s+done|mark.*?done)', message_lower):
                    # Use a non-greedy match and lookahead to avoid capturing trailing filler words like "as done"
                    # Fixed: More specific pattern to avoid matching words like "market" as "mark"
                    match = re.search(r'(?:comp|fin|don|mark.*?c|mark.*?d|as\s+done|mark.*?done).*?(?:task|:|called|named)?\s+(.+?)(?:\s+as\s+done|\s+is\s+done|\s+done)?$', message_lower, re.IGNORECASE) or \
                            re.search(r'(?:comp|fin|don|mark.*?c|mark.*?d|as\s+done|mark.*?done)\s+(.+?)\s*(?:task)?$', message_lower, re.IGNORECASE) or \
                            re.search(r'mark.*?(?:task)?\s+(.+?)\s+as\s+done', message_lower, re.IGNORECASE)

                    if match:
                        task_identifier = clean_fallback_title(match.group(1))
                        from ..services.task_service import TaskService
                        from sqlmodel import Session
                        from ..database.session import engine
                        db = Session(engine)
                        try:
                            task, status = TaskService.resolve_task(db, user_id, task_identifier)
                            if status == "FOUND":
                                fallback_response = f"Theek hai, task '{task.title}' complete kar diya hai. 🙂"
                                fallback_tool_calls = [{
                                    "name": "complete_task",
                                    "arguments": {
                                        "task_id": task.id,
                                        "user_id": user_id
                                    }
                                }]
                            elif status == "AMBIGUOUS":
                                fallback_response = "Multiple tasks mile hain matching your message. Aap please wazahat karenge?"
                            else:
                                fallback_response = f"Mujhe '{task_identifier}' task nahi mila."
                        finally:
                            db.close()
                    else:
                        fallback_response = "Aapne konsa kaam khatam kar liya hai? 🙂"

                elif "list" in message_lower or "show" in message_lower or "all" in message_lower:
                    # Check if user is asking for specific status or priority
                    if "pending" in message_lower:
                        fallback_response = f"Here are your pending tasks:\n{tasks_context_clean}"
                        fallback_tool_calls = [{
                            "name": "list_tasks",
                            "arguments": {
                                "status": "pending",
                                "user_id": user_id
                            }
                        }]
                    elif "completed" in message_lower or "done" in message_lower:
                        fallback_response = f"Here are your completed tasks:\n{tasks_context_clean}"
                        fallback_tool_calls = [{
                            "name": "list_tasks",
                            "arguments": {
                                "status": "completed",
                                "user_id": user_id
                            }
                        }]
                    else:
                        fallback_response = f"Here are your tasks:\n{tasks_context_clean}"
                        fallback_tool_calls = [{
                            "name": "list_tasks",
                            "arguments": {
                                "status": "all",
                                "user_id": user_id
                            }
                        }]

                elif "search" in message_lower or "find" in message_lower or "look" in message_lower or "high priority" in message_lower or "low priority" in message_lower or "medium priority" in message_lower or "urgent" in message_lower:
                    # Determine if user is searching by priority
                    priority = None
                    if "high priority" in message_lower or "high" in message_lower or "urgent" in message_lower:
                        priority = "high"
                    elif "medium priority" in message_lower or "medium" in message_lower:
                        priority = "medium"
                    elif "low priority" in message_lower or "low" in message_lower:
                        priority = "low"
                    
                    # Extract search query from message
                    search_match = re.search(r'(?:search|find|look for|look up|show me|show|tasks? with|tasks? for)\s+(?:tasks?|task|for)?\s+(.+?)(?:\s+(?:priority|status|due))?', message_lower, re.IGNORECASE)
                    if not search_match:
                        search_match = re.search(r'.*\b(for|about)\s+(.+)', message_lower, re.IGNORECASE)

                    search_query = None
                    if search_match:
                        search_query = clean_fallback_title(search_match.group(-1) if search_match.groups() else search_match.group(0))
                    
                    # Check for due date keywords
                    due_date_keywords = ["today", "tomorrow", "this week", "due today", "due tomorrow", "due date"]
                    has_due_date_keyword = any(keyword in message_lower for keyword in due_date_keywords)
                    
                    if has_due_date_keyword:
                        search_query = "due today" if "today" in message_lower else "due tomorrow" if "tomorrow" in message_lower else "this week"
                    
                    fallback_response = f"Searching for tasks..."
                    fallback_tool_calls = [{
                        "name": "search_tasks",
                        "arguments": {
                            "query": search_query,
                            "priority": priority,
                            "user_id": user_id
                        }
                    }]

                elif "sort" in message_lower or "order" in message_lower or "latest" in message_lower or "oldest" in message_lower:
                    # Extract sort field and order from message
                    sort_match = re.search(r'(?:sort|order|arrange|latest|newest|oldest)\s+(?:tasks|task|by|according to|based on)?\s+(.+?)(?:\s+(?:by|in))?(\s+(?:asc|desc|ascending|descending|latest|oldest|newest))?', message_lower, re.IGNORECASE)
                    
                    field = "created_at"  # default
                    order = "desc" if "latest" in message_lower or "newest" in message_lower else "asc"
                    
                    if sort_match:
                        field_text = sort_match.group(1).strip()
                        
                        # Check if there's an order term in the match
                        if len(sort_match.groups()) > 1 and sort_match.group(2):
                            order_text = sort_match.group(2).strip()
                            if "desc" in order_text or "oldest" in order_text:
                                order = "desc"
                            elif "asc" in order_text or "latest" in order_text or "newest" in order_text:
                                order = "asc"
                        
                        # Map common terms to valid fields
                        field_mapping = {
                            "due date": "due_date",
                            "priority": "priority",
                            "title": "title",
                            "created": "created_at",
                            "date": "created_at",
                            "status": "status"
                        }

                        for key, val in field_mapping.items():
                            if key in field_text.lower():
                                field = val
                                break
                    else:
                        # Determine field based on keywords in the message
                        if "due" in message_lower or "date" in message_lower:
                            field = "due_date"
                        elif "priority" in message_lower:
                            field = "priority"
                        elif "title" in message_lower:
                            field = "title"
                        elif "status" in message_lower:
                            field = "status"

                    fallback_response = f"Sorting tasks by {field} in {'descending' if order == 'desc' else 'ascending'} order..."
                    fallback_tool_calls = [{
                        "name": "sort_tasks",
                        "arguments": {
                            "field": field,
                            "order": order,
                            "user_id": user_id
                        }
                    }]

                else:
                    # Pure greeting or other message
                    if is_pure_greeting and not has_task_verb:
                        fallback_response = "Hi 🙂 How can I help you?"
                    else:
                        fallback_response = "I see you're asking about a task. Could you please clarify what you'd like to do? 🙂"

                # Fallback title generation from message text
                fallback_title = " ".join(message.split()[:4])
                if len(fallback_title) > 30:
                    fallback_title = fallback_title[:30] + "..."

                return {
                    "response": fallback_response,
                    "tool_calls": fallback_tool_calls,
                    "conversation_id": conversation_id,
                    "chat_title": fallback_title
                }
                
            # Robust JSON extraction
            import json
            
            # Clean text from potential markdown blocks
            clean_text = raw_text
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[-1].split("```")[0].strip()
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[-1].split("```")[0].strip()

            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if json_match:
                try:
                    extracted_json = json_match.group(0)
                    result = json.loads(extracted_json)
                except Exception as e:
                    import logging
                    logging.error(f"JSON parse error: {str(e)}")
                    result = {"response": raw_text, "tool_calls": []}
            else:
                result = {"response": raw_text, "tool_calls": []}
            
            # Filter and inject user_id into tool calls
            processed_tool_calls = []
            for call in result.get("tool_calls", []):
                if call.get("name") in ["add_task", "delete_task", "update_task", "complete_task", "list_tasks", "search_tasks", "sort_tasks"]:
                    if "arguments" not in call:
                        call["arguments"] = {}
                    call["arguments"]["user_id"] = user_id
                    processed_tool_calls.append(call)
            
            response_text = result.get("response")
            if not response_text or (isinstance(response_text, str) and not response_text.strip()):
                response_text = raw_text if not json_match else "I've processed your request."
            
            # Final check: if AI returned a generic greeting but task verb was present, override or warn?
            # For now, trust the AI if it actually replied, but if it failed to return JSON, result["response"] might be empty.
            
            if has_task_verb and response_text == "Hi 🙂 How can I help you?":
                 response_text = "I see you're asking about a task. Could you please clarify what you'd like to do? 🙂"

            return {
                "response": response_text,
                "tool_calls": processed_tool_calls,
                "conversation_id": conversation_id,
                "chat_title": result.get("chat_title")
            }
        except Exception as e:
            import logging
            logging.error(f"Error in process_message: {str(e)}")
            fallback_msg = "Hi 🙂 How can I help you?"
            if 'has_task_verb' in locals() and has_task_verb:
                fallback_msg = "I see you're asking about a task. Could you please clarify what you'd like to do? 🙂"
            # Fallback title generation from message text
            fallback_title = " ".join(message.split()[:4])
            if len(fallback_title) > 30:
                fallback_title = fallback_title[:30] + "..."

            return {
                "response": fallback_msg,
                "tool_calls": [],
                "conversation_id": conversation_id,
                "chat_title": fallback_title
            }

    def generate_conversation_title(self, message: str) -> str:
        try:
            prompt = f"Generate a very short, concise title (MAX 4 words) for a chat that starts with this message: \"{message}\". Return ONLY the title text, no quotes."
            response = self.model.generate_content(prompt)
            if response and response.text:
                title = response.text.strip().replace('"', '')
                return title[:100]
            return "New Task Chat"
        except Exception as e:
            import logging
            logging.error(f"Error generating title: {str(e)}")
            return "New Chat"
