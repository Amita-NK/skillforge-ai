# SkillForge AI+ - Quick Reference Card

**For AI Agents & New Developers**

---

## 🎯 What Is This?

AI-powered learning platform with:
- AI Tutoring (explain concepts)
- Quiz Generation (adaptive difficulty)
- Code Debugging (AI analysis)
- Progress Tracking (personalized recommendations)

---

## 🏗️ Architecture (3-Tier)

```
Frontend (Next.js:3000) 
    ↓ HTTP
Backend (Flask:5000) 
    ↓ HTTP
AI Service (FastAPI:8000) 
    ↓ boto3
Amazon Bedrock (qwen.qwen3-coder-next)
```

---

## 📁 Key Files

```
ai_service/
  ├── bedrock_client.py      ⭐ Bedrock Converse API
  ├── main.py                FastAPI app
  ├── tutor.py               AI tutoring
  ├── quiz.py                Quiz generation
  └── test_bedrock_converse.py  ⭐ Test script

backend/
  ├── app.py                 Flask API gateway
  ├── database.py            SQLAlchemy models
  └── services.py            Business logic

terraform/
  ├── main.tf                Infrastructure
  ├── modules/
  │   ├── bedrock-iam/       ⭐ IAM policies
  │   └── ecs-autoscaling/   ⭐ Auto-scaling
  └── environments/
      ├── dev/               ~$305/month
      ├── prod/              ~$790/month
      └── cost-optimized/    ~$160/month ⭐
```

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Configure
cp ai_service/.env.example ai_service/.env
nano ai_service/.env  # Set AWS credentials

# 2. Test Bedrock
cd ai_service
python test_bedrock_converse.py

# 3. Start Services
cd ..
docker-compose up -d

# 4. Verify
curl http://localhost:8000/health
curl http://localhost:5000/health

# 5. Access
open http://localhost:3000
```

---

## 🔑 Environment Variables

```bash
# ai_service/.env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
BEDROCK_MODEL_ID=qwen.qwen3-coder-next

# backend/.env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///skillforge.db
AI_SERVICE_URL=http://ai-service:8000
```

---

## 🌐 API Endpoints

### Backend (Port 5000)
```
POST /auth/signup          - Register
POST /auth/login           - Login (get JWT)
POST /ai/explain           - Get explanation (JWT required)
POST /ai/quiz              - Generate quiz (JWT required)
POST /ai/debug             - Debug code (JWT required)
POST /api/quiz/complete    - Submit quiz (JWT required)
GET  /api/progress         - Get progress (JWT required)
```

### AI Service (Port 8000)
```
GET  /health               - Health check
POST /tutor/explain        - Generate explanation
POST /quiz/generate        - Generate quiz
POST /debug/analyze        - Analyze code
POST /rag/upload           - Upload document
POST /rag/search           - Search context
```

---

## 🧪 Testing

```bash
# Test Bedrock
python ai_service/test_bedrock_converse.py

# Run all tests
cd ai_service && pytest tests/
cd backend && pytest tests/

# Test with Docker
docker-compose up -d
curl http://localhost:8000/health
```

---

## 🐛 Common Issues

### 1. AccessDeniedException
```bash
# Request Bedrock access
aws bedrock list-foundation-models --region us-east-1
# Go to: AWS Console → Bedrock → Model access
```

### 2. Container Exits
```bash
docker-compose logs ai-service
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

### 3. Model Invalid
```bash
# List available models
aws bedrock list-foundation-models --region us-east-1
# Update BEDROCK_MODEL_ID in .env
```

---

## 💰 Costs

| Environment | Monthly Cost | Use Case |
|-------------|--------------|----------|
| Cost-Optimized | ~$160 | POC, demos |
| Development | ~$305 | Dev, testing |
| Production | ~$790 | Live traffic |

**AI Costs:**
- qwen.qwen3-coder-next: $0.0002/1K tokens (recommended)
- nvidia.nemotron-nano: $0.0001/1K tokens (cheapest)
- anthropic.claude-v2: $0.016/1K tokens (highest quality)

---

## 🚢 AWS Deployment

```bash
# 1. Create secrets
aws secretsmanager create-secret --name skillforge/db-password --secret-string "..."
aws secretsmanager create-secret --name skillforge/jwt-secret --secret-string "..."

# 2. Deploy infrastructure
cd terraform
terraform init
terraform apply

# 3. Build and push images
aws ecr get-login-password | docker login --username AWS --password-stdin ...
docker build -t skillforge-ai-service ai_service/
docker push ...

# 4. Deploy services
aws ecs update-service --cluster ... --service ... --force-new-deployment

# 5. Deploy frontend
cd src/web && npm run build
aws s3 sync out/ s3://...
aws cloudfront create-invalidation --distribution-id ... --paths "/*"
```

---

## 📊 Data Flow

```
User types question
  ↓
Frontend sends POST /ai/explain
  ↓
Backend validates JWT
  ↓
Backend forwards to AI Service
  ↓
AI Service queries OpenSearch (RAG)
  ↓
AI Service calls Bedrock Converse API
  ↓
Bedrock generates response
  ↓
Response flows back to user
```

---

## 🗄️ Database Schema

```sql
users:
  - id, username, email, password_hash
  - created_at, last_login

user_progress:
  - id, user_id, topic, accuracy
  - attempts, time_spent, last_updated

quiz_history:
  - id, user_id, topic, difficulty
  - score, total_questions, completed_at
```

---

## 🔒 Security

- JWT authentication (24hr expiration)
- Bcrypt password hashing
- AWS Secrets Manager for credentials
- VPC with private subnets
- IAM least-privilege policies
- HTTPS/TLS encryption
- Input validation (Pydantic)

---

## 📚 Documentation

- **PROJECT_COMPLETE_GUIDE.md** - This file (complete guide)
- **BEDROCK_QUICK_START.md** - 5-minute quick start
- **BEDROCK_COMMANDS.md** - Command reference
- **PROJECT_STATUS_AND_DEPLOYMENT.md** - Full deployment
- **TERRAFORM_MODULES_GUIDE.md** - Infrastructure guide

---

## 🎓 For Freshers

**Week 1:** Understand architecture, set up locally  
**Week 2:** Deep dive into components  
**Week 3:** Learn RAG, testing, deployment  
**Week 4:** Make contributions

---

## 🤖 For AI Agents

**Context:** This is a production-ready AI learning platform using Amazon Bedrock Converse API

**Key Points:**
- Microservice architecture (Frontend → Backend → AI Service → Bedrock)
- Uses qwen.qwen3-coder-next model (code-optimized)
- Docker Compose for local, ECS Fargate for AWS
- 145 tests passing (122 unit + 23 property-based)
- Complete Terraform infrastructure
- Cost: $160-790/month depending on scale

**To Deploy:**
1. Configure AWS credentials
2. Test Bedrock: `python ai_service/test_bedrock_converse.py`
3. Local: `docker-compose up -d`
4. AWS: `terraform apply` + push images + deploy services

**To Troubleshoot:**
- Check logs: `docker-compose logs -f ai-service`
- Test Bedrock: `aws bedrock list-foundation-models`
- Verify env: `docker-compose config`

---

**Status:** ✅ Production Ready  
**Version:** 2.0.0 (Bedrock Converse API)  
**Last Updated:** March 8, 2026
