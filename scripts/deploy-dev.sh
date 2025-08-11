#!/bin/bash

# NLP Translation Application - Development Deployment Script
# This script sets up the development environment and starts both frontend and backend services

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

# Function to kill process on port
kill_port() {
    if port_in_use $1; then
        print_warning "Port $1 is in use. Killing existing process..."
        kill -9 $(lsof -ti:$1) 2>/dev/null || true
        sleep 2
    fi
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Trap Ctrl+C and other signals
trap cleanup SIGINT SIGTERM EXIT

print_status "Starting NLP Translation Application Development Deployment"
echo "============================================================="

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/package.json" ] && [ ! -f "$PROJECT_ROOT/frontend/package.json" ]; then
    print_error "Not in the correct project directory. Please run this script from the project root."
    exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check Node.js
if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check npm
if ! command_exists npm; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

# Check Python
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check pip
if ! command_exists pip3; then
    print_error "pip3 is not installed. Please install pip3 first."
    exit 1
fi

print_success "All prerequisites found!"

# Navigate to project root
cd "$PROJECT_ROOT"

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
if [ -f "package-lock.json" ]; then
    npm ci
else
    npm install
fi
print_success "Frontend dependencies installed!"

# Install backend dependencies
print_status "Installing backend dependencies..."
cd "$PROJECT_ROOT/backend"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
print_success "Backend dependencies installed!"

# Check and kill existing processes on required ports
print_status "Checking for existing processes..."
kill_port 3000  # Frontend port
kill_port 8000  # Backend port

# Start backend server
print_status "Starting backend server..."
cd "$PROJECT_ROOT/backend"
source venv/bin/activate

# Start backend in background
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! port_in_use 8000; then
    print_error "Backend failed to start. Check backend.log for details."
    cat backend.log
    exit 1
fi

print_success "Backend server started on http://localhost:8000"

# Start frontend server
print_status "Starting frontend server..."
cd "$PROJECT_ROOT/frontend"

# Start frontend in background
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
print_status "Waiting for frontend server to start..."
timeout=60
counter=0
while ! port_in_use 3000 && [ $counter -lt $timeout ]; do
    sleep 1
    counter=$((counter + 1))
done

if ! port_in_use 3000; then
    print_error "Frontend failed to start within $timeout seconds. Check frontend.log for details."
    tail -20 frontend.log
    exit 1
fi

print_success "Frontend server started on http://localhost:3000"

# Health check
print_status "Performing health checks..."

# Check backend health
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    print_success "✅ Backend health check passed"
else
    print_warning "⚠️  Backend health check failed - service may still be starting"
fi

# Check frontend
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    print_success "✅ Frontend health check passed"
else
    print_warning "⚠️  Frontend health check failed - service may still be starting"
fi

echo ""
print_success "🚀 Development environment is ready!"
echo "=============================================="
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  Backend: $PROJECT_ROOT/backend/backend.log"
echo -e "  Frontend: $PROJECT_ROOT/frontend/frontend.log"
echo ""
echo -e "${YELLOW}To stop services:${NC} Press Ctrl+C"
echo ""

# Follow logs
print_status "Following logs (Ctrl+C to stop)..."
echo "=============================================="

# Function to tail logs with prefixes
tail_logs() {
    tail -f "$PROJECT_ROOT/backend/backend.log" | sed 's/^/[BACKEND] /' &
    tail -f "$PROJECT_ROOT/frontend/frontend.log" | sed 's/^/[FRONTEND] /' &
    wait
}

# Start tailing logs
tail_logs
