# Makefile for NLP Translation Application

# Variables
PYTHON = python3
PIP = pip3
DOCKER_COMPOSE = docker-compose -f docker/docker-compose.yml
TEST_RUNNER = tests/run_tests.py
VENV = venv

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help test test-unit test-integration test-performance test-smoke test-all clean setup install-test-deps docker-up docker-down docker-restart frontend backend dev dev-full

help: ## Show this help message
	@echo "$(GREEN)NLP Translation Application - Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup Commands:$(NC)"
	@echo "  setup              - Set up development environment"
	@echo "  install-test-deps  - Install testing dependencies"
	@echo ""
	@echo "$(YELLOW)Development Commands:$(NC)"
	@echo "  dev                - Install dependencies and start both frontend and backend"
	@echo "  dev-full           - Full development deployment with logging and health checks"
	@echo "  frontend           - Start React frontend development server"
	@echo "  backend            - Start FastAPI backend development server"
	@echo ""
	@echo "$(YELLOW)Docker Commands:$(NC)"
	@echo "  docker-up          - Start Docker services"
	@echo "  docker-down        - Stop Docker services"
	@echo "  docker-restart     - Restart Docker services"
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(NC)"
	@echo "  test-smoke         - Run smoke tests (quick validation)"
	@echo "  test-unit          - Run unit tests"
	@echo "  test-integration   - Run integration tests"
	@echo "  test-performance   - Run performance tests"
	@echo "  test-all           - Run all tests"
	@echo "  test               - Run smoke tests (default)"
	@echo ""
	@echo "$(YELLOW)Utility Commands:$(NC)"
	@echo "  clean              - Clean test artifacts and cache"
	@echo "  check-health       - Check if services are healthy"
	@echo ""

# Setup development environment
setup:
	@echo "Setting up development environment..."
	cd frontend && npm install
	cd backend && pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete! Edit .env file with your configuration."

# Quick development start - install dependencies and start both services
dev:
	@echo "$(GREEN)Starting development environment...$(NC)"
	./scripts/dev-simple.sh

# Full development deployment with logging and health checks
dev-full:
	@echo "$(GREEN)Starting full development deployment...$(NC)"
	./scripts/deploy-dev.sh

# Start frontend development server
frontend:
	cd frontend && npm start

# Start backend development server
backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start all services with Docker
docker-up:
	docker-compose -f docker/docker-compose.yml up -d

# Stop Docker services
docker-down:
	docker-compose -f docker/docker-compose.yml down

# Run tests
test: test-smoke

test-smoke: ## Run smoke tests for quick validation
	@echo "$(GREEN)Running smoke tests...$(NC)"
	$(PYTHON) $(TEST_RUNNER) --smoke

test-integration: ## Run integration tests  
	@echo "$(GREEN)Running integration tests...$(NC)"
	$(PYTHON) $(TEST_RUNNER) --integration

test-performance: ## Run performance tests
	@echo "$(GREEN)Running performance tests...$(NC)"
	$(PYTHON) $(TEST_RUNNER) --performance

test-all: ## Run all test suites
	@echo "$(GREEN)Running complete test suite...$(NC)"
	$(PYTHON) $(TEST_RUNNER) --all

check-health: ## Check if services are healthy
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -s http://localhost:8000/health | grep -q "healthy" && echo "$(GREEN)✅ Backend is healthy$(NC)" || echo "$(RED)❌ Backend is not healthy$(NC)"

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	cd frontend && rm -rf build/
	docker system prune -f
