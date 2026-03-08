# SkillForge AI+ - Bedrock Converse API Quick Start

## 🚀 Quick Start (5 Minutes)

### Step 1: Update Environment Variables

Edit `ai_service/.env`:
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
BEDROCK_MODEL_ID=qwen.qwen3-coder-next
```

### Step 2: Test Bedrock Connection

```bash
cd ai_service
python test_bedrock_converse.py
```

✅ **Expected:** "SUCCESS: Bedrock Converse API is working correctly!"

### Step 3: Start Services

```bash
docker-compose up -d
```

### Step 4: Verify Services

```bash
# Check AI service health
curl http://localhost:8000/health

# Test AI explanation
curl -X POST http://localhost:8000/tutor/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search"}'
```

✅ **Expected:** JSON response with explanation

### Step 5: Test via Backend

```bash
# Test backend health
curl http://localhost:5000/health

# Test AI endpoint through backend
# (requires JWT token from login)
curl -X POST http://localhost:5000/ai/explain \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"topic": "binary search"}'
```

## 🔧 What Was Updated

### Bedrock Client
- ✅ Now uses Converse API (`client.converse()`)
- ✅ Works with all Bedrock models
- ✅ Unified response parsing
- ✅ Better error handling

### Supported Models
- `qwen.qwen3-coder-next` ⭐ (recommended for code)
- `nvidia.nemotron-nano-12b-v2`
- `anthropic.claude-v2`
- All other Converse API compatible models

### Response Format
```python
# Old (invoke_model)
response_body = json.loads(response['body'].read())
text = response_body.get('completion')  # Model-specific

# New (converse)
text = response["output"]["message"]["content"][0]["text"]  # Universal
```

## 🐛 Troubleshooting

### "AccessDeniedException"
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

**Fix:** Request Bedrock access in AWS Console → Bedrock → Model access

### "Model ID is invalid"
```bash
# List available models
aws bedrock list-foundation-models --region us-east-1
```

**Fix:** Use a model ID from the list

### Docker container exits
```bash
# Check logs
docker-compose logs ai-service

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Architecture Flow

```
Frontend (Next.js)
    ↓
Backend (Flask) :5000
    ↓
AI Service (FastAPI) :8000
    ↓
Amazon Bedrock Converse API
    ↓
Model (qwen.qwen3-coder-next)
```

## ✅ Verification Checklist

- [ ] Environment variables configured
- [ ] `test_bedrock_converse.py` passes
- [ ] Docker containers running
- [ ] Health endpoints respond
- [ ] AI explanation works
- [ ] Backend proxy works
- [ ] Frontend can call backend

## 📚 Documentation

- **Full Update Guide:** `ai_service/BEDROCK_CONVERSE_UPDATE.md`
- **Deployment Guide:** `PROJECT_STATUS_AND_DEPLOYMENT.md`
- **API Documentation:** `API_ENDPOINTS.md`

## 🎯 Next Steps

1. **Test all AI features:**
   - Tutoring (explain concepts)
   - Quiz generation
   - Code debugging

2. **Deploy to AWS:**
   - No Terraform changes needed
   - Update ECS environment variables
   - Same IAM permissions work

3. **Monitor performance:**
   - Check CloudWatch logs
   - Monitor Bedrock usage
   - Track response times

## 💡 Tips

- **Model Selection:** Use `qwen.qwen3-coder-next` for code-related tasks
- **Cost Optimization:** Use `anthropic.claude-instant-v1` for faster/cheaper responses
- **Error Handling:** All errors are logged with full context
- **Retry Logic:** Automatic exponential backoff for rate limits

## 🔗 Quick Links

- [Bedrock Console](https://console.aws.amazon.com/bedrock/)
- [Model Access](https://console.aws.amazon.com/bedrock/home#/modelaccess)
- [IAM Policies](https://console.aws.amazon.com/iam/)
- [CloudWatch Logs](https://console.aws.amazon.com/cloudwatch/)

---

**Need Help?** Check `ai_service/BEDROCK_CONVERSE_UPDATE.md` for detailed troubleshooting.
