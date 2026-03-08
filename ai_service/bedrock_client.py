"""
Bedrock Client Wrapper
Provides a clean interface for Amazon Bedrock Converse API with retry logic and error handling
"""
import json
import time
import logging
from typing import Dict, Any, Optional, List
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class BedrockClientError(Exception):
    """Custom exception for Bedrock client errors"""
    pass


class BedrockClient:
    """
    Wrapper for Amazon Bedrock Converse API
    Implements retry logic with exponential backoff for resilient API calls
    Uses the unified Converse API that works with all Bedrock models
    """
    
    def __init__(
        self,
        region: str,
        model_id: str,
        max_retries: int = 3,
        timeout: int = 60
    ):
        """
        Initialize Bedrock client with configuration
        
        Args:
            region: AWS region for Bedrock service
            model_id: Bedrock model identifier (e.g., 'qwen.qwen3-coder-next', 'anthropic.claude-v2')
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.region = region
        self.model_id = model_id
        self.max_retries = max_retries
        
        # Configure boto3 client with retries
        self.config = Config(
            region_name=region,
            retries={'max_attempts': max_retries, 'mode': 'adaptive'},
            connect_timeout=timeout,
            read_timeout=timeout
        )
        
        # Initialize Bedrock runtime client
        try:
            self.client = boto3.client('bedrock-runtime', config=self.config)
            logger.info(f"Initialized Bedrock Converse client for region {region} with model {model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise BedrockClientError(f"Failed to initialize Bedrock client: {str(e)}")
    
    def _build_converse_request(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float
    ) -> Dict[str, Any]:
        """
        Build request for Bedrock Converse API
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
            
        Returns:
            Request parameters for converse() API
        """
        return {
            "modelId": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p
            }
        }
    
    def _extract_converse_response(self, response: Dict[str, Any]) -> str:
        """
        Extract generated text from Converse API response
        
        Args:
            response: Response from Bedrock Converse API
            
        Returns:
            Generated text content
        """
        try:
            # Extract text from response structure:
            # response["output"]["message"]["content"][0]["text"]
            output = response.get("output", {})
            message = output.get("message", {})
            content = message.get("content", [])
            
            if not content or len(content) == 0:
                logger.error("No content in response")
                raise BedrockClientError("Empty response from Bedrock")
            
            text = content[0].get("text", "")
            
            if not text:
                logger.error("No text in content block")
                raise BedrockClientError("No text in response content")
            
            return text
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to extract response text: {str(e)}")
            logger.error(f"Response structure: {json.dumps(response, indent=2)}")
            raise BedrockClientError(f"Failed to parse response: {str(e)}")
    
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Invoke Bedrock model using Converse API with retry logic and exponential backoff
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate (default: 2000)
            temperature: Sampling temperature 0.0-1.0 (default: 0.7)
            top_p: Nucleus sampling parameter (default: 0.9)
            
        Returns:
            Generated text from the model
            
        Raises:
            BedrockClientError: If the API call fails after all retries
        """
        # Build request parameters for Converse API
        request_params = self._build_converse_request(prompt, max_tokens, temperature, top_p)
        
        # Retry loop with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Invoking Bedrock model {self.model_id} via Converse API (attempt {attempt + 1}/{self.max_retries})")
                
                # Call Bedrock Converse API
                response = self.client.converse(**request_params)
                
                # Extract text from response
                result = self._extract_converse_response(response)
                
                logger.info(f"Successfully invoked Bedrock model, generated {len(result)} characters")
                return result
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                error_message = e.response.get('Error', {}).get('Message', str(e))
                
                logger.warning(f"Bedrock API error (attempt {attempt + 1}): {error_code} - {error_message}")
                last_exception = e
                
                # Handle rate limiting with exponential backoff
                if error_code in ['ThrottlingException', 'TooManyRequestsException']:
                    if attempt < self.max_retries - 1:
                        backoff_time = (2 ** attempt) + (time.time() % 1)  # Add jitter
                        logger.info(f"Rate limited, backing off for {backoff_time:.2f} seconds")
                        time.sleep(backoff_time)
                        continue
                
                # Handle service errors with retry
                elif error_code in ['ServiceUnavailableException', 'InternalServerError']:
                    if attempt < self.max_retries - 1:
                        backoff_time = 2 ** attempt
                        logger.info(f"Service error, retrying in {backoff_time} seconds")
                        time.sleep(backoff_time)
                        continue
                
                # Don't retry on validation errors
                elif error_code in ['ValidationException', 'AccessDeniedException']:
                    logger.error(f"Non-retryable error: {error_code} - {error_message}")
                    raise BedrockClientError(f"Bedrock API error: {error_message}")
                
                # Retry on other errors
                if attempt < self.max_retries - 1:
                    backoff_time = 2 ** attempt
                    logger.info(f"Retrying in {backoff_time} seconds")
                    time.sleep(backoff_time)
                    
            except BotoCoreError as e:
                logger.warning(f"Boto core error (attempt {attempt + 1}): {str(e)}")
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    backoff_time = 2 ** attempt
                    logger.info(f"Retrying in {backoff_time} seconds")
                    time.sleep(backoff_time)
                    
            except Exception as e:
                logger.error(f"Unexpected error invoking Bedrock: {str(e)}")
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    backoff_time = 2 ** attempt
                    logger.info(f"Retrying in {backoff_time} seconds")
                    time.sleep(backoff_time)
        
        # All retries exhausted
        error_msg = f"Failed to invoke Bedrock after {self.max_retries} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"
        logger.error(error_msg)
        raise BedrockClientError(error_msg)
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about the configured model
        
        Returns:
            Dictionary with model configuration details
        """
        return {
            'model_id': self.model_id,
            'region': self.region,
            'max_retries': str(self.max_retries),
            'api_version': 'converse'
        }
