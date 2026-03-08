"""
Configuration management for AI Service
Loads environment variables and provides application settings
"""
import os
import sys
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-v2")
    BEDROCK_EMBEDDING_MODEL: str = os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v1")
    
    # OpenSearch Configuration
    OPENSEARCH_ENDPOINT: Optional[str] = os.getenv("OPENSEARCH_ENDPOINT")
    OPENSEARCH_USERNAME: Optional[str] = os.getenv("OPENSEARCH_USERNAME")
    OPENSEARCH_PASSWORD: Optional[str] = os.getenv("OPENSEARCH_PASSWORD")
    
    # S3 Configuration
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # API Configuration
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P: float = float(os.getenv("TOP_P", "0.9"))


def validate_required_environment_variables() -> None:
    """
    Validate that all required environment variables are present.
    
    This function checks for critical environment variables needed for the AI Service
    to function properly. If any required variables are missing, it logs descriptive
    error messages and raises a RuntimeError to prevent the service from starting.
    
    Required variables:
    - AWS_REGION: AWS region for Bedrock and other services
    - BEDROCK_MODEL_ID: Model ID for Bedrock inference
    
    Raises:
        RuntimeError: If any required environment variables are missing
    """
    missing_vars: List[str] = []
    
    # Check required AWS configuration
    if not os.getenv("AWS_REGION"):
        missing_vars.append("AWS_REGION")
    
    # Check required Bedrock configuration
    if not os.getenv("BEDROCK_MODEL_ID"):
        missing_vars.append("BEDROCK_MODEL_ID")
    
    # If any required variables are missing, fail with descriptive error
    if missing_vars:
        error_message = (
            f"ERROR: Missing required environment variables: {', '.join(missing_vars)}\n"
            f"The AI Service cannot start without these variables.\n"
            f"Please set the following environment variables:\n"
        )
        for var in missing_vars:
            error_message += f"  - {var}\n"
        error_message += "\nRefer to .env.example for configuration guidance."
        
        # Log to stderr for visibility
        print(error_message, file=sys.stderr)
        
        # Raise error to prevent service startup
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Global settings instance
settings = Settings()


class PromptTemplates:
    """Prompt templates for different AI operations"""
    
    TUTOR = """You are an expert programming tutor.
Explain the following concept in simple language.

Include:
- Step-by-step explanation
- Real-world analogy
- Example code with comments

Topic: {topic}

Context from course materials:
{context}
"""

    QUIZ = """Generate {count} multiple choice questions on the topic: {topic}

Difficulty: {difficulty}

Return JSON format:
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct": 0,
    "explanation": "..."
  }}
]
"""

    DEBUGGER = """You are a senior software engineer.

Analyze the following {language} code.
Identify errors and provide corrected code.

Code:
{code}

Return JSON format:
{{
  "errors": [{{"line": 0, "message": "..."}}],
  "corrected_code": "...",
  "explanation": "..."
}}
"""
