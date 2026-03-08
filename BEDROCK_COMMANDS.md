# Bedrock Converse API - Command Reference

## 🚀 Quick Commands

### Test Bedrock Connection
```bash
cd ai_service
python test_bedrock_converse.py
```

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# AI service only
docker-compose logs -f ai-service

# Backend only
docker-compose logs -f backend
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# AI explanation
curl -X POST http://localhost:8000/tutor/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search"}'

# Quiz generation
curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python", "difficulty": "medium", "count": 5}'

# Code debugging
curl -X POST http://localhost:8000/debug/analyze \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "code": "def add(a, b)\n    return a + b"}'
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart AI service only
docker-compose restart ai-service
```

### Rebuild Containers
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

## 🔧 AWS Commands

### Check Bedrock Access
```bash
aws bedrock list-foundation-models --region us-east-1
```

### List Available Models
```bash
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query 'modelSummaries[*].[modelId,modelName]' \
  --output table
```

### Check AWS Credentials
```bash
aws sts get-caller-identity
```

### Deploy to ECS
```bash
# Update service
aws ecs update-service \
  --cluster skillforge-cluster \
  --service ai-service \
  --force-new-deployment \
  --region us-east-1

# Check status
aws ecs describe-services \
  --cluster skillforge-cluster \
  --services ai-service \
  --region us-east-1
```

### View CloudWatch Logs
```bash
aws logs tail /ecs/skillforge-ai-ai-service --follow --region us-east-1
```

## 🐛 Troubleshooting Commands

### Check Docker Status
```bash
docker-compose ps
```

### View Container Details
```bash
docker inspect skillforge-ai-service
```

### Check Environment Variables
```bash
docker-compose config
```

### Test Network Connectivity
```bash
# From host to AI service
curl http://localhost:8000/health

# From backend container to AI service
docker-compose exec backend curl http://ai-service:8000/health
```

### Check Disk Space
```bash
docker system df
```

### Clean Up Docker
```bash
# Remove stopped containers
docker-compose down

# Remove all unused images
docker system prune -a

# Remove volumes
docker-compose down -v
```

## 📝 Configuration Commands

### Update Model ID
```bash
# Edit .env file
nano ai_service/.env

# Change this line:
BEDROCK_MODEL_ID=qwen.qwen3-coder-next

# Restart
docker-compose restart ai-service
```

### View Current Configuration
```bash
# Show environment variables
docker-compose config | grep BEDROCK

# Show AI service config
docker-compose exec ai-service env | grep BEDROCK
```

## 🧪 Testing Commands

### Run All Tests
```bash
cd ai_service
pytest tests/
```

### Run Specific Test
```bash
pytest tests/test_bedrock_client.py
```

### Test with Coverage
```bash
pytest --cov=. tests/
```

## 📊 Monitoring Commands

### Check Service Health
```bash
# AI service
curl http://localhost:8000/health

# Backend
curl http://localhost:5000/health
```

### Monitor Resource Usage
```bash
docker stats
```

### Check Container Logs (Last 100 Lines)
```bash
docker-compose logs --tail=100 ai-service
```

## 🔄 Update Commands

### Pull Latest Code
```bash
git pull origin main
```

### Update Dependencies
```bash
cd ai_service
pip install -r requirements.txt --upgrade
```

### Rebuild After Update
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## 💾 Backup Commands

### Export Environment Variables
```bash
docker-compose config > docker-config-backup.yml
```

### Backup Database
```bash
docker-compose exec backend python -c "from database import backup_db; backup_db()"
```

## 🎯 One-Liners

### Complete Reset
```bash
docker-compose down -v && docker-compose build --no-cache && docker-compose up -d
```

### Quick Test
```bash
python ai_service/test_bedrock_converse.py && docker-compose up -d && curl http://localhost:8000/health
```

### View All Logs
```bash
docker-compose logs -f --tail=50
```

### Check Everything
```bash
docker-compose ps && curl http://localhost:8000/health && curl http://localhost:5000/health
```

## 📱 Mobile-Friendly Commands

### Status Check
```bash
docker-compose ps && curl -s http://localhost:8000/health | jq
```

### Quick Restart
```bash
docker-compose restart && sleep 5 && curl http://localhost:8000/health
```

### Error Check
```bash
docker-compose logs --tail=20 ai-service | grep -i error
```

## 🔗 Useful Aliases

Add these to your `.bashrc` or `.zshrc`:

```bash
# SkillForge aliases
alias sf-up='docker-compose up -d'
alias sf-down='docker-compose down'
alias sf-logs='docker-compose logs -f'
alias sf-test='python ai_service/test_bedrock_converse.py'
alias sf-health='curl http://localhost:8000/health && curl http://localhost:5000/health'
alias sf-restart='docker-compose restart'
alias sf-rebuild='docker-compose down && docker-compose build && docker-compose up -d'
```

## 📚 Documentation Commands

### View Documentation
```bash
# Quick start
cat BEDROCK_QUICK_START.md

# Full guide
cat ai_service/BEDROCK_CONVERSE_UPDATE.md

# Summary
cat BEDROCK_UPDATE_SUMMARY.md
```

### Search Documentation
```bash
grep -r "qwen" *.md
grep -r "converse" ai_service/*.md
```

---

**Tip:** Bookmark this file for quick reference!

**Last Updated:** March 8, 2026
