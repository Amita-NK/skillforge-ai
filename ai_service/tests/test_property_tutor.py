"""
Property-based tests for tutor service
Tests explanation completeness and structure
**Validates: Requirements 2.3**
"""
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch
from tutor import TutorService


# Strategy for generating valid topics
topics_strategy = st.text(min_size=1, max_size=100).filter(lambda x: x.strip())


@given(topic=topics_strategy)
@settings(max_examples=100)
def test_property_explanation_completeness(topic):
    """
    Property 5: Explanation completeness
    
    For all valid topics, the explanation response must contain:
    - A non-empty explanation field
    - An examples list (may be empty)
    - An analogy field (may be empty)
    
    **Validates: Requirements 2.3**
    """
    # Setup mock Bedrock client
    mock_bedrock = Mock()
    mock_bedrock.invoke_model.return_value = f"""
    Here is a detailed explanation of {topic}:
    
    {topic} is an important concept in programming. It involves understanding
    how different components work together to achieve a specific goal.
    
    ```python
    # Example code for {topic}
    def example():
        return "demonstration"
    ```
    
    Analogy: Think of {topic} like a recipe in cooking - you follow steps to get a result.
    """
    
    # Create service and generate explanation
    service = TutorService(mock_bedrock)
    result = service.explain_concept(topic)
    
    # Property: Response must have required structure
    assert isinstance(result, dict), "Result must be a dictionary"
    assert 'explanation' in result, "Result must contain 'explanation' field"
    assert 'examples' in result, "Result must contain 'examples' field"
    assert 'analogy' in result, "Result must contain 'analogy' field"
    
    # Property: Explanation must be non-empty
    assert isinstance(result['explanation'], str), "Explanation must be a string"
    assert len(result['explanation']) > 0, "Explanation must not be empty"
    
    # Property: Examples must be a list
    assert isinstance(result['examples'], list), "Examples must be a list"
    
    # Property: Analogy must be a string (can be empty)
    assert isinstance(result['analogy'], str), "Analogy must be a string"


@given(topic=topics_strategy)
@settings(max_examples=100)
def test_property_explanation_with_context(topic):
    """
    Property: Explanation with context
    
    For all valid topics with context, the service must accept and process
    the context parameter without errors.
    
    **Validates: Requirements 2.3, 6.7**
    """
    mock_bedrock = Mock()
    mock_bedrock.invoke_model.return_value = f"Explanation of {topic} with context."
    
    service = TutorService(mock_bedrock)
    context = "Additional learning materials about the topic."
    
    result = service.explain_concept(topic, context=context)
    
    # Property: Must return valid structure regardless of context
    assert isinstance(result, dict)
    assert 'explanation' in result
    assert len(result['explanation']) > 0


@given(topic=st.text(max_size=10).filter(lambda x: not x.strip()))
@settings(max_examples=50)
def test_property_empty_topic_rejection(topic):
    """
    Property: Empty topic rejection
    
    For all empty or whitespace-only topics, the service must raise ValueError.
    
    **Validates: Requirements 2.7**
    """
    mock_bedrock = Mock()
    service = TutorService(mock_bedrock)
    
    with pytest.raises(ValueError, match="Topic cannot be empty"):
        service.explain_concept(topic)
