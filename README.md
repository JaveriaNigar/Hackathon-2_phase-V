# Todo AI Chatbot

An AI-powered todo application that allows users to manage their tasks through natural language conversation.

## Features

- Natural language processing for task management
- AI-powered chat interface for interacting with your todos
- Full task management capabilities (add, list, update, complete, delete)
- Conversation history and persistence
- Responsive web interface

## Tech Stack

- **Frontend**: Next.js 16+, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.13+
- **Database**: Neon Serverless PostgreSQL with SQLModel ORM
- **AI Integration**: Google Gemini API
- **Authentication**: JWT tokens

## Setup Instructions

### Prerequisites

- Node.js (v18 or later)
- Python (v3.13 or later)
- pip (Python package manager)
- npm or yarn
- Access to Neon PostgreSQL database
- Google Gemini API key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   DATABASE_URL=your_neon_postgres_connection_string
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn src.api.main:app --reload
   ```

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file based on `.env.example`:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8001/api
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```

## Usage

### Access the Application

1. Open your browser and go to `http://localhost:3000`
2. Navigate to the dashboard or ask-agent page to interact with the AI

### Interacting with the AI Agent

On the "Ask Todo Agent" page, type natural language commands such as:
- "Add a task to buy groceries"
- "Show me my pending tasks"
- "Mark task 'buy groceries' as complete"
- "Delete the task 'call mom'"
- "Update task 'meeting' to 'team meeting at 3pm'"

## API Endpoints

- Backend API: `http://localhost:8001/api`
- Frontend: `http://localhost:3000`

### Chat Endpoint
- `POST /api/{user_id}/chat` - Interact with the AI agent

### Task Management Endpoints
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks` - Get all tasks (with optional status filter)
- `GET /api/{user_id}/tasks/{task_id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update a task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete a task

## Architecture

The application follows a microservice architecture with separate frontend and backend:

- **Frontend**: Next.js application with a ChatGPT-like interface
- **Backend**: FastAPI application with AI integration and database operations
- **Database**: Neon PostgreSQL for persistent storage of tasks, conversations, and messages
- **AI Agent**: Google Gemini API for natural language processing

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm run test
```

### Project Structure

```
backend/
├── src/
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── api/             # API routes
│   ├── tools/           # MCP tools
│   ├── agents/          # AI agent logic
│   └── config/          # Configuration
frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Next.js pages
│   ├── services/        # API services
│   ├── hooks/           # Custom hooks
│   └── utils/           # Utility functions
```

## Deployment

For production deployment:
1. Set up environment variables for your production environment
2. Build the frontend: `npm run build`
3. Deploy the backend with your preferred Python hosting solution
4. Deploy the frontend with your preferred static hosting solution

## Troubleshooting

- If you encounter database connection issues, verify your Neon PostgreSQL connection string
- If the AI agent isn't responding, check that your Gemini API key is correctly set in the environment
- For frontend styling issues, ensure Tailwind CSS is properly configured