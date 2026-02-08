import os
import requests
from typing import Dict, Any, Optional
from ..config.settings import settings


class BackendAPIClient:
    """
    HTTP client for making API calls to the backend services.
    This allows the agent to interact with the backend through HTTP requests
    instead of directly accessing the database.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("BACKEND_BASE_URL", "http://localhost:8001")
        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "TodoAgent/1.0"
        }
    
    def _make_request(self, method: str, endpoint: str, user_id: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the backend API with proper authentication.
        """
        url = f"{self.base_url}/api/{user_id}{endpoint}"
        headers = self.default_headers.copy()
        
        # In a real implementation, we would need to generate a proper JWT token
        # For now, we'll simulate the authentication header
        # headers["Authorization"] = f"Bearer {self._generate_auth_token(user_id)}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            elif method.upper() == "PATCH":
                response = requests.patch(url, json=data, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            # Return the response as JSON if possible, otherwise return text
            try:
                return response.json()
            except ValueError:
                # If response is not JSON, return the text content
                return {"status_code": response.status_code, "content": response.text}
                
        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": f"Request failed: {str(e)}"
            }
    
    def create_task(self, user_id: str, title: str, description: str = None, 
                   priority: str = None, due_date: str = None, tags: list = None,
                   recurrence_pattern: str = None) -> Dict[str, Any]:
        """
        Create a new task via the API.
        """
        task_data = {
            "title": title,
            "description": description,
            "completed": False,
            "priority": priority,
            "due_date": due_date,
            "tags": tags,
            "recurrence_pattern": recurrence_pattern
        }
        
        # Remove None/empty values to avoid sending null to the API
        task_data = {k: v for k, v in task_data.items() 
                    if v is not None and (not isinstance(v, str) or v != "") and (not isinstance(v, list) or len(v) > 0)}
        
        return self._make_request("POST", "/tasks", user_id, data=task_data)
    
    def get_tasks(self, user_id: str, status: str = None, priority: str = None, 
                 tag: str = None, sort: str = None, order: str = "asc", 
                 page: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Get user's tasks via the API.
        """
        params = {
            "status": status,
            "priority": priority,
            "tag": tag,
            "sort": sort,
            "order": order,
            "page": page,
            "limit": limit
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        return self._make_request("GET", "/tasks", user_id, params=params)
    
    def get_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Get a specific task by ID via the API.
        """
        return self._make_request("GET", f"/tasks/{task_id}", user_id)
    
    def update_task(self, user_id: str, task_id: str, title: str = None, 
                   description: str = None, completed: bool = None, 
                   priority: str = None, due_date: str = None, 
                   tags: list = None) -> Dict[str, Any]:
        """
        Update a task via the API.
        """
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if completed is not None:
            update_data["completed"] = completed
        if priority is not None:
            update_data["priority"] = priority
        if due_date is not None:
            update_data["due_date"] = due_date
        if tags is not None:
            update_data["tags"] = tags
            
        return self._make_request("PUT", f"/tasks/{task_id}", user_id, data=update_data)
    
    def delete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Delete a task via the API.
        """
        return self._make_request("DELETE", f"/tasks/{task_id}", user_id)
    
    def complete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Mark a task as completed via the API.
        """
        return self._make_request("POST", f"/tasks/{task_id}/complete", user_id)
    
    def toggle_task_completion(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Toggle task completion status via the API.
        """
        return self._make_request("PATCH", f"/tasks/{task_id}/complete", user_id)
    
    def search_tasks(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        Search tasks via the API.
        """
        params = {"q": query}
        return self._make_request("GET", "/tasks/search", user_id, params=params)
    
    def get_task_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get task statistics via the API.
        """
        return self._make_request("GET", "/tasks/stats", user_id)
    
    def get_pending_tasks_count(self, user_id: str) -> Dict[str, Any]:
        """
        Get pending tasks count via the API.
        """
        return self._make_request("GET", "/pending-tasks", user_id)
    
    def get_completed_tasks_count(self, user_id: str) -> Dict[str, Any]:
        """
        Get completed tasks count via the API.
        """
        return self._make_request("GET", "/completed-tasks", user_id)