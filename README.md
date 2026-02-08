Hackathon 2 – Phase 5 Deployment

Project:
Todo Chatbot
GitHub Repo: https://github.com/JaveriaNigar/Hackathon-2_phase-Vis

Overview:
Phase 5 focuses on full deployment and advanced features:
- Backend: FastAPI + Dapr
- Frontend: Next.js
- Event-driven: Pub/Sub, State, Kafka demo using Python queue
- CI/CD: GitHub Actions
- Monitoring: Grafana Cloud

Goal: Fully functional, free-tier deployment, demo-ready online.

Deployment Steps:

1. Backend (FastAPI + Dapr)
- Platform: Replit Free Tier
- Install dependencies: fastapi, uvicorn[standard], dapr
- Run commands:
  uvicorn main:app --host 0.0.0.0 --port 3000
  dapr run --app-id todo-backend --app-port 3000 -- uvicorn main:app --host 0.0.0.0 --port 3000


2. Frontend (Next.js)
- Platform: Vercel Free Tier
- Connect Next.js repo
- Update API endpoint to point to Replit backend URL


3. Dapr Components
- Pub/Sub and State store inside Replit container
- Redis or Python queue used for demo
- Demo verified

4. Kafka Demo
- Local Python/asyncio queue used as free alternative
- Event-driven demo verified

5. CI/CD (GitHub Actions)
- Backend workflow: .github/workflows/deploy.yml
- Frontend workflow: similar setup
- Pushes auto-deploy backend and frontend verified

6. Monitoring and Logging
- Grafana Cloud Free Tier
- Prometheus metrics from FastAPI + Dapr

Final Status:
- Backend live on Replit URL
- Frontend live on Vercel URL
- Dapr working with Pub/Sub and State demo
- Kafka demo using Python queue
- CI/CD working via GitHub Actions
- Monitoring and logging working via Grafana Cloud

Notes:
- Project remains 100% free and card-less
- Fully demo-ready online
- Built following spec-driven workflow
- Video demos can be made directly from this setup
