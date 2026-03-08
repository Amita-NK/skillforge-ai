"""
SkillForge AI+ - AI Service Main Application
FastAPI application for AI operations and Amazon Bedrock integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from config import settings, validate_required_environment_variables
from models import (
    ExplainRequest, ExplanationResponse, QuizRequest, QuizResponse, 
    DebugRequest, DebugResponse, RAGUploadRequest, RAGUploadResponse,
    RAGSearchRequest, RAGSearchResponse
)
from bedrock_client import BedrockClient
from tutor import TutorService
from quiz import QuizService
from debugger import DebuggerService
from embeddings import EmbeddingsService
from rag import RAGPipeline
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate required environment variables on startup
try:
    validate_required_environment_variables()
    logger.info("Environment variable validation passed")
except RuntimeError as e:
    logger.error(f"Environment variable validation failed: {str(e)}")
    raise

# Initialize FastAPI application
app = FastAPI(
    title="SkillForge AI Service",
    description="AI microservice for tutoring, quiz generation, and code debugging",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bedrock client and services
bedrock_client = BedrockClient(
    region=settings.AWS_REGION,
    model_id=settings.BEDROCK_MODEL_ID
)
tutor_service = TutorService(bedrock_client)
quiz_service = QuizService(bedrock_client)
debugger_service = DebuggerService(bedrock_client)

# Initialize RAG pipeline (if OpenSearch is configured)
rag_pipeline = None
opensearch_endpoint = os.getenv('OPENSEARCH_ENDPOINT')
if opensearch_endpoint:
    try:
        embeddings_service = EmbeddingsService(region=settings.AWS_REGION)
        rag_pipeline = RAGPipeline(
            embeddings_service=embeddings_service,
            opensearch_endpoint=opensearch_endpoint,
            opensearch_user=os.getenv('OPENSEARCH_USER'),
            opensearch_password=os.getenv('OPENSEARCH_PASSWORD')
        )
        logger.info("RAG pipeline initialized successfully")
    except Exception as e:
        logger.warning(f"RAG pipeline initialization failed: {str(e)}")
        logger.warning("RAG features will be disabled")
else:
    logger.info("OpenSearch not configured, RAG features disabled")


@app.get("/health")
async def health_check():
    """
    Health check endpoint for ECS monitoring
    Returns service status and configuration info
    """
    return {
        "status": "healthy",
        "service": "ai-service",
        "version": "1.0.0",
        "aws_region": settings.AWS_REGION,
        "model_id": settings.BEDROCK_MODEL_ID
    }


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "SkillForge AI Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "tutor": "/tutor/explain",
            "quiz": "/quiz/generate",
            "debug": "/debug/analyze"
        }
    }


@app.post("/tutor/explain", response_model=ExplanationResponse)
async def explain_concept(request: ExplainRequest):
    """
    Generate a comprehensive explanation for a given topic
    
    Args:
        request: ExplainRequest containing topic and optional user_id
        
    Returns:
        ExplanationResponse with explanation, examples, and analogy
        
    Raises:
        HTTPException: 400 if topic is empty or invalid
        HTTPException: 500 if AI generation fails
    """
    # Validate topic parameter
    if not request.topic or not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    try:
        # Get context from RAG if available
        context = ""
        if rag_pipeline:
            try:
                context = rag_pipeline.get_context_for_query(request.topic, top_k=3)
                logger.info(f"Retrieved context for topic: {request.topic}")
            except Exception as e:
                logger.warning(f"Failed to retrieve context: {str(e)}")
        
        # Call tutor service with context
        result = tutor_service.explain_concept(request.topic, context=context)
        
        # Return structured response
        return ExplanationResponse(**result)
    
    except ValueError as e:
        # Handle validation errors from tutor service
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Failed to generate explanation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate explanation. Please try again later."
        )


@app.post("/quiz/generate", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """
    Generate a quiz with multiple choice questions
    
    Args:
        request: QuizRequest containing topic, difficulty, and count
        
    Returns:
        QuizResponse with list of questions
        
    Raises:
        HTTPException: 400 if parameters are invalid (topic empty, invalid difficulty, count out of range)
        HTTPException: 500 if quiz generation fails
    """
    # Validate topic parameter
    if not request.topic or not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    # Validate count is between 1 and 20
    if request.count < 1 or request.count > 20:
        raise HTTPException(
            status_code=400,
            detail="Count must be between 1 and 20"
        )
    
    # Validate difficulty
    if request.difficulty not in ['easy', 'medium', 'hard']:
        raise HTTPException(
            status_code=400,
            detail="Difficulty must be 'easy', 'medium', or 'hard'"
        )
    
    try:
        # Call quiz service
        questions = quiz_service.generate_quiz(
            topic=request.topic,
            difficulty=request.difficulty,
            count=request.count
        )
        
        # Return structured response
        return QuizResponse(questions=questions)
    
    except ValueError as e:
        # Handle validation errors from quiz service
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Handle quiz generation errors
        logger.error(f"Failed to generate quiz: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate quiz. Please try again later."
        )


@app.post("/debug/analyze", response_model=DebugResponse)
async def analyze_code(request: DebugRequest):
    """
    Analyze code and provide debugging assistance
    
    Args:
        request: DebugRequest containing language and code
        
    Returns:
        DebugResponse with errors, corrected code, and explanation
        
    Raises:
        HTTPException: 400 if parameters are invalid (empty code, unsupported language)
        HTTPException: 500 if code analysis fails
    """
    # Validate language parameter
    if not request.language or not request.language.strip():
        raise HTTPException(status_code=400, detail="Language cannot be empty")
    
    # Validate code parameter
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    # Validate code length
    if len(request.code) > 10000:
        raise HTTPException(
            status_code=400,
            detail="Code is too long (maximum 10000 characters)"
        )
    
    try:
        # Call debugger service
        result = debugger_service.analyze_code(
            language=request.language,
            code=request.code
        )
        
        # Return structured response
        return DebugResponse(**result)
    
    except ValueError as e:
        # Handle validation errors from debugger service
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Handle code analysis errors
        logger.error(f"Failed to analyze code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze code. Please try again later."
        )


@app.post("/rag/upload", response_model=RAGUploadResponse)
async def upload_document(request: RAGUploadRequest):
    """
    Upload and process a document for RAG
    Supports both S3 document ingestion and direct content upload
    
    Args:
        request: RAGUploadRequest with either:
            - s3_bucket + s3_key for S3 ingestion
            - content for direct upload
            - file_url + metadata.content (legacy)
        
    Returns:
        RAGUploadResponse with processing status
        
    Raises:
        HTTPException: 503 if RAG is not configured
        HTTPException: 400 if parameters are invalid
        HTTPException: 500 if processing fails
    """
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline is not configured. Set OPENSEARCH_ENDPOINT environment variable."
        )
    
    try:
        chunks_processed = 0
        
        # S3 ingestion path
        if request.s3_bucket and request.s3_key:
            logger.info(f"Processing S3 document: s3://{request.s3_bucket}/{request.s3_key}")
            chunks_processed = rag_pipeline.process_s3_document(
                bucket=request.s3_bucket,
                key=request.s3_key,
                metadata=request.metadata
            )
        
        # Direct content upload path
        elif request.content:
            logger.info("Processing direct content upload")
            source = request.metadata.get('source', 'direct_upload')
            chunks_processed = rag_pipeline.process_document(
                content=request.content,
                metadata={
                    **request.metadata,
                    'source': source
                }
            )
        
        # Legacy path (file_url with content in metadata)
        elif request.file_url:
            content = request.metadata.get('content', '')
            if not content:
                raise HTTPException(
                    status_code=400,
                    detail="Content must be provided in metadata.content field when using file_url"
                )
            
            logger.info(f"Processing legacy upload: {request.file_url}")
            chunks_processed = rag_pipeline.process_document(
                content=content,
                metadata={
                    'source': request.file_url,
                    'topic': request.metadata.get('topic', 'unknown'),
                    'upload_date': request.metadata.get('upload_date', 'unknown')
                }
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either s3_bucket+s3_key, content, or file_url with metadata.content"
            )
        
        logger.info(f"Successfully processed document: {chunks_processed} chunks")
        
        return RAGUploadResponse(
            status="success",
            chunks_processed=chunks_processed
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Failed to process document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )


@app.post("/rag/search", response_model=RAGSearchResponse)
async def search_context(request: RAGSearchRequest):
    """
    Search for relevant context in the knowledge base
    
    Args:
        request: RAGSearchRequest with query and top_k
        
    Returns:
        RAGSearchResponse with search results
        
    Raises:
        HTTPException: 503 if RAG is not configured
        HTTPException: 400 if query is invalid
        HTTPException: 500 if search fails
    """
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline is not configured. Set OPENSEARCH_ENDPOINT environment variable."
        )
    
    # Validate query
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Search for relevant context
        results = rag_pipeline.search(
            query=request.query,
            top_k=request.top_k
        )
        
        logger.info(f"Search returned {len(results)} results for query: {request.query[:50]}...")
        
        return RAGSearchResponse(results=results)
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Search failed. Please try again later."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
