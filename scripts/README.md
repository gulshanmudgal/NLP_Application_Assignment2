# Development Deployment Scripts

This directory contains scripts for setting up and running the NLP Translation Application in development mode.

## Scripts

### 1. `deploy-dev.sh` (Full Development Deployment)

A comprehensive development deployment script that:
- Checks all prerequisites (Node.js, npm, Python 3, pip3)
- Installs all frontend dependencies (npm packages)
- Creates Python virtual environment and installs backend dependencies
- Starts both frontend and backend servers concurrently
- Performs health checks on both services
- Provides real-time log monitoring
- Handles graceful shutdown with Ctrl+C

**Usage:**
```bash
./scripts/deploy-dev.sh
```

**Features:**
- ✅ Automatic dependency installation
- ✅ Port conflict detection and resolution
- ✅ Health checks for both services
- ✅ Real-time log monitoring
- ✅ Graceful shutdown handling
- ✅ Colored output for better readability

**Services Started:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 2. `dev-simple.sh` (Quick Development Start)

A simpler script for quick development setup:
- Installs frontend and backend dependencies
- Starts backend in background
- Starts frontend in foreground

**Usage:**
```bash
./scripts/dev-simple.sh
```

## Makefile Integration

The scripts are integrated into the project Makefile for easy access:

```bash
# Quick development start
make dev

# Full development deployment with monitoring
make dev-full

# Traditional setup (dependencies only)
make setup

# Start only frontend
make frontend

# Start only backend  
make backend
```

## Prerequisites

Before running any development deployment script, ensure you have:

1. **Node.js** (v14 or higher)
2. **npm** (usually comes with Node.js)
3. **Python 3** (v3.8 or higher)
4. **pip3** (Python package manager)

## Ports Used

The application uses the following ports in development:

- **3000**: React frontend development server
- **8000**: FastAPI backend server

Make sure these ports are available before running the scripts.

## Logs

When using `deploy-dev.sh`, logs are saved to:
- Backend logs: `backend/backend.log`
- Frontend logs: `frontend/frontend.log`

## Stopping Services

### For `deploy-dev.sh`:
- Press `Ctrl+C` to stop both services gracefully

### For `dev-simple.sh`:
- Press `Ctrl+C` to stop the frontend
- Backend runs in background - you may need to find and kill the process manually:
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```

## Troubleshooting

### Port Already in Use
The `deploy-dev.sh` script automatically detects and kills processes using ports 3000 and 8000. If you encounter port conflicts with `dev-simple.sh`, manually kill the processes:

```bash
# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9

# Kill process on port 8000 (backend)  
lsof -ti:8000 | xargs kill -9
```

### Dependencies Not Installing
1. Ensure you have the correct Node.js and Python versions
2. Check your internet connection
3. Clear npm cache: `npm cache clean --force`
4. Remove `node_modules` and reinstall: `rm -rf frontend/node_modules && cd frontend && npm install`

### Backend Not Starting
1. Check if all Python dependencies are installed
2. Ensure you're using the correct Python version
3. Check the backend logs for detailed error messages

### Frontend Not Starting
1. Check if all npm packages are installed correctly
2. Ensure port 3000 is available
3. Check the frontend logs for detailed error messages

## Development Workflow

Recommended workflow for development:

1. **First time setup:**
   ```bash
   make dev-full
   ```

2. **Subsequent development sessions:**
   ```bash
   make dev
   ```

3. **When you need to see detailed logs:**
   ```bash
   make dev-full
   ```

4. **For testing individual components:**
   ```bash
   make backend  # Start only backend
   # or
   make frontend # Start only frontend
   ```
