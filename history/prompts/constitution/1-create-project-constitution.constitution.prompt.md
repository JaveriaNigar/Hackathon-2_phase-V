---
id: 1
title: Create Project Constitution
stage: constitution
date_iso: 2026-01-06
surface: agent
model: Qwen
feature: Hackathon II Todo Full-Stack Web App
branch: main
user: M.R Computers
command: /sp.constitution
labels: ["constitution", "setup", "governance"]
links: 
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - ".specify/memory/constitution.md"
tests_yaml: []
---

# Create Project Constitution

## User Input

```
/sp.constitution  Hackathon II Todo Full-Stack Web App

project:
  name: Hackathon II - Todo Full-Stack Web App
  description: >
    Evolution of Todo App from CLI to Full-Stack Web Application with multi-user
    support, persistent storage, and spec-driven development using Claude Code
    and Spec-Kit Plus.

goals:
  - Transform Phase I CLI Todo app into a modern multi-user web application
  - Implement all basic CRUD operations (Add, Delete, Update, View, Mark Complete)
  - Provide persistent storage via Neon Serverless PostgreSQL
  - Implement secure authentication with Better Auth + JWT tokens
  - Maintain clean, maintainable, and spec-driven code

tech_stack:
  frontend:
    framework: Next.js 16+
    language: TypeScript
    styling: Tailwind CSS
    routing: App Router
  backend:
    framework: FastAPI
    language: Python 3.13+
    orm: SQLModel
    authentication: JWT (Better Auth)
  database:
    engine: Neon Serverless PostgreSQL
  dev_tools:
    spec_management: Spec-Kit Plus
    code_generation: Claude Code
    containerization: Docker Compose

features:
  - Task CRUD (Add, View, Update, Delete, Complete/Incomplete)
  - User Authentication & Signup/Signin
  - RESTful API endpoints for all task operations
  - Frontend responsive UI with Tailwind CSS
  - API secured with JWT tokens (Authorization: Bearer <token>)
  - Multi-user isolation

api_endpoints:
  - GET /api/{user_id}/tasks
  - POST /api/{user_id}/tasks
  - GET /api/{user_id}/tasks/{id}
  - PUT /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH /api/{user_id}/tasks/{id}/complete

repository_structure:
  root:
    - .spec-kit/
    - specs/
    - CLAUDE.md
    - frontend/
    - backend/
    - docker-compose.yml
    - README.md

workflow:
  spec_driven_development: true
  steps:
    - Read spec: @specs/[feature].md
    - Implement backend: @backend/CLAUDE.md
    - Implement frontend: @frontend/CLAUDE.md
    - Test feature & iterate

rules:
  - All code changes must reference relevant specs
  - All endpoints require JWT token after authentication
  - Each user can only see and modify their own tasks
  - Follow CLAUDE.md guidelines for frontend and backend implementation
  - Update specs if any requirement changes

environment_variables:
  - DATABASE_URL
  - BETTER_AUTH_SECRET

notes:
  - Monorepo approach recommended for full-stack project
  - Single CLAUDE.md context for cross-cutting changes
  - Use Spec-Kit for organized and structured spec referencing
```

## Response Summary

Successfully created a comprehensive constitution for the Hackathon II Todo Full-Stack Web App project. The constitution includes:

- Six core principles aligned with the project's spec-driven development approach
- Technology stack requirements and performance standards
- Development workflow and code review requirements
- Governance section with amendment procedures

The constitution replaces the generic template with project-specific content that reflects the requirements for the full-stack web application with multi-user support, persistent storage, and spec-driven development.

## Outcome

The project constitution has been successfully created and saved to `.specify/memory/constitution.md`. The version is 1.0.0, representing a complete rewrite of the template with project-specific content. All templates were checked for consistency and no updates were needed.