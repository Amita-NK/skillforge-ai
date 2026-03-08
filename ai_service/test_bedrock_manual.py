"""
Manual test script to verify Bedrock client implementation
Run this to check if the client is working correctly
"""
import sys
from unittest.mock import Mock, patch
import json

# Add current directory to path
sys.path.insert(0, '.')

from bedrock_client import BedrockClient, BedrockClientError


def test_basic_functionality():
    """Test basic client functionality"""
    print("Testing BedrockClient basic functionality...")
    
    with patch('bedrock_client.boto3.client') as mock_boto:
        # Test 1: Initialization
        print("✓ Test 1: Client initialization")
        client = BedrockClient(region='us