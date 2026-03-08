"""
Tests for Pydantic models
"""
import pytest
from pydantic import ValidationError
from models import (
    ExplainRequest, ExplanationResponse,
    QuizRequest, Question, QuizResponse,
    DebugRequest, DebugError, DebugResponse,
    ErrorResponse
)


class TestExplainRequest:
    """Tests for ExplainRequest model"""
    
    def test_valid_request(self):
        """Test valid explain request"""
        request = ExplainRequest(topic="binary search", user_id="user123")
        assert request.topic == "binary search"
        assert request.user_id == "user123"
    
    def test_topic_whitespace_stripped(self):
        """Test topic whitespace is stripped"""
        request = ExplainRequest(topic="  recursion  ")
        assert request.topic == "recursion"
    
    def test_empty_topic_raises_error(self):
        """Test empty topic raises validation error"""
        with pytest.raises(ValidationError):
            ExplainRequest(topic="")
    
    def test_whitespace_only_topic_raises_error(self):
        """Test whitespace-only topic raises validation error"""
        with pytest.raises(ValidationError):
            ExplainRequest(topic="   ")
    
    def test_topic_too_long_raises_error(self):
        """Test topic exceeding max length raises error"""
        with pytest.raises(ValidationError):
            ExplainRequest(topic="a" * 501)


class TestQuizRequest:
    """Tests for QuizRequest model"""
    
    def test_valid_request(self):
        """Test valid quiz request"""
        request = QuizRequest(topic="arrays", difficulty="medium", count=5)
        assert request.topic == "arrays"
        assert request.difficulty == "medium"
        assert request.count == 5
    
    def test_invalid_difficulty_raises_error(self):
        """Test invalid difficulty raises validation error"""
        with pytest.raises(ValidationError):
            QuizRequest(topic="arrays", difficulty="extreme", count=5)
    
    def test_count_below_minimum_raises_error(self):
        """Test count below 1 raises validation error"""
        with pytest.raises(ValidationError):
            QuizRequest(topic="arrays", difficulty="easy", count=0)
    
    def test_count_above_maximum_raises_error(self):
        """Test count above 20 raises validation error"""
        with pytest.raises(ValidationError):
            QuizRequest(topic="arrays", difficulty="easy", count=21)


class TestDebugRequest:
    """Tests for DebugRequest model"""
    
    def test_valid_request(self):
        """Test valid debug request"""
        code = "def hello():\n    print('Hello')"
        request = DebugRequest(language="python", code=code)
        assert request.language == "python"
        assert request.code == code
    
    def test_empty_code_raises_error(self):
        """Test empty code raises validation error"""
        with pytest.raises(ValidationError):
            DebugRequest(language="python", code="")
    
    def test_code_too_long_raises_error(self):
        """Test code exceeding max length raises error"""
        with pytest.raises(ValidationError):
            DebugRequest(language="python", code="a" * 10001)


class TestQuestion:
    """Tests for Question model"""
    
    def test_valid_question(self):
        """Test valid question model"""
        question = Question(
            question="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct=1,
            explanation="2+2 equals 4"
        )
        assert question.question == "What is 2+2?"
        assert len(question.options) == 4
        assert question.correct == 1
    
    def test_too_few_options_raises_error(self):
        """Test fewer than 2 options raises error"""
        with pytest.raises(ValidationError):
            Question(
                question="Test?",
                options=["A"],
                correct=0
            )


class TestErrorResponse:
    """Tests for ErrorResponse model"""
    
    def test_create_error_response(self):
        """Test creating error response"""
        error = ErrorResponse.create(
            code="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "topic"}
        )
        assert error.error["code"] == "VALIDATION_ERROR"
        assert error.error["message"] == "Invalid input"
        assert error.error["details"]["field"] == "topic"
        assert "timestamp" in error.error
