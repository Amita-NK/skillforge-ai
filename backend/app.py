"""
SkillForge AI+ Backend - Flask Application
API gateway and business logic for the SkillForge platform
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from functools import wraps
import logging
import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Environment Variable Validation
# ============================================================================

def validate_environment_variables():
    """
    Validate that all required environment variables are present.
    
    Requirements: 12.3, 12.5, 12.6
    - Backend SHALL load database credentials from environment variables
    - Services SHALL validate that required environment variables are present
    - IF required environment variables are missing, service SHALL fail to start
    
    Raises:
        SystemExit: If required environment variables are missing
    """
    required_vars = {
        'DATABASE_URL': 'Database connection URL (e.g., mysql+pymysql://user:pass@host:port/db)',
        'SECRET_KEY': 'Flask secret key for session management',
        'JWT_SECRET_KEY': 'JWT secret key for token signing',
        'AI_SERVICE_URL': 'URL of the AI microservice'
    }
    
    missing_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value or value.strip() == '':
            missing_vars.append(f"  - {var_name}: {description}")
            logger.error(f"Missing required environment variable: {var_name}")
    
    if missing_vars:
        error_message = (
            "\n" + "="*80 + "\n"
            "CONFIGURATION ERROR: Required environment variables are missing\n"
            "="*80 + "\n"
            "The following environment variables must be set:\n\n"
            + "\n".join(missing_vars) + "\n\n"
            "Please set these variables in your environment or .env file.\n"
            "See .env.example for reference.\n"
            "="*80
        )
        logger.critical(error_message)
        print(error_message, file=sys.stderr)
        sys.exit(1)
    
    logger.info("Environment variable validation passed")
    
    # Log configuration (without sensitive values)
    logger.info(f"Database URL configured: {os.getenv('DATABASE_URL', '').split('@')[-1] if '@' in os.getenv('DATABASE_URL', '') else 'SQLite'}")
    logger.info(f"AI Service URL: {os.getenv('AI_SERVICE_URL')}")


# Validate environment variables before initializing the app
validate_environment_variables()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///skillforge.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
jwt = JWTManager(app)

# AI Service configuration
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://localhost:8000')
AI_SERVICE_TIMEOUT = 60  # seconds

# Import database and models
from database import db, init_db
from models import User, UserProgress, QuizHistory
from services import UserProgressService, QuizHistoryService, AdaptiveLearningEngine

# Initialize database
init_db(app)


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Health Check
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'skillforge-backend',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'SkillForge Backend API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'auth': {
                'login': '/auth/login',
                'register': '/auth/register'
            },
            'ai': {
                'explain': '/ai/explain',
                'quiz': '/ai/quiz',
                'debug': '/ai/debug',
                'recommendations': '/ai/recommendations'
            },
            'progress': {
                'get': '/api/progress',
                'quiz_complete': '/api/quiz/complete'
            }
        }
    })


# ============================================================================
# AI Service Client
# ============================================================================

class AIServiceClient:
    """Client for communicating with the AI microservice"""
    
    @staticmethod
    def explain(topic: str) -> dict:
        """
        Get explanation from AI service
        
        Args:
            topic: Topic to explain
            
        Returns:
            Explanation response
            
        Raises:
            requests.RequestException: If request fails
        """
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
    
    @staticmethod
    def generate_quiz(topic: str, difficulty: str, count: int) -> dict:
        """
        Generate quiz from AI service
        
        Args:
            topic: Quiz topic
            difficulty: Difficulty level
            count: Number of questions
            
        Returns:
            Quiz response
        """
        try:
            response = requests.post(
                f"{AI_SERVICE_URL}/quiz/generate",
                json={
                    'topic': topic,
                    'difficulty': difficulty,
                    'count': count
                },
                timeout=AI_SERVICE_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise Exception("AI service request timed out")
        except requests.RequestException as e:
            logger.error(f"AI service error: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")
    
    @staticmethod
    def debug_code(language: str, code: str) -> dict:
        """
        Debug code using AI service
        
        Args:
            language: Programming language
            code: Code to debug
            
        Returns:
            Debug response
        """
        try:
            response = requests.post(
                f"{AI_SERVICE_URL}/debug/analyze",
                json={
                    'language': language,
                    'code': code
                },
                timeout=AI_SERVICE_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise Exception("AI service request timed out")
        except requests.RequestException as e:
            logger.error(f"AI service error: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")
    
    @staticmethod
    def upload_rag_document(s3_bucket: str = None, s3_key: str = None, 
                           content: str = None, metadata: dict = None) -> dict:
        """
        Upload document to RAG pipeline
        
        Args:
            s3_bucket: S3 bucket name (optional)
            s3_key: S3 object key (optional)
            content: Direct content (optional)
            metadata: Document metadata
            
        Returns:
            Upload response
        """
        try:
            payload = {'metadata': metadata or {}}
            
            if s3_bucket and s3_key:
                payload['s3_bucket'] = s3_bucket
                payload['s3_key'] = s3_key
            elif content:
                payload['content'] = content
            else:
                raise ValueError("Must provide either s3_bucket+s3_key or content")
            
            response = requests.post(
                f"{AI_SERVICE_URL}/rag/upload",
                json=payload,
                timeout=AI_SERVICE_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise Exception("AI service request timed out")
        except requests.RequestException as e:
            logger.error(f"AI service error: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")


# ============================================================================
# Authentication Endpoints (Placeholder - integrate with existing auth)
# ============================================================================

@app.route('/auth/login', methods=['POST'])
def login():
    """
    User login endpoint
    
    Expected JSON:
        {
            "username": "user@example.com",
            "password": "password123"
        }
    
    Returns:
        {
            "access_token": "jwt_token",
            "user": {"id": 1, "username": "user@example.com"}
        }
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    try:
        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/auth/register', methods=['POST'])
def register():
    """
    User registration endpoint
    
    Expected JSON:
        {
            "username": "user@example.com",
            "password": "password123",
            "email": "user@example.com",
            "name": "John Doe"
        }
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    try:
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            name=data.get('name', '')
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {user.username}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


# ============================================================================
# AI Endpoints (Protected)
# ============================================================================

@app.route('/ai/explain', methods=['POST'])
@jwt_required()
def explain_concept():
    """
    Get AI explanation for a concept
    
    Expected JSON:
        {
            "topic": "binary search"
        }
    
    Returns:
        {
            "explanation": "...",
            "examples": [...],
            "analogy": "..."
        }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400
    
    try:
        # Call AI service
        result = AIServiceClient.explain(data['topic'])
        
        # Log interaction (TODO: save to database)
        logger.info(f"User {current_user} requested explanation for: {data['topic']}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Failed to get explanation: {str(e)}")
        return jsonify({'error': 'Failed to generate explanation'}), 500


@app.route('/ai/quiz', methods=['POST'])
@jwt_required()
def generate_quiz():
    """
    Generate AI quiz
    
    Expected JSON:
        {
            "topic": "Python basics",
            "difficulty": "medium",
            "count": 5
        }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400
    
    if not data.get('difficulty') or data['difficulty'] not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Valid difficulty required (easy, medium, hard)'}), 400
    
    count = data.get('count', 5)
    if not isinstance(count, int) or count < 1 or count > 20:
        return jsonify({'error': 'Count must be between 1 and 20'}), 400
    
    try:
        # Call AI service
        result = AIServiceClient.generate_quiz(
            topic=data['topic'],
            difficulty=data['difficulty'],
            count=count
        )
        
        logger.info(f"User {current_user} generated quiz on: {data['topic']}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Failed to generate quiz: {str(e)}")
        return jsonify({'error': 'Failed to generate quiz'}), 500


@app.route('/ai/debug', methods=['POST'])
@jwt_required()
def debug_code():
    """
    Debug code using AI
    
    Expected JSON:
        {
            "language": "python",
            "code": "def add(a, b)\n    return a + b"
        }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('language') or not data.get('code'):
        return jsonify({'error': 'Language and code are required'}), 400
    
    try:
        # Call AI service
        result = AIServiceClient.debug_code(
            language=data['language'],
            code=data['code']
        )
        
        logger.info(f"User {current_user} debugged {data['language']} code")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Failed to debug code: {str(e)}")
        return jsonify({'error': 'Failed to analyze code'}), 500


@app.route('/ai/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """
    Get personalized learning recommendations based on user progress
    
    Returns:
        {
            "recommendations": [
                {
                    "topic": "Python Functions",
                    "type": "PRACTICE",
                    "reason": "Practice more questions on Python Functions"
                }
            ]
        }
    """
    current_user_id = int(get_jwt_identity())
    
    try:
        # Get recommendations from adaptive learning engine
        recommendations = AdaptiveLearningEngine.generate_recommendations(current_user_id)
        
        return jsonify({'recommendations': recommendations}), 200
    
    except Exception as e:
        logger.error(f"Failed to get recommendations: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500


# ============================================================================
# Progress Tracking Endpoints
# ============================================================================

@app.route('/api/quiz/complete', methods=['POST'])
@jwt_required()
def complete_quiz():
    """
    Record quiz completion and update user progress
    
    Expected JSON:
        {
            "topic": "Python basics",
            "difficulty": "medium",
            "score": 80,
            "total_questions": 10,
            "time_spent": 300
        }
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('topic') or data.get('score') is None or data.get('total_questions') is None:
        return jsonify({'error': 'Topic, score, and total_questions are required'}), 400
    
    try:
        # Record quiz completion
        quiz_record = QuizHistoryService.record_quiz_completion(
            user_id=current_user_id,
            topic=data['topic'],
            difficulty=data.get('difficulty', 'medium'),
            score=data['score'],
            total_questions=data['total_questions'],
            time_spent=data.get('time_spent', 0)
        )
        
        # Update user progress
        progress = UserProgressService.update_progress(
            user_id=current_user_id,
            topic=data['topic'],
            score=data['score'],
            total_questions=data['total_questions'],
            time_spent=data.get('time_spent', 0)
        )
        
        logger.info(f"User {current_user_id} completed quiz: {data['topic']}, score: {data['score']}")
        
        return jsonify({
            'message': 'Quiz completion recorded',
            'score': data['score'],
            'accuracy': progress.accuracy,
            'quiz_id': quiz_record.id
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to record quiz completion: {str(e)}")
        return jsonify({'error': 'Failed to record quiz completion'}), 500


@app.route('/api/progress', methods=['GET'])
@jwt_required()
def get_progress():
    """
    Get user progress data
    
    Returns:
        {
            "progress": [
                {
                    "topic": "Python Basics",
                    "accuracy": 75.5,
                    "attempts": 5,
                    "time_spent": 1200,
                    "last_updated": "2024-01-15T10:30:00"
                }
            ]
        }
    """
    current_user_id = int(get_jwt_identity())
    
    try:
        # Get user progress from database
        progress_records = UserProgressService.get_user_progress(current_user_id)
        
        progress = [record.to_dict() for record in progress_records]
        
        return jsonify({'progress': progress}), 200
    
    except Exception as e:
        logger.error(f"Failed to get progress: {str(e)}")
        return jsonify({'error': 'Failed to get progress'}), 500


@app.route('/ai/rag/upload', methods=['POST'])
@jwt_required()
def upload_rag_document():
    """
    Upload document to RAG pipeline for knowledge base ingestion
    Supports both S3 document ingestion and direct content upload
    
    Expected JSON:
        {
            "s3_bucket": "my-bucket",  // Optional: S3 bucket name
            "s3_key": "docs/python.pdf",  // Optional: S3 object key
            "content": "...",  // Optional: Direct content
            "metadata": {  // Optional: Document metadata
                "topic": "Python Programming",
                "author": "John Doe",
                "upload_date": "2024-01-15"
            }
        }
    
    Returns:
        {
            "status": "success",
            "chunks_processed": 42
        }
    """
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    # Extract parameters
    s3_bucket = data.get('s3_bucket')
    s3_key = data.get('s3_key')
    content = data.get('content')
    metadata = data.get('metadata', {})
    
    # Validate input
    if not ((s3_bucket and s3_key) or content):
        return jsonify({
            'error': 'Must provide either s3_bucket+s3_key or content'
        }), 400
    
    try:
        # Call AI service
        result = AIServiceClient.upload_rag_document(
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            content=content,
            metadata=metadata
        )
        
        logger.info(f"User {current_user} uploaded document to RAG: {s3_bucket}/{s3_key if s3_bucket else 'direct'}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Failed to upload document: {str(e)}")
        return jsonify({'error': f'Failed to upload document: {str(e)}'}), 500


# ============================================================================
# Run Application
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting SkillForge Backend on port {port}")
    logger.info(f"AI Service URL: {AI_SERVICE_URL}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
