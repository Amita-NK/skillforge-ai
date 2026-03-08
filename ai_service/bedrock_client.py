"""
Bedrock Client Wrapper
Provides a clean interface for Amazon Bedrock API with retry logic and error handling
"""
import json
import time
import logging
from typing import Dict, Any, Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class BedrockClientError(Exception):
    """Custom exception for Bedrock client errors"""
    pass


class BedrockClient:
    """
    Wrapper for Amazon Bedrock API with support for multiple model families
    Implements retry logic with exponential backoff for resilient API calls
    """
    
    # Model family configurations
    MODEL_CONFIGS = {
        'claude': {
            'request_format': 'anthropic',
            'response_key': 'completion'
        },
        'titan': {
            'request_format': 'amazon',
            'response_key': 'results'
        },
        'llama': {
            'request_format': 'meta',
            'response_key': 'generation'
        }
    }
    
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
            model_id: Bedrock model identifier (e.g., 'anthropic.claude-v2')
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
            logger.info(f"Initialized Bedrock client for region {region} with model {model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise BedrockClientError(f"Failed to initialize Bedrock client: {str(e)}")
        
        # Determine model family
        self.model_family = self._detect_model_family(model_id)
    
    def _detect_model_family(self, model_id: str) -> str:
        """
        Detect model family from model ID
        
        Args:
            model_id: Bedrock model identifier
            
        Returns:
            Model family name ('claude', 'titan', or 'llama')
        """
        model_id_lower = model_id.lower()
        if 'claude' in model_id_lower or 'anthropic' in model_id_lower:
            return 'claude'
        elif 'titan' in model_id_lower or 'amazon' in model_id_lower:
            return 'titan'
        elif 'llama' in model_id_lower or 'meta' in model_id_lower:
            return 'llama'
        else:
            logger.warning(f"Unknown model family for {model_id}, defaulting to claude")
            return 'claude'

    def _build_request_body(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float
    ) -> Dict[str, Any]:
        """
        Build request body based on model family
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
            
        Returns:
            Request body formatted for the specific model family
        """
        if self.model_family == 'claude':
            return {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop_sequences": ["\n\nHuman:"]
            }
        elif self.model_family == 'titan':
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": temperature,
                    "topP": top_p
                }
            }
        elif self.model_family == 'llama':
            return {
                "prompt": prompt,
                "max_gen_len": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
        else:
            raise BedrockClientError(f"Unsupported model family: {self.model_family}")
    
    def _extract_response_text(self, response_body: Dict[str, Any]) -> str:
        """
        Extract generated text from response based on model family
        
        Args:
            response_body: Response body from Bedrock API
            
        Returns:
            Generated text content
        """
        try:
            if self.model_family == 'claude':
                return response_body.get('completion', '')
            elif self.model_family == 'titan':
                results = response_body.get('results', [])
                if results and len(results) > 0:
                    return results[0].get('outputText', '')
                return ''
            elif self.model_family == 'llama':
                return response_body.get('generation', '')
            else:
                raise BedrockClientError(f"Unsupported model family: {self.model_family}")
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to extract response text: {str(e)}")
            raise BedrockClientError(f"Failed to parse response: {str(e)}")
    
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Invoke Bedrock model with retry logic and exponential backoff
        
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
        # Build request body
        body = self._build_request_body(prompt, max_tokens, temperature, top_p)
        
        # Retry loop with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Invoking Bedrock model {self.model_id} (attempt {attempt + 1}/{self.max_retries})")
                
                # Call Bedrock API
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body),
                    contentType='application/json',
                    accept='application/json'
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                result = self._extract_response_text(response_body)
                
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
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse response JSON: {str(e)}")
                raise BedrockClientError(f"Invalid JSON response from Bedrock: {str(e)}")
                
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
            'model_family': self.model_family,
            'region': self.region,
            'max_retries': str(self.max_retries)
        }
