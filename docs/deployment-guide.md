# Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the NLP Translation Application to production environments. The application uses Docker containers with comprehensive monitoring, security, and high availability features.

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended) or macOS
- **Docker**: Version 24.0+ with Docker Compose
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: Minimum 50GB available space
- **Network**: HTTPS/SSL certificates for production domains

### Required Software

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose (if not included)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/nlp-translation-app.git
cd nlp-translation-app
```

### 2. Configure Environment Variables

```bash
# Copy the production environment template
cp docker/.env.prod.template docker/.env.prod

# Edit the production environment file
nano docker/.env.prod
```

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `nlp_user` |
| `POSTGRES_PASSWORD` | Database password | `secure_password_123` |
| `POSTGRES_DB` | Database name | `nlp_translation_prod` |
| `REDIS_PASSWORD` | Redis password | `redis_password_123` |
| `SECRET_KEY` | Django secret key | `your-very-long-secret-key` |
| `ALLOWED_HOSTS` | Allowed hostnames | `yourdomain.com,api.yourdomain.com` |
| `CORS_ORIGINS` | CORS allowed origins | `https://yourdomain.com` |
| `GRAFANA_PASSWORD` | Grafana admin password | `grafana_admin_123` |

### 3. SSL Certificate Setup

Place your SSL certificates in the appropriate directory:

```bash
mkdir -p docker/nginx/ssl
cp your-cert.pem docker/nginx/ssl/cert.pem
cp your-private-key.pem docker/nginx/ssl/key.pem
```

## Deployment Process

### Option 1: Automated Deployment (Recommended)

Use the provided deployment script:

```bash
# Make the script executable
chmod +x scripts/deploy-production.sh

# Run the deployment
./scripts/deploy-production.sh
```

The script will:
- Check prerequisites
- Create backups
- Pull latest images
- Deploy containers
- Run health checks
- Send notifications

### Option 2: Manual Deployment

#### Step 1: Pull Latest Images

```bash
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod pull
```

#### Step 2: Stop Existing Containers

```bash
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod down
```

#### Step 3: Start New Containers

```bash
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod up -d
```

#### Step 4: Verify Deployment

```bash
# Check container status
docker ps

# Check logs
docker-compose -f docker/docker-compose.prod.yml logs -f
```

## Post-Deployment Verification

### 1. Health Checks

```bash
# Backend API health
curl http://localhost:8000/health

# Frontend availability
curl http://localhost:80

# Database connection
docker exec nlp_postgres_prod pg_isready -U nlp_user

# Redis connection
docker exec nlp_redis_prod redis-cli ping
```

### 2. Functional Testing

```bash
# Run smoke tests
cd tests
python run_tests.py --type smoke

# Test translation functionality
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "source_lang": "en", "target_lang": "es"}'
```

### 3. Performance Testing

```bash
# Run performance tests
python run_tests.py --type performance

# Monitor resource usage
docker stats
```

## Monitoring and Observability

### Access Monitoring Dashboards

- **Grafana**: http://your-domain:3001
  - Username: `admin`
  - Password: Set in `GRAFANA_PASSWORD`

- **Prometheus**: http://your-domain:9090
  - Metrics and alerting interface

### Key Metrics to Monitor

1. **Application Metrics**
   - Request rate and response time
   - Error rate and status codes
   - Translation request volume
   - Model loading performance

2. **Infrastructure Metrics**
   - CPU and memory usage
   - Disk space and I/O
   - Network throughput
   - Container health status

3. **Database Metrics**
   - Connection pool usage
   - Query performance
   - Storage utilization
   - Backup status

### Setting Up Alerts

Configure alert rules in `docker/monitoring/rules/nlp_app.yml`:

```yaml
# Example alert for high error rate
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High error rate detected"
```

## Backup and Disaster Recovery

### Automated Backups

Backups are automatically created during deployment. Manual backup:

```bash
# Create backup directory
mkdir -p /var/backups/nlp-app

# Backup PostgreSQL
docker exec nlp_postgres_prod pg_dumpall -U nlp_user > /var/backups/nlp-app/postgres_$(date +%Y%m%d).sql

# Backup Redis
docker exec nlp_redis_prod redis-cli --rdb - > /var/backups/nlp-app/redis_$(date +%Y%m%d).rdb
```

### Disaster Recovery

In case of complete system failure:

1. **Restore from Backup**
   ```bash
   # Restore PostgreSQL
   docker exec -i nlp_postgres_prod psql -U nlp_user < /var/backups/nlp-app/postgres_backup.sql
   
   # Restore Redis
   docker cp /var/backups/nlp-app/redis_backup.rdb nlp_redis_prod:/data/dump.rdb
   docker restart nlp_redis_prod
   ```

2. **Verify Data Integrity**
   ```bash
   # Check database
   docker exec nlp_postgres_prod psql -U nlp_user -d nlp_translation_prod -c "\dt"
   
   # Check Redis
   docker exec nlp_redis_prod redis-cli info
   ```

## Security Configuration

### 1. Network Security

- Use HTTPS/SSL for all external communications
- Implement proper firewall rules
- Use Docker networks for container isolation

### 2. Application Security

- Keep SECRET_KEY secure and unique
- Use strong passwords for all services
- Regularly update container images
- Implement rate limiting

### 3. Database Security

- Use strong database passwords
- Enable PostgreSQL SSL connections
- Restrict database access to application containers only

### 4. Monitoring Security

- Secure Grafana with strong admin password
- Use authentication for Prometheus if exposed
- Monitor for security events and anomalies

## Scaling and Performance

### Horizontal Scaling

```yaml
# In docker-compose.prod.yml
backend:
  deploy:
    replicas: 4  # Increase number of backend instances
```

### Vertical Scaling

```yaml
# Increase resource limits
backend:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 4G
```

### Database Optimization

```sql
-- Example PostgreSQL optimizations
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '2GB';
ALTER SYSTEM SET work_mem = '8MB';
```

### Redis Optimization

```bash
# Increase Redis memory limit
redis-cli CONFIG SET maxmemory 1gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker logs nlp_backend_prod
   
   # Check environment variables
   docker exec nlp_backend_prod env
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   docker exec nlp_postgres_prod pg_isready
   
   # Check network connectivity
   docker exec nlp_backend_prod nc -zv postgres 5432
   ```

3. **High Memory Usage**
   ```bash
   # Check memory usage
   docker stats
   
   # Adjust container limits
   docker-compose -f docker/docker-compose.prod.yml up -d --force-recreate
   ```

4. **SSL Certificate Issues**
   ```bash
   # Verify certificate files
   openssl x509 -in docker/nginx/ssl/cert.pem -text -noout
   
   # Check Nginx configuration
   docker exec nlp_nginx_prod nginx -t
   ```

### Performance Issues

1. **Slow Response Times**
   - Check backend logs for errors
   - Monitor database query performance
   - Verify cache hit rates
   - Check ML model loading times

2. **High CPU Usage**
   - Monitor translation request volume
   - Check for infinite loops in logs
   - Verify resource limits are appropriate

3. **Memory Leaks**
   - Monitor memory usage trends
   - Check for unclosed database connections
   - Verify ML model memory cleanup

## Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Review monitoring dashboards
   - Check backup integrity
   - Update container images
   - Review security logs

2. **Monthly**
   - Rotate log files
   - Review and tune performance
   - Update SSL certificates if needed
   - Test disaster recovery procedures

3. **Quarterly**
   - Security audit and penetration testing
   - Capacity planning review
   - Update monitoring and alerting rules

### Update Procedures

```bash
# 1. Pull latest code
git pull origin main

# 2. Run tests
cd tests && python run_tests.py

# 3. Deploy to staging first
./scripts/deploy-staging.sh

# 4. Deploy to production
./scripts/deploy-production.sh
```

## Support and Contacts

- **Operations Team**: ops@yourdomain.com
- **Development Team**: dev@yourdomain.com
- **Security Team**: security@yourdomain.com
- **On-call Rotation**: oncall@yourdomain.com

## Additional Resources

- [API Documentation](api-documentation.md)
- [Monitoring Runbook](monitoring-runbook.md)
- [Security Guidelines](security-guidelines.md)
- [Performance Tuning Guide](performance-tuning.md)
