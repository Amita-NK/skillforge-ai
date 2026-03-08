# API Endpoints Documentation

## Overview

This document lists all API endpoints for the SkillForge AI+ platform.

**Architecture**: Frontend → Flask Backend → AI Service → Bedrock

**Important**: Frontend should ONLY call Flask Backend endpoints. AI Service endpoints are internal only.

---

## Flask Backend API (Port 5000)

**Base URL**: `http://localhost:5000` (development) or `https://api.skillforge.com` (production)

### Health & Info

#### GET /health
Health check endpoint for monitoring.

**Authentication**: None

**Request**:
```bash
curl http://localhost:5000/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "skillforge-backend",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

#### GET /
Root endpoint with API information.

**Authentication**: None

**Request**:
```bash
curl http://localhost:5000/
```

**Response** (200 OK):
```json
{
  "service": "SkillForge Backend API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "auth": {
      "login": "/auth/login",
      "register": "/auth/register"
    },
    "ai": {
      "explain": "/ai/explain",
      "quiz": "/ai/quiz",
      "debug": "/ai/debug",
      "recommendations": "/ai/recommendations"
    },
    "progress": {
      "get": "/api/progress",
      "quiz_complete": "/api/quiz/complete"
    }
  }
}
```

---

### Authentication

#### POST /auth/register
Register a new user.

**Authentication**: None

**Request**:
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

**Request Body**:
```json
{
  "username": "string (required)",
  "email": "string (required)",
  "password": "string (required)",
  "name": "string (optional)"
}
```

**Response** (201 Created):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "name": "John Doe",
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Missing required fields
- `409 Conflict`: User already exists
- `500 Internal Server Error`: Registration failed

---

#### POST /auth/login
Login and receive JWT token.

**Authentication**: None

**Request**:
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

**Request Body**:
```json
{
  "username": "string (required) - username or email",
  "password": "string (required)"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials
- `500 Internal Server Error`: Login failed

---

### AI Endpoints (Protected)

All AI endpoints require JWT authentication. Include the token in the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

#### POST /ai/explain
Get AI-powered explanation for a concept.

**Authentication**: Required (JWT)

**Request**:
```bash
curl -X POST http://localhost:5000/ai/explain \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "binary search algorithm"
  }'
```

**Request Body**:
```json
{
  "topic": "string (required) - concept to explain"
}
```

**Response** (200 OK):
```json
{
  "explanation": "Binary search is an efficient algorithm for finding an item...",
  "examples": [
    "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    ..."
  ],
  "analogy": "Binary search is like finding a word in a dictionary..."
}
```

**Error Responses**:
- `400 Bad Request`: Topic is required
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Failed to generate explanation

---

#### POST /ai/quiz
Generate an AI-powered quiz.

**Authentication**: Required (JWT)

**Request**:
```bash
curl -X POST http://localhost:5000/ai/quiz \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python basics",
    "difficulty": "medium",
    "count": 5
  }'
```

**Request Body**:
```json
{
  "topic": "string (required) - quiz topic",
  "difficulty": "string (required) - easy, medium, or hard",
  "count": "integer (required) - number of questions (1-20)"
}
```

**Response** (200 OK):
```json
{
  "questions": [
    {
      "question": "What is a variable in Python?",
      "options": [
        "A container for storing data",
        "A function",
        "A loop",
        "A class"
      ],
      "correct": 0,
      "explanation": "A variable is a container that stores data values..."
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid topic, difficulty, or count
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Failed to generate quiz

---

#### POST /ai/debug
Debug code using AI.

**Authentication**: Required (JWT)

**Request**:
```bash
curl -X POST http://localhost:5000/ai/debug \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "def add(a, b)\n    return a + b"
  }'
```

**Request Body**:
```json
{
  "language": "string (required) - programming language",
  "code": "string (required) - code to debug (max 10,000 chars)"
}
```

**Supported Languages**:
- python
- javascript
- typescript
- java
- cpp (C++)
- go
- rust

**Response** (200 OK):
```json
{
  "errors": [
    {
      "line": 1,
      "message": "Missing colon after function definition",
      "severity": "error"
    }
  ],
  "corrected_code": "def add(a, b):\n    return a + b",
  "explanation": "The function definition was missing a colon at the end..."
}
```

**Error Responses**:
- `400 Bad Request`: Missing language or code
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Failed to analyze code

---

#### GET /ai/recommendations
Get personalized learning recommendations.

**Authentication**: Required (JWT)

**Request**:
```bash
curl http://localhost:5000/ai/recommendations \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response** (200 OK):
```json
{
  "recommendations": [
    {
      "topic": "Python Basics",
      "type": "EASIER",
      "reason": "Review fundamentals of Python Basics (current accuracy: 45.0%)"
    },
    {
      "topic": "Data Structures",
      "type": "PRACTICE",
      "reason": "Practice more questions on Data Structures (current accuracy: 65.0%)"
    },
    {
      "topic": "Algorithms",
      "type": "ADVANCE",
      "reason": "Ready to move to next topic (mastered Algorithms with 85.0% accuracy)"
    }
  ]
}
```

**Recommendation Types**:
- `EASIER`: Accuracy < 50% - Review fundamentals
- `PRACTICE`: Accuracy 50-80% - Practice more
- `ADVANCE`: Accuracy > 80% - Move to next topic
- `START`: No progress yet - Begin learning

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Failed to get recommendations

---

### Progress Tracking (Protected)

#### POST /api/quiz/complete
Record quiz completion and update user progress.

**Authentication**: Required (JWT)

**Request**:
```bash
curl -X POST http://localhost:5000/api/quiz/complete \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python basics",
    "difficulty": "medium",
    "score": 8,
    "total_questions": 10,
    "time_spent": 300
  }'
```

**Request Body**:
```json
{
  "topic": "string (required) - quiz topic",
  "difficulty": "string (required) - easy, medium, or hard",
  "score": "number (required) - number of correct answers",
  "total_questions": "number (required) - total questions",
  "time_spent": "number (optional) - time in seconds"
}
```

**Response** (200 OK):
```json
{
  "message": "Quiz completion recorded",
  "score": 8,
  "accuracy": 80.0,
  "quiz_id": 123
}
```

**Error Responses**:
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Failed to record completion

---

#### GET /api/progress
Get user progress data.

**Authentication**: Required (JWT)

**Request**:
```bash
curl http://localhost:5000/api/progress \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response** (200 OK):
```json
{
  "progress": [
    {
      "id": 1,
      "user_id": 123,
      "topic": "Python Basics",
      "accuracy": 75.5,
      "attempts": 5,
      "time_spent": 1200,
      "last_updated": "2024-01-15T10:30:00.000Z"
    },
    {
      "id": 2,
      "user_id": 123,
      "topic": "Data Structures",
      "accuracy": 82.3,
      "attempts": 3,
      "time_spent": 900,
      "last_updated": "2024-01-14T15:20:00.000Z"
    }
  ]
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Failed to get progress

---

#### POST /ai/rag/upload
Upload document to RAG pipeline for knowledge base ingestion.

**Authentication**: Required (JWT)

**Request (S3 ingestion)**:
```bash
curl -X POST http://localhost:5000/ai/rag/upload \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "s3_bucket": "my-documents-bucket",
    "s3_key": "courses/python/intro.pdf",
    "metadata": {
      "topic": "Python Programming",
      "author": "John Doe"
    }
  }'
```

**Request (Direct content)**:
```bash
curl -X POST http://localhost:5000/ai/rag/upload \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Python Basics\n\nPython is a high-level programming language...",
    "metadata": {
      "topic": "Python Programming",
      "source": "manual_upload"
    }
  }'
```

**Request Body** (S3 ingestion):
```json
{
  "s3_bucket": "string (required with s3_key) - S3 bucket name",
  "s3_key": "string (required with s3_bucket) - S3 object key",
  "metadata": "object (optional) - document metadata"
}
```

**Request Body** (Direct content):
```json
{
  "content": "string (required) - document content",
  "metadata": "object (optional) - document metadata"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "chunks_processed": 42
}
```

**Error Responses**:
- `400 Bad Request`: Invalid parameters (must provide s3_bucket+s3_key OR content)
- `401 Unauthorized`: Missing or invalid JWT token
- `500 Internal Server Error`: Upload failed

**Notes**:
- Supports both S3 document ingestion and direct content upload
- Use S3 ingestion for large documents stored in S3
- Use direct content for smaller documents or text snippets
- Documents are automatically chunked and embedded for RAG retrieval

---

## AI Service API (Port 8000 - Internal Only)

**Base URL**: `http://ai-service:8000` (Docker network) or `http://localhost:8000` (local development)

**⚠️ IMPORTANT**: These endpoints are for **internal use only**. They should NEVER be called directly from the frontend. Only the Flask backend should communicate with the AI service.

### Health & Info

#### GET /health
Health check endpoint.

**Request**:
```bash
curl http://localhost:8000/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "skillforge-ai-service",
  "version": "1.0.0"
}
```

---

#### GET /
Service information.

**Request**:
```bash
curl http://localhost:8000/
```

**Response** (200 OK):
```json
{
  "service": "SkillForge AI Service",
  "version": "1.0.0",
  "endpoints": {
    "tutor": "/tutor/explain",
    "quiz": "/quiz/generate",
    "debug": "/debug/analyze",
    "rag": {
      "upload": "/rag/upload",
      "search": "/rag/search"
    }
  }
}
```

---

### AI Tutor

#### POST /tutor/explain
Generate AI explanation for a concept.

**Authentication**: None (internal only)

**Request**:
```bash
curl -X POST http://localhost:8000/tutor/explain \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "recursion in programming"
  }'
```

**Request Body**:
```json
{
  "topic": "string (required, max 500 chars)"
}
```

**Response** (200 OK):
```json
{
  "explanation": "Recursion is a programming technique where a function calls itself...",
  "examples": [
    "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
  ],
  "analogy": "Recursion is like Russian nesting dolls..."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: AI generation failed

---

### Quiz Generator

#### POST /quiz/generate
Generate a quiz using AI.

**Authentication**: None (internal only)

**Request**:
```bash
curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python basics",
    "difficulty": "medium",
    "count": 5
  }'
```

**Request Body**:
```json
{
  "topic": "string (required, max 200 chars)",
  "difficulty": "string (required) - easy, medium, or hard",
  "count": "integer (required, 1-20)"
}
```

**Response** (200 OK):
```json
{
  "questions": [
    {
      "question": "What is a variable?",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "explanation": "..."
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Quiz generation failed

---

### Code Debugger

#### POST /debug/analyze
Analyze and debug code.

**Authentication**: None (internal only)

**Request**:
```bash
curl -X POST http://localhost:8000/debug/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "def add(a, b)\n    return a + b"
  }'
```

**Request Body**:
```json
{
  "language": "string (required) - python, javascript, java, cpp, typescript, go, rust",
  "code": "string (required, max 10,000 chars)"
}
```

**Response** (200 OK):
```json
{
  "errors": [
    {
      "line": 1,
      "message": "Missing colon",
      "severity": "error"
    }
  ],
  "corrected_code": "def add(a, b):\n    return a + b",
  "explanation": "..."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Analysis failed

---

### RAG Pipeline

#### POST /rag/upload
Upload and process document for RAG.

**Authentication**: None (internal only)

**Request (S3 ingestion)**:
```bash
curl -X POST http://localhost:8000/rag/upload \
  -H "Content-Type: application/json" \
  -d '{
    "s3_bucket": "my-documents-bucket",
    "s3_key": "courses/python/intro.pdf",
    "metadata": {
      "topic": "Python Programming",
      "author": "John Doe"
    }
  }'
```

**Request (Direct content)**:
```bash
curl -X POST http://localhost:8000/rag/upload \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Document content here...",
    "metadata": {
      "topic": "Python Tutorial",
      "source": "manual_upload"
    }
  }'
```

**Request Body** (S3 ingestion):
```json
{
  "s3_bucket": "string (required with s3_key) - S3 bucket name",
  "s3_key": "string (required with s3_bucket) - S3 object key",
  "metadata": "object (optional) - document metadata"
}
```

**Request Body** (Direct content):
```json
{
  "content": "string (required) - document content",
  "metadata": "object (optional) - document metadata"
}
```

**Request Body** (Legacy format):
```json
{
  "file_url": "string (deprecated) - file URL",
  "metadata": {
    "content": "string (required) - document content",
    "topic": "string (optional)",
    "upload_date": "string (optional)"
  }
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "chunks_processed": 42
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input (must provide s3_bucket+s3_key, content, or file_url)
- `500 Internal Server Error`: Processing failed or S3 access error
- `503 Service Unavailable`: RAG pipeline not configured

**Notes**:
- S3 ingestion requires AWS credentials configured in the AI service
- Documents are automatically chunked (500 chars, 50 overlap)
- Embeddings are generated using Bedrock Titan (1536 dimensions)
- Chunks are stored in OpenSearch with metadata for retrieval

---

#### POST /rag/search
Search for relevant context.

**Authentication**: None (internal only)

**Request**:
```bash
curl -X POST http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is recursion?",
    "top_k": 5
  }'
```

**Request Body**:
```json
{
  "query": "string (required) - search query",
  "top_k": "integer (optional, default 5) - number of results"
}
```

**Response** (200 OK):
```json
{
  "results": [
    {
      "content": "Recursion is a technique...",
      "score": 0.95,
      "metadata": {
        "source": "tutorial.pdf",
        "page": 42
      }
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Search failed

---

## Error Response Format

All endpoints return errors in a consistent format:

```json
{
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Request successful |
| 201 | Created | Resource created (e.g., user registration) |
| 400 | Bad Request | Invalid input or missing required fields |
| 401 | Unauthorized | Missing or invalid JWT token |
| 404 | Not Found | Endpoint doesn't exist |
| 409 | Conflict | Resource already exists (e.g., duplicate user) |
| 500 | Internal Server Error | Server-side error |

---

## Authentication

### JWT Token Usage

1. **Obtain Token**: Call `POST /auth/login` with credentials
2. **Store Token**: Save the `access_token` from response
3. **Use Token**: Include in `Authorization` header for protected endpoints

```bash
# Example with token
curl -X POST http://localhost:5000/ai/explain \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search"}'
```

### Token Expiration

- Tokens expire after 24 hours
- Expired tokens return `401 Unauthorized`
- Obtain a new token by logging in again

---

## Rate Limiting

**Backend Endpoints**:
- Default: 200 requests per day, 50 per hour
- AI endpoints: 10 requests per minute per user

**AI Service Endpoints**:
- No rate limiting (internal only)
- Backend handles rate limiting

---

## Examples

### Complete User Flow

```bash
# 1. Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePass123!",
    "name": "Alice Smith"
  }'

# 2. Login
TOKEN=$(curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "SecurePass123!"
  }' | jq -r '.access_token')

# 3. Get explanation
curl -X POST http://localhost:5000/ai/explain \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search"}'

# 4. Generate quiz
curl -X POST http://localhost:5000/ai/quiz \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python basics",
    "difficulty": "medium",
    "count": 5
  }'

# 5. Complete quiz
curl -X POST http://localhost:5000/api/quiz/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python basics",
    "difficulty": "medium",
    "score": 4,
    "total_questions": 5,
    "time_spent": 180
  }'

# 6. Get progress
curl http://localhost:5000/api/progress \
  -H "Authorization: Bearer $TOKEN"

# 7. Get recommendations
curl http://localhost:5000/ai/recommendations \
  -H "Authorization: Bearer $TOKEN"
```

---

## Summary

### Flask Backend (Port 5000) - Public API

**Total Endpoints**: 11

**Public** (No Auth):
- `GET /health`
- `GET /`
- `POST /auth/register`
- `POST /auth/login`

**Protected** (JWT Required):
- `POST /ai/explain`
- `POST /ai/quiz`
- `POST /ai/debug`
- `GET /ai/recommendations`
- `POST /ai/rag/upload`
- `POST /api/quiz/complete`
- `GET /api/progress`

### AI Service (Port 8000) - Internal Only

**Total Endpoints**: 7

**All Internal** (No Auth):
- `GET /health`
- `GET /`
- `POST /tutor/explain`
- `POST /quiz/generate`
- `POST /debug/analyze`
- `POST /rag/upload`
- `POST /rag/search`

**⚠️ Remember**: Frontend should ONLY call Flask Backend endpoints!
