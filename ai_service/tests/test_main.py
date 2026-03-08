"""
Tests for main FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint returns 200 and correct structure"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-service"
    assert "version" in data
    assert "aws_region" in data
    assert "model_id" in data


def test_root_endpoint():
    """Test root endpoint returns service information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "SkillForge AI Service"
    assert "version" in data
    assert "endpoints" in data
    assert "health" in data["endpoints"]
    assert "tutor" in data["endpoints"]
    assert "quiz" in data["endpoints"]
    assert "debug" in data["endpoints"]


def test_cors_headers():
    """Test CORS middleware is configured"""
    response = client.options("/health")
    # FastAPI/Starlette handles OPTIONS automatically with CORS middleware
    assert response.status_code in [200, 405]  # 405 if no explicit OPTIONS handler


class TestExplainEndpoint:
    """Tests for POST /tutor/explain endpoint"""
    
    @patch('main.rag_pipeline', None)  # Disable RAG for this test
    @patch('main.tutor_service')
    def test_successful_explanation(self, mock_tutor_service):
        """Test successful explanation generation"""
        # Mock the tutor service response
        mock_tutor_service.explain_concept.return_value = {
            'explanation': 'Binary search is an efficient algorithm...',
            'examples': ['def binary_search(arr, target): ...'],
            'analogy': 'Like finding a word in a dictionary'
        }
        
        # Make request
        response = client.post(
            "/tutor/explain",
            json={"topic": "binary search"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert 'explanation' in data
        assert 'examples' in data
        assert 'analogy' in data
        assert data['explanation'] == 'Binary search is an efficient algorithm...'
        
        # Verify service was called
        mock_tutor_service.explain_concept.assert_called_once()
    
    def test_empty_topic_validation(self):
        """Test that empty topic returns 422 validation error"""
        response = client.post(
            "/tutor/explain",
            json={"topic": ""}
        )
        
        assert response.status_code == 422  # Pydantic validation error
        # Empty string triggers min_length validation
        assert "at least 1 character" in str(response.json())
    
    def test_whitespace_only_topic_validation(self):
        """Test that whitespace-only topic returns 422 validation error"""
        response = client.post(
            "/tutor/explain",
            json={"topic": "   "}
        )
        
        assert response.status_code == 422  # Pydantic validation error
        assert "Topic cannot be empty" in str(response.json())
    
    def test_missing_topic_field(self):
        """Test that missing topic field returns 422 validation error"""
        response = client.post(
            "/tutor/explain",
            json={}
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    @patch('main.rag_pipeline', None)
    @patch('main.tutor_service')
    def test_service_value_error(self, mock_tutor_service):
        """Test handling of ValueError from tutor service"""
        mock_tutor_service.explain_concept.side_effect = ValueError("Invalid topic format")
        
        response = client.post(
            "/tutor/explain",
            json={"topic": "test topic"}
        )
        
        assert response.status_code == 400
        assert "Invalid topic format" in response.json()["detail"]
    
    @patch('main.rag_pipeline', None)
    @patch('main.tutor_service')
    def test_service_unexpected_error(self, mock_tutor_service):
        """Test handling of unexpected errors from tutor service"""
        mock_tutor_service.explain_concept.side_effect = Exception("Bedrock API error")
        
        response = client.post(
            "/tutor/explain",
            json={"topic": "test topic"}
        )
        
        assert response.status_code == 500
        assert "Failed to generate explanation" in response.json()["detail"]
    
    @patch('main.rag_pipeline', None)
    @patch('main.tutor_service')
    def test_with_user_id(self, mock_tutor_service):
        """Test explanation request with optional user_id"""
        mock_tutor_service.explain_concept.return_value = {
            'explanation': 'Test explanation',
            'examples': [],
            'analogy': 'Test analogy'
        }
        
        response = client.post(
            "/tutor/explain",
            json={"topic": "test topic", "user_id": "user123"}
        )
        
        assert response.status_code == 200
        mock_tutor_service.explain_concept.assert_called_once()


class TestQuizGenerateEndpoint:
    """Tests for POST /quiz/generate endpoint"""
    
    @patch('main.quiz_service')
    def test_successful_quiz_generation(self, mock_quiz_service):
        """Test successful quiz generation"""
        # Mock the quiz service response
        mock_quiz_service.generate_quiz.return_value = [
            {
                'question': 'What is Python?',
                'options': ['A snake', 'A programming language', 'A tool', 'A framework'],
                'correct': 1,
                'explanation': 'Python is a high-level programming language'
            },
            {
                'question': 'What is a variable?',
                'options': ['A constant', 'A storage location', 'A function', 'A class'],
                'correct': 1,
                'explanation': 'A variable stores data in memory'
            }
        ]
        
        # Make request
        response = client.post(
            "/quiz/generate",
            json={"topic": "Python basics", "difficulty": "easy", "count": 2}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert 'questions' in data
        assert len(data['questions']) == 2
        assert data['questions'][0]['question'] == 'What is Python?'
        assert data['questions'][0]['correct'] == 1
        
        # Verify service was called
        mock_quiz_service.generate_quiz.assert_called_once()
    
    def test_empty_topic_validation(self):
        """Test that empty topic returns 422 validation error"""
        response = client.post(
            "/quiz/generate",
            json={"topic": "", "difficulty": "easy", "count": 5}
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_whitespace_only_topic_validation(self):
        """Test that whitespace-only topic returns 422 validation error"""
        response = client.post(
            "/quiz/generate",
            json={"topic": "   ", "difficulty": "easy", "count": 5}
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_count_below_minimum(self):
        """Test that count < 1 returns 422 validation error"""
        response = client.post(
            "/quiz/generate",
            json={"topic": "Python", "difficulty": "easy", "count": 0}
        )
        
        assert response.status_code == 422  # Pydantic validation error
        assert "greater than or equal to 1" in str(response.json())
    
    def test_count_above_maximum(self):
        """Test that count > 20 returns 422 validation error"""
        response = client.post(
            "/quiz/generate",
            json={"topic": "Python", "difficulty": "easy", "count": 21}
        )
        
        assert response.status_code == 422  # Pydantic validation error
        assert "less than or equal to 20" in str(response.json())
    
    def test_count_boundary_minimum(self):
        """Test that count = 1 is valid (boundary test)"""
        with patch('main.quiz_service.generate_quiz') as mock_generate:
            mock_generate.return_value = [
                {
                    'question': 'Test question?',
                    'options': ['A', 'B', 'C', 'D'],
                    'correct': 0,
                    'explanation': 'Test explanation'
                }
            ]
            
            response = client.post(
                "/quiz/generate",
                json={"topic": "Python", "difficulty": "easy", "count": 1}
            )
            
            assert response.status_code == 200
            assert len(response.json()['questions']) == 1
    
    def test_count_boundary_maximum(self):
        """Test that count = 20 is valid (boundary test)"""
        with patch('main.quiz_service.generate_quiz') as mock_generate:
            # Create 20 mock questions
            mock_questions = [
                {
                    'question': f'Question {i}?',
                    'options': ['A', 'B', 'C', 'D'],
                    'correct': 0,
                    'explanation': f'Explanation {i}'
                }
                for i in range(20)
            ]
            mock_generate.return_value = mock_questions
            
            response = client.post(
                "/quiz/generate",
                json={"topic": "Python", "difficulty": "easy", "count": 20}
            )
            
            assert response.status_code == 200
            assert len(response.json()['questions']) == 20
    
    def test_invalid_difficulty(self):
        """Test that invalid difficulty returns 422 validation error"""
        response = client.post(
            "/quiz/generate",
            json={"topic": "Python", "difficulty": "extreme", "count": 5}
        )
        
        assert response.status_code == 422  # Pydantic validation error
        assert "difficulty" in str(response.json()).lower()
    
    def test_valid_difficulties(self):
        """Test that all valid difficulty levels are accepted"""
        with patch('main.quiz_service.generate_quiz') as mock_generate:
            mock_generate.return_value = [
                {
                    'question': 'Test?',
                    'options': ['A', 'B'],
                    'correct': 0,
                    'explanation': 'Test'
                }
            ]
            
            for difficulty in ['easy', 'medium', 'hard']:
                response = client.post(
                    "/quiz/generate",
                    json={"topic": "Python", "difficulty": difficulty, "count": 1}
                )
                assert response.status_code == 200, f"Failed for difficulty: {difficulty}"
    
    def test_missing_required_fields(self):
        """Test that missing required fields return 422 validation error"""
        # Missing topic
        response = client.post(
            "/quiz/generate",
            json={"difficulty": "easy", "count": 5}
        )
        assert response.status_code == 422
        
        # Missing difficulty
        response = client.post(
            "/quiz/generate",
            json={"topic": "Python", "count": 5}
        )
        assert response.status_code == 422
        
        # Missing count
        response = client.post(
            "/quiz/generate",
            json={"topic": "Python", "difficulty": "easy"}
        )
        assert response.status_code == 422
    
    @patch('main.quiz_service')
    def test_service_value_error(self, mock_quiz_service):
        """Test handling of ValueError from quiz service"""
        mock_quiz_service.generate_quiz.side_effect = ValueError("Invalid quiz parameters")
        
        response = client.post(
            "/quiz/generate",
            json={"topic": "Python", "difficulty": "easy", "count": 5}
        )
        
        assert response.status_code == 400
        assert "Invalid quiz parameters" in response.json()["detail"]
    
    @patch('main.quiz_service')
    def test_service_unexpected_error(self, mock_quiz_service):
        """Test handling of unexpected errors from quiz service"""
        mock_quiz_service.generate_quiz.side_effect = Exception("Bedrock API error")
        
        response = client.post(
            "/quiz/generate",
            json={"topic": "Python", "difficulty": "easy", "count": 5}
        )
        
        assert response.status_code == 500
        assert "Failed to generate quiz" in response.json()["detail"]
    
    @patch('main.quiz_service')
    def test_quiz_response_structure(self, mock_quiz_service):
        """Test that response has correct structure"""
        mock_quiz_service.generate_quiz.return_value = [
            {
                'question': 'What is 2+2?',
                'options': ['3', '4', '5', '6'],
                'correct': 1,
                'explanation': '2+2 equals 4'
            }
        ]
        
        response = client.post(
            "/quiz/generate",
            json={"topic": "Math", "difficulty": "easy", "count": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify top-level structure
        assert 'questions' in data
        assert isinstance(data['questions'], list)
        
        # Verify question structure
        question = data['questions'][0]
        assert 'question' in question
        assert 'options' in question
        assert 'correct' in question
        assert 'explanation' in question
        assert isinstance(question['options'], list)
        assert isinstance(question['correct'], int)
