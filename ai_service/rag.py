"""
RAG (Retrieval Augmented Generation) Pipeline
Handles document processing, embedding storage, and context retrieval
Supports S3 document ingestion
"""
import logging
import re
import boto3
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import OpenSearchException
from embeddings import EmbeddingsService
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class RAGError(Exception):
    """Custom exception for RAG pipeline errors"""
    pass


class RAGPipeline:
    """
    RAG pipeline for document processing and context retrieval
    Handles text chunking, embedding generation, and vector search
    """
    
    # Default configuration
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_CHUNK_OVERLAP = 50
    DEFAULT_INDEX_NAME = "course_materials"
    
    def __init__(
        self,
        embeddings_service: EmbeddingsService,
        opensearch_endpoint: str,
        opensearch_user: Optional[str] = None,
        opensearch_password: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        aws_region: Optional[str] = None
    ):
        """
        Initialize RAG pipeline
        
        Args:
            embeddings_service: Service for generating embeddings
            opensearch_endpoint: OpenSearch endpoint URL
            opensearch_user: OpenSearch username (optional)
            opensearch_password: OpenSearch password (optional)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            aws_region: AWS region for S3 access (optional)
        """
        self.embeddings = embeddings_service
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.index_name = self.DEFAULT_INDEX_NAME
        
        # Initialize S3 client if region provided
        self.s3_client = None
        if aws_region:
            try:
                self.s3_client = boto3.client('s3', region_name=aws_region)
                logger.info(f"Initialized S3 client for region {aws_region}")
            except Exception as e:
                logger.warning(f"Failed to initialize S3 client: {str(e)}")
        
        # Initialize OpenSearch client
        try:
            auth = None
            if opensearch_user and opensearch_password:
                auth = (opensearch_user, opensearch_password)
            
            self.opensearch = OpenSearch(
                hosts=[opensearch_endpoint],
                http_auth=auth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection
            )
            
            logger.info(f"Initialized RAG pipeline with OpenSearch at {opensearch_endpoint}")
            
            # Create index if it doesn't exist
            self._ensure_index_exists()
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenSearch client: {str(e)}")
            raise RAGError(f"Failed to initialize OpenSearch: {str(e)}")
    
    def _ensure_index_exists(self):
        """Create OpenSearch index if it doesn't exist"""
        try:
            if not self.opensearch.indices.exists(index=self.index_name):
                # Define index mapping with knn_vector
                index_body = {
                    "settings": {
                        "index": {
                            "knn": True,
                            "knn.algo_param.ef_search": 100
                        }
                    },
                    "mappings": {
                        "properties": {
                            "content": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "embedding": {
                                "type": "knn_vector",
                                "dimension": self.embeddings.get_embedding_dimension()
                            },
                            "metadata": {
                                "properties": {
                                    "source": {"type": "keyword"},
                                    "topic": {"type": "keyword"},
                                    "chunk_index": {"type": "integer"},
                                    "upload_date": {"type": "date"}
                                }
                            }
                        }
                    }
                }
                
                self.opensearch.indices.create(
                    index=self.index_name,
                    body=index_body
                )
                logger.info(f"Created OpenSearch index: {self.index_name}")
        
        except OpenSearchException as e:
            logger.error(f"Failed to create index: {str(e)}")
            raise RAGError(f"Failed to create index: {str(e)}")
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        # Clean text
        text = text.strip()
        
        # Split into chunks with overlap
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary if possible
            if end < len(text):
                # Look for sentence ending
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size // 2:
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def process_document(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> int:
        """
        Process a document: chunk, embed, and store in OpenSearch
        
        Args:
            content: Document content
            metadata: Document metadata (source, topic, etc.)
            
        Returns:
            Number of chunks processed
            
        Raises:
            RAGError: If document processing fails
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        try:
            # Split into chunks
            chunks = self.split_text(content)
            
            if not chunks:
                raise RAGError("No chunks generated from content")
            
            # Generate embeddings for all chunks
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self.embeddings.generate_embeddings_batch(chunks)
            
            # Store in OpenSearch
            stored_count = 0
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_id = f"{metadata.get('source', 'unknown')}_{i}"
                
                document = {
                    'content': chunk,
                    'embedding': embedding,
                    'metadata': {
                        **metadata,
                        'chunk_index': i
                    }
                }
                
                try:
                    self.opensearch.index(
                        index=self.index_name,
                        id=doc_id,
                        body=document,
                        refresh=True
                    )
                    stored_count += 1
                except OpenSearchException as e:
                    logger.warning(f"Failed to store chunk {i}: {str(e)}")
            
            logger.info(f"Stored {stored_count}/{len(chunks)} chunks in OpenSearch")
            return stored_count
            
        except Exception as e:
            logger.error(f"Failed to process document: {str(e)}")
            raise RAGError(f"Failed to process document: {str(e)}")
    
    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant context using vector similarity
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results with content, score, and metadata
            
        Raises:
            RAGError: If search fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            # Generate query embedding
            logger.info(f"Searching for: {query[:100]}...")
            query_embedding = self.embeddings.generate_embedding(query)
            
            # Perform knn search
            search_body = {
                'size': top_k,
                'query': {
                    'knn': {
                        'embedding': {
                            'vector': query_embedding,
                            'k': top_k
                        }
                    }
                }
            }
            
            response = self.opensearch.search(
                index=self.index_name,
                body=search_body
            )
            
            # Parse results
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    'content': hit['_source']['content'],
                    'score': hit['_score'],
                    'metadata': hit['_source'].get('metadata', {})
                })
            
            logger.info(f"Found {len(results)} relevant chunks")
            return results
            
        except OpenSearchException as e:
            logger.error(f"OpenSearch search error: {str(e)}")
            raise RAGError(f"Search failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected search error: {str(e)}")
            raise RAGError(f"Search failed: {str(e)}")
    
    def get_context_for_query(
        self,
        query: str,
        top_k: int = 3
    ) -> str:
        """
        Get formatted context string for a query
        
        Args:
            query: Search query
            top_k: Number of context chunks to retrieve
            
        Returns:
            Formatted context string
        """
        try:
            results = self.search(query, top_k)
            
            if not results:
                return "No relevant context found."
            
            # Format context
            context_parts = []
            for i, result in enumerate(results, 1):
                source = result['metadata'].get('source', 'Unknown')
                content = result['content']
                context_parts.append(f"[Source {i}: {source}]\n{content}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"Failed to get context: {str(e)}")
            return "No additional context available."
    
    def fetch_from_s3(self, bucket: str, key: str) -> str:
        """
        Fetch document content from S3
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            Document content as string
            
        Raises:
            RAGError: If S3 fetch fails
        """
        if not self.s3_client:
            raise RAGError("S3 client not initialized. Provide aws_region during initialization.")
        
        try:
            logger.info(f"Fetching document from S3: s3://{bucket}/{key}")
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully fetched {len(content)} characters from S3")
            return content
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise RAGError(f"Document not found in S3: s3://{bucket}/{key}")
            elif error_code == 'NoSuchBucket':
                raise RAGError(f"S3 bucket not found: {bucket}")
            elif error_code == 'AccessDenied':
                raise RAGError(f"Access denied to S3 object: s3://{bucket}/{key}")
            else:
                raise RAGError(f"S3 error: {str(e)}")
        
        except BotoCoreError as e:
            logger.error(f"BotoCore error fetching from S3: {str(e)}")
            raise RAGError(f"Failed to fetch from S3: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error fetching from S3: {str(e)}")
            raise RAGError(f"Failed to fetch from S3: {str(e)}")
    
    def process_s3_document(
        self,
        bucket: str,
        key: str,
        metadata: Dict[str, Any]
    ) -> int:
        """
        Fetch document from S3 and process it
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            metadata: Document metadata
            
        Returns:
            Number of chunks processed
            
        Raises:
            RAGError: If processing fails
        """
        try:
            # Fetch content from S3
            content = self.fetch_from_s3(bucket, key)
            
            # Add S3 location to metadata
            enhanced_metadata = {
                **metadata,
                'source': f"s3://{bucket}/{key}",
                's3_bucket': bucket,
                's3_key': key
            }
            
            # Process document
            return self.process_document(content, enhanced_metadata)
        
        except RAGError:
            raise
        except Exception as e:
            logger.error(f"Failed to process S3 document: {str(e)}")
            raise RAGError(f"Failed to process S3 document: {str(e)}")
    
    def delete_index(self):
        """Delete the OpenSearch index (use with caution)"""
        try:
            if self.opensearch.indices.exists(index=self.index_name):
                self.opensearch.indices.delete(index=self.index_name)
                logger.info(f"Deleted index: {self.index_name}")
        except OpenSearchException as e:
            logger.error(f"Failed to delete index: {str(e)}")
            raise RAGError(f"Failed to delete index: {str(e)}")


def create_rag_pipeline(
    embeddings_service: EmbeddingsService,
    opensearch_endpoint: str,
    opensearch_user: Optional[str] = None,
    opensearch_password: Optional[str] = None
) -> RAGPipeline:
    """
    Factory function to create a RAGPipeline instance
    
    Args:
        embeddings_service: Embeddings service
        opensearch_endpoint: OpenSearch endpoint
        opensearch_user: OpenSearch username
        opensearch_password: OpenSearch password
        
    Returns:
        RAGPipeline instance
    """
    return RAGPipeline(
        embeddings_service=embeddings_service,
        opensearch_endpoint=opensearch_endpoint,
        opensearch_user=opensearch_user,
        opensearch_password=opensearch_password
    )
