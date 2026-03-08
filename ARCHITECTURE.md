# SkillForge AI+ Architecture

## Overview

SkillForge AI+ follows a **microservices architecture** with Flask backend serving as the **central API gateway**. All client requests flow through the backend, which handles authentication, business logic, and orchestrates calls to the AI service.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Browser    │  │  Mobile App  │  │  Desktop App │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┼──────────────────┘                   │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                             │ HTTPS (JWT Token)
                             │
┌────────────────────────────▼──────────────────────────────────────┐
│                    API GATEWAY LAYER                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Flask Backend (Port 5000)                      │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  • JWT Authentication & Authorization                 │  │  │
│  │  │  • Request Validation & Rate Limiting                 │  │  │
│  │  │  • Business Logic & Data Processing                   │  │  │
│  │  │  • Database Operations (User, Progress, Quiz History) │  │  │
│  │  │  • AI Service Orchestration                           │  │  │
│  │  │  • Response Formatting & Error Handling               │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             │ Internal HTTP
                             │
┌────────────────────────────▼──────────────────────────────────────┐
│                    AI SERVICE LAYER                               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │            FastAPI AI Service (Port 8000)                   │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  • AI Model Invocation (Bedrock)                      │  │  │
│  │  │  • Prompt Engineering & Template Management           │  │  │
│  │  │  • Response Parsing & Validation                      │  │  │
│  │  │  • RAG Pipeline (Document Processing & Search)        │  │  │
│  │  │  • Vector Embeddings Generation                       │  │  │
│  │  │  • Retry Logic & Error Recovery                       │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             │ AWS SDK
                             │
┌────────────────────────────▼──────────────────────────────────────┐
│                    EXTERNAL SERVICES                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Bedrock    │  │  OpenSearch  │  │   Database   │           │
│  │   (Claude,   │  │  (Vector DB) │  │ (MySQL/SQLite│           │
│  │ Titan, Llama)│  │              │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└───────────────────────────────────────────────────────────────────┘
```

## Request Flow

### 1. User Authentication Flow

```
Frontend → POST /auth/login → Flask Backend
                                    │
                                    ├─ Validate credentials
                                    ├─ Check password hash
                                    ├─ Generate JWT token
                                    │
                                    └─ Return JWT token
```

### 2. AI Explanation Flow

```
Frontend → POST /ai/explain (+ JWT) → Flask Backend
                                            │
                                            ├─ Validate JWT token
                                            ├─ Extract user ID
                                            ├─ Log request
                                            │
                                            └─ POST /tutor/explain → AI Service
                                                                          │
                                                                          ├─ Retrieve RAG context
                                                                          ├─ Build prompt
                                                                          ├─ Call Bedrock
                                                                          ├─ Parse response
                                                                          │
                                                                          └─ Return explanation
                                            │
                                            ├─ Receive response
                                            ├─ Format response
                                            │
                                            └─ Return to frontend
```

### 3. Quiz Generation & Completion Flow

```
Frontend → POST /ai/quiz (+ JWT) → Flask Backend
                                         │
                                         ├─ Validate JWT & parameters
                                         │
                                         └─ POST /quiz/generate → AI Service
                                                                       │
                                                                       ├─ Call Bedrock
                                                                       ├─ Parse JSON
                                                                       │
                                                                       └─ Return quiz
                                         │
                                         └─ Return quiz to frontend

User completes quiz...

Frontend → POST /api/quiz/complete (+ JWT) → Flask Backend
                                                   │
                                                   ├─ Validate JWT
                                                   ├─ Calculate accuracy
                                                   ├─ Update UserProgress
                                                   ├─ Store QuizHistory
                                                   ├─ Generate recommendations
                                                   │
                                                   └─ Return results
```

### 4. Code Debugging Flow

```
Frontend → POST /ai/debug (+ JWT) → Flask Backend
                                          │
                                          ├─ Validate JWT & code
                                          │
                                          └─ POST /debug/analyze → AI Service
                                                                        │
                                                                        ├─ Call Bedrock
                                                                        ├─ Parse errors
                                                                        │
                                                                        └─ Return analysis
                                          │
                                          └─ Return to frontend
```

## Security Architecture

### Authentication & Authorization

```
┌─────────────┐
│  Frontend   │
└──────┬──────┘
       │ 1. Login (username/password)
       ▼
┌─────────────┐
│   Backend   │
│             │
│ 2. Validate │
│ credentials │
│             │
│ 3. Generate │
│ JWT token   │
└──────┬──────┘
       │ 4. Return JWT
       ▼
┌─────────────┐
│  Frontend   │
│ (Store JWT) │
└──────┬──────┘
       │ 5. All requests include JWT
       ▼
┌─────────────┐
│   Backend   │
│             │
│ 6. Validate │
│ JWT on each │
│ request     │
│             │
│ 7. Extract  │
│ user_id     │
└─────────────┘
```

### Security Layers

1. **Frontend Layer**
   - HTTPS only
   - JWT token storage (httpOnly cookies recommended)
   - CORS configuration
   - Input sanitization

2. **Backend Layer (API Gateway)**
   - JWT validation on all protected endpoints
   - Password hashing (bcrypt)
   - Rate limiting
   - Request validation
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection

3. **AI Service Layer**
   - Internal network only (not exposed to internet)
   - Input validation
   - Output sanitization
   - Retry logic with exponential backoff

4. **External Services**
   - AWS IAM roles and policies
   - Encrypted connections (TLS)
   - Secrets management (AWS Secrets Manager)

## Data Flow

### User Data

```
Frontend → Backend → Database
                      │
                      ├─ users (authentication)
                      ├─ user_progress (learning analytics)
                      └─ quiz_history (performance tracking)
```

### AI Requests

```
Frontend → Backend → AI Service → Bedrock
                                    │
                                    └─ Claude/Titan/Llama models
```

### RAG Pipeline

```
Document Upload → Backend → AI Service → Process & Chunk
                                              │
                                              ├─ Generate embeddings (Bedrock Titan)
                                              │
                                              └─ Store in OpenSearch

Query → Backend → AI Service → Search OpenSearch
                                    │
                                    ├─ Retrieve relevant chunks
                                    ├─ Build context
                                    │
                                    └─ Call Bedrock with context
```

## Component Responsibilities

### Flask Backend (API Gateway)

**Primary Responsibilities:**
- ✅ User authentication and authorization
- ✅ JWT token generation and validation
- ✅ Request validation and sanitization
- ✅ Business logic execution
- ✅ Database operations (CRUD)
- ✅ AI service orchestration
- ✅ Response formatting
- ✅ Error handling and logging
- ✅ Rate limiting
- ✅ Progress tracking
- ✅ Adaptive learning recommendations

**Endpoints:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /ai/explain` - Get AI explanation (proxies to AI service)
- `POST /ai/quiz` - Generate quiz (proxies to AI service)
- `POST /ai/debug` - Debug code (proxies to AI service)
- `GET /ai/recommendations` - Get learning recommendations
- `POST /api/quiz/complete` - Record quiz completion
- `GET /api/progress` - Get user progress

### FastAPI AI Service

**Primary Responsibilities:**
- ✅ AI model invocation (Bedrock)
- ✅ Prompt engineering and template management
- ✅ Response parsing and validation
- ✅ RAG pipeline (document processing, embeddings, search)
- ✅ Vector embeddings generation
- ✅ Retry logic and error recovery
- ✅ Model-specific optimizations

**Endpoints:**
- `POST /tutor/explain` - Generate explanation
- `POST /quiz/generate` - Generate quiz
- `POST /debug/analyze` - Analyze code
- `POST /rag/upload` - Upload document
- `POST /rag/search` - Search documents

**Note:** These endpoints are **internal only** and should not be exposed to the internet.

## Network Architecture

### Development (Local)

```
localhost:3000 (Frontend)
    │
    └─ http://localhost:5000 (Backend)
            │
            └─ http://localhost:8000 (AI Service)
                    │
                    └─ AWS Bedrock API
```

### Development (Docker)

```
Host Machine
    │
    ├─ Port 3000 → frontend:3000
    ├─ Port 5000 → backend:5000
    └─ Port 8000 → ai-service:8000 (optional, for debugging)

Docker Network (skillforge-network)
    │
    ├─ frontend → backend:5000
    ├─ backend → ai-service:8000
    └─ ai-service → AWS Bedrock API
```

### Production (AWS)

```
Internet
    │
    └─ CloudFront (CDN)
            │
            └─ S3 (Frontend Static Files)

Internet
    │
    └─ Application Load Balancer (HTTPS)
            │
            └─ ECS Service (Backend)
                    │
                    ├─ RDS (Database)
                    │
                    └─ ECS Service (AI Service) - Private Subnet
                            │
                            ├─ Bedrock API
                            └─ OpenSearch
```

## Why This Architecture?

### 1. Security
- **Single Entry Point**: All external requests go through backend
- **JWT Validation**: Centralized authentication
- **No Direct AI Access**: AI service is internal only
- **Secrets Management**: Backend manages all credentials

### 2. Scalability
- **Independent Scaling**: Backend and AI service scale independently
- **Load Balancing**: Backend can distribute load across multiple AI service instances
- **Caching**: Backend can cache AI responses
- **Rate Limiting**: Backend controls request rates

### 3. Maintainability
- **Separation of Concerns**: Clear boundaries between layers
- **Single Responsibility**: Each service has one job
- **Easy Testing**: Services can be tested independently
- **Version Control**: Services can be versioned independently

### 4. Flexibility
- **Model Switching**: Change AI models without affecting frontend
- **Business Logic**: Add/modify logic without touching AI service
- **Multiple Frontends**: Support web, mobile, desktop from same backend
- **Feature Flags**: Control features at backend level

## Configuration

### Backend Configuration

```env
# Backend acts as API gateway
AI_SERVICE_URL=http://ai-service:8000  # Internal URL
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=mysql://user:pass@db:3306/skillforge
```

### AI Service Configuration

```env
# AI service is internal only
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
BEDROCK_MODEL_ID=anthropic.claude-v2
OPENSEARCH_HOST=your-opensearch-endpoint
```

### Frontend Configuration

```env
# Frontend only knows about backend
REACT_APP_API_URL=https://api.skillforge.com  # Backend URL
# NO AI_SERVICE_URL - Frontend never calls AI service directly
```

## Best Practices

### ✅ DO

- Always route AI requests through backend
- Validate JWT tokens on all protected endpoints
- Log all requests for audit trail
- Implement retry logic in backend for AI service calls
- Cache AI responses when appropriate
- Use environment variables for configuration
- Implement health checks on all services
- Use HTTPS in production

### ❌ DON'T

- Never expose AI service directly to internet
- Never store AWS credentials in frontend
- Never bypass backend authentication
- Never hardcode secrets in code
- Never trust client-side validation alone
- Never expose internal service URLs to frontend

## Monitoring & Observability

### Metrics to Track

**Backend:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- JWT validation failures
- Database query time
- AI service call latency

**AI Service:**
- Bedrock API latency
- Bedrock API errors
- Token usage
- Cache hit rate
- RAG search latency
- Embedding generation time

### Logging

**Backend:**
```python
logger.info(f"User {user_id} requested explanation for: {topic}")
logger.error(f"AI service error: {str(e)}")
```

**AI Service:**
```python
logger.info(f"Bedrock request: model={model_id}, tokens={tokens}")
logger.error(f"Bedrock error: {str(e)}")
```

## Disaster Recovery

### Backup Strategy

1. **Database**: Automated daily backups (RDS)
2. **OpenSearch**: Snapshot every 6 hours
3. **Configuration**: Version controlled in Git
4. **Secrets**: Stored in AWS Secrets Manager

### Failover Strategy

1. **Backend**: Multi-AZ deployment with auto-scaling
2. **AI Service**: Multiple instances with load balancing
3. **Database**: RDS Multi-AZ with automatic failover
4. **OpenSearch**: Multi-node cluster

## Summary

The SkillForge AI+ architecture ensures:

1. **Security**: All requests authenticated through backend
2. **Scalability**: Services scale independently
3. **Maintainability**: Clear separation of concerns
4. **Reliability**: Multiple layers of redundancy
5. **Performance**: Optimized request flow

**Key Principle**: Frontend → Backend (API Gateway) → AI Service → Bedrock

The backend is the **single source of truth** and **central control point** for all operations.
