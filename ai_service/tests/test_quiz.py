"""
Unit tests for quiz generation module
"""
import pytest
import json
from unittest.mock import Mock, patch
from quiz import QuizService, QuizGenerationError, create_quiz_service
from bedrock_client import BedrockClient, BedrockClientError


@pytest.fixture
def mock_bedrock_client():
    """Create a mock BedrockClient for testing"""
    client = Mock(spec=BedrockClient)
    return client


@pytest.fixture
def quiz_service(mock_bedrock_client):
    """Create a QuizService instance with mock client"""
    return QuizService(mock_bedrock_client)


class TestQuizServiceValidation:
    """Test input validation"""
    
    def test_empty_topic_raises_error(self, quiz_service):
        """Test that empty topic raises ValueError"""
        with pytest.raises(ValueError, match="Topic cannot be empty"):
            quiz_service.generate_quiz("", "easy", 5)
    
    def test_whitespace_topic_raises_error(self, quiz_service):
        """Test that whitespace-only topic raises ValueError"""
        with pytest.raises(ValueError, match="Topic cannot be empty"):
            quiz_service.generate_quiz("   ", "medium", 5)
    
    def test_invalid_difficulty_raises_error(self, quiz_service):
        """Test that invalid difficulty raises ValueError"""
        with pytest.raises(ValueError, match="Difficulty must be one of"):
            quiz_service.generate_quiz("Python", "super_hard", 5)
    
    def test_count_below_minimum_raises_error(self, quiz_service):
        """Test that count below 1 raises ValueError"""
        with pytest.raises(ValueError, match="Count must be between"):
            quiz_service.generate_quiz("Python", "easy", 0)
    
    def test_count_above_maximum_raises_error(self, quiz_service):
        """Test that count above 20 raises ValueError"""
        with pytest.raises(ValueError, match="Count must be between"):
            quiz_service.generate_quiz("Python", "easy", 21)
    
    def test_non_integer_count_raises_error(self, quiz_service):
        """Test that non-integer count raises ValueError"""
        with pytest.raises(ValueError, match="Count must be an integer"):
            quiz_service.generate_quiz("Python", "easy", "5")


class TestQuizGeneration:
    """Test quiz generation functionality"""
    
    def test_successful_quiz_generation(self, quiz_service, mock_bedrock_client):
        """Test successful quiz generation with valid response"""
        # Mock Bedrock response
        mock_response = json.dumps([
            {
                "question": "What is a variable?",
                "options": ["A storage location", "A function", "A loop", "A class"],
                "correct": 0,
                "explanation": "A variable is a storage location for data"
            },
            {
                "question": "What is a function?",
                "options": ["A variable", "A reusable code block", "A data type", "An operator"],
                "correct": 1,
                "explanation": "A function is a reusable block of code"
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        # Generate quiz
        questions = quiz_service.generate_quiz("Python basics", "easy", 2)
        
        # Verify results
        assert len(questions) == 2
        assert questions[0]['question'] == "What is a variable?"
        assert len(questions[0]['options']) == 4
        assert questions[0]['correct'] == 0
        assert questions[0]['explanation'] == "A variable is a storage location for data"
        
        # Verify Bedrock was called correctly
        mock_bedrock_client.invoke_model.assert_called_once()
        call_args = mock_bedrock_client.invoke_model.call_args
        assert "Python basics" in call_args.kwargs['prompt']
        assert "easy" in call_args.kwargs['prompt']
    
    def test_quiz_generation_with_different_difficulties(self, quiz_service, mock_bedrock_client):
        """Test quiz generation with different difficulty levels"""
        mock_response = json.dumps([
            {
                "question": "Test question",
                "options": ["A", "B", "C", "D"],
                "correct": 0,
                "explanation": "Test explanation"
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        # Test each difficulty level
        for difficulty in ['easy', 'medium', 'hard']:
            questions = quiz_service.generate_quiz("Python", difficulty, 1)
            assert len(questions) == 1
            
            # Verify difficulty was passed to prompt
            call_args = mock_bedrock_client.invoke_model.call_args
            assert difficulty in call_args.kwargs['prompt']
    
    def test_quiz_generation_with_json_in_code_block(self, quiz_service, mock_bedrock_client):
        """Test parsing JSON from code block"""
        mock_response = """Here are your questions:
```json
[
    {
        "question": "What is Python?",
        "options": ["A snake", "A programming language", "A tool", "A framework"],
        "correct": 1,
        "explanation": "Python is a programming language"
    }
]
```
"""
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        questions = quiz_service.generate_quiz("Python", "easy", 1)
        
        assert len(questions) == 1
        assert questions[0]['question'] == "What is Python?"
    
    def test_quiz_generation_handles_missing_explanation(self, quiz_service, mock_bedrock_client):
        """Test that missing explanation field is handled gracefully"""
        mock_response = json.dumps([
            {
                "question": "What is a variable?",
                "options": ["A", "B", "C", "D"],
                "correct": 0
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        questions = quiz_service.generate_quiz("Python", "easy", 1)
        
        assert len(questions) == 1
        assert questions[0]['explanation'] == ""


class TestQuizParsingErrors:
    """Test error handling for malformed responses"""
    
    def test_invalid_json_raises_error(self, quiz_service, mock_bedrock_client):
        """Test that invalid JSON raises QuizGenerationError"""
        mock_bedrock_client.invoke_model.return_value = "This is not JSON"
        
        with pytest.raises(QuizGenerationError, match="did not contain valid JSON"):
            quiz_service.generate_quiz("Python", "easy", 1)
    
    def test_malformed_json_raises_error(self, quiz_service, mock_bedrock_client):
        """Test that malformed JSON raises QuizGenerationError"""
        mock_bedrock_client.invoke_model.return_value = "[{invalid json}]"
        
        with pytest.raises(QuizGenerationError, match="Failed to parse JSON"):
            quiz_service.generate_quiz("Python", "easy", 1)
    
    def test_non_array_json_raises_error(self, quiz_service, mock_bedrock_client):
        """Test that non-array JSON raises QuizGenerationError"""
        mock_bedrock_client.invoke_model.return_value = json.dumps({"not": "an array"})
        
        with pytest.raises(QuizGenerationError, match="did not contain valid JSON"):
            quiz_service.generate_quiz("Python", "easy", 1)
    
    def test_empty_array_raises_error(self, quiz_service, mock_bedrock_client):
        """Test that empty array raises QuizGenerationError"""
        mock_bedrock_client.invoke_model.return_value = json.dumps([])
        
        with pytest.raises(QuizGenerationError, match="No questions were generated"):
            quiz_service.generate_quiz("Python", "easy", 1)
    
    def test_missing_required_field_skips_question(self, quiz_service, mock_bedrock_client):
        """Test that questions with missing fields are skipped"""
        mock_response = json.dumps([
            {
                "question": "Valid question",
                "options": ["A", "B"],
                "correct": 0
            },
            {
                "question": "Missing options field",
                "correct": 0
            },
            {
                "question": "Another valid question",
                "options": ["A", "B"],
                "correct": 1
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        questions = quiz_service.generate_quiz("Python", "easy", 3)
        
        # Should get 2 valid questions
        assert len(questions) == 2
        assert questions[0]['question'] == "Valid question"
        assert questions[1]['question'] == "Another valid question"
    
    def test_invalid_correct_index_skips_question(self, quiz_service, mock_bedrock_client):
        """Test that questions with invalid correct index are skipped"""
        mock_response = json.dumps([
            {
                "question": "Valid question",
                "options": ["A", "B"],
                "correct": 0
            },
            {
                "question": "Invalid correct index",
                "options": ["A", "B"],
                "correct": 5  # Out of range
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        questions = quiz_service.generate_quiz("Python", "easy", 2)
        
        # Should get 1 valid question
        assert len(questions) == 1
        assert questions[0]['question'] == "Valid question"
    
    def test_too_few_options_skips_question(self, quiz_service, mock_bedrock_client):
        """Test that questions with fewer than 2 options are skipped"""
        mock_response = json.dumps([
            {
                "question": "Only one option",
                "options": ["A"],
                "correct": 0
            },
            {
                "question": "Valid question",
                "options": ["A", "B"],
                "correct": 0
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        questions = quiz_service.generate_quiz("Python", "easy", 2)
        
        assert len(questions) == 1
        assert questions[0]['question'] == "Valid question"


class TestBedrockIntegration:
    """Test Bedrock client integration"""
    
    def test_bedrock_error_raises_quiz_generation_error(self, quiz_service, mock_bedrock_client):
        """Test that Bedrock errors are wrapped in QuizGenerationError"""
        mock_bedrock_client.invoke_model.side_effect = BedrockClientError("API error")
        
        with pytest.raises(QuizGenerationError, match="Failed to generate quiz"):
            quiz_service.generate_quiz("Python", "easy", 1)
    
    def test_bedrock_called_with_correct_parameters(self, quiz_service, mock_bedrock_client):
        """Test that Bedrock is called with appropriate parameters"""
        mock_response = json.dumps([
            {
                "question": "Test",
                "options": ["A", "B"],
                "correct": 0
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        quiz_service.generate_quiz("Python", "medium", 5)
        
        # Verify call parameters
        call_args = mock_bedrock_client.invoke_model.call_args
        assert call_args.kwargs['max_tokens'] == 3000
        assert call_args.kwargs['temperature'] == 0.7
        assert call_args.kwargs['top_p'] == 0.9


class TestFactoryFunction:
    """Test factory function"""
    
    def test_create_quiz_service(self, mock_bedrock_client):
        """Test that factory function creates QuizService instance"""
        service = create_quiz_service(mock_bedrock_client)
        
        assert isinstance(service, QuizService)
        assert service.bedrock == mock_bedrock_client


class TestEdgeCases:
    """Test edge cases"""
    
    def test_boundary_count_values(self, quiz_service, mock_bedrock_client):
        """Test boundary values for count parameter"""
        mock_response = json.dumps([
            {
                "question": "Test",
                "options": ["A", "B"],
                "correct": 0
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        # Test minimum count (1)
        questions = quiz_service.generate_quiz("Python", "easy", 1)
        assert len(questions) >= 1
        
        # Test maximum count (20)
        questions = quiz_service.generate_quiz("Python", "easy", 20)
        assert len(questions) >= 1
    
    def test_whitespace_in_fields_is_stripped(self, quiz_service, mock_bedrock_client):
        """Test that whitespace in fields is properly stripped"""
        mock_response = json.dumps([
            {
                "question": "  What is Python?  ",
                "options": ["  A  ", "  B  "],
                "correct": 0,
                "explanation": "  Test explanation  "
            }
        ])
        mock_bedrock_client.invoke_model.return_value = mock_response
        
        questions = quiz_service.generate_quiz("Python", "easy", 1)
        
        assert questions[0]['question'] == "What is Python?"
        assert questions[0]['options'][0] == "A"
        assert questions[0]['explanation'] == "Test explanation"
