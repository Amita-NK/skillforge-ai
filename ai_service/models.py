"""
Pydantic models for API requests and responses
Defines data validation and serialization schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any


# Tutor Models
class ExplainRequest(BaseModel):
    """Request model for concept explanation"""
    topic: str = Field(..., min_length=1, max_length=500, description="Topic to explain")
    user_id: Optional[str] = Field(None, description="User ID for logging")
    
    @field_validator('topic')
    @classmethod
    def topic_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Topic cannot be empty or whitespace only')
        return v.strip()


class ExplanationResponse(BaseModel):
    """Response model for concept explanation"""
    explanation: str = Field(..., description="Detailed explanation of the concept")
    examples: List[str] = Field(default_factory=list, description="Code examples")
    analogy: str = Field(default="", description="Real-world analogy")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Source citations from RAG")


# Quiz Models
class QuizRequest(BaseModel):
    """Request model for quiz generation"""
    topic: str = Field(..., min_length=1, max_length=500, description="Quiz topic")
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$", description="Difficulty level")
    count: int = Field(..., ge=1, le=20, description="Number of questions")
    
    @field_validator('topic')
    @classmethod
    def topic_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Topic cannot be empty or whitespace only')
        return v.strip()


class Question(BaseModel):
    """Model for a single quiz question"""
    question: str = Field(..., description="Question text")
    options: List[str] = Field(..., min_length=2, max_length=6, description="Answer options")
    correct: int = Field(..., ge=0, description="Index of correct answer")
    explanation: str = Field(default="", description="Explanation of the answer")


class QuizResponse(BaseModel):
    """Response model for quiz generation"""
    questions: List[Question] = Field(..., description="List of quiz questions")


# Debugger Models
class DebugRequest(BaseModel):
    """Request model for code debugging"""
    language: str = Field(..., min_length=1, max_length=50, description="Programming language")
    code: str = Field(..., min_length=1, max_length=10000, description="Code to analyze")
    
    @field_validator('code')
    @classmethod
    def code_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Code cannot be empty or whitespace only')
        return v


class DebugError(BaseModel):
    """Model for a detected error"""
    line: int = Field(..., ge=0, description="Line number where error occurs")
    message: str = Field(..., description="Error description")


class DebugResponse(BaseModel):
    """Response model for code debugging"""
    errors: List[DebugError] = Field(default_factory=list, description="Detected errors")
    corrected_code: str = Field(..., description="Corrected version of the code")
    explanation: str = Field(..., description="Explanation of fixes")


# RAG Models
class RAGUploadRequest(BaseModel):
    """Request model for document upload"""
    file_url: Optional[str] = Field(None, description="File URL (deprecated, use s3_bucket/s3_key or content)")
    s3_bucket: Optional[str] = Field(None, description="S3 bucket name for document ingestion")
    s3_key: Optional[str] = Field(None, description="S3 object key for document ingestion")
    content: Optional[str] = Field(None, description="Direct content (for non-S3 uploads)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    @field_validator('s3_bucket')
    @classmethod
    def validate_s3_bucket(cls, v: Optional[str], info) -> Optional[str]:
        if v and info.data.get('s3_key') is None:
            raise ValueError('s3_key is required when s3_bucket is provided')
        return v
    
    @field_validator('s3_key')
    @classmethod
    def validate_s3_key(cls, v: Optional[str], info) -> Optional[str]:
        if v and info.data.get('s3_bucket') is None:
            raise ValueError('s3_bucket is required when s3_key is provided')
        return v


class RAGUploadResponse(BaseModel):
    """Response model for document upload"""
    status: str = Field(..., description="Processing status")
    chunks_processed: int = Field(..., ge=0, description="Number of chunks created")


class RAGSearchRequest(BaseModel):
    """Request model for context search"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class RAGSearchResult(BaseModel):
    """Model for a single search result"""
    content: str = Field(..., description="Chunk content")
    score: float = Field(..., description="Relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")


class RAGSearchResponse(BaseModel):
    """Response model for context search"""
    results: List[RAGSearchResult] = Field(..., description="Search results")


# Error Models
class ErrorDetail(BaseModel):
    """Model for error details"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    reason: str = Field(..., description="Error reason")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: Dict[str, Any] = Field(..., description="Error information")
    
    @classmethod
    def create(cls, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Create a standard error response"""
        from datetime import datetime, timezone
        return cls(error={
            "code": code,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
