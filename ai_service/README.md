# SkillForge AI Service

Python FastAPI microservice for AI operations and Amazon Bedrock integration.

## Features

- AI Tutoring: Concept explanations with examples and analogies
- Quiz Generation: Adaptive quiz creation with multiple difficulty levels
- Code Debugging: AI-powered code analysis and error correction
- RAG Pipeline: Knowledge retrieval using vector embeddings

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your AWS credentials and configuration
```

3. Run the service:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /` - Service information
- `POST /tutor/explain` - Request concept explanation
- `POST /quiz/generate` - Generate quiz questions
- `POST /debug/analyze` - Analyze and debug code
- `POST /rag/upload` - Upload course materials
- `GET /rag/search` - Search knowledge base

## Testing

Run tests with pytest:
```bash
pytest tests/ -v --cov
```

## Architecture

- **main.py**: FastAPI application entry point
- **config.py**: Configuration management and prompt templates
- **models.py**: Pydantic data models for validation
- **bedrock_client.py**: Amazon Bedrock API wrapper (to be implemented)
- **tutor.py**: AI tutoring logic (to be implemented)
- **quiz.py**: Quiz generation logic (to be implemented)
- **debugger.py**: Code debugging logic (to be implemented)
- **rag.py**: RAG pipeline implementation (to be implemented)
- **embeddings.py**: Embedding generation (to be implemented)
