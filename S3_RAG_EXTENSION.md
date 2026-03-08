# S3 RAG Extension - Implementation Summary

## Overview

Extended the RAG (Retrieval Augmented Generation) pipeline to support S3 document ingestion in addition to direct content upload. This allows the SkillForge AI+ platform to process documents stored in Amazon S3 buckets for the knowledge base.

## Changes Made

### 1. AI Service - RAG Pipeline (`ai_service/rag.py`)

Added two new methods to the `RAGPipeline` class:

#### `fetch_from_s3(bucket: str, key: str) -> str`
- Fetches document content from S3 using boto3
- Handles S3-specific errors (NoSuchKey, NoSuchBucket, AccessDenied)
- Returns document content as string
- Requires S3 client initialization with AWS region

#### `process_s3_document(bucket: str, key: str, metadata: Dict) -> int`
- Fetches document from S3 and processes it through the RAG pipeline
- Automatically adds S3 location to metadata (source, s3_bucket, s3_key)
- Returns number of chunks processed
- Combines S3 fetch with existing document processing logic

**Key Features**:
- S3 client is initialized in `__init__` if `aws_region` parameter is provided
- Comprehensive error handling for S3 operations
- Automatic metadata enrichment with S3 location

### 2. AI Service - Request Models (`ai_service/models.py`)

Updated `RAGUploadRequest` model to support multiple upload methods:

```python
class RAGUploadRequest(BaseModel):
    file_url: Optional[str] = None  # Legacy support
    s3_bucket: Optional[str] = None  # S3 bucket name
    s3_key: Optional[str] = None     # S3 object key
    content: Optional[str] = None    # Direct content
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

**Validation**:
- `s3_bucket` requires `s3_key` and vice versa
- Must provide either `s3_bucket+s3_key`, `content`, or `file_url`

### 3. AI Service - Upload Endpoint (`ai_service/main.py`)

Updated `POST /rag/upload` endpoint to handle three upload methods:

1. **S3 Ingestion**: `s3_bucket` + `s3_key`
   - Calls `rag_pipeline.process_s3_document()`
   - Fetches content from S3 and processes it

2. **Direct Content**: `content`
   - Calls `rag_pipeline.process_document()`
   - Processes content directly

3. **Legacy Format**: `file_url` + `metadata.content`
   - Maintains backward compatibility
   - Processes content from metadata

**Response**:
```json
{
  "status": "success",
  "chunks_processed": 42
}
```

### 4. Backend - AI Service Client (`backend/app.py`)

Added `upload_rag_document()` method to `AIServiceClient` class:

```python
@staticmethod
def upload_rag_document(s3_bucket=None, s3_key=None, content=None, metadata=None) -> dict
```

- Constructs appropriate payload based on parameters
- Validates that either S3 or content is provided
- Calls AI service `/rag/upload` endpoint
- Returns upload response

### 5. Backend - RAG Upload Endpoint (`backend/app.py`)

Added new protected endpoint `POST /ai/rag/upload`:

**Authentication**: Required (JWT Bearer token)

**Request Body** (S3):
```json
{
  "s3_bucket": "my-documents-bucket",
  "s3_key": "courses/python/intro.pdf",
  "metadata": {
    "topic": "Python Programming",
    "author": "John Doe"
  }
}
```

**Request Body** (Direct):
```json
{
  "content": "Document content...",
  "metadata": {
    "topic": "Python Programming"
  }
}
```

**Features**:
- JWT authentication required
- Validates input parameters
- Proxies request to AI service
- Logs user activity

### 6. Documentation Updates

#### `API_ENDPOINTS.md`
- Updated AI Service `/rag/upload` endpoint documentation
- Added Backend `/ai/rag/upload` endpoint documentation
- Included examples for both S3 and direct content upload
- Updated endpoint counts (11 backend endpoints, 7 AI service endpoints)

#### `API_QUICK_REFERENCE.md`
- Added `/ai/rag/upload` to protected endpoints table
- Added quick examples for S3 and direct content upload
- Updated endpoint counts

## Usage Examples

### S3 Document Ingestion

```bash
# Via Backend (with authentication)
curl -X POST http://localhost:5000/ai/rag/upload \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "s3_bucket": "my-documents-bucket",
    "s3_key": "courses/python/intro.pdf",
    "metadata": {
      "topic": "Python Programming",
      "author": "John Doe"
    }
  }'
```

### Direct Content Upload

```bash
# Via Backend (with authentication)
curl -X POST http://localhost:5000/ai/rag/upload \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Python Basics\n\nPython is a high-level programming language...",
    "metadata": {
      "topic": "Python Programming",
      "source": "manual_upload"
    }
  }'
```

## Configuration Requirements

### Environment Variables

The AI service requires AWS credentials to access S3:

```bash
# .env file
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### IAM Permissions

The AWS credentials must have the following S3 permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

## Error Handling

### S3-Specific Errors

- **NoSuchKey**: Document not found in S3
- **NoSuchBucket**: S3 bucket not found
- **AccessDenied**: Insufficient permissions to access S3 object
- **BotoCoreError**: General AWS SDK errors

All errors are caught and returned as HTTP 500 with descriptive messages.

### Validation Errors

- **400 Bad Request**: Missing or invalid parameters
- **503 Service Unavailable**: RAG pipeline not configured (OpenSearch not available)

## Architecture Flow

```
Frontend
   ↓
Backend (JWT Auth)
   ↓
AI Service
   ↓
   ├─→ S3 (fetch document)
   ├─→ Bedrock Titan (generate embeddings)
   └─→ OpenSearch (store vectors)
```

## Benefits

1. **Scalability**: Process large documents stored in S3 without uploading through API
2. **Flexibility**: Support both S3 and direct content upload methods
3. **Security**: Backend enforces JWT authentication for all uploads
4. **Efficiency**: Documents are fetched directly from S3 by AI service
5. **Backward Compatibility**: Legacy upload format still supported

## Testing Recommendations

1. **Unit Tests**:
   - Test `fetch_from_s3()` with valid and invalid S3 paths
   - Test `process_s3_document()` with various document types
   - Test error handling for S3 access errors

2. **Integration Tests**:
   - Test end-to-end S3 document ingestion
   - Test direct content upload
   - Test authentication enforcement on backend endpoint

3. **Property-Based Tests**:
   - Test that all uploaded documents are properly chunked
   - Test that embeddings are generated for all chunks
   - Test that metadata is preserved through the pipeline

## Next Steps

1. Add support for additional file formats (PDF, DOCX, etc.)
2. Implement batch S3 document processing
3. Add progress tracking for large document uploads
4. Implement document versioning in OpenSearch
5. Add document deletion/update endpoints

## Files Modified

- `ai_service/rag.py` - Added S3 fetch and processing methods
- `ai_service/models.py` - Updated RAGUploadRequest model
- `ai_service/main.py` - Updated /rag/upload endpoint
- `backend/app.py` - Added AIServiceClient method and /ai/rag/upload endpoint
- `API_ENDPOINTS.md` - Updated documentation
- `API_QUICK_REFERENCE.md` - Updated quick reference

## Dependencies

All required dependencies are already in `ai_service/requirements.txt`:
- `boto3==1.34.34` - AWS SDK for Python
- `botocore==1.34.34` - Low-level AWS SDK core

No additional dependencies required.
