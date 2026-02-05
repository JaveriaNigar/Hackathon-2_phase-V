---
id: "001"
title: "AI Todo Chatbot Plan"
stage: "plan"
date_iso: "2026-01-19"
surface: "agent"
model: "Qwen"
feature: "ai-todo-chatbot"
branch: "001-ai-todo-chatbot"
user: "M.R Computers"
command: "/sp.plan"
labels:
  - "planning"
  - "ai-integration"
  - "todo-app"
  - "architecture"
links:
  spec: "/specs/001-ai-todo-chatbot/spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "specs/001-ai-todo-chatbot/plan.md"
  - "specs/001-ai-todo-chatbot/research.md"
  - "specs/001-ai-todo-chatbot/data-model.md"
  - "specs/001-ai-todo-chatbot/contracts/api-contracts.md"
  - "specs/001-ai-todo-chatbot/quickstart.md"
tests_yaml: []
prompt_text: |
  ---
  description: Execute the implementation planning workflow using the plan template to generate design artifacts.
  handoffs: 
    - label: Create Tasks
      agent: sp.tasks
      prompt: Break the plan into tasks
      send: true
    - label: Create Checklist
      agent: sp.checklist
      prompt: Create a checklist for the following domain...
  ---

  ## User Input

  ```text
  $ARGUMENTS
  ```

  You **MUST** consider the user input before proceeding (if not empty).

  ## Outline

  1. **Setup**: Run `.specify/scripts/powershell/setup-plan.ps1 -Json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

  2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

  3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
     - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
     - Fill Constitution Check section from constitution
     - Evaluate gates (ERROR if violations unjustified)
     - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
     - Phase 1: Generate data-model.md, contracts/, quickstart.md
     - Phase 1: Update agent context by running the agent script
     - Re-evaluate Constitution Check post-design

  4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

  ## Phases

  ### Phase 0: Outline & Research

  1. **Extract unknowns from Technical Context** above:
     - For each NEEDS CLARIFICATION → research task
     - For each dependency → best practices task
     - For each integration → patterns task

  2. **Generate and dispatch research agents**:

     ```text
     For each unknown in Technical Context:
       Task: "Research {unknown} for {feature context}"
     For each technology choice:
       Task: "Find best practices for {tech} in {domain}"
     ```

  3. **Consolidate findings** in `research.md` using format:
     - Decision: [what was chosen]
     - Rationale: [why chosen]
     - Alternatives considered: [what else evaluated]

  **Output**: research.md with all NEEDS CLARIFICATION resolved

  ### Phase 1: Design & Contracts

  **Prerequisites:** `research.md` complete

  1. **Extract entities from feature spec** → `data-model.md`:
     - Entity name, fields, relationships
     - Validation rules from requirements
     - State transitions if applicable

  2. **Generate API contracts** from functional requirements:
     - For each user action → endpoint
     - Use standard REST/GraphQL patterns
     - Output OpenAPI/GraphQL schema to `/contracts/`

  3. **Agent context update**:
     - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType qwen`
     - These scripts detect which AI agent is in use
     - Update the appropriate agent-specific context file
     - Add only new technology from current plan
     - Preserve manual additions between markers

  **Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

  ## Key rules

  - Use absolute paths
  - ERROR on gate failures or unresolved clarifications

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


  /sp.plan /sp.plan

  You are an AI agent tasked with implementing the Todo AI Chatbot project. Follow this **step-by-step development plan** exactly as described. Each step is independent, reproducible, and clear. No ambiguity.  

  ---

  ## Phase 0: Project Setup
  1. Initialize **frontend project** (Next.js / ChatKit UI)
  2. Initialize **backend project** (FastAPI)
  3. Create `.env` file with `GEMINI_API_KEY=<your_key_here>`
  4. Set up **Neon PostgreSQL database**
  5. Install dependencies:
     - Frontend: ChatKit, Axios/Fetch
     - Backend: FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK, Python-dotenv

  ---

  ## Phase 1: Backend Setup
  1. **Preserve existing Todo backend functionality**
     - Ensure all current endpoints and database models remain intact
  2. Implement **database models** for AI:
     - Task: `user_id, id, title, description, completed, created_at, updated_at`
     - Conversation: `user_id, id, created_at, updated_at`
     - Message: `user_id, id, conversation_id, role, content, created_at`
  3. Implement **FastAPI MCP Server** with MCP SDK:
     - Tools:
       - `add_task`
       - `list_tasks`
       - `update_task`
       - `complete_task`
       - `delete_task`
     - Each tool stateless, store state in DB
  4. Implement **chat endpoint**:
     - POST `/api/{user_id}/chat`
     - Inputs: `conversation_id` (optional), `message`
     - Outputs: `conversation_id`, `response`, `tool_calls`
  5. Connect **Gemini API key** from `.env` for agent logic

  ---

  ## Phase 2: Agent Setup
  1. Integrate **OpenAI Agents SDK**
  2. Configure **agent behavior mapping**:
     - "Add / Create / Remember" → `add_task`
     - "Show / List / Pending / Completed" → `list_tasks`
     - "Done / Complete / Finished" → `complete_task`
     - "Delete / Remove / Cancel" → `delete_task`
     - "Change / Update / Rename" → `update_task`
  3. Ensure **friendly confirmation** messages
  4. Implement **error handling** for invalid tasks / missing IDs
  5. Maintain **stateless conversation flow** (all state in DB)

  ---

  ## Phase 3: Frontend Setup
  1. On `/ask-agent?username=Burhan`:
     - Two buttons:
       - **Back to Dashboard**
       - **"Ask Todo Agent"** → opens full-page chat interface
         - Sidebar: **New Chat**, **History** placeholders
         - Chat box for natural language input
  2. On **Dashboard page**:
     - Add **"Ask Todo Agent"** button next to Logout
     - Clicking redirects to full-page chat interface
  3. Connect frontend to backend `/chat` endpoint
  4. Maintain responsive UI for full-page chat like ChatGPT

  ---

  ## Phase 4: Integration Testing
  1. Verify **chat endpoint** returns proper `tool_calls` for example messages:
     - "Add task to buy groceries"
     - "Show pending tasks"
     - "Complete task 3"
     - "Delete old task"
     - "Update task 2 title"
  2. Verify **frontend buttons** navigate correctly:
     - Dashboard → Ask Todo Agent
     - `/ask-agent` page → Ask Todo Agent
  3. Confirm **database stores tasks, conversations, messages** correctly
  4. Confirm **stateless server**: restart does not lose data

  ---

  ## Phase 5: Deployment Preparation
  1. Ensure `.env` includes `GEMINI_API_KEY`
  2. Configure domain if hosting ChatKit (optional)
  3. Prepare **README**:
     - Project setup
     - Backend & frontend run instructions
     - Environment variables
  4. Verify **AI agent works with natural language** after deployment

  ---

  ## Phase 6: Final Verification
  1. All MCP tools functional
  2. Chat endpoint fully integrated with agent
  3. Frontend buttons redirect correctly
  4. Full-page AI chat works like ChatGPT
  5. Database stores all required data
  6. Errors handled gracefully
  7. Conversation can resume after server restart

  ---

  **End of Plan**
response_text: |
  I have successfully completed the implementation planning for the AI-Powered Todo Chatbot. Here's what was accomplished:

  1. Executed the setup-plan script to establish the planning environment
  2. Conducted research to resolve technical unknowns and create the research.md file
  3. Filled in the technical context for the implementation plan
  4. Created a comprehensive data model for Tasks, Conversations, and Messages
  5. Defined API contracts for all required endpoints
  6. Created a quickstart guide for easy project setup
  7. Updated the agent context with new technology information
  8. Validated all constitutional requirements were met in the design

  The following artifacts were generated:
  - Implementation plan (plan.md): Contains technical context, project structure, and constitutional checks
  - Research findings (research.md): Details on technology stack and architectural decisions
  - Data model (data-model.md): Defines the structure for Tasks, Conversations, and Messages
  - API contracts (contracts/api-contracts.md): Specifies all required endpoints and their behavior
  - Quickstart guide (quickstart.md): Step-by-step instructions for setting up and running the application

  All constitutional requirements have been addressed in the design, including:
  - Agentic Development Stack implementation
  - MCP tools that are stateless and database-backed
  - AI-Powered User Experience with natural language processing
  - Security-first design with proper authentication
  - Persistent Data Management with Neon PostgreSQL

  The plan is now ready for the next phase: breaking it down into specific implementation tasks using /sp.tasks.
outcome_evaluation: |
  The implementation planning for the AI-Powered Todo Chatbot has been completed successfully. All required artifacts have been created according to the constitution and feature specification. The plan addresses all technical requirements and follows the agentic development approach. The next step is to break the plan down into specific tasks for implementation.
---