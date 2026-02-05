
<!--
Sync Impact Report:
- Version change: 1.0.0 → 2.0.0
- Modified principles: All principles updated to reflect AI-powered application focus
- Added sections: AI Integration, MCP Tool Development, Agentic Development
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated
  - .specify/templates/tasks-template.md ✅ updated
- Follow-up TODOs: None
-->

# Todo AI Chatbot Constitution

## Core Principles

### I. Agentic Development Stack
All development must leverage the Agentic Dev Stack: MCP tools written → Agent behavior defined → AI integration implemented; Every AI feature must be connected to specifiable tools; Requirements changes must update agent behavior specs first before implementation.

### II. AI-Powered User Experience
The application integrates AI for natural language processing: Natural language commands processed by AI agents; Conversational interfaces replacing traditional UI controls; Seamless integration between AI responses and backend functionality.

### III. Test-First for AI Features (NON-NEGOTIABLE)
TDD mandatory for all AI features: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced; Both backend API tests and AI response validation required.

### IV. AI Security-First Design
Security considerations for AI integration: All API endpoints require JWT token authentication after user login; Each user can only access and modify their own tasks via AI agents; Input validation and sanitization required for all AI interactions; Protection against prompt injection attacks.

### V. MCP Tool Development
MCP (Model Context Protocol) tools must be stateless and database-backed: All tools expose CRUD operations for task management; Tools must store state in Neon PostgreSQL using SQLModel; Tools must be registered with OpenAI Agents SDK; Tools must follow official MCP SDK specifications.

### VI. Persistent Data Management
Reliable data storage and retrieval: Neon Serverless PostgreSQL for persistent storage; Proper database schema design and migration strategies; Data backup and recovery considerations; Support for conversation history and message persistence.

## Additional Constraints

Technology stack requirements:
- Frontend: Next.js 16+, TypeScript, Tailwind CSS, App Router with ChatKit UI
- Backend: FastAPI, Python 3.13+, SQLModel ORM, OpenAI Agents SDK, MCP SDK
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT tokens
- AI Integration: Gemini API for agent processing
- Containerization: Docker Compose for local development

AI Integration requirements:
- MCP Server with Official MCP SDK exposing all task management tools
- Single chat endpoint: POST /api/{user_id}/chat
- Support for natural language processing of task commands
- State management through database rather than session state

Performance standards:
- API response times under 1000ms for AI operations
- Frontend page load times under 3 seconds
- Support for at least 100 concurrent users in testing environment
- AI response times under 3000ms for complex operations

## Development Workflow

Agentic development process:
- Write spec: @specs/[feature].md defining AI behaviors and MCP tools
- Generate plan: @backend/CLAUDE.md for backend AI integration
- Break into tasks: @frontend/CLAUDE.md for frontend AI interfaces
- Implement via AI agents: Using Claude/Gemini for code generation

Code review requirements:
- All pull requests require at least one reviewer
- Code must pass all tests before merging
- Spec compliance verification required
- AI behavior and security considerations review for all new features

Quality gates:
- All automated tests must pass
- Code coverage must not decrease
- Linting and formatting checks must pass
- Spec alignment verification
- AI response validation and safety checks

## Governance

This constitution supersedes all other development practices for this project. All team members must adhere to these principles and guidelines. Amendments to this constitution require documentation of the change, team approval, and migration plan for existing codebase if needed.

All pull requests and code reviews must verify compliance with these principles. Complexity must be justified with clear benefits to the project. Use this constitution as the primary guidance document for all development decisions.

**Version**: 2.0.0 | **Ratified**: 2026-01-06 | **Last Amended**: 2026-01-19
