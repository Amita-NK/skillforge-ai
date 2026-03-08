"""
Tests for configuration management and prompt templates
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings, PromptTemplates


class TestSettings:
    """Tests for Settings class"""
    
    def test_settings_defaults(self):
        """Test that settings have appropriate default values"""
        settings = Settings()
        
        assert settings.AWS_REGION == "us-east-1"
        assert settings.BEDROCK_MODEL_ID == "anthropic.claude-v2"
        assert settings.BEDROCK_EMBEDDING_MODEL == "amazon.titan-embed-text-v1"
        assert settings.CHUNK_SIZE == 500
        assert settings.CHUNK_OVERLAP == 50
        assert settings.MAX_TOKENS == 2000
        assert settings.TEMPERATURE == 0.7
        assert settings.TOP_P == 0.9


class TestPromptTemplates:
    """Tests for PromptTemplates class"""
    
    def test_tutor_template_exists(self):
        """Test that TUTOR template is defined"""
        assert hasattr(PromptTemplates, 'TUTOR')
        assert isinstance(PromptTemplates.TUTOR, str)
        assert len(PromptTemplates.TUTOR) > 0
    
    def test_quiz_template_exists(self):
        """Test that QUIZ template is defined"""
        assert hasattr(PromptTemplates, 'QUIZ')
        assert isinstance(PromptTemplates.QUIZ, str)
        assert len(PromptTemplates.QUIZ) > 0
    
    def test_debugger_template_exists(self):
        """Test that DEBUGGER template is defined"""
        assert hasattr(PromptTemplates, 'DEBUGGER')
        assert isinstance(PromptTemplates.DEBUGGER, str)
        assert len(PromptTemplates.DEBUGGER) > 0
    
    def test_tutor_template_formatting(self):
        """Test that TUTOR template can be formatted with required parameters"""
        formatted = PromptTemplates.TUTOR.format(
            topic="Python functions",
            context="Functions are reusable blocks of code"
        )
        
        assert "Python functions" in formatted
        assert "Functions are reusable blocks of code" in formatted
        assert "expert programming tutor" in formatted
        assert "Step-by-step explanation" in formatted
    
    def test_quiz_template_formatting(self):
        """Test that QUIZ template can be formatted with required parameters"""
        formatted = PromptTemplates.QUIZ.format(
            count=5,
            topic="JavaScript arrays",
            difficulty="medium"
        )
        
        assert "5" in formatted
        assert "JavaScript arrays" in formatted
        assert "medium" in formatted
        assert "JSON format" in formatted
    
    def test_debugger_template_formatting(self):
        """Test that DEBUGGER template can be formatted with required parameters"""
        code_sample = "def add(a, b)\n    return a + b"
        formatted = PromptTemplates.DEBUGGER.format(
            language="Python",
            code=code_sample
        )
        
        assert "Python" in formatted
        assert code_sample in formatted
        assert "senior software engineer" in formatted
        assert "JSON format" in formatted
    
    def test_tutor_template_contains_required_sections(self):
        """Test that TUTOR template includes all required sections"""
        template = PromptTemplates.TUTOR
        
        assert "Step-by-step explanation" in template
        assert "Real-world analogy" in template
        assert "Example code" in template
        assert "{topic}" in template
        assert "{context}" in template
    
    def test_quiz_template_contains_required_fields(self):
        """Test that QUIZ template specifies required JSON fields"""
        template = PromptTemplates.QUIZ
        
        assert "{count}" in template
        assert "{topic}" in template
        assert "{difficulty}" in template
        assert "question" in template
        assert "options" in template
        assert "correct" in template
        assert "explanation" in template
    
    def test_debugger_template_contains_required_fields(self):
        """Test that DEBUGGER template specifies required JSON fields"""
        template = PromptTemplates.DEBUGGER
        
        assert "{language}" in template
        assert "{code}" in template
        assert "errors" in template
        assert "corrected_code" in template
        assert "explanation" in template
