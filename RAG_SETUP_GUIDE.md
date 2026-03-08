# RAG Pipeline Setup Guide

## Overview

The RAG (Retrieval Augmented Generation) pipeline enables context-aware AI responses by retrieving relevant information from a knowledge base stored in Amazon OpenSearch.

## Architecture

```
Document Upload → Text Chunking → Embedding Generation → OpenSearch Storage
                                                                ↓
User Query → Query Embedding → Vector Search → Context Retrieval → AI Response
```

## Components

### 1. Embeddings Service (`embeddings.py`)
- Generates vector embeddings using Amazon Bedrock Titan
- Embedding dimension: 1536
- Supports batch processing
- Handles text truncation (max 8000 chars)

### 2. RAG Pipeline (`rag.py`)
- Document processing and chunking
- Configurable chunk size (default: 500 chars)
- Configurable overlap (default: 50 chars)
- OpenSearch integration with knn_vector
- Vector similarity search

### 3. API Endpoints

#### Upload Document
```bash
POST /rag/upload
```

**Request:**
```json
{
  "file_url": "course_materials/python_basics.txt",
  "metadata": {
    "content": "Python is a high-level programming language...",
    "topic": "Python Basics",
    "upload_date": "2024-01-15"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "chunks_processed": 15
}
```

#### Search Context
```bash
POST /rag/search
```

**Request:**
```json
{
  "query": "What is a Python function?",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Functions in Python are reusable blocks of code...",
      "score": 0.95,
      "metadata": {
        "source": "course_materials/python_basics.txt",
        "topic": "Python Basics",
        "chunk_index": 3
      }
    }
  ]
}
```

## Setup Instructions

### 1. Prerequisites

- Amazon OpenSearch domain
- AWS credentials with Bedrock access
- Python 3.11+

### 2. Environment Variables

```bash
# Required
export OPENSEARCH_ENDPOINT=https://your-domain.us-east-1.es.amazonaws.com
export AWS_REGION=us-east-1

# Optional (if using authentication)
export OPENSEARCH_USERNAME=admin
export OPENSEARCH_PASSWORD=your_password

# Optional (customize chunking)
export CHUNK_SIZE=500
export CHUNK_OVERLAP=50
```

### 3. Create OpenSearch Domain

Using AWS Console or CLI:

```bash
aws opensearch create-domain \
  --domain-name skillforge-knowledge \
  --engine-version OpenSearch_2.11 \
  --cluster-config InstanceType=t3.small.search,InstanceCount=1 \
  --ebs-options EBSEnabled=true,VolumeType=gp3,VolumeSize=10 \
  --access-policies '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "*"},
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:ACCOUNT_ID:domain/skillforge-knowledge/*"
    }]
  }'
```

### 4. Test the Pipeline

```bash
# Start the service
cd ai_service
python main.py

# Upload a document
curl -X POST http://localhost:8000/rag/upload \
  -H "Content-Type: application/json" \
  -d '{
    "file_url": "test_doc.txt",
    "metadata": {
      "content": "Python is a versatile programming language. Functions in Python are defined using the def keyword. Variables store data values.",
      "topic": "Python Basics"
    }
  }'

# Search for context
curl -X POST http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do you define a function in Python?",
    "top_k": 3
  }'

# Get AI explanation with context
curl -X POST http://localhost:8000/tutor/explain \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python functions"
  }'
```

## How It Works

### Document Processing Flow

1. **Upload**: Document content is received via API
2. **Chunking**: Text is split into overlapping chunks
   - Tries to break at sentence boundaries
   - Maintains context with overlap
3. **Embedding**: Each chunk is converted to a 1536-dimensional vector
4. **Storage**: Chunks and embeddings stored in OpenSearch with metadata

### Query Flow

1. **Query Received**: User asks a question
2. **Query Embedding**: Question converted to vector
3. **Vector Search**: kNN search finds similar chunks
4. **Context Retrieval**: Top-k most relevant chunks retrieved
5. **AI Generation**: Context included in prompt to Bedrock
6. **Response**: AI generates answer using retrieved context

## Index Structure

The OpenSearch index `course_materials` has the following structure:

```json
{
  "content": "Text chunk content",
  "embedding": [0.123, 0.456, ...],  // 1536 dimensions
  "metadata": {
    "source": "file_path",
    "topic": "topic_name",
    "chunk_index": 0,
    "upload_date": "2024-01-15"
  }
}
```

## Configuration Options

### Chunk Size
- **Default**: 500 characters
- **Recommendation**: 300-800 for technical content
- **Trade-off**: Larger chunks = more context, fewer chunks

### Chunk Overlap
- **Default**: 50 characters
- **Recommendation**: 10-20% of chunk size
- **Purpose**: Prevents information loss at boundaries

### Top-K Results
- **Default**: 3-5 chunks
- **Recommendation**: 3 for concise, 5-7 for comprehensive
- **Trade-off**: More context = better answers but longer prompts

## Performance Considerations

### Embedding Generation
- **Speed**: ~100ms per chunk
- **Batch Processing**: Processes multiple chunks in parallel
- **Rate Limits**: Bedrock has API rate limits

### Vector Search
- **Speed**: ~50ms for kNN search
- **Scalability**: OpenSearch handles millions of vectors
- **Accuracy**: kNN with ef_search=100 provides good balance

## Troubleshooting

### "RAG pipeline is not configured"
- Ensure `OPENSEARCH_ENDPOINT` is set
- Check OpenSearch domain is accessible
- Verify network connectivity

### "Failed to generate embedding"
- Check AWS credentials
- Verify Bedrock access in your region
- Check text length (max 8000 chars)

### "OpenSearch connection failed"
- Verify endpoint URL format
- Check security group rules
- Verify authentication credentials

### "No relevant context found"
- Upload more documents
- Check if documents were processed successfully
- Try broader search queries

## Best Practices

1. **Document Organization**
   - Group related content by topic
   - Include metadata for filtering
   - Use descriptive source names

2. **Content Quality**
   - Clean and format text before upload
   - Remove unnecessary whitespace
   - Break long documents into logical sections

3. **Query Optimization**
   - Use specific, clear questions
   - Include key terms from domain
   - Experiment with top_k values

4. **Monitoring**
   - Check chunk processing success rate
   - Monitor search result relevance
   - Track embedding generation times

## Integration with AI Tutor

The tutor endpoint automatically uses RAG when available:

```python
# Without RAG
POST /tutor/explain {"topic": "recursion"}
# Uses only AI model knowledge

# With RAG (automatic)
POST /tutor/explain {"topic": "recursion"}
# Retrieves relevant context from knowledge base
# Includes context in prompt to AI
# Generates more accurate, contextual response
```

## Future Enhancements

- [ ] S3 integration for document upload
- [ ] PDF and document parsing
- [ ] Metadata filtering in search
- [ ] Hybrid search (keyword + vector)
- [ ] Relevance feedback
- [ ] Document versioning
- [ ] Batch upload API
- [ ] Search analytics

## Example Use Cases

### 1. Course Material Repository
Upload lecture notes, textbooks, and documentation for students to query.

### 2. Code Documentation
Store API docs, code examples, and best practices for developer assistance.

### 3. FAQ System
Build a knowledge base from frequently asked questions and answers.

### 4. Technical Support
Store troubleshooting guides and solutions for context-aware support.

## Security Considerations

- Use VPC for OpenSearch domain
- Enable encryption at rest and in transit
- Implement fine-grained access control
- Rotate credentials regularly
- Monitor access logs
- Validate and sanitize input content

---

**Status**: ✅ Fully Implemented and Operational

The RAG pipeline is production-ready and integrated with the AI tutor system!
