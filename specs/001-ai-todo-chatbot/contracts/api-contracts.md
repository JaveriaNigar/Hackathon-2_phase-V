# API Contracts: AI-Powered Todo Chatbot

## Overview
This document defines the API contracts for the AI-Powered Todo Chatbot application. The API follows REST principles with a single chat endpoint for AI interactions and traditional CRUD endpoints for managing tasks, conversations, and messages.

## Authentication
All endpoints require JWT token authentication in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Base URL
```
https://api.yourdomain.com/api
```

## Endpoints

### Chat Endpoint (AI Interaction)
**POST** `/api/{user_id}/chat`

Interacts with the AI agent to manage tasks through natural language.

#### Path Parameters
- `user_id` (string, required): The ID of the user making the request

#### Request Body
```json
{
  "conversation_id": "string (optional)",
  "message": "string (required)"
}
```

#### Response
```json
{
  "conversation_id": "string",
  "response": "string",
  "tool_calls": [
    {
      "name": "string",
      "arguments": "object"
    }
  ]
}
```

#### Example Requests
```
POST /api/user123/chat
{
  "message": "Add a task to buy groceries"
}
```

```
POST /api/user123/chat
{
  "conversation_id": "conv456",
  "message": "Show me my pending tasks"
}
```

### Task Management Endpoints

#### Create Task
**POST** `/api/{user_id}/tasks`

Creates a new task for the user.

##### Request Body
```json
{
  "title": "string (required)",
  "description": "string (optional)"
}
```

##### Response
```json
{
  "id": "string",
  "user_id": "string",
  "title": "string",
  "description": "string",
  "completed": false,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Get All Tasks
**GET** `/api/{user_id}/tasks`

Retrieves all tasks for the user.

##### Query Parameters
- `status` (string, optional): Filter by status ("all", "pending", "completed"; default: "all")

##### Response
```json
[
  {
    "id": "string",
    "user_id": "string",
    "title": "string",
    "description": "string",
    "completed": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

#### Get Task by ID
**GET** `/api/{user_id}/tasks/{task_id}`

Retrieves a specific task.

##### Response
```json
{
  "id": "string",
  "user_id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Update Task
**PUT** `/api/{user_id}/tasks/{task_id}`

Updates an existing task.

##### Request Body
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "completed": "boolean (optional)"
}
```

##### Response
```json
{
  "id": "string",
  "user_id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Delete Task
**DELETE** `/api/{user_id}/tasks/{task_id}`

Deletes a specific task.

##### Response
```json
{
  "success": "boolean",
  "message": "string"
}
```

### Conversation Management Endpoints

#### Create Conversation
**POST** `/api/{user_id}/conversations`

Starts a new conversation.

##### Response
```json
{
  "id": "string",
  "user_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Get All Conversations
**GET** `/api/{user_id}/conversations`

Retrieves all conversations for the user.

##### Response
```json
[
  {
    "id": "string",
    "user_id": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### Message Management Endpoints

#### Get Messages in Conversation
**GET** `/api/{user_id}/conversations/{conversation_id}/messages`

Retrieves all messages in a specific conversation.

##### Response
```json
[
  {
    "id": "string",
    "user_id": "string",
    "conversation_id": "string",
    "role": "string (user|assistant)",
    "content": "string",
    "created_at": "datetime"
  }
]
```

#### Add Message to Conversation
**POST** `/api/{user_id}/conversations/{conversation_id}/messages`

Adds a message to a specific conversation.

##### Request Body
```json
{
  "role": "string (user|assistant)",
  "content": "string (required)"
}
```

##### Response
```json
{
  "id": "string",
  "user_id": "string",
  "conversation_id": "string",
  "role": "string",
  "content": "string",
  "created_at": "datetime"
}
```