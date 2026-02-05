---
id: 1
title: backend-task-api-spec
stage: spec
date_iso: 2026-01-08
surface: agent
model: Qwen
feature: backend-tasks
branch: 001-backend-tasks
user: M.R Computers
command: sp.specify
labels:
  - specification
  - backend
  - api
  - tasks
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "specs/001-backend-tasks/spec.md"
  - "specs/001-backend-tasks/checklists/requirements.md"
tests_yaml: []
---

# PHR: backend-task-api-spec

## Prompt

```
$ARGUMENTS
```

## Response

```
# Feature Specification: Backend Task Management API

**Feature Branch**: `001-backend-tasks`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "Task: Implement the full backend for the Phase II Todo Full-Stack Web Application according to the specifications. Do not touch the frontend. Requirements: Database: Connect to Neon PostgreSQL using the DATABASE_URL environment variable. Use SQLModel ORM. Tables required: users (managed by Better Auth) tasks (id, user_id, title, description, completed, created_at, updated_at) Authentication: Use JWT tokens issued by Better Auth. Verify JWT on every request using BETTER_AUTH_SECRET. Only allow users to access their own tasks (user_id filtering). REST API Endpoints: GET /api/{user_id}/tasks → List all tasks for the authenticated user. POST /api/{user_id}/tasks → Create a new task. GET /api/{user_id}/tasks/{id} → Get task details. PUT /api/{user_id}/tasks/{id} → Update a task. DELETE /api/{user_id}/tasks/{id} → Delete a task. PATCH /api/{user_id}/tasks/{id}/complete → Toggle task completion. Error Handling: Return proper HTTP status codes (401 if JWT invalid, 404 if task not found, etc.) Middleware: Add JWT verification middleware for FastAPI. Environment Variables: Ensure the backend uses: DATABASE_URL → Neon PostgreSQL connection string BETTER_AUTH_SECRET → JWT verification secret BETTER_AUTH_URL → Frontend/auth service URL Instructions: Follow the specs in /specs/backend/ (task-crud.md, auth.md, database.md). All responses should be JSON. Do not implement any frontend changes. Ensure user isolation and security with JWT. Write clean, maintainable code, following FastAPI + SQLModel best practices. these are my keys use this keys for thi project: neon database key: psql 'postgresql://neondb_owner:npg_I5sxglHN6jhF@ep-red-lab-a7x0pi70-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require' BETTER_AUTH_SECRET=zJX6jmfhj7rHBjE56kyR59KAwfe5z5YG90MLSSWHEE8= BETTER_AUTH_URL=http://localhost:3000"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create New Task (Priority: P1)

As an authenticated user, I want to create new tasks in my personal task list so that I can keep track of my responsibilities and goals.

**Why this priority**: This is the core functionality of a todo application - users need to be able to add tasks to the system.

**Independent Test**: A user can successfully create a new task with a title and description, and it appears in their personal task list.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user, **When** I submit a new task with a title and description, **Then** the task is created and associated with my user ID
2. **Given** I am an authenticated user, **When** I submit a new task with minimal required fields, **Then** the task is created with appropriate default values for optional fields

---

### User Story 2 - View Personal Task List (Priority: P1)

As an authenticated user, I want to view all my tasks in one place so that I can get an overview of what I need to do.

**Why this priority**: This is essential functionality that allows users to see their tasks, which is fundamental to the value of a todo application.

**Independent Test**: A user can retrieve and view a list of all tasks associated with their account.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with existing tasks, **When** I request my task list, **Then** I see only tasks associated with my user ID
2. **Given** I am an authenticated user with no tasks, **When** I request my task list, **Then** I see an empty list without errors

---

### User Story 3 - Update Task Details (Priority: P2)

As an authenticated user, I want to update my tasks (title, description, completion status) so that I can keep my task information current.

**Why this priority**: Users need to modify tasks as circumstances change or as they make progress on their goals.

**Independent Test**: A user can modify an existing task that belongs to them, changing its properties.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with an existing task, **When** I update the task details, **Then** the changes are saved and reflected when I view the task again
2. **Given** I am an authenticated user, **When** I try to update a task that doesn't belong to me, **Then** I receive an authorization error

---

### User Story 4 - Delete Tasks (Priority: P2)

As an authenticated user, I want to delete tasks that are no longer relevant so that I can keep my task list clean and focused.

**Why this priority**: Users need to remove completed or irrelevant tasks to maintain an organized task list.

**Independent Test**: A user can remove a task from their personal task list.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with an existing task, **When** I delete the task, **Then** it is removed from my task list
2. **Given** I am an authenticated user, **When** I try to delete a task that doesn't belong to me, **Then** I receive an authorization error

---

### User Story 5 - Toggle Task Completion Status (Priority: P2)

As an authenticated user, I want to mark tasks as completed or incomplete so that I can track my progress.

**Why this priority**: This is a core feature of todo applications that allows users to mark tasks as done and track their productivity.

**Independent Test**: A user can change the completion status of their tasks.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with an incomplete task, **When** I mark it as complete, **Then** its status is updated to completed
2. **Given** I am an authenticated user with a completed task, **When** I mark it as incomplete, **Then** its status is updated to incomplete

### Edge Cases

- What happens when a user tries to access tasks belonging to another user?
- How does the system handle expired JWT tokens during API requests?
- What happens when a user tries to access a task that doesn't exist?
- How does the system handle database connection failures?
- What happens when a user tries to create a task with invalid or missing required fields?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate users via JWT tokens issued by Better Auth
- **FR-002**: System MUST verify JWT tokens using the BETTER_AUTH_SECRET environment variable
- **FR-003**: System MUST connect to Neon PostgreSQL database using the DATABASE_URL environment variable
- **FR-004**: System MUST use SQLModel ORM for database operations
- **FR-005**: System MUST ensure users can only access their own tasks through user_id filtering
- **FR-006**: System MUST provide REST API endpoints for task management operations
- **FR-007**: System MUST return proper HTTP status codes (401 for invalid JWT, 404 for not found, etc.)
- **FR-008**: System MUST store task data with the following fields: id, user_id, title, description, completed, created_at, updated_at
- **FR-009**: System MUST implement GET /api/{user_id}/tasks endpoint to list all tasks for an authenticated user
- **FR-010**: System MUST implement POST /api/{user_id}/tasks endpoint to create a new task
- **FR-011**: System MUST implement GET /api/{user_id}/tasks/{id} endpoint to get task details
- **FR-012**: System MUST implement PUT /api/{user_id}/tasks/{id} endpoint to update a task
- **FR-013**: System MUST implement DELETE /api/{user_id}/tasks/{id} endpoint to delete a task
- **FR-014**: System MUST implement PATCH /api/{user_id}/tasks/{id}/complete endpoint to toggle task completion
- **FR-015**: System MUST use JWT verification middleware for all API endpoints
- **FR-016**: System MUST return JSON responses for all API endpoints
- **FR-017**: System MUST validate that the authenticated user matches the user_id in the URL path

### Key Entities *(include if feature involves data)*

- **Task**: Represents a user's task with attributes: id (unique identifier), user_id (foreign key to user), title (required string), description (optional string), completed (boolean), created_at (timestamp), updated_at (timestamp)
- **User**: Represents an authenticated user managed by Better Auth with attributes: id (unique identifier) and authentication details

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully create, read, update, and delete their own tasks with 99% success rate
- **SC-002**: API endpoints respond within 500ms for 95% of requests under normal load conditions
- **SC-003**: Users can only access their own tasks, with 100% enforcement of user isolation
- **SC-004**: Authentication and authorization failures are properly handled with appropriate HTTP status codes (401, 403, 404)
- **SC-005**: System maintains 99.9% uptime for authenticated API requests
- **SC-006**: All API endpoints return valid JSON responses with appropriate HTTP status codes
```