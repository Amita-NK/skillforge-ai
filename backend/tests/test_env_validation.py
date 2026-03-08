"""
Tests for environment variable validation

Requirements: 12.3, 12.5, 12.6
- Backend SHALL load database credentials from environment variables
- Services SHALL validate that required environment variables are present
- IF required environment variables are missing, service SHALL fail to start
"""
import pytest
import os
import sys
from unittest.mock import patch
import importlib


class TestEnvironmentValidation:
    """Test environment variable validation on startup"""
    
    def test_missing_database_url_fails_startup(self):
        """Test that missing DATABASE_URL causes startup failure"""
        # Save original environment
        original_env = os.environ.copy()
        
        try:
            # Remove DATABASE_URL
            if 'DATABASE_URL' in os.environ:
                del os.environ['DATABASE_URL']
            
            # Ensure other required vars are present
            os.environ['SECRET_KEY'] = 'test-secret'
            os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
            os.environ['AI_SERVICE_URL'] = 'http://localhost:8000'
            
            # Attempt to import app should fail
            with pytest.raises(SystemExit) as exc_info:
                # Force reload to trigger validation
                if 'app' in sys.modules:
                    del sys.modules['app']
                import app
            
            assert exc_info.value.code == 1
        
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_missing_secret_key_fails_startup(self):
        """Test that missing SECRET_KEY causes startup failure"""
        original_env = os.environ.copy()
        
        try:
            # Remove SECRET_KEY
            if 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
            
            # Ensure other required vars are present
            os.environ['DATABASE_URL'] = 'sqlite:///test.db'
            os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
            os.environ['AI_SERVICE_URL'] = 'http://localhost:8000'
            
            with pytest.raises(SystemExit) as exc_info:
                if 'app' in sys.modules:
                    del sys.modules['app']
                import app
            
            assert exc_info.value.code == 1
        
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_missing_jwt_secret_key_fails_startup(self):
        """Test that missing JWT_SECRET_KEY causes startup failure"""
        original_env = os.environ.copy()
        
        try:
            # Remove JWT_SECRET_KEY
            if 'JWT_SECRET_KEY' in os.environ:
                del os.environ['JWT_SECRET_KEY']
            
            # Ensure other required vars are present
            os.environ['DATABASE_URL'] = 'sqlite:///test.db'
            os.environ['SECRET_KEY'] = 'test-secret'
            os.environ['AI_SERVICE_URL'] = 'http://localhost:8000'
            
            with pytest.raises(SystemExit) as exc_info:
                if 'app' in sys.modules:
                    del sys.modules['app']
                import app
            
            assert exc_info.value.code == 1
        
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_missing_ai_service_url_fails_startup(self):
        """Test that missing AI_SERVICE_URL causes startup failure"""
        original_env = os.environ.copy()
        
        try:
            # Remove AI_SERVICE_URL
            if 'AI_SERVICE_URL' in os.environ:
                del os.environ['AI_SERVICE_URL']
            
            # Ensure other required vars are present
            os.environ['DATABASE_URL'] = 'sqlite:///test.db'
            os.environ['SECRET_KEY'] = 'test-secret'
            os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
            
            with pytest.raises(SystemExit) as exc_info:
                if 'app' in sys.modules:
                    del sys.modules['app']
                import app
            
            assert exc_info.value.code == 1
        
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_all_required_vars_present_succeeds(self):
        """Test that startup succeeds when all required variables are present"""
        original_env = os.environ.copy()
        
        try:
            # Set all required variables
            os.environ['DATABASE_URL'] = 'sqlite:///test.db'
            os.environ['SECRET_KEY'] = 'test-secret-key'
            os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
            os.environ['AI_SERVICE_URL'] = 'http://localhost:8000'
            
            # Import should succeed
            if 'app' in sys.modules:
                del sys.modules['app']
            
            try:
                import app
                # If we get here, validation passed
                assert True
            except SystemExit:
                pytest.fail("Startup should not fail when all required variables are present")
        
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_empty_string_values_fail_validation(self):
        """Test that empty string values are treated as missing"""
        original_env = os.environ.copy()
        
        try:
            # Set required variables with empty strings
            os.environ['DATABASE_URL'] = ''
            os.environ['SECRET_KEY'] = 'test-secret'
            os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
            os.environ['AI_SERVICE_URL'] = 'http://localhost:8000'
            
            with pytest.raises(SystemExit) as exc_info:
                if 'app' in sys.modules:
                    del sys.modules['app']
                import app
            
            assert exc_info.value.code == 1
        
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_whitespace_only_values_fail_validation(self):
        """Test that whitespace-only values are treated as missing"""
        original_env = os.environ.copy()
        
        try:
            # Set required variables with whitespace
            os.environ['DATABASE_URL'] = 'sqlite:///test.db'
            os.environ['SECRET_KEY'] = '   '
            os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
            os.environ['AI_SERVICE_URL'] = 'http://localhost:8000'
            
            with pytest.raises(SystemExit) as exc_info:
                if 'app' in sys.modules:
                    del sys.modules['app']
                import app
            
            assert exc_info.value.code == 1
        
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_database_credentials_loaded_from_environment(self):
        """
        Test that database credentials are loaded from environment variables
        Requirement 12.3: Backend SHALL load database credentials from environment
        """
        original_env = os.environ.copy()
        
        try:
            # Set database URL with credentials (use SQLite for testing)
            test_db_url = 'sqlite:///test_credentials.db'
            os.environ['DATABASE_URL'] = test_db_url
            os.environ['SECRET_KEY'] = 'test-secret'
            os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
            os.environ['AI_SERVICE_URL'] = 'http://localhost:8000'
            
            # Import app
            if 'app' in sys.modules:
                del sys.modules['app']
            import app
            
            # Verify database URL is loaded from environment
            assert app.app.config['SQLALCHEMY_DATABASE_URI'] == test_db_url
        
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            # Clean up test database
            import os as os_module
            if os_module.path.exists('test_credentials.db'):
                os_module.remove('test_credentials.db')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
