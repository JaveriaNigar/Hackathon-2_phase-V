# Deploying to Replit

## Quick Setup

1. Create a new Repl on [Replit](https://replit.com)
2. Import your `FastAPI-Todo-Chatbot` repository
3. The `.replit` file will configure the run command automatically

## Dependencies Installation

After importing, run in the shell:
```bash
pip install fastapi uvicorn[standard] dapr
pip install -r requirements.txt
```

## Running the Application

The application is configured to run with Dapr. The `.replit` file contains the command:
```
dapr run --app-id todo-backend --app-port 3000 -- uvicorn src.api.main:app --host 0.0.0.0 --port 3000
```

If Dapr is not available in the free tier, you can run without it:
```
uvicorn src.api.main:app --host 0.0.0.0 --port 3000
```

## Environment Variables

Set the following environment variables in Replit:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `DATABASE_URL`: Your Neon PostgreSQL connection string

## Dapr Configuration

To use Dapr features in Replit:
1. Create a `components` folder in your project
2. Add your Dapr component files (state store, pub/sub, etc.)
3. The application is configured to use Dapr for state management and pub/sub

## Port Configuration

The application runs on port 3000, which is the standard for Replit web applications.