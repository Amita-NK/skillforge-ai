"""
Property-based tests for debugger service
Tests debug response completeness
**Validates: Requirements 4.4**
"""
import pytest
import json
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock
from debugger import DebuggerService


# Strategies for generating valid inputs
languages_strategy = st.sampled_from(['python', 'javascript', 'java', 'cpp', 'c++', 'typescript', 'go', 'rust'])
code_strategy = st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())


@given(language=languages_strategy, code=code_strategy)
@settings(max_examples=100)
def test_property_debug_response_completeness(language, code):
    """
    Property 7: Debug response completeness
    
    For all valid language and code inputs, the debug response must contain:
    - errors: list (may be empty)
    - corrected_code: string (may be empty)
    - explanation: string (may be empty)
    
    **Validates: Requirements 4.4**
    """
    # Setup mock Bedrock client with valid response
    mock_bedrock = Mock()
    response_json = {
        "errors": [
            {"line": 1, "message": "Syntax error"},
            {"line": 5, "message": "Undefined variable"}
        ],
        "corrected_code": "# Corrected code here\nprint('Hello')",
        "explanation": "The code had syntax errors that were fixed."
    }
    
    mock_bedrock.invoke_model.return_value = json.dumps(response_json)
    
    # Create service and analyze code
    service = DebuggerService(mock_bedrock)
    result = service.analyze_code(language, code)
    
    # Property: Result must have required structure
    assert isinstance(result, dict), "Result must be a dictionary"
    assert 'errors' in result, "Result must contain 'errors' field"
    assert 'corrected_code' in result, "Result must contain 'corrected_code' field"
    assert 'explanation' in result, "Result must contain 'explanation' field"
    
    # Property: Errors must be a list
    assert isinstance(result['errors'], list), "Errors must be a list"
    
    # Property: Each error must have line and message
    for i, error in enumerate(result['errors']):
        assert isinstance(error, dict), f"Error {i} must be a dictionary"
        assert 'line' in error, f"Error {i} must have 'line' field"
        assert 'message' in error, f"Error {i} must have 'message' field"
        assert isinstance(error['line'], int), f"Error {i} line must be integer"
        assert isinstance(error['message'], str), f"Error {i} message must be string"
    
    # Property: Corrected code must be a string
    assert isinstance(result['corrected_code'], str), "Corrected code must be a string"
    
    # Property: Explanation must be a string
    assert isinstance(result['explanation'], str), "Explanation must be a string"


@given(language=languages_strategy, code=code_strategy)
@settings(max_examples=50)
def test_property_debug_text_fallback(language, code):
    """
    Property: Debug text fallback parsing
    
    When JSON parsing fails, the service must still return a valid structure
    by parsing the text response.
    
    **Validates: Requirements 4.4**
    """
    # Setup mock with non-JSON response
    mock_bedrock = Mock()
    mock_bedrock.invoke_model.return_value = """
    The code has the following issues:
    
    Error on line 3: Missing semicolon
    Line 7: Undefined variable 'x'
    
    Here's the corrected code:
    ```python
    def hello():
        print("Hello, World!")
    ```
    
    Explanation: Fixed syntax errors and undefined variables.
    """
    
    # Create service and analyze code
    service = DebuggerService(mock_bedrock)
    result = service.analyze_code(language, code)
    
    # Property: Must still return valid structure
    assert isinstance(result, dict)
    assert 'errors' in result
    assert 'corrected_code' in result
    assert 'explanation' in result
    assert isinstance(result['errors'], list)
    assert isinstance(result['corrected_code'], str)
    assert isinstance(result['explanation'], str)


@given(
    language=st.text(min_size=1, max_size=20).filter(
        lambda x: x.lower() not in {'python', 'javascript', 'java', 'cpp', 'c++', 'typescript', 'go', 'rust'}
    ),
    code=code_strategy
)
@settings(max_examples=50)
def test_property_unsupported_language_rejection(language, code):
    """
    Property: Unsupported language rejection
    
    For all unsupported languages, the service must raise ValueError.
    
    **Validates: Requirements 4.7**
    """
    mock_bedrock = Mock()
    service = DebuggerService(mock_bedrock)
    
    with pytest.raises(ValueError, match="is not supported"):
        service.analyze_code(language, code)


@given(language=languages_strategy)
@settings(max_examples=50)
def test_property_empty_code_rejection(language):
    """
    Property: Empty code rejection
    
    For all empty or whitespace-only code, the service must raise ValueError.
    
    **Validates: Requirements 4.7**
    """
    mock_bedrock = Mock()
    service = DebuggerService(mock_bedrock)
    
    empty_code = "   \n\t  "
    
    with pytest.raises(ValueError, match="Code cannot be empty"):
        service.analyze_code(language, empty_code)


@given(language=languages_strategy)
@settings(max_examples=20)
def test_property_code_length_limit(language):
    """
    Property: Code length limit
    
    For all code exceeding 10000 characters, the service must raise ValueError.
    
    **Validates: Requirements 4.7**
    """
    mock_bedrock = Mock()
    service = DebuggerService(mock_bedrock)
    
    # Generate code that's too long
    long_code = "x" * 10001
    
    with pytest.raises(ValueError, match="Code is too long"):
        service.analyze_code(language, long_code)
