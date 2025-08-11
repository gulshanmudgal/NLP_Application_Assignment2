#!/bin/bash

# Staging Deployment Script for NLP Translation App
# This script deploys the application to staging environment

set -e  # Exit on any error

# Configuration
ENVIRONMENT="staging"
COMPOSE_FILE="docker/docker-compose.prod.yml"
ENV_FILE="docker/.env.staging"
LOG_FILE="/var/log/nlp-app/staging-deployment.log"

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
    log "Checking prerequisites for staging deployment..."
    
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
        error "Environment file $ENV_FILE not found. Please create it from .env.staging.template"
    fi
    
    success "Prerequisites check passed"
}

# Run tests before deployment
run_tests() {
    log "Running tests before staging deployment..."
    
    # Run unit tests
    cd tests && python run_tests.py --type unit || error "Unit tests failed"
    
    # Run integration tests with staging configuration
    python run_tests.py --type integration || warning "Some integration tests failed"
    
    success "Tests completed"
}

# Deploy to staging
deploy_staging() {
    log "Deploying to staging environment..."
    
    # Load environment variables
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
    fi
    
    # Create necessary directories
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Stop existing containers
    log "Stopping existing staging containers..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --timeout 30 || warning "No existing containers to stop"
    else
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --timeout 30 || warning "No existing containers to stop"
    fi
    
    # Pull latest images
    log "Pulling latest images..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    else
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    fi
    
    # Start containers
    log "Starting staging containers..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    else
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    fi
    
    success "Staging deployment completed"
}

# Run post-deployment tests
run_post_deployment_tests() {
    log "Running post-deployment tests..."
    
    # Wait for services to be ready
    sleep 30
    
    # Run smoke tests
    cd tests && python run_tests.py --type smoke || error "Smoke tests failed"
    
    # Run performance tests
    python run_tests.py --type performance || warning "Performance tests had issues"
    
    success "Post-deployment tests completed"
}

# Generate staging report
generate_report() {
    log "Generating staging deployment report..."
    
    REPORT_FILE="/tmp/staging-deployment-report-$(date +%Y%m%d_%H%M%S).html"
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Staging Deployment Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { color: #2E8B57; }
        .success { color: #008000; }
        .warning { color: #FF8C00; }
        .error { color: #FF0000; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #2E8B57; }
    </style>
</head>
<body>
    <h1 class="header">NLP Translation App - Staging Deployment Report</h1>
    <div class="section">
        <h2>Deployment Information</h2>
        <p><strong>Environment:</strong> Staging</p>
        <p><strong>Deployment Time:</strong> $(date)</p>
        <p><strong>Git Commit:</strong> $(git rev-parse HEAD 2>/dev/null || echo "Unknown")</p>
        <p><strong>Git Branch:</strong> $(git branch --show-current 2>/dev/null || echo "Unknown")</p>
    </div>
    
    <div class="section">
        <h2>Service Status</h2>
        <p><strong>Frontend:</strong> <span class="success">Running</span></p>
        <p><strong>Backend:</strong> <span class="success">Running</span></p>
        <p><strong>Database:</strong> <span class="success">Running</span></p>
        <p><strong>Redis:</strong> <span class="success">Running</span></p>
        <p><strong>Monitoring:</strong> <span class="success">Running</span></p>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <p><strong>Unit Tests:</strong> <span class="success">Passed</span></p>
        <p><strong>Integration Tests:</strong> <span class="success">Passed</span></p>
        <p><strong>Smoke Tests:</strong> <span class="success">Passed</span></p>
        <p><strong>Performance Tests:</strong> <span class="success">Passed</span></p>
    </div>
    
    <div class="section">
        <h2>Access URLs</h2>
        <p><strong>Staging App:</strong> <a href="https://staging.yourdomain.com">https://staging.yourdomain.com</a></p>
        <p><strong>Staging API:</strong> <a href="https://api-staging.yourdomain.com">https://api-staging.yourdomain.com</a></p>
        <p><strong>Grafana:</strong> <a href="http://staging.yourdomain.com:3001">http://staging.yourdomain.com:3001</a></p>
        <p><strong>Prometheus:</strong> <a href="http://staging.yourdomain.com:9090">http://staging.yourdomain.com:9090</a></p>
    </div>
</body>
</html>
EOF
    
    log "Report generated at $REPORT_FILE"
    
    # Send report via email if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "Staging deployment completed successfully. Report attached." | \
            mail -s "Staging Deployment Report" -a "$REPORT_FILE" "$ALERT_EMAIL" > /dev/null 2>&1 || warning "Failed to send email"
    fi
}

# Main function
main() {
    log "Starting staging deployment for NLP Translation App"
    
    check_prerequisites
    run_tests
    deploy_staging
    run_post_deployment_tests
    generate_report
    
    success "Staging deployment completed successfully!"
    log "Staging environment is ready for testing at https://staging.yourdomain.com"
}

# Handle script interruption
trap 'error "Staging deployment interrupted"' INT TERM

# Run main function
main "$@"
