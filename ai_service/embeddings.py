"""
Embeddings Module
Generates vector embeddings using Amazon Bedrock Titan
"""
import logging
import json
from typing import List, Dict, Any
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EmbeddingsError(Exception):
    """Custom exception for embeddings errors"""
    pass


class EmbeddingsService:
    """Service for generating text embeddings using Bedrock Titan"""
    
    # Bedrock Titan Embeddings model
    EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"
    EMBEDDING_DIMENSION = 1536
    
    def __init__(self, region: str):
        """
        Initialize embeddings service
        
        Args:
            region: AWS region for Bedrock service
        """
        self.region = region
        
        # Configure boto3 client
        config = Config(
            region_name=region,
            retries={'max_attempts': 3, 'mode': 'adaptive'}
        )
        
        try:
            self.client = boto3.client('bedrock-runtime', config=config)
            logger.info(f"Initialized embeddings service in region {region}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings client: {str(e)}")
            raise EmbeddingsError(f"Failed to initialize embeddings client: {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            EmbeddingsError: If embedding generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Truncate text if too long (Titan has limits)
        max_length = 8000
        if len(text) > max_length:
            logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]
        
        try:
            # Prepare request body
            body = json.dumps({
                "inputText": text.strip()
            })
            
            # Call Bedrock Titan Embeddings
            response = self.client.invoke_model(
                modelId=self.EMBEDDING_MODEL_ID,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding')
            
            if not embedding:
                raise EmbeddingsError("No embedding returned from Bedrock")
            
            logger.debug(f"Generated embedding of dimension {len(embedding)}")
            return embedding
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Bedrock API error: {error_code} - {error_message}")
            raise EmbeddingsError(f"Failed to generate embedding: {error_message}")
        
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {str(e)}")
            raise EmbeddingsError(f"Failed to generate embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingsError: If batch embedding generation fails
        """
        if not texts:
            return []
        
        embeddings = []
        failed_count = 0
        
        for i, text in enumerate(texts):
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for text {i}: {str(e)}")
                failed_count += 1
                # Add zero vector as placeholder
                embeddings.append([0.0] * self.EMBEDDING_DIMENSION)
        
        if failed_count > 0:
            logger.warning(f"Failed to generate {failed_count}/{len(texts)} embeddings")
        
        logger.info(f"Generated {len(embeddings)} embeddings ({failed_count} failures)")
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this service
        
        Returns:
            Embedding dimension
        """
        return self.EMBEDDING_DIMENSION


def create_embeddings_service(region: str) -> EmbeddingsService:
    """
    Factory function to create an EmbeddingsService instance
    
    Args:
        region: AWS region
        
    Returns:
        EmbeddingsService instance
    """
    return EmbeddingsService(region)
