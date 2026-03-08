# API Gateway Architecture - SkillForge AI+

## Executive Summary

SkillForge AI+ implements a **secure API gateway pattern** where the Flask backend serves as the **single entry point** for all client requests. This architecture ensures security, scalability, and maintainability by centralizing authentication, authorization, and business logic.

## Core Principle

```
┌─────────────────────────────────────────────────────────────┐
│                     GOLDEN RULE                              │
│                                                              │
│  Frontend → Backend (API Gateway) → AI Service → Bedrock    │
│                                                              │
│  ✅ Frontend calls Backend ONLY                             │
│  ❌ Frontend NEVER calls AI Service directly                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Why API Gateway Pattern?

### 1. Security

**Problem**: If frontend calls AI service directly:
- No authentication (anyone can access)
- AWS credentials exposed
- No rate limiting
- No audit logging
- Direct access to expensive AI models

**Solution**: Backend as API gateway:
- ✅ JWT authentication on every request
- ✅ AWS credentials secured in backend
- ✅ Rate limiting enforced
- ✅ Complete audit trail
- ✅ Cost control through backend logic

### 2. Business Logic

**Problem**: If frontend calls AI service directly:
- No progress tracking
- No adaptive learning
- No user analytics
- No quiz history
- Business logic in frontend (insecure)

**Solution**: Backend handles all business logic:
- ✅ Track user progress in database
- ✅ Generate personalized recommendations
- ✅ Store quiz history
- ✅ Calculate accuracy metrics
- ✅ Implement adaptive learning rules

### 3. Scalability

**Problem**: If frontend calls AI service directly:
- No caching
- No load balancing
- No request queuing
- Difficult to scale

**Solution**: Backend orchestrates scaling:
- ✅ Cache AI responses
- ✅ Load balance across AI instances
- ✅ Queue requests during high load
- ✅ Scale backend and AI independently

## Request Flow Examples

### Example 1: User Requests AI Explanation

```
┌──────────┐
│ Frontend │
└────┬─────┘
     │ 1. POST /ai/explain
     │    Headers: Authorization: Bearer <JWT>
     │    Body: { "topic": "binary search" }
     ▼
┌──────────┐
│ Backend  │
│ (Flask)  │
└────┬─────┘
     │ 2. Validate JWT token
     │    ├─ Check signature
     │    ├─ Check expiration
     │    └─ Extract user_id
     │
     │ 3. Validate input
     │    ├─ Check topic is not empty
     │    └─ Sanitize topic string
     │
     │ 4. Log request
     │    └─ "User 123 requested explanation for: binary search"
     │
     │ 5. Call AI Service (internal)
     ▼
┌──────────┐
│AI Service│
│(FastAPI) │
└────┬─────┘
     │ 6. Retrieve RAG context (if available)
     │    └─ Search OpenSearch for relevant docs
     │
     │ 7. Build prompt with context
     │
     │ 8. Call Bedrock API
     ▼
┌──────────┐
│ Bedrock  │
│ (Claude) │
└────┬─────┘
     │ 9. Generate explanation
     │
     │ 10. Return response
     ▼
┌──────────┐
│AI Service│
└────┬─────┘
     │ 11. Parse response
     │     ├─ Extract explanation
     │     ├─ Extract examples
     │     └─ Extract analogy
     │
     │ 12. Return to backend
     ▼
┌──────────┐
│ Backend  │
└────┬─────┘
     │ 13. Format response
     │
     │ 14. Log completion
     │     └─ "Explanation generated for user 123"
     │
     │ 15. Return to frontend
     ▼
┌──────────┐
│ Frontend │
└──────────┘
     │ 16. Display to user
```

### Example 2: User Completes Quiz

```
┌──────────┐
│ Frontend │
└────┬─────┘
     │ 1. POST /api/quiz/complete
     │    Headers: Authorization: Bearer <JWT>
     │    Body: {
     │      "topic": "Python",
     │      "difficulty": "medium",
     │      "score": 8,
     │      "total_questions": 10,
     │      "time_spent": 300
     │    }
     ▼
┌──────────┐
│ Backend  │
│ (Flask)  │
└────┬─────┘
     │ 2. Validate JWT → user_id = 123
     │
     │ 3. Validate input
     │    ├─ Check all required fields
     │    └─ Validate score <= total_questions
     │
     │ 4. Calculate accuracy
     │    └─ accuracy = (8/10) * 100 = 80%
     │
     │ 5. Update UserProgress table
     │    ├─ Get existing progress for "Python"
     │    ├─ Calculate weighted average accuracy
     │    ├─ Increment attempts counter
     │    └─ Add time_spent
     │
     │ 6. Store in QuizHistory table
     │    └─ Record: user_id, topic, difficulty, score, time
     │
     │ 7. Generate recommendations
     │    └─ AdaptiveLearningEngine.generate_recommendations(123)
     │        ├─ accuracy = 80% (50-80% range)
     │        └─ Recommendation: "PRACTICE" more questions
     │
     │ 8. Return response
     ▼
┌──────────┐
│ Frontend │
└──────────┘
     │ 9. Display results and recommendations
```

## Backend Responsibilities

### 1. Authentication & Authorization

```python
@app.route('/ai/explain', methods=['POST'])
@jwt_required()  # ← Validates JWT token
def explain_concept():
    current_user_id = int(get_jwt_identity())  # ← Extract user ID
    # ... rest of logic
```

**What it does:**
- Validates JWT signature
- Checks token expiration
- Extracts user identity
- Rejects invalid/expired tokens

### 2. Input Validation

```python
def generate_quiz():
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400
    
    # Validate difficulty
    if data['difficulty'] not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400
    
    # Validate count range
    count = data.get('count', 5)
    if not isinstance(count, int) or count < 1 or count > 20:
        return jsonify({'error': 'Count must be between 1 and 20'}), 400
```

**What it does:**
- Checks required fields exist
- Validates data types
- Enforces business rules
- Sanitizes inputs

### 3. Business Logic

```python
def complete_quiz():
    # Calculate accuracy
    accuracy = (score / total_questions) * 100
    
    # Update user progress (weighted average)
    progress = UserProgressService.update_progress(
        user_id=user_id,
        topic=topic,
        score=score,
        total_questions=total_questions,
        time_spent=time_spent
    )
    
    # Store quiz history
    quiz_record = QuizHistoryService.record_quiz_completion(...)
    
    # Generate recommendations
    recommendations = AdaptiveLearningEngine.generate_recommendations(user_id)
```

**What it does:**
- Calculates metrics
- Updates database
- Applies business rules
- Generates insights

### 4. AI Service Orchestration

```python
class AIServiceClient:
    @staticmethod
    def explain(topic: str) -> dict:
        try:
            response = requests.post(
                f"{AI_SERVICE_URL}/tutor/explain",
                json={'topic': topic},
                timeout=AI_SERVICE_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.error("AI service timeout")
            raise Exception("AI service request timed out")
        except requests.RequestException as e:
            logger.error(f"AI service error: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")
```

**What it does:**
- Calls AI service internally
- Handles timeouts
- Implements retry logic
- Logs errors

### 5. Response Formatting

```python
def explain_concept():
    try:
        result = AIServiceClient.explain(data['topic'])
        logger.info(f"User {current_user} requested explanation for: {data['topic']}")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to get explanation: {str(e)}")
        return jsonify({'error': 'Failed to generate explanation'}), 500
```

**What it does:**
- Formats responses consistently
- Adds metadata
- Handles errors gracefully
- Returns appropriate HTTP status codes

## AI Service Responsibilities

### 1. AI Model Invocation

```python
def explain_concept(topic: str) -> dict:
    # Build prompt
    prompt = f"Explain {topic} in simple terms..."
    
    # Call Bedrock
    response = bedrock_client.invoke_model(
        model_id=BEDROCK_MODEL_ID,
        prompt=prompt
    )
    
    # Parse response
    explanation = parse_explanation(response)
    return explanation
```

**What it does:**
- Manages AI model interactions
- Handles prompt engineering
- Parses AI responses
- Implements retry logic

### 2. RAG Pipeline

```python
def search_context(query: str) -> list:
    # Generate embedding
    embedding = generate_embedding(query)
    
    # Search OpenSearch
    results = opensearch_client.search(
        index=INDEX_NAME,
        body={
            "query": {
                "knn": {
                    "embedding": {
                        "vector": embedding,
                        "k": 5
                    }
                }
            }
        }
    )
    
    return results
```

**What it does:**
- Processes documents
- Generates embeddings
- Searches vector database
- Retrieves relevant context

## Configuration

### Backend Configuration

```env
# Backend is the API gateway
AI_SERVICE_URL=http://ai-service:8000  # Internal URL (Docker network)
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///skillforge.db
PORT=5000
```

### AI Service Configuration

```env
# AI service is internal only
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
BEDROCK_MODEL_ID=anthropic.claude-v2
```

### Frontend Configuration

```env
# Frontend only knows about backend
REACT_APP_API_URL=http://localhost:5000  # Backend URL
# NO AI_SERVICE_URL - Frontend never calls AI service
```

## Docker Configuration

### Correct Configuration

```yaml
services:
  ai-service:
    expose:
      - "8000"  # ✅ Internal only
    # NO port mapping to host
    
  backend:
    ports:
      - "5000:5000"  # ✅ Exposed to host
    environment:
      - AI_SERVICE_URL=http://ai-service:8000  # ✅ Internal URL
```

### Incorrect Configuration (DO NOT USE)

```yaml
services:
  ai-service:
    ports:
      - "8000:8000"  # ❌ Exposes AI service to internet
```

## Testing the Architecture

### Test 1: Verify AI Service is Not Accessible

```bash
# This should FAIL (connection refused)
curl http://localhost:8000/health

# This should SUCCEED
curl http://localhost:5000/health
```

### Test 2: Verify Backend Proxies to AI Service

```bash
# 1. Register user
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "pass123"}'

# 2. Login and get JWT
TOKEN=$(curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "pass123"}' \
  | jq -r '.access_token')

# 3. Call AI endpoint through backend
curl -X POST http://localhost:5000/ai/explain \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search"}'
```

### Test 3: Verify Authentication is Required

```bash
# This should FAIL (401 Unauthorized)
curl -X POST http://localhost:5000/ai/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search"}'
```

## Benefits of This Architecture

### Security Benefits

| Benefit | Description |
|---------|-------------|
| Centralized Authentication | All requests authenticated in one place |
| Credential Protection | AWS credentials never exposed to frontend |
| Rate Limiting | Control API usage at gateway level |
| Audit Logging | Complete trail of all requests |
| Attack Surface Reduction | Only one service exposed to internet |

### Scalability Benefits

| Benefit | Description |
|---------|-------------|
| Independent Scaling | Scale backend and AI service separately |
| Caching | Cache AI responses at gateway level |
| Load Balancing | Distribute load across multiple AI instances |
| Request Queuing | Queue requests during high load |

### Maintainability Benefits

| Benefit | Description |
|---------|-------------|
| Separation of Concerns | Clear boundaries between layers |
| Single Responsibility | Each service has one job |
| Easy Testing | Services tested independently |
| Version Control | Services versioned independently |
| Model Switching | Change AI models without affecting frontend |

## Common Mistakes to Avoid

### ❌ Mistake 1: Exposing AI Service

```yaml
# WRONG
ai-service:
  ports:
    - "8000:8000"  # Exposes to internet
```

**Why it's wrong:**
- No authentication
- Security risk
- Bypasses business logic

### ❌ Mistake 2: Frontend Calling AI Service Directly

```javascript
// WRONG
const response = await fetch('http://localhost:8000/tutor/explain', {
  method: 'POST',
  body: JSON.stringify({ topic: 'binary search' })
});
```

**Why it's wrong:**
- No authentication
- No progress tracking
- No audit logging

### ❌ Mistake 3: Storing AWS Credentials in Frontend

```javascript
// WRONG
const AWS_ACCESS_KEY = 'AKIAIOSFODNN7EXAMPLE';
```

**Why it's wrong:**
- Credentials exposed in browser
- Anyone can use your AWS account
- Massive security risk

## Correct Implementation

### ✅ Frontend Code

```javascript
// CORRECT
const response = await fetch('http://localhost:5000/ai/explain', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ topic: 'binary search' })
});
```

### ✅ Backend Code

```python
# CORRECT
@app.route('/ai/explain', methods=['POST'])
@jwt_required()
def explain_concept():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400
    
    # Call AI service internally
    result = AIServiceClient.explain(data['topic'])
    
    # Log request
    logger.info(f"User {current_user} requested explanation")
    
    return jsonify(result), 200
```

## Summary

**Key Takeaways:**

1. ✅ **Backend is the API Gateway** - All requests flow through it
2. ✅ **AI Service is Internal Only** - Never exposed to internet
3. ✅ **Frontend calls Backend Only** - Never calls AI service directly
4. ✅ **Authentication at Gateway** - JWT validation in backend
5. ✅ **Business Logic in Backend** - Progress tracking, recommendations
6. ✅ **Security by Design** - Multiple layers of protection

**Remember**: The API gateway pattern is not just about routing requests—it's about security, scalability, and maintainability. Every request must flow through the backend for proper authentication, validation, and business logic execution.
