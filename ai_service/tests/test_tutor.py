"""
Unit tests for AI tutoring module
Tests explanation generation, parsing, and error handling
"""
import pytest
from unittest.mock import Mock, patch
from bedrock_client import BedrockClient, BedrockClientError
from tutor import TutorService, create_tutor_service


class TestTutorServiceInitialization:
    """Tests for TutorService initialization"""
    
    def test_initialization(self):
        """Test successful initialization with BedrockClient"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        assert service.bedrock == mock_client
    
    def test_factory_function(self):
        """Test create_tutor_service factory function"""
        mock_client = Mock(spec=BedrockClient)
        service = create_tutor_service(mock_client)
        assert isinstance(service, TutorService)
        assert service.bedrock == mock_client


class TestExplainConcept:
    """Tests for explain_concept method"""
    
    def test_successful_explanation_generation(self):
        """Test successful explanation generation"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.return_value = """
Recursion is a programming technique where a function calls itself.

Here's how it works step by step:
1. Base case: Define when to stop
2. Recursive case: Call the function again with modified input

Analogy: Think of it like Russian nesting dolls - each doll contains a smaller version of itself until you reach the smallest one.

Example code:
```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
```
"""
        
        service = TutorService(mock_client)
        result = service.explain_concept("recursion")
        
        assert 'explanation' in result
        assert 'examples' in result
        assert 'analogy' in result
        assert len(result['examples']) > 0
        assert 'Russian nesting dolls' in result['analogy']
        mock_client.invoke_model.assert_called_once()
    
    def test_explanation_with_context(self):
        """Test explanation generation with RAG context"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.return_value = "Explanation with context"
        
        service = TutorService(mock_client)
        context = "From course materials: Recursion is fundamental..."
        result = service.explain_concept("recursion", context=context)
        
        # Verify context was included in the prompt
        call_args = mock_client.invoke_model.call_args
        prompt = call_args[1]['prompt']
        assert context in prompt
    
    def test_empty_topic_raises_error(self):
        """Test that empty topic raises ValueError"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        with pytest.raises(ValueError) as exc_info:
            service.explain_concept("")
        
        assert "Topic cannot be empty" in str(exc_info.value)
        mock_client.invoke_model.assert_not_called()
    
    def test_whitespace_only_topic_raises_error(self):
        """Test that whitespace-only topic raises ValueError"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        with pytest.raises(ValueError) as exc_info:
            service.explain_concept("   \n\t  ")
        
        assert "Topic cannot be empty" in str(exc_info.value)
        mock_client.invoke_model.assert_not_called()
    
    def test_topic_is_trimmed(self):
        """Test that topic whitespace is trimmed"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.return_value = "Explanation"
        
        service = TutorService(mock_client)
        service.explain_concept("  recursion  ")
        
        # Verify the prompt contains trimmed topic
        call_args = mock_client.invoke_model.call_args
        prompt = call_args[1]['prompt']
        assert "recursion" in prompt
    
    def test_bedrock_error_propagates(self):
        """Test that Bedrock errors are propagated"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.side_effect = BedrockClientError("API error")
        
        service = TutorService(mock_client)
        
        with pytest.raises(BedrockClientError) as exc_info:
            service.explain_concept("recursion")
        
        assert "API error" in str(exc_info.value)
    
    def test_invocation_parameters(self):
        """Test that correct parameters are passed to Bedrock"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.return_value = "Explanation"
        
        service = TutorService(mock_client)
        service.explain_concept("recursion")
        
        # Verify invocation parameters
        call_args = mock_client.invoke_model.call_args
        assert call_args[1]['max_tokens'] == 2000
        assert call_args[1]['temperature'] == 0.7
        assert call_args[1]['top_p'] == 0.9


class TestParseExplanation:
    """Tests for _parse_explanation method"""
    
    def test_parse_with_code_blocks(self):
        """Test parsing response with code blocks"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        response = """
Explanation text here.

```python
def example():
    return 42
```

More explanation.

```javascript
function test() {
    return true;
}
```
"""
        result = service._parse_explanation(response)
        
        assert len(result['examples']) == 2
        assert 'def example()' in result['examples'][0]
        assert 'function test()' in result['examples'][1]
    
    def test_parse_with_analogy(self):
        """Test parsing response with analogy section"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        response = """
Explanation of the concept.

Analogy: It's like a filing cabinet where each drawer contains folders.
"""
        result = service._parse_explanation(response)
        
        assert 'filing cabinet' in result['analogy']
    
    def test_parse_with_alternative_analogy_format(self):
        """Test parsing response with different analogy formats"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        test_cases = [
            "Think of it like a tree with branches.",
            "It's like a recipe with steps.",
            "Similar to a chain of dominoes.",
            "Imagine a stack of plates."
        ]
        
        for response in test_cases:
            result = service._parse_explanation(response)
            assert len(result['analogy']) > 0
    
    def test_parse_without_code_blocks(self):
        """Test parsing response without code examples"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        response = "Simple explanation without code."
        result = service._parse_explanation(response)
        
        assert len(result['examples']) == 0
        assert len(result['explanation']) > 0
    
    def test_parse_without_analogy(self):
        """Test parsing response without analogy"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        response = "Explanation without analogy."
        result = service._parse_explanation(response)
        
        assert result['analogy'] == ''
    
    def test_parse_complex_response(self):
        """Test parsing complex response with all elements"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        response = """
Recursion is a powerful technique.

Step-by-step breakdown:
1. Define base case
2. Define recursive case
3. Ensure progress toward base case

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

Real-world analogy: Think of it like looking into two mirrors facing each other.

```java
public int factorial(int n) {
    if (n == 0) return 1;
    return n * factorial(n - 1);
}
```
"""
        result = service._parse_explanation(response)
        
        assert len(result['examples']) == 2
        assert 'fibonacci' in result['examples'][0]
        assert 'factorial' in result['examples'][1]
        assert 'mirrors' in result['analogy']
        assert 'Recursion is a powerful technique' in result['explanation']
    
    def test_parse_empty_response(self):
        """Test parsing empty response"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        response = ""
        result = service._parse_explanation(response)
        
        assert result['explanation'] == ''
        assert result['examples'] == []
        assert result['analogy'] == ''
    
    def test_parse_code_block_with_language_specifier(self):
        """Test parsing code blocks with various language specifiers"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        response = """
```python
print("Hello")
```

```javascript
console.log("Hello");
```

```
# No language specified
echo "Hello"
```
"""
        result = service._parse_explanation(response)
        
        assert len(result['examples']) == 3
    
    def test_parse_preserves_code_formatting(self):
        """Test that code formatting is preserved"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        response = """
```python
def nested_function():
    if True:
        for i in range(10):
            print(i)
```
"""
        result = service._parse_explanation(response)
        
        # Check that indentation is preserved
        assert '    if True:' in result['examples'][0]
        assert '        for i in range(10):' in result['examples'][0]


class TestErrorHandling:
    """Tests for error handling scenarios"""
    
    def test_none_topic_raises_error(self):
        """Test that None topic raises ValueError"""
        mock_client = Mock(spec=BedrockClient)
        service = TutorService(mock_client)
        
        with pytest.raises((ValueError, AttributeError)):
            service.explain_concept(None)
    
    def test_unexpected_exception_propagates(self):
        """Test that unexpected exceptions are propagated"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.side_effect = Exception("Unexpected error")
        
        service = TutorService(mock_client)
        
        with pytest.raises(Exception) as exc_info:
            service.explain_concept("recursion")
        
        assert "Unexpected error" in str(exc_info.value)
    
    def test_malformed_response_handling(self):
        """Test handling of malformed AI responses"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.return_value = "```\nUnclosed code block"
        
        service = TutorService(mock_client)
        result = service.explain_concept("recursion")
        
        # Should still return a result, even if parsing is imperfect
        assert 'explanation' in result
        assert 'examples' in result
        assert 'analogy' in result


class TestLogging:
    """Tests for logging functionality"""
    
    @patch('tutor.logger')
    def test_logs_request(self, mock_logger):
        """Test that requests are logged"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.return_value = "Explanation"
        
        service = TutorService(mock_client)
        service.explain_concept("recursion")
        
        # Verify info log was called with topic
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any('recursion' in str(call) for call in info_calls)
    
    @patch('tutor.logger')
    def test_logs_success(self, mock_logger):
        """Test that successful generation is logged"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.return_value = "Explanation"
        
        service = TutorService(mock_client)
        service.explain_concept("recursion")
        
        # Verify success was logged
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any('Successfully generated' in str(call) for call in info_calls)
    
    @patch('tutor.logger')
    def test_logs_error(self, mock_logger):
        """Test that errors are logged"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.invoke_model.side_effect = BedrockClientError("API error")
        
        service = TutorService(mock_client)
        
        with pytest.raises(BedrockClientError):
            service.explain_concept("recursion")
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert 'Failed to generate explanation' in error_call
        assert 'recursion' in error_call
