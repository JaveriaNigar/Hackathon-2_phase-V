---
id: "001"
title: "Update for AI Chatbot"
stage: "constitution"
date_iso: "2026-01-19"
surface: "agent"
model: "Qwen"
feature: "none"
branch: "main"
user: "M.R Computers"
command: "/sp.constitution"
labels:
  - "constitution"
  - "ai-integration"
  - "todo-app"
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - ".specify/memory/constitution.md"
  - ".specify/templates/plan-template.md"
  - ".specify/templates/spec-template.md"
  - ".specify/templates/tasks-template.md"
tests_yaml: []
prompt_text: |
  ---
  description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync.
  handoffs: 
    - label: Build Specification
      agent: sp.specify
      prompt: Implement the feature specification based on the updated constitution. I want to build...
  ---

  ## User Input

  ```text
  $ARGUMENTS
  ```

  You **MUST** consider the user input before proceeding (if not empty).

  ## Outline

  You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

  Follow this execution flow:

  1. Load the existing constitution template at `.specify/memory/constitution.md`.
     - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
     **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

  2. Collect/derive values for placeholders:
     - If user input (conversation) supplies a value, use it.
     - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
     - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
     - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
       - MAJOR: Backward incompatible governance/principle removals or redefinitions.
       - MINOR: New principle/section added or materially expanded guidance.
       - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
     - If version bump type ambiguous, propose reasoning before finalizing.

  3. Draft the updated constitution content:
     - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
     - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
     - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
     - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

  4. Consistency propagation checklist (convert prior checklist into active validations):
     - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
     - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
     - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
     - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
     - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

  5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
     - Version change: old → new
     - List of modified principles (old title → new title if renamed)
     - Added sections
     - Removed sections
     - Templates requiring updates (✅ updated / ⚠ pending) with file paths
     - Follow-up TODOs if any placeholders intentionally deferred.

  6. Validation before final output:
     - No remaining unexplained bracket tokens.
     - Version line matches report.
     - Dates ISO format YYYY-MM-DD.
     - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

  7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

  8. Output a final summary to the user with:
     - New version and bump rationale.
     - Any files flagged for manual follow-up.
     - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

  Formatting & Style Requirements:

  - Use Markdown headings exactly as in the template (do not demote/promote levels).
  - Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
  - Keep a single blank line between sections.
  - Avoid trailing whitespace.

  If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

  If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

  Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

  ---

  As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

  1) Determine Stage
     - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

  2) Generate Title and Determine Routing:
     - Generate Title: 3–7 words (slug for filename)
     - Route is automatically determined by stage:
       - `constitution` → `history/prompts/constitution/`
       - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
       - `general` → `history/prompts/general/`

  3) Create and Fill PHR (Shell first; fallback agent‑native)
     - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
     - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
     - If the script fails:
       - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
       - Allocate an ID; compute the output path based on stage from step 2; write the file
       - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

  4) Validate + report
     - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
     - On failure: warn, don't block. Skip only for `/sp.phr`.


  /sp.constitution /sp.constitution

  You are an AI assistant tasked with fully implementing the Todo AI Chatbot project. Follow these instructions carefully. The project should convert the existing normal web Todo app into a **fully AI-powered application** using the Agentic Dev Stack, OpenAI Agents SDK, MCP tools, and Gemini API.

  1. **Backend Requirements**:
     - Preserve **all existing backend functionality** of the current Todo app.
     - Implement **AI agent integration** for handling natural language commands.
     - Use **FastAPI** for the backend server.
     - Integrate **OpenAI Agents SDK** to connect user messages to MCP tools.
     - Implement **MCP Server** with Official MCP SDK exposing all task management tools:
       - `add_task`
       - `list_tasks`
       - `update_task`
       - `complete_task`
       - `delete_task`
     - All MCP tools must be **stateless** and store state in the database (Neon PostgreSQL) using SQLModel.
     - Backend must read **Gemini API key** from `.env` and use it for agent requests.
     - Provide a **single chat endpoint**: `POST /api/{user_id}/chat`:
       - Input: `conversation_id` (optional), `message` (string)
       - Output: `conversation_id`, `response`, `tool_calls`
     - Maintain **chat history** and **task state** in database models:
       - Task: `user_id, id, title, description, completed, created_at, updated_at`
       - Conversation: `user_id, id, created_at, updated_at`
       - Message: `user_id, id, conversation_id, role, content, created_at`

  2. **Frontend Requirements**:
     - On `http://localhost:3000/ask-agent?username=Burhan`:
       - Two buttons:
         1. **Back to Dashboard** → navigates to dashboard.
         2. **Back to Welcome Page** → replace with **"Ask Todo Agent"** button.
           - Clicking opens **full-page AI chat interface** (like ChatGPT).
           - Sidebar includes **New Chat, History** placeholders.
     - On **Dashboard page**:
       - Next to **Logout button**, add **"Ask Todo Agent"** button.
       - Clicking it also navigates to **full-page agent chat**.
     - Frontend should integrate with backend chat endpoint for future AI responses.

  3. **Agent Behavior**:
     - Agent must process **natural language commands**:
       - Create, list, update, complete, delete tasks.
     - Follow behavior mapping:
       - "Add / Create / Remember" → `add_task`
       - "Show / List / Pending / Completed" → `list_tasks`
       - "Done / Complete / Finished" → `complete_task`
       - "Delete / Remove / Cancel" → `delete_task`
       - "Change / Update / Rename" → `update_task`
     - Always confirm actions with friendly response.
     - Gracefully handle errors (task not found, invalid command).

  4. **Stateless Architecture**:
     - Backend does not hold session state.
     - All state is stored in **database**.
     - Server must handle multiple requests independently.
     - Must be horizontally scalable.

  5. **Environment Setup**:
     - `.env` must have `GEMINI_API_KEY=<your_key_here>` for agent.
     - Backend reads API key to authenticate with Gemini agent.
     - Frontend must be configured to call backend `/chat` endpoint.

  6. **Database**:
     - Use **Neon Serverless PostgreSQL** with SQLModel ORM.
     - Maintain tables for tasks, conversations, messages.

  7. **Deliverables**:
     - `/frontend` → ChatKit UI integrated with AI agent
     - `/backend` → FastAPI + MCP tools + OpenAI Agents SDK + Gemini integration
     - `/specs` → specification files for MCP tools and agent behavior
     - **Database migration scripts**
     - **README** → setup, run instructions, environment variables
     - Fully working AI-powered Todo agent:
       - Can manage tasks via natural language
       - Maintains chat context
       - Friendly confirmations
       - Handles errors
       - Resume conversations after server restart

  8. **Implementation Rules**:
     - Follow Agentic Dev Stack workflow:
       1. Write spec
       2. Generate plan
       3. Break into tasks
       4. Implement via Claude/Gemini code
     - **No manual coding** allowed.
     - Provide **step-by-step explanations** for each generated code section.
     - All outputs must be reproducible and fully functional.

  9. **Testing & Verification**:
     - Agent must handle example user commands correctly.
     - Backend chat endpoint must respond with proper MCP tool calls.
     - Frontend navigation buttons must redirect as described.

  10. **Next Steps for Qwen**:
     - Generate **full project spec** if not done.
     - Create **development plan** (frontend + backend + MCP + agent).
     - Break plan into **tasks** ready for Claude/Gemini code implementation.
     - Scaffold **frontend and backend projects**.
     - Implement **MCP tools**.
     - Connect **Gemini API key** to agent backend.
     - Implement **full-page chat interface** and navigation buttons.

  End of constitution.
response_text: |
  I have successfully updated the project constitution to transform the Todo app into an AI-powered application using the Agentic Dev Stack, OpenAI Agents SDK, MCP tools, and Gemini API. Here's what was accomplished:

  1. Updated the constitution from version 1.0.0 to 2.0.0, changing the focus from a traditional full-stack Todo app to an AI-powered Todo chatbot.

  2. Revised all core principles to reflect the new AI-focused direction:
     - Agentic Development Stack
     - AI-Powered User Experience
     - Test-First for AI Features
     - AI Security-First Design
     - MCP Tool Development
     - Persistent Data Management

  3. Updated technology stack requirements to include AI integration elements like ChatKit UI, OpenAI Agents SDK, MCP SDK, and Gemini API.

  4. Modified the development workflow to follow the agentic development process: Write spec → Generate plan → Break into tasks → Implement via AI agents.

  5. Updated dependent templates to align with the new constitution:
     - .specify/templates/plan-template.md: Updated Constitution Check section
     - .specify/templates/spec-template.md: Added AI-specific functional requirements
     - .specify/templates/tasks-template.md: Added AI-specific foundational tasks and implementation strategy

  6. Generated a comprehensive Sync Impact Report documenting all changes made.

  The updated constitution now properly reflects the project's transformation into an AI-powered Todo chatbot with MCP tools, agentic development practices, and Gemini API integration.
outcome_evaluation: |
  The constitution has been successfully updated to reflect the AI-powered Todo chatbot project requirements. All dependent templates have been updated to align with the new principles, and the version has been incremented from 1.0.0 to 2.0.0 to reflect the significant changes in project direction. The Sync Impact Report confirms all necessary files have been updated.
---