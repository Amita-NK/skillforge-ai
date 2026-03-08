# Quick Deployment Guide

## 🚀 Local Development Setup (5 Minutes)

### Prerequisites
- Docker and Docker Compose installed
- AWS credentials configured (for Bedrock access)
- Python 3.11+ (for local testing)
- Node.js 18+ (for frontend development)

### Step 1: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your AWS credentials
# Required variables:
# - AWS_REGION=us-east-1
# - AWS_ACCESS_KEY_ID=your_key
# - AWS_SECRET_ACCESS_KEY=your_secret
# - BEDROCK_MODEL_ID=anthropic.claude-v2
```

### Step 2: Start All Services
```bash
# Start backend services with Docker
docker-compose up -d

# Services will be available at:
# - Backend API: http://localhost:5000
# - AI Service: http://localhost:8000 (internal only)
# - OpenSearch: http://localhost:9200
# - MySQL: localhost:3306
```

### Step 3: Verify Services
```bash
# Check backend health
curl http://localhost:5000/health

# Expected response:
# {"status":"healthy","service":"SkillForge Backend","timestamp":"..."}

# Check AI service health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"SkillForge AI Service"}
```

### Step 4: Test the API

#### Register a User
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# Save the JWT token from the response
```

#### Get AI Explanation
```bash
curl -X POST http://localhost:5000/ai/explain \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "topic": "recursion in programming"
  }'
```

#### Generate Quiz
```bash
curl -X POST http://localhost:5000/ai/quiz \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "topic": "Python basics",
    "difficulty": "medium",
    "count": 5
  }'
```

#### Debug Code
```bash
curl -X POST http://localhost:5000/ai/debug \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "language": "python",
    "code": "def hello()\n    print(\"Hello\")"
  }'
```

---

## 🧪 Running Tests

### AI Service Tests
```bash
cd ai_service
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_bedrock_client.py -v
python -m pytest tests/test_property_*.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

---

## 🔧 Development Workflow

### AI Service Development
```bash
cd ai_service

# Install dependencies
pip install -r requirements.txt

# Run service locally (without Docker)
uvicorn main:app --reload --port 8000

# Run tests
python -m pytest tests/ -v
```

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run service locally
python app.py

# Run tests
python -m pytest tests/ -v
```

### Frontend Development
```bash
cd src/web

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

---

## 📊 Monitoring and Debugging

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ai-service
docker-compose logs -f opensearch
```

### Access Database
```bash
# Connect to MySQL
docker-compose exec db mysql -u skillforge -p

# View tables
USE skillforge;
SHOW TABLES;
SELECT * FROM users;
SELECT * FROM user_progress;
SELECT * FROM quiz_history;
```

### Access OpenSearch
```bash
# Check cluster health
curl http://localhost:9200/_cluster/health?pretty

# List indices
curl http://localhost:9200/_cat/indices?v

# Search documents
curl http://localhost:9200/documents/_search?pretty
```

---

## 🛑 Stopping Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Issue: AI Service Can't Connect to Bedrock
**Solution**: Check AWS credentials in .env file
```bash
# Verify credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### Issue: Backend Can't Connect to AI Service
**Solution**: Ensure AI service is running and accessible
```bash
# Check AI service health
curl http://localhost:8000/health

# Check Docker network
docker network inspect skillforge-ai_default
```

### Issue: Database Connection Errors
**Solution**: Wait for MySQL to fully initialize
```bash
# Check MySQL logs
docker-compose logs db

# Restart backend after MySQL is ready
docker-compose restart backend
```

### Issue: OpenSearch Not Starting
**Solution**: Increase Docker memory allocation
```bash
# Edit docker-compose.yml
# Reduce opensearch memory:
# - "ES_JAVA_OPTS=-Xms256m -Xmx256m"
```

---

## 📦 Production Deployment (AWS)

### Prerequisites
- AWS account with appropriate permissions
- Terraform installed
- AWS CLI configured

### Step 1: Infrastructure Setup (Coming Soon)
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Step 2: Build and Push Docker Images
```bash
# Build images
docker build -t skillforge-ai-service:latest ./ai_service
docker build -t skillforge-backend:latest ./backend

# Tag for ECR
docker tag skillforge-ai-service:latest <ECR_URI>/skillforge-ai-service:latest
docker tag skillforge-backend:latest <ECR_URI>/skillforge-backend:latest

# Push to ECR
docker push <ECR_URI>/skillforge-ai-service:latest
docker push <ECR_URI>/skillforge-backend:latest
```

### Step 3: Deploy to ECS (Coming Soon)
```bash
# Update ECS services
aws ecs update-service --cluster skillforge --service ai-service --force-new-deployment
aws ecs update-service --cluster skillforge --service backend --force-new-deployment
```

---

## 🔐 Security Checklist

- [ ] Change default passwords in .env
- [ ] Use strong JWT secret
- [ ] Enable HTTPS in production
- [ ] Restrict CORS origins
- [ ] Use AWS IAM roles instead of access keys
- [ ] Enable CloudWatch logging
- [ ] Set up AWS WAF
- [ ] Enable database encryption
- [ ] Use secrets manager for sensitive data
- [ ] Implement rate limiting

---

## 📈 Performance Optimization

### AI Service
- Use connection pooling for Bedrock
- Cache frequent embeddings
- Implement request batching
- Use async/await for concurrent requests

### Backend
- Enable database query caching
- Use Redis for session storage
- Implement API rate limiting
- Enable gzip compression

### Frontend
- Enable Next.js static generation
- Use CDN for static assets
- Implement code splitting
- Enable image optimization

---

## 🎯 Next Steps

1. ✅ Local development setup complete
2. ⏳ Deploy to AWS (optional)
3. ⏳ Set up CI/CD pipeline
4. ⏳ Configure monitoring and alerting
5. ⏳ Performance testing
6. ⏳ Security audit

---

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review documentation in `/docs`
3. Check test output: `pytest tests/ -v`
4. Verify environment variables in `.env`

---

## ✅ Success Indicators

Your deployment is successful when:
- ✅ All services start without errors
- ✅ Health checks return 200 OK
- ✅ User registration works
- ✅ JWT authentication works
- ✅ AI endpoints return responses
- ✅ Database stores data correctly
- ✅ Tests pass (102 tests)

**You're ready to start using SkillForge AI+!** 🎉
