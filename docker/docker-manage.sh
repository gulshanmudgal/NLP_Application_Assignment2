#!/bin/bash

# Docker Management Script for NLP Translation Application
# Usage: ./docker-manage.sh [dev|prod|stop|clean|logs]

set -e

PROJECT_NAME="nlp-translation"
DOCKER_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$DOCKER_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
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

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

start_development() {
    print_info "Starting development environment..."
    cd "$DOCKER_DIR"
    
    # Build and start services
    docker-compose -f docker-compose.yml -p "${PROJECT_NAME}-dev" up --build -d
    
    print_success "Development environment started!"
    print_info "Frontend: http://localhost:3000"
    print_info "Backend API: http://localhost:8000"
    print_info "API Docs: http://localhost:8000/docs"
    print_info "Redis: localhost:6379"
    print_info "PostgreSQL: localhost:5432"
}

start_production() {
    print_info "Starting production environment..."
    cd "$DOCKER_DIR"
    
    # Build and start services
    docker-compose -f docker-compose.prod.yml -p "${PROJECT_NAME}-prod" up --build -d
    
    print_success "Production environment started!"
    print_info "Application: http://localhost"
    print_info "Backend API: http://localhost:8000"
}

stop_services() {
    print_info "Stopping all services..."
    cd "$DOCKER_DIR"
    
    # Stop development services
    docker-compose -f docker-compose.yml -p "${PROJECT_NAME}-dev" down || true
    
    # Stop production services
    docker-compose -f docker-compose.prod.yml -p "${PROJECT_NAME}-prod" down || true
    
    print_success "All services stopped!"
}

clean_all() {
    print_warning "This will remove all containers, images, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        cd "$DOCKER_DIR"
        
        # Stop and remove everything
        docker-compose -f docker-compose.yml -p "${PROJECT_NAME}-dev" down -v --rmi all || true
        docker-compose -f docker-compose.prod.yml -p "${PROJECT_NAME}-prod" down -v --rmi all || true
        
        # Remove unused volumes and networks
        docker volume prune -f
        docker network prune -f
        
        print_success "Cleanup completed!"
    else
        print_info "Cleanup cancelled."
    fi
}

show_logs() {
    cd "$DOCKER_DIR"
    
    print_info "Showing logs for development environment..."
    docker-compose -f docker-compose.yml -p "${PROJECT_NAME}-dev" logs -f --tail=100
}

show_status() {
    cd "$DOCKER_DIR"
    
    print_info "Development Environment Status:"
    docker-compose -f docker-compose.yml -p "${PROJECT_NAME}-dev" ps
    
    echo
    print_info "Production Environment Status:"
    docker-compose -f docker-compose.prod.yml -p "${PROJECT_NAME}-prod" ps
}

show_help() {
    echo "NLP Translation Application - Docker Management"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  dev       Start development environment"
    echo "  prod      Start production environment"
    echo "  stop      Stop all services"
    echo "  clean     Remove all containers, images, and volumes"
    echo "  logs      Show logs (development)"
    echo "  status    Show status of all services"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 dev     # Start development environment"
    echo "  $0 prod    # Start production environment"
    echo "  $0 logs    # View logs"
    echo "  $0 stop    # Stop all services"
}

# Main script logic
check_docker

case "${1:-help}" in
    "dev"|"development")
        start_development
        ;;
    "prod"|"production")
        start_production
        ;;
    "stop")
        stop_services
        ;;
    "clean")
        clean_all
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
