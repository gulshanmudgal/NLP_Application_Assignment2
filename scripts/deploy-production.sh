#!/bin/bash

# Production Deployment Script for NLP Translation App
# This script deploys the application to production environment

set -e  # Exit on any error

# Configuration
ENVIRONMENT="production"
COMPOSE_FILE="docker/docker-compose.prod.yml"
ENV_FILE="docker/.env.prod"
BACKUP_DIR="/var/backups/nlp-app"
LOG_FILE="/var/log/nlp-app/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running"
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file $ENV_FILE not found. Please create it from .env.prod.template"
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Docker compose file $COMPOSE_FILE not found"
    fi
    
    success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "docker/nginx/ssl"
    mkdir -p "docker/postgres"
    mkdir -p "docker/redis"
    
    success "Directories created"
}

# Backup current data
backup_data() {
    log "Creating backup of current data..."
    
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup PostgreSQL data if container is running
    if docker ps --format "table {{.Names}}" | grep -q "nlp_postgres_prod"; then
        log "Backing up PostgreSQL database..."
        docker exec nlp_postgres_prod pg_dumpall -U "$POSTGRES_USER" > "$BACKUP_PATH/postgres_backup.sql"
    fi
    
    # Backup Redis data if container is running
    if docker ps --format "table {{.Names}}" | grep -q "nlp_redis_prod"; then
        log "Backing up Redis data..."
        docker exec nlp_redis_prod redis-cli --rdb - > "$BACKUP_PATH/redis_backup.rdb"
    fi
    
    # Backup application logs
    if [ -d "/var/log/nlp-app" ]; then
        log "Backing up application logs..."
        cp -r /var/log/nlp-app "$BACKUP_PATH/"
    fi
    
    success "Backup created at $BACKUP_PATH"
}

# Pull latest images
pull_images() {
    log "Pulling latest Docker images..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    else
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    fi
    
    success "Images pulled successfully"
}

# Run health checks
health_check() {
    log "Running health checks..."
    
    # Wait for services to be ready
    sleep 30
    
    # Check backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Backend health check passed"
    else
        error "Backend health check failed"
    fi
    
    # Check frontend availability
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        success "Frontend health check passed"
    else
        warning "Frontend health check failed, but continuing..."
    fi
    
    # Check database connection
    if docker exec nlp_postgres_prod pg_isready -U "$POSTGRES_USER" > /dev/null 2>&1; then
        success "Database health check passed"
    else
        error "Database health check failed"
    fi
    
    # Check Redis connection
    if docker exec nlp_redis_prod redis-cli ping > /dev/null 2>&1; then
        success "Redis health check passed"
    else
        error "Redis health check failed"
    fi
}

# Deploy application
deploy() {
    log "Starting deployment process..."
    
    # Stop existing containers gracefully
    log "Stopping existing containers..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --timeout 30
    else
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --timeout 30
    fi
    
    # Start new containers
    log "Starting new containers..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    else
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    fi
    
    success "Containers started successfully"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Wait for database to be ready
    sleep 10
    
    # Run migrations (adjust command based on your migration system)
    docker exec nlp_backend_prod python manage.py migrate || warning "Migration command failed or not applicable"
    
    success "Migrations completed"
}

# Clean up old images
cleanup() {
    log "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f
    
    success "Cleanup completed"
}

# Send deployment notification
send_notification() {
    log "Sending deployment notification..."
    
    # Send to Slack if webhook is configured
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 NLP Translation App deployed to production successfully!\"}" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || warning "Failed to send Slack notification"
    fi
    
    # Send email if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "NLP Translation App deployed to production successfully at $(date)" | \
            mail -s "Production Deployment Success" "$ALERT_EMAIL" > /dev/null 2>&1 || warning "Failed to send email notification"
    fi
    
    success "Notifications sent"
}

# Main deployment function
main() {
    log "Starting production deployment for NLP Translation App"
    
    # Load environment variables
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
    fi
    
    check_prerequisites
    create_directories
    backup_data
    pull_images
    deploy
    run_migrations
    health_check
    cleanup
    send_notification
    
    success "Production deployment completed successfully!"
    log "Application is now running at:"
    log "  - Frontend: https://yourdomain.com"
    log "  - API: https://api.yourdomain.com"
    log "  - Monitoring: http://localhost:3001 (Grafana)"
    log "  - Metrics: http://localhost:9090 (Prometheus)"
}

# Handle script interruption
trap 'error "Deployment interrupted"' INT TERM

# Run main function
main "$@"
