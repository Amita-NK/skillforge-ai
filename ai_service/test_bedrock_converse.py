"""
Test script for Bedrock Converse API integration
Run this to verify the AI service can communicate with Amazon Bedrock
"""
import os
import sys
import logging
from bedrock_client import BedrockClient, BedrockClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_bedrock_connection():
    """Test basic Bedrock connection and model invocation"""
    
    # Get configuration from environment
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    model_id = os.getenv('BEDROCK_MODEL_ID', 'qwen.qwen3-coder-next')
    
    logger.info(f"Testing Bedrock connection with model: {model_id} in region: {aws_region}")
    
    try:
        # Initialize Bedrock client
        client = BedrockClient(
            region=aws_region,
            model_id=model_id
        )
        
        logger.info("✓ Bedrock client initialized successfully")
        
        # Test simple prompt
        test_prompt = "Explain what a binary search algorithm is in one sentence."
        logger.info(f"Testing with prompt: {test_prompt}")
        
        response = client.invoke_model(
            prompt=test_prompt,
            max_tokens=200,
            temperature=0.7,
            top_p=0.9
        )
        
        logger.info("✓ Model invocation successful")
        logger.info(f"Response length: {len(response)} characters")
        logger.info(f"Response preview: {response[:200]}...")
        
        # Get model info
        model_info = client.get_model_info()
        logger.info(f"Model info: {model_info}")
        
        print("\n" + "="*80)
        print("SUCCESS: Bedrock Converse API is working correctly!")
        print("="*80)
        print(f"\nModel: {model_id}")
        print(f"Region: {aws_region}")
        print(f"\nTest Response:\n{response}\n")
        print("="*80)
        
        return True
        
    except BedrockClientError as e:
        logger.error(f"✗ Bedrock client error: {str(e)}")
        print("\n" + "="*80)
        print("ERROR: Bedrock Converse API test failed")
        print("="*80)
        print(f"\nError: {str(e)}\n")
        print("Troubleshooting:")
        print("1. Verify AWS credentials are configured correctly")
        print("2. Ensure Bedrock access is enabled in your AWS account")
        print("3. Check that the model ID is correct and accessible")
        print("4. Verify AWS_REGION and BEDROCK_MODEL_ID environment variables")
        print("="*80)
        return False
        
    except Exception as e:
        logger.error(f"✗ Unexpected error: {str(e)}")
        print("\n" + "="*80)
        print("ERROR: Unexpected error during test")
        print("="*80)
        print(f"\nError: {str(e)}\n")
        print("="*80)
        return False


if __name__ == "__main__":
    # Load environment variables from .env file if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded environment variables from .env file")
    except ImportError:
        logger.warning("python-dotenv not installed, using system environment variables")
    
    # Run test
    success = test_bedrock_connection()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
