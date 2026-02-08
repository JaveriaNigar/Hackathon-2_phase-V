# Deployment Instructions for Todo AI Chatbot

## Step 1: Create GitHub Repositories

Before you can push the code, you need to create two GitHub repositories:

1. **Backend Repository**: `FastAPI-Todo-Chatbot`
2. **Frontend Repository**: `Nextjs-Todo-Frontend`

To create these repositories:
1. Go to GitHub.com
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Create the `FastAPI-Todo-Chatbot` repository
5. Create the `Nextjs-Todo-Frontend` repository

## Step 2: Push Code to Repositories

Once you've created the repositories, run the following commands:

### For Backend:
```bash
cd /tmp/minimal-backend
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/FastAPI-Todo-Chatbot.git
git branch -M main
git push -u origin main
```

### For Frontend:
```bash
cd /tmp/minimal-frontend
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/Nextjs-Todo-Frontend.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy Backend to Replit

1. Go to [Replit.com](https://replit.com/)
2. Sign in with your GitHub account
3. Click "Create" and select "Import from GitHub"
4. Import the `FastAPI-Todo-Chatbot` repository
5. Once imported, go to the shell and install dependencies:
   ```bash
   pip install fastapi uvicorn[standard] dapr
   ```
6. Run the application:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 3000
   ```
7. To run with Dapr:
   ```bash
   dapr run --app-id todo-backend --app-port 3000 -- uvicorn src.api.main:app --host 0.0.0.0 --port 3000
   ```

## Step 4: Deploy Frontend to Vercel

1. Go to [Vercel.com](https://vercel.com/)
2. Sign in with your GitHub account
3. Click "New Project"
4. Import the `Nextjs-Todo-Frontend` repository
5. Configure the deployment settings:
   - Framework Preset: Next.js
   - Environment Variables:
     - `NEXT_PUBLIC_API_BASE_URL`: Set this to your Replit backend URL
6. Click "Deploy"

## Step 5: Configure Dapr Components

For the Dapr components in Replit, create a components directory and add the following files:

### For State Store (Redis):
Create `components/statestore.yaml`:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

### For Pub/Sub (Redis):
Create `components/pubsub.yaml`:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

## Step 6: Set Up Kafka Alternative

Since Kafka requires a credit card, use Python asyncio Queue for pubsub demo:

Create a simple queue service in your backend:
```python
import asyncio
from typing import Dict, List

class SimpleQueueService:
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}
    
    async def publish(self, topic: str, message: dict):
        if topic not in self.queues:
            self.queues[topic] = asyncio.Queue()
        await self.queues[topic].put(message)
    
    async def subscribe(self, topic: str):
        if topic not in self.queues:
            self.queues[topic] = asyncio.Queue()
        return await self.queues[topic].get()

# Initialize globally
queue_service = SimpleQueueService()
```

## Step 7: GitHub Actions CI/CD

Create `.github/workflows/deploy-backend.yml` in the backend repo:
```yaml
name: Deploy Backend to Replit

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Replit
      run: |
        # Add your Replit deployment script here
        # This might involve using Replit's API or SSH
```

Create `.github/workflows/deploy-frontend.yml` in the frontend repo:
```yaml
name: Deploy Frontend to Vercel

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Vercel
      run: |
        # Vercel deployments happen automatically when you connect your repo
        # This step is just for any additional processing
```

## Step 8: Grafana Monitoring Setup

1. Go to [Grafana Cloud](https://grafana.com/products/cloud/)
2. Sign up for a free account
3. Follow the instructions to set up Prometheus and Grafana
4. Add the following to your FastAPI app for metrics:
   ```python
   from prometheus_fastapi_instrumentator import Instrumentator
   
   instrumentator = Instrumentator()
   instrumentator.instrument(app).expose(app)
   ```

## Step 9: Update Frontend API Endpoint

In your frontend's `.env.local` file, update the API URL:
```
NEXT_PUBLIC_API_BASE_URL=https://YOUR_REPLIT_APP_NAME.repl.co/api
```

## Verification

After completing all steps:
1. Visit your Vercel frontend URL
2. Verify that it connects to your Replit backend
3. Test creating, updating, and deleting tasks
4. Verify that the AI agent responds correctly
5. Check that monitoring is working in Grafana