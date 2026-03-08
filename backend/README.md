# SkillForge Backend (Flask)

Flask-based backend API gateway for the SkillForge AI+ platform.

## Features

- JWT-based authentication
- User registration and login
- AI service integration (tutor, quiz, debugger)
- Progress tracking and adaptive learning
- SQLAlchemy ORM with MySQL/SQLite support

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///skillforge.db
AI_SERVICE_URL=http://localhost:8000
```

### 3. Initialize Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 4. Run the Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### AI Services (Requires JWT)

- `POST /ai/explain` - Get AI explanation
- `POST /ai/quiz` - Generate quiz
- `POST /ai/debug` - Debug code
- `GET /ai/recommendations` - Get learning recommendations

### Progress Tracking (Requires JWT)

- `POST /api/quiz/complete` - Record quiz completion
- `GET /api/progress` - Get user progress

### Health

- `GET /health` - Health check
- `GET /` - API information

## Testing

```bash
pytest tests/ -v
```

## Database Models

### User
- id, username, email, password_hash, name
- Relationships: progress, quiz_history

### UserProgress
- id, user_id, topic, accuracy, attempts, time_spent
- Tracks learning progress per topic

### QuizHistory
- id, user_id, topic, difficulty, score, total_questions, time_spent
- Records all quiz completions

## Services

### UserProgressService
- `update_progress()` - Update user progress after quiz
- `get_user_progress()` - Get all progress for user
- `get_topic_progress()` - Get progress for specific topic

### QuizHistoryService
- `record_quiz_completion()` - Record quiz completion
- `get_user_quiz_history()` - Get quiz history
- `get_topic_statistics()` - Get statistics for topic

### AdaptiveLearningEngine
- `generate_recommendations()` - Generate personalized recommendations
- `get_next_difficulty()` - Suggest next difficulty level

## Adaptive Learning Rules

- Accuracy < 50% → Recommend easier material
- Accuracy 50-80% → Recommend practice
- Accuracy > 80% → Recommend advancing

## Architecture

```
backend/
├── app.py              # Flask application and routes
├── database.py         # Database initialization
├── models.py           # SQLAlchemy models
├── services.py         # Business logic services
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── tests/              # Unit tests
    └── test_app.py
```

## Integration with AI Service

The backend communicates with the AI microservice via HTTP:

```python
AIServiceClient.explain(topic)
AIServiceClient.generate_quiz(topic, difficulty, count)
AIServiceClient.debug_code(language, code)
```

All AI endpoints require JWT authentication and forward requests to the AI service.
