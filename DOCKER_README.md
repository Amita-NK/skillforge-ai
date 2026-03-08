# Docker Deployment for SkillForge AI+

Quick guide for running SkillForge AI+ with Docker.

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your AWS credentials

# 2. Start all services
docker-compose up -d

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f
```

## Services

The docker-compose setup includes:

- **ai-service** (Port 8000) - FastAPI AI microservice
- **backend** (Port 5000) - Flask API gateway
- **db** (Port 3306) - MySQL database (optional)

## Configuration

### Required Environment Variables

```env
# AWS Credentials (Required)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
BEDROCK_MODEL_ID=anthropic.claude-v2

# Backend Secrets
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Optional: OpenSearch for RAG

```env
OPENSEARCH_HOST=your-endpoint.es.amazonaws.com
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=your_password
```

### Optional: MySQL Database

Uncomment the `db` service in `docker-compose.yml` and add:

```env
DATABASE_URL=mysql+pymysql://skillforge:password@db:3306/skillforge
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=skillforge
MYSQL_USER=skillforge
MYSQL_PASSWORD=password
```

## Commands

### Start Services

```bash
# Start in foreground
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up ai-service
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ai-service

# Last 100 lines
docker-compose logs --tail=100
```

### Rebuild Images

```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build ai-service

# Rebuild without cache
docker-compose build --no-cache
```

### Execute Commands in Container

```bash
# Open shell in backend
docker-compose exec backend bash

# Run tests in AI service
docker-compose exec ai-service pytest tests/ -v

# Check Python version
docker-compose exec ai-service python --version
```

## Testing

### Test AI Service

```bash
# Health check
curl http://localhost:8000/health

# Generate explanation
curl -X POST http://localhost:8000/tutor/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search"}'
```

### Test Backend

```bash
# Health check
curl http://localhost:5000/health

# Register user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "password123"
  }'
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check if ports are in use
netstat -an | grep 8000
netstat -an | grep 5000

# Remove old containers
docker-compose down
docker-compose up -d
```

### Cannot Connect to Services

```bash
# Check container status
docker-compose ps

# Check networks
docker network ls
docker network inspect skillforge-network

# Restart services
docker-compose restart
```

### Database Issues

```bash
# Check database logs
docker-compose logs db

# Connect to database
docker-compose exec db mysql -u skillforge -p

# Reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

### AWS Credentials Not Working

```bash
# Verify environment variables
docker-compose exec ai-service env | grep AWS

# Test AWS connection
docker-compose exec ai-service python -c "import boto3; print(boto3.client('bedrock-runtime', region_name='us-east-1'))"
```

### Out of Memory

```bash
# Check resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Recommended: 4GB+ for all services
```

## Development Workflow

### Making Code Changes

1. **Edit code locally**
2. **Rebuild affected service**
   ```bash
   docker-compose build ai-service
   ```
3. **Restart service**
   ```bash
   docker-compose up -d ai-service
   ```
4. **View logs**
   ```bash
   docker-compose logs -f ai-service
   ```

### Running Tests

```bash
# AI Service tests
docker-compose exec ai-service pytest tests/ -v

# Backend tests
docker-compose exec backend pytest tests/ -v
```

### Debugging

```bash
# Open shell in container
docker-compose exec ai-service bash

# Check Python packages
docker-compose exec ai-service pip list

# Check file structure
docker-compose exec ai-service ls -la
```

## Production Considerations

### Security

- Use secrets management (AWS Secrets Manager, HashiCorp Vault)
- Don't commit .env file
- Use strong passwords
- Enable HTTPS
- Restrict network access

### Performance

- Use production WSGI server (Gunicorn) for Flask
- Enable connection pooling
- Configure resource limits
- Use CDN for static assets
- Enable caching

### Monitoring

- Add health check endpoints
- Configure log aggregation
- Set up metrics collection
- Enable alerting
- Monitor resource usage

### Scaling

- Use Docker Swarm or Kubernetes
- Configure auto-scaling
- Use load balancer
- Implement session management
- Use managed database service

## Docker Compose Reference

### Service Dependencies

```yaml
backend:
  depends_on:
    ai-service:
      condition: service_healthy
```

### Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

### Volumes

```yaml
volumes:
  - backend-data:/app/data  # Persistent storage
  - ./backend:/app          # Development mount
```

### Networks

```yaml
networks:
  skillforge-network:
    driver: bridge
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)

## Support

For Docker-related issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Check Docker version: `docker --version`
4. Review Docker Desktop settings
5. Consult Docker documentation
