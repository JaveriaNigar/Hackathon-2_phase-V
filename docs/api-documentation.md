# Advanced Todo Features API Documentation

## Overview
This API provides advanced todo features including recurring tasks, reminders, priorities, tags, search, filter, sort, and event-driven architecture.

## Base URL
`http://localhost:8000/api/{user_id}`

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
`Authorization: Bearer {jwt_token}`

## Common Headers
- `Content-Type: application/json`
- `Authorization: Bearer {token}`

## Common Response Format
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": false,
  "due_date": "2023-12-31T23:59:59",
  "priority": "low|medium|high",
  "status": "active|completed|archived",
  "tags": ["tag1", "tag2"],
  "recurrence_pattern": {
    "type": "daily|weekly|monthly|yearly",
    "interval": 1,
    "days_of_week": [0, 6],
    "end_condition": {
      "type": "after_n_occurrences|on_date",
      "value": 10
    }
  },
  "next_occurrence": "2023-12-31T23:59:59",
  "user_id": "string",
  "created_at": "2023-12-31T23:59:59",
  "updated_at": "2023-12-31T23:59:59"
}
```

## Endpoints

### Task Management

#### Create a Task
`POST /api/{user_id}/tasks`

Create a new task with advanced features.

**Request Body:**
```json
{
  "title": "Task title (required)",
  "description": "Task description",
  "due_date": "2023-12-31T23:59:59",
  "priority": "low|medium|high",
  "tags": ["tag1", "tag2"],
  "recurrence_pattern": {
    "type": "daily|weekly|monthly|yearly",
    "interval": 1,
    "days_of_week": [0, 6],
    "end_condition": {
      "type": "after_n_occurrences|on_date",
      "value": 10
    }
  }
}
```

**Response:** 201 Created with Task object

#### Get All Tasks
`GET /api/{user_id}/tasks`

Get all tasks for a user with optional filtering, sorting, and pagination.

**Query Parameters:**
- `status`: Filter by status (active, completed, archived)
- `priority`: Filter by priority (low, medium, high)
- `tag`: Filter by tag
- `sort`: Sort by field (due_date, priority, created_at, title, status)
- `order`: Sort order (asc, desc) - default: asc
- `page`: Page number - default: 0
- `limit`: Items per page - default: 100, max: 100

**Response:** 200 OK with paginated tasks
```json
{
  "tasks": [...],
  "pagination": {
    "page": 0,
    "limit": 100,
    "total": 150,
    "pages": 2
  }
}
```

#### Get Specific Task
`GET /api/{user_id}/tasks/{id}`

Get a specific task by ID.

**Response:** 200 OK with Task object

#### Update Task
`PUT /api/{user_id}/tasks/{id}`

Update a specific task.

**Request Body:**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "due_date": "2023-12-31T23:59:59",
  "priority": "high",
  "status": "active",
  "tags": ["updated", "tags"],
  "recurrence_pattern": {
    "type": "weekly",
    "interval": 2,
    "end_condition": {
      "type": "on_date",
      "value": "2024-12-31T23:59:59"
    }
  }
}
```

**Response:** 200 OK with updated Task object

#### Delete Task
`DELETE /api/{user_id}/tasks/{id}`

Delete a specific task.

**Response:** 204 No Content

#### Complete Task
`POST /api/{user_id}/tasks/{id}/complete`

Mark a task as completed. If the task is recurring, this will trigger the creation of the next occurrence.

**Response:** 200 OK with completed Task object

### Recurring Task Management

#### Schedule Recurrence
`POST /api/{user_id}/tasks/{id}/schedule-recurrence`

Schedule recurrence for an existing task.

**Request Body:**
```json
{
  "recurrence_pattern": {
    "type": "daily|weekly|monthly|yearly",
    "interval": 1,
    "days_of_week": [0, 6],
    "end_condition": {
      "type": "after_n_occurrences|on_date",
      "value": 10
    }
  }
}
```

**Response:** 200 OK with updated Task object

#### Update Recurrence
`PUT /api/{user_id}/tasks/{id}/update-recurrence`

Update the recurrence pattern for a task.

**Request Body:**
```json
{
  "recurrence_pattern": {
    "type": "weekly",
    "interval": 2,
    "days_of_week": [1, 3, 5],
    "end_condition": {
      "type": "on_date",
      "value": "2024-12-31T23:59:59"
    }
  }
}
```

**Response:** 200 OK with updated Task object

#### Cancel Recurrence
`DELETE /api/{user_id}/tasks/{id}/cancel-recurrence`

Cancel recurrence for a task.

**Response:** 200 OK with updated Task object

### Search and Filtering

#### Search Tasks
`GET /api/{user_id}/tasks/search`

Search tasks by title, description, or tags.

**Query Parameters:**
- `q`: Search query string

**Response:** 200 OK with array of Task objects

### Statistics

#### Get Task Stats
`GET /api/{user_id}/tasks/stats`

Get comprehensive task statistics for the user.

**Response:** 200 OK
```json
{
  "total": 150,
  "pending": 75,
  "completed": 75,
  "by_priority": {
    "low": 30,
    "medium": 70,
    "high": 50
  },
  "by_status": {
    "active": 75,
    "completed": 75,
    "archived": 0
  }
}
```

### Notification Management

#### Get User Notifications
`GET /api/{user_id}/notifications`

Get all notifications for a user.

**Query Parameters:**
- `sent_status`: Filter by status (pending, sent, failed)

**Response:** 200 OK with array of Notification objects

#### Get Specific Notification
`GET /api/{user_id}/notifications/{id}`

Get a specific notification by ID.

**Response:** 200 OK with Notification object

#### Mark Notification as Sent
`PUT /api/{user_id}/notifications/{id}/mark-sent`

Mark a notification as sent.

**Response:** 200 OK with updated Notification object

## Notification Object
```json
{
  "id": "string",
  "task_id": "string",
  "user_id": "string",
  "message": "string",
  "scheduled_time": "2023-12-31T23:59:59",
  "sent_status": "pending|sent|failed",
  "sent_at": "2023-12-31T23:59:59",
  "delivery_method": "email|push|sms",
  "created_at": "2023-12-31T23:59:59"
}
```

## Error Responses

All error responses follow this format:
```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Event-Driven Architecture

All task operations publish events to the event system:
- `task.created`: When a task is created
- `task.updated`: When a task is updated
- `task.completed`: When a task is completed
- `task.deleted`: When a task is deleted

Events contain correlation IDs for tracing and include relevant task data.

## Rate Limiting

API endpoints are subject to rate limiting to prevent abuse. Exceeding limits will result in 429 Too Many Requests responses.

## Security Considerations

- All endpoints require authentication
- Users can only access their own tasks
- Input validation is performed on all fields
- SQL injection and XSS protection is implemented