"""
Unit tests for environment variable validation
Tests that the AI Service validates required environment variables on startup
"""
import pytest
import os
import sys
from unittest.mock import patch


def test_validate_required_environment_variables_success():
    """
    Test that validation passes when all required variables are present
    Requirements: 12.5, 12.6
    """
    # Set required environment variables
    with patch.dict(os.environ, {
        'AWS_REGION': 'us-east-1',
        'BEDROCK_MODEL_ID': 'anthropic.claude-v2'
    }):
        # Import after setting environment variables
        from config import validate_required_environment_variables
        
        # Should not raise any exception
        try:
            validate_required_environment_variables()
        except RuntimeError:
            pytest.fail("Validation should pass when all required variables are present")


def test_validate_missing_aws_region():
    """
    Test that validation fails with descriptive error when AWS_REGION is missing
    Requirements: 12.5, 12.6
    """
    # Remove AWS_REGION from environment
    with patch.dict(os.environ, {
        'BEDROCK_MODEL_ID': 'anthropic.claude-v2'
    }, clear=True):
        # Import after clearing environment
        from config import validate_required_environment_variables
        
        # Should raise RuntimeError with descriptive message
        with pytest.raises(RuntimeError) as exc_info:
            validate_required_environment_variables()
        
        error_message = str(exc_info.value)
        assert 'AWS_REGION' in error_message
        assert 'Missing required environment variables' in error_message


def test_validate_missing_bedrock_model_id():
    """
    Test that validation fails with descriptive error when BEDROCK_MODEL_ID is missing
    Requirements: 12.5, 12.6
    """
    # Remove BEDROCK_MODEL_ID from environment
    with patch.dict(os.environ, {
        'AWS_REGION': 'us-east-1'
    }, clear=True):
        # Import after clearing environment
        from config import validate_required_environment_variables
        
        # Should raise RuntimeError with descriptive message
        with pytest.raises(RuntimeError) as exc_info:
            validate_required_environment_variables()
        
        error_message = str(exc_info.value)
        assert 'BEDROCK_MODEL_ID' in error_message
        assert 'Missing required environment variables' in error_message


def test_validate_missing_multiple_variables():
    """
    Test that validation fails and lists all missing variables
    Requirements: 12.5, 12.6
    """
    # Remove all required variables from environment
    with patch.dict(os.environ, {}, clear=True):
        # Import after clearing environment
        from config import validate_required_environment_variables
        
        # Should raise RuntimeError with all missing variables
        with pytest.raises(RuntimeError) as exc_info:
            validate_required_environment_variables()
        
        error_message = str(exc_info.value)
        assert 'AWS_REGION' in error_message
        assert 'BEDROCK_MODEL_ID' in error_message
        assert 'Missing required environment variables' in error_message


def test_service_startup_fails_without_required_vars():
    """
    Test that the service fails to start when required variables are missing
    This is an integration test that verifies the validation is called on startup
    Requirements: 12.5, 12.6
    """
    # Clear required environment variables
    with patch.dict(os.environ, {}, clear=True):
        # Attempting to import main should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            # Force reload of modules to trigger validation
            import importlib
            import sys
            
            # Remove cached modules
            modules_to_remove = [m for m in sys.modules if m.startswith('config') or m.startswith('main')]
            for module in modules_to_remove:
                del sys.modules[module]
            
            # Import main which should trigger validation
            import main
        
        error_message = str(exc_info.value)
        assert 'Missing required environment variables' in error_message


def test_descriptive_error_message_format():
    """
    Test that the error message is descriptive and helpful
    Requirements: 12.6
    """
    with patch.dict(os.environ, {}, clear=True):
        from config import validate_required_environment_variables
        
        with pytest.raises(RuntimeError) as exc_info:
            validate_required_environment_variables()
        
        error_message = str(exc_info.value)
        
        # Check that error message contains helpful information
        assert 'Missing required environment variables' in error_message
        
        # The error should list the missing variables
        assert 'AWS_REGION' in error_message or 'BEDROCK_MODEL_ID' in error_message
