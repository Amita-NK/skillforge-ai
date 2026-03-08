# API Quick Reference

## Flask Backend (Port 5000) - Frontend Calls These

### Public Endpoints (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API info |
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login & get JWT |

### Protected Endpoints (JWT Required)

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/ai/explain` | Get AI explanation | `{"topic": "string"}` |
| POST | `/ai/quiz` | Generate quiz | `{"topic": "string", "difficulty": "easy\|medium\|hard", "count": 1-20}` |
| POST | `/ai/debug` | Debug code | `{"language": "string", "code": "string"}` |
| GET | `/ai/recommendations` | Get recommendations | None |
| POST | `/ai/rag/upload` | Upload RAG document | `{"s3_bucket": "string", "s3_key": "string"}` OR `{"content": "string"}` |
| POST | `/api/quiz/complete` | Record quiz | `{"topic": "string", "difficulty": "string", "score": number, "total_questions": number}` |
| GET | `/api/progress` | Get progress | None |

---

## AI Service (Port 8000) - Internal Only

### ⚠️ DO NOT CALL FROM FRONTEND

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Service info |
| POST | `/tutor/explain` | Generate explanation |
| POST | `/quiz/generate` | Generate quiz |
| POST | `/debug/analyze` | Analyze code |
| POST | `/rag/upload` | Upload document |
| POST | `/rag/search` | Search context |

---

## Quick Examples

### Register & Login
```bash
# Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'
```

### Use AI Features (with JWT)
```bash
# Get explanation
curl -X POST http://localhost:5000/ai/explain \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"topic":"binary search"}'

# Generate quiz
curl -X POST http://localhost:5000/ai/quiz \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Python","difficulty":"medium","count":5}'

# Debug code
curl -X POST http://localhost:5000/ai/debug \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"language":"python","code":"def add(a,b)\n  return a+b"}'
```

### Track Progress
```bash
# Upload document to RAG (S3)
curl -X POST http://localhost:5000/ai/rag/upload \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"s3_bucket":"my-docs","s3_key":"python/intro.pdf","metadata":{"topic":"Python"}}'

# Upload document to RAG (Direct)
curl -X POST http://localhost:5000/ai/rag/upload \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"content":"Python is...","metadata":{"topic":"Python"}}'

# Complete quiz
curl -X POST http://localhost:5000/api/quiz/complete \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Python","difficulty":"medium","score":8,"total_questions":10}'

# Get progress
curl http://localhost:5000/api/progress \
  -H "Authorization: Bearer <TOKEN>"

# Get recommendations
curl http://localhost:5000/ai/recommendations \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 409 | Conflict |
| 500 | Server Error |

---

## Authentication

**Header Format**:
```
Authorization: Bearer <your_jwt_token>
```

**Token Expiration**: 24 hours

---

## Supported Languages (Debug)

- python
- javascript
- typescript
- java
- cpp
- go
- rust

---

## Quiz Difficulties

- easy
- medium
- hard

---

## Recommendation Types

- **EASIER**: Accuracy < 50%
- **PRACTICE**: Accuracy 50-80%
- **ADVANCE**: Accuracy > 80%
- **START**: No progress yet
