#!/bin/bash
# Build script for todo app images

# Build backend
cd /mnt/c/Projects/hachathon-phase-4/backend
docker build -t todo-backend:latest .

# Build frontend
cd /mnt/c/Projects/hachathon-phase-4/frontend
docker build -t todo-frontend:latest .