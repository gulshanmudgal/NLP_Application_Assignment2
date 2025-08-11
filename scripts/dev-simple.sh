#!/bin/bash

# Simple development setup and start script
# This script installs dependencies and starts both services

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Setting up development environment...${NC}"

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
cd frontend && npm install

# Install backend dependencies  
echo -e "${YELLOW}Installing backend dependencies...${NC}"
cd ../backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo -e "${GREEN}Dependencies installed!${NC}"
echo -e "${YELLOW}Starting services...${NC}"

# Start backend in background
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Start frontend
cd ../frontend
npm start
