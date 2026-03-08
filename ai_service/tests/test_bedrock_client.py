"""
Unit tests for Bedrock client wrapper
Tests successful invocation, error handling, and retry logic
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError, BotoCoreError
import time

from bedrock_client import BedrockClient, BedrockClientError


class TestBedrockClientInitialization:
    """Tests for BedrockClient initialization"""
    
    def test_initialization_with_claude_model(self):
        """Test successful initialization with Claude model"""
        with patch('bedrock_client.boto3.client') as mock_boto:
            client = BedrockClient(
                region='us-east-1',
                model_id='anthropic.claude-v2'
            )
            assert client.region == 'us-east-1'
            assert client.model_id == 'anthropic.claude-v2'
            assert client.model_family == 'claude'
            assert client.max_retries == 3
            mock_boto.assert_called_once()
    
    def test_initialization_with_titan_model(self):
        """Test initialization detects Titan model family"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(
                region='us-west-2',
                model_id='amazon.titan-text-express-v1'
            )
            assert client.model_family == 'titan'
    
    def test_initialization_with_llama_model(self):
        """Test initialization detects Llama model family"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(
                region='us-east-1',
                model_id='meta.llama2-70b-v1'
            )
            assert client.model_family == 'llama'
    
    def test_initialization_with_custom_retries(self):
        """Test initialization with custom retry configuration"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(
                region='us-east-1',
                model_id='anthropic.claude-v2',
                max_retries=5,
                timeout=120
            )
            assert client.max_retries == 5
    
    def test_initialization_failure(self):
        """Test initialization handles boto3 client creation failure"""
        with patch('bedrock_client.boto3.client', side_effect=Exception("AWS credentials not found")):
            with pytest.raises(BedrockClientError) as exc_info:
                BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            assert "Failed to initialize Bedrock client" in str(exc_info.value)


class TestModelFamilyDetection:
    """Tests for model family detection"""
    
    def test_detect_claude_variants(self):
        """Test detection of various Claude model IDs"""
        with patch('bedrock_client.boto3.client'):
            test_cases = [
                'anthropic.claude-v2',
                'anthropic.claude-instant-v1',
                'claude-3-sonnet'
            ]
            for model_id in test_cases:
                client = BedrockClient(region='us-east-1', model_id=model_id)
                assert client.model_family == 'claude', f"Failed for {model_id}"
    
    def test_detect_titan_variants(self):
        """Test detection of various Titan model IDs"""
        with patch('bedrock_client.boto3.client'):
            test_cases = [
                'amazon.titan-text-express-v1',
                'amazon.titan-text-lite-v1'
            ]
            for model_id in test_cases:
                client = BedrockClient(region='us-east-1', model_id=model_id)
                assert client.model_family == 'titan', f"Failed for {model_id}"
    
    def test_unknown_model_defaults_to_claude(self):
        """Test unknown model IDs default to Claude format"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(region='us-east-1', model_id='unknown.model-v1')
            assert client.model_family == 'claude'


class TestRequestBodyBuilding:
    """Tests for request body construction"""
    
    def test_build_claude_request_body(self):
        """Test Claude request body format"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            body = client._build_request_body(
                prompt="Explain recursion",
                max_tokens=1000,
                temperature=0.5,
                top_p=0.8
            )
            assert "prompt" in body
            assert "Human: Explain recursion" in body["prompt"]
            assert "Assistant:" in body["prompt"]
            assert body["max_tokens_to_sample"] == 1000
            assert body["temperature"] == 0.5
            assert body["top_p"] == 0.8
            assert "stop_sequences" in body
    
    def test_build_titan_request_body(self):
        """Test Titan request body format"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(region='us-east-1', model_id='amazon.titan-text-express-v1')
            body = client._build_request_body(
                prompt="Explain recursion",
                max_tokens=1000,
                temperature=0.5,
                top_p=0.8
            )
            assert body["inputText"] == "Explain recursion"
            assert body["textGenerationConfig"]["maxTokenCount"] == 1000
            assert body["textGenerationConfig"]["temperature"] == 0.5
            assert body["textGenerationConfig"]["topP"] == 0.8
    
    def test_build_llama_request_body(self):
        """Test Llama request body format"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(region='us-east-1', model_id='meta.llama2-70b-v1')
            body = client._build_request_body(
                prompt="Explain recursion",
                max_tokens=1000,
                temperature=0.5,
                top_p=0.8
            )
            assert body["prompt"] == "Explain recursion"
            assert body["max_gen_len"] == 1000
            assert body["temperature"] == 0.5
            assert body["top_p"] == 0.8


class TestResponseExtraction:
    """Tests for response text extraction"""
    
    def test_extract_claude_response(self):
        """Test extracting text from Claude response"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            response_body = {
                "completion": "Recursion is a programming technique...",
                "stop_reason": "stop_sequence"
            }
            text = client._extract_response_text(response_body)
            assert text == "Recursion is a programming technique..."
    
    def test_extract_titan_response(self):
        """Test extracting text from Titan response"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(region='us-east-1', model_id='amazon.titan-text-express-v1')
            response_body = {
                "results": [
                    {"outputText": "Recursion is a programming technique..."}
                ]
            }
            text = client._extract_response_text(response_body)
            assert text == "Recursion is a programming technique..."
    
    def test_extract_llama_response(self):
        """Test extracting text from Llama response"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(region='us-east-1', model_id='meta.llama2-70b-v1')
            response_body = {
                "generation": "Recursion is a programming technique..."
            }
            text = client._extract_response_text(response_body)
            assert text == "Recursion is a programming technique..."
    
    def test_extract_response_handles_missing_fields(self):
        """Test extraction handles malformed responses gracefully"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            response_body = {}
            # Empty response should return empty string for Claude
            text = client._extract_response_text(response_body)
            assert text == ""


class TestInvokeModel:
    """Tests for model invocation with retry logic"""
    
    def test_successful_invocation(self):
        """Test successful model invocation on first attempt"""
        with patch('bedrock_client.boto3.client') as mock_boto:
            # Setup mock response
            mock_client = Mock()
            mock_response = {
                'body': Mock()
            }
            mock_response['body'].read.return_value = json.dumps({
                'completion': 'This is the AI response'
            }).encode('utf-8')
            mock_client.invoke_model.return_value = mock_response
            mock_boto.return_value = mock_client
            
            # Create client and invoke
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            result = client.invoke_model(prompt="Test prompt")
            
            assert result == 'This is the AI response'
            assert mock_client.invoke_model.call_count == 1
    
    def test_invocation_with_custom_parameters(self):
        """Test invocation with custom temperature and token settings"""
        with patch('bedrock_client.boto3.client') as mock_boto:
            mock_client = Mock()
            mock_response = {
                'body': Mock()
            }
            mock_response['body'].read.return_value = json.dumps({
                'completion': 'Response'
            }).encode('utf-8')
            mock_client.invoke_model.return_value = mock_response
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            result = client.invoke_model(
                prompt="Test",
                max_tokens=500,
                temperature=0.3,
                top_p=0.95
            )
            
            # Verify the request body had correct parameters
            call_args = mock_client.invoke_model.call_args
            body = json.loads(call_args[1]['body'])
            assert body['max_tokens_to_sample'] == 500
            assert body['temperature'] == 0.3
            assert body['top_p'] == 0.95

    def test_retry_on_throttling_exception(self):
        """Test retry logic with exponential backoff on rate limiting"""
        with patch('bedrock_client.boto3.client') as mock_boto, \
             patch('bedrock_client.time.sleep') as mock_sleep:
            
            mock_client = Mock()
            
            # First call fails with throttling, second succeeds
            throttle_error = ClientError(
                {'Error': {'Code': 'ThrottlingException', 'Message': 'Rate exceeded'}},
                'InvokeModel'
            )
            mock_response = {
                'body': Mock()
            }
            mock_response['body'].read.return_value = json.dumps({
                'completion': 'Success after retry'
            }).encode('utf-8')
            
            mock_client.invoke_model.side_effect = [throttle_error, mock_response]
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            result = client.invoke_model(prompt="Test")
            
            assert result == 'Success after retry'
            assert mock_client.invoke_model.call_count == 2
            assert mock_sleep.call_count == 1  # Should have slept once
    
    def test_retry_on_service_unavailable(self):
        """Test retry on service unavailable errors"""
        with patch('bedrock_client.boto3.client') as mock_boto, \
             patch('bedrock_client.time.sleep') as mock_sleep:
            
            mock_client = Mock()
            
            # First call fails with service error, second succeeds
            service_error = ClientError(
                {'Error': {'Code': 'ServiceUnavailableException', 'Message': 'Service unavailable'}},
                'InvokeModel'
            )
            mock_response = {
                'body': Mock()
            }
            mock_response['body'].read.return_value = json.dumps({
                'completion': 'Success after retry'
            }).encode('utf-8')
            
            mock_client.invoke_model.side_effect = [service_error, mock_response]
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            result = client.invoke_model(prompt="Test")
            
            assert result == 'Success after retry'
            assert mock_client.invoke_model.call_count == 2
    
    def test_no_retry_on_validation_error(self):
        """Test that validation errors are not retried"""
        with patch('bedrock_client.boto3.client') as mock_boto:
            mock_client = Mock()
            
            validation_error = ClientError(
                {'Error': {'Code': 'ValidationException', 'Message': 'Invalid input'}},
                'InvokeModel'
            )
            mock_client.invoke_model.side_effect = validation_error
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            
            with pytest.raises(BedrockClientError) as exc_info:
                client.invoke_model(prompt="Test")
            
            assert "Invalid input" in str(exc_info.value)
            assert mock_client.invoke_model.call_count == 1  # No retries
    
    def test_no_retry_on_access_denied(self):
        """Test that access denied errors are not retried"""
        with patch('bedrock_client.boto3.client') as mock_boto:
            mock_client = Mock()
            
            access_error = ClientError(
                {'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}},
                'InvokeModel'
            )
            mock_client.invoke_model.side_effect = access_error
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            
            with pytest.raises(BedrockClientError) as exc_info:
                client.invoke_model(prompt="Test")
            
            assert "Access denied" in str(exc_info.value)
            assert mock_client.invoke_model.call_count == 1
    
    def test_exhausted_retries(self):
        """Test failure after all retry attempts are exhausted"""
        with patch('bedrock_client.boto3.client') as mock_boto, \
             patch('bedrock_client.time.sleep'):
            
            mock_client = Mock()
            
            # All attempts fail
            service_error = ClientError(
                {'Error': {'Code': 'InternalServerError', 'Message': 'Internal error'}},
                'InvokeModel'
            )
            mock_client.invoke_model.side_effect = service_error
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2', max_retries=3)
            
            with pytest.raises(BedrockClientError) as exc_info:
                client.invoke_model(prompt="Test")
            
            assert "Failed to invoke Bedrock after 3 attempts" in str(exc_info.value)
            assert mock_client.invoke_model.call_count == 3
    
    def test_exponential_backoff_timing(self):
        """Test that exponential backoff increases correctly"""
        with patch('bedrock_client.boto3.client') as mock_boto, \
             patch('bedrock_client.time.sleep') as mock_sleep:
            
            mock_client = Mock()
            service_error = ClientError(
                {'Error': {'Code': 'InternalServerError', 'Message': 'Error'}},
                'InvokeModel'
            )
            mock_client.invoke_model.side_effect = service_error
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2', max_retries=3)
            
            with pytest.raises(BedrockClientError):
                client.invoke_model(prompt="Test")
            
            # Check that sleep was called with increasing durations
            # First retry: 2^0 = 1, Second retry: 2^1 = 2
            assert mock_sleep.call_count == 2
            sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
            assert sleep_calls[0] == 1  # 2^0
            assert sleep_calls[1] == 2  # 2^1
    
    def test_json_decode_error(self):
        """Test handling of invalid JSON responses"""
        with patch('bedrock_client.boto3.client') as mock_boto:
            mock_client = Mock()
            mock_response = {
                'body': Mock()
            }
            mock_response['body'].read.return_value = b'Invalid JSON'
            mock_client.invoke_model.return_value = mock_response
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            
            with pytest.raises(BedrockClientError) as exc_info:
                client.invoke_model(prompt="Test")
            
            assert "Invalid JSON response" in str(exc_info.value)
    
    def test_botocore_error_retry(self):
        """Test retry on BotoCoreError"""
        with patch('bedrock_client.boto3.client') as mock_boto, \
             patch('bedrock_client.time.sleep') as mock_sleep:
            
            mock_client = Mock()
            
            # First call fails with BotoCoreError, second succeeds
            botocore_error = BotoCoreError()
            mock_response = {
                'body': Mock()
            }
            mock_response['body'].read.return_value = json.dumps({
                'completion': 'Success'
            }).encode('utf-8')
            
            mock_client.invoke_model.side_effect = [botocore_error, mock_response]
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            result = client.invoke_model(prompt="Test")
            
            assert result == 'Success'
            assert mock_client.invoke_model.call_count == 2


class TestGetModelInfo:
    """Tests for get_model_info method"""
    
    def test_get_model_info(self):
        """Test retrieving model configuration information"""
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(
                region='us-west-2',
                model_id='anthropic.claude-v2',
                max_retries=5
            )
            info = client.get_model_info()
            
            assert info['model_id'] == 'anthropic.claude-v2'
            assert info['model_family'] == 'claude'
            assert info['region'] == 'us-west-2'
            assert info['max_retries'] == '5'


class TestErrorHandling:
    """Tests for error handling scenarios"""
    
    def test_empty_prompt_handling(self):
        """Test that empty prompts are handled"""
        with patch('bedrock_client.boto3.client') as mock_boto:
            mock_client = Mock()
            mock_response = {
                'body': Mock()
            }
            mock_response['body'].read.return_value = json.dumps({
                'completion': ''
            }).encode('utf-8')
            mock_client.invoke_model.return_value = mock_response
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            result = client.invoke_model(prompt="")
            
            # Should still make the call, even with empty prompt
            assert mock_client.invoke_model.call_count == 1
    
    def test_unexpected_exception_retry(self):
        """Test retry on unexpected exceptions"""
        with patch('bedrock_client.boto3.client') as mock_boto, \
             patch('bedrock_client.time.sleep') as mock_sleep:
            
            mock_client = Mock()
            
            # First call raises unexpected exception, second succeeds
            mock_response = {
                'body': Mock()
            }
            mock_response['body'].read.return_value = json.dumps({
                'completion': 'Success'
            }).encode('utf-8')
            
            mock_client.invoke_model.side_effect = [
                Exception("Unexpected error"),
                mock_response
            ]
            mock_boto.return_value = mock_client
            
            client = BedrockClient(region='us-east-1', model_id='anthropic.claude-v2')
            result = client.invoke_model(prompt="Test")
            
            assert result == 'Success'
            assert mock_client.invoke_model.call_count == 2
