# SkillForge AI+ Quick Start Guide

Complete guide to running the SkillForge AI+ platform locally.

## System Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│    Backend   │─────▶│ AI Service  │
│   (React)   │      │    (Flask)   │      │  (FastAPI)  │
│  Port 3000  │      │   Port 5000  │      │  Port 8000  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │   Database   │      │   Bedrock   │
                     │ (SQLite/SQL) │      │  + OpenSearch│
                     └──────────────┘      └─────────────┘
```

## Prerequisites

- Python 3.11+
- AWS Account with Bedrock access
- OpenSearch instance (optional for RAG)
- Node.js 18+ (for frontend, when implemented)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd skillforge-ai
```

### 2. Install AI Service Dependencies

```bash
cd ai_service
pip install -r requirements.txt
```

### 3. Install Backend Dependencies

```bash
cd ../backend
pip install -r requirements.txt
```

## Configuration

### AI Service Configuration

Create `ai_service/.env`:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Bedrock Model
BEDROCK_MODEL_ID=anthropic.claude-v2

# OpenSearch (Optional - for RAG)
OPENSEARCH_HOST=your-opensearch-endpoint.region.es.amazonaws.com
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=your_password
OPENSEARCH_INDEX=skillforge-docs
```

### Backend Configuration

Create `backend/.env`:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
FLASK_ENV=development

# Database (SQLite for development)
DATABASE_URL=sqlite:///skillforge.db

# AI Service URL
AI_SERVICE_URL=http://localhost:8000

# Server
PORT=5000
```

## Running the Services

### Terminal 1: Start AI Service

```bash
cd ai_service
python main.py
```

Output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Backend

```bash
cd backend
python app.py
```

Output:
```
INFO:app:Starting SkillForge Backend on port 5000
 * Running on http://0.0.0.0:5000
```

## Testing the Setup

### 1. Test AI Service

```bash
# Health check
curl http://localhost:8000/health

# Generate explanation
curl -X POST http://localhost:8000/tutor/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "recursion in programming"}'
```

### 2. Test Backend

```bash
# Health check
curl http://localhost:5000/health

# Register a user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

Save the JWT token from the login response.

### 3. Test AI Endpoints (with JWT)

```bash
# Set your JWT token
TOKEN="your_jwt_token_here"

# Get AI explanation
curl -X POST http://localhost:5000/ai/explain \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search algorithm"}'

# Generate quiz
curl -X POST http://localhost:5000/ai/quiz \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python basics",
    "difficulty": "medium",
    "count": 5
  }'

# Debug code
curl -X POST http://localhost:5000/ai/debug \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "def add(a, b)\n    return a + b"
  }'
```

### 4. Test Progress Tracking

```bash
# Complete a quiz
curl -X POST http://localhost:5000/api/quiz/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python basics",
    "difficulty": "medium",
    "score": 8,
    "total_questions": 10,
    "time_spent": 300
  }'

# Get progress
curl http://localhost:5000/api/progress \
  -H "Authorization: Bearer $TOKEN"

# Get recommendations
curl http://localhost:5000/ai/recommendations \
  -H "Authorization: Bearer $TOKEN"
```

## Running Tests

### AI Service Tests

```bash
cd ai_service
pytest tests/ -v
```

Expected: 60+ tests passing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

Expected: 15 tests passing

## Troubleshooting

### AI Service Issues

**Problem**: `ModuleNotFoundError: No module named 'boto3'`
```bash
cd ai_service
pip install -r requirements.txt
```

**Problem**: `NoCredentialsError: Unable to locate credentials`
- Set AWS credentials in `.env` file
- Or configure AWS CLI: `aws configure`

**Problem**: `AccessDeniedException` from Bedrock
- Ensure your AWS account has Bedrock access
- Check model availability in your region

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'flask'`
```bash
cd backend
pip install -r requirements.txt
```

**Problem**: Database connection errors
- Check `DATABASE_URL` in `.env`
- For SQLite, ensure write permissions in backend directory

**Problem**: AI Service connection timeout
- Ensure AI service is running on port 8000
- Check `AI_SERVICE_URL` in backend `.env`

### RAG Pipeline Issues

**Problem**: OpenSearch connection errors
- Verify `OPENSEARCH_HOST` is correct
- Check network connectivity to OpenSearch
- Verify credentials

## API Documentation

### AI Service Endpoints

- `GET /health` - Health check
- `GET /` - Service info
- `POST /tutor/explain` - Get AI explanation
- `POST /quiz/generate` - Generate quiz
- `POST /debug/analyze` - Debug code
- `POST /rag/upload` - Upload document for RAG
- `POST /rag/search` - Search RAG context

### Backend Endpoints

- `GET /health` - Health check
- `GET /` - API info
- `POST /auth/register` - Register user
- `POST /auth/login` - Login user
- `POST /ai/explain` - Get explanation (JWT required)
- `POST /ai/quiz` - Generate quiz (JWT required)
- `POST /ai/debug` - Debug code (JWT required)
- `GET /ai/recommendations` - Get recommendations (JWT required)
- `POST /api/quiz/complete` - Record quiz completion (JWT required)
- `GET /api/progress` - Get user progress (JWT required)

## Development Workflow

1. **Make changes** to code
2. **Run tests** to verify changes
3. **Restart services** to apply changes
4. **Test endpoints** manually or with automated tests

## Next Steps

- [ ] Implement React frontend
- [ ] Add Docker containerization
- [ ] Set up CI/CD pipeline
- [ ] Deploy to AWS
- [ ] Add monitoring and logging

## Support

For issues or questions:
- Check `IMPLEMENTATION_STATUS.md` for current progress
- Review `backend/README.md` for backend details
- Review `ai_service/README.md` for AI service details (if exists)

---

**Status**: AI Service ✅ | Backend ✅ | Frontend ⏳ | Deployment ⏳
