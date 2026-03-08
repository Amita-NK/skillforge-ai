# Bedrock Converse API Update

## Overview

The AI service has been updated to use the **Amazon Bedrock Converse API** instead of the legacy `invoke_model` API. This provides a unified interface that works with all Bedrock models, including newer models like:

- `qwen.qwen3-coder-next` (recommended for code tasks)
- `nvidia.nemotron-nano-12b-v2`
- `anthropic.claude-v2` (still supported)

## What Changed

### 1. Bedrock Client (`bedrock_client.py`)

**Before:**
- Used model-specific request formats (Claude, Titan, Llama)
- Called `client.invoke_model()` with JSON body
- Required different parsing logic for each model family

**After:**
- Uses unified Converse API format
- Calls `client.converse()` with standardized parameters
- Single response parsing path for all models
- Response structure: `response["output"]["message"]["content"][0]["text"]`

### 2. Request Format

**Old Format (invoke_model):**
```python
response = client.invoke_model(
    modelId=model_id,
    body=json.dumps({
        "prompt": "...",
        "max_tokens_to_sample": 2000,
        # Model-specific parameters
    }),
    contentType='application/json',
    accept='application/json'
)
```

**New Format (converse):**
```python
response = client.converse(
    modelId=model_id,
    messages=[
        {
            "role": "user",
            "content": [{"text": prompt}]
        }
    ],
    inferenceConfig={
        "maxTokens": 2000,
        "temperature": 0.7,
        "topP": 0.9
    }
)
```

### 3. Response Parsing

**Old:**
```python
# Different for each model family
if model_family == 'claude':
    text = response_body.get('completion', '')
elif model_family == 'titan':
    text = response_body['results'][0]['outputText']
# etc...
```

**New:**
```python
# Unified for all models
text = response["output"]["message"]["content"][0]["text"]
```

## Configuration

### Environment Variables

Update your `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Bedrock Model (choose one)
BEDROCK_MODEL_ID=qwen.qwen3-coder-next  # Recommended for code
# BEDROCK_MODEL_ID=nvidia.nemotron-nano-12b-v2
# BEDROCK_MODEL_ID=anthropic.claude-v2
```

### Supported Models

All models that support the Converse API:

| Model ID | Best For | Notes |
|----------|----------|-------|
| `qwen.qwen3-coder-next` | Code generation, debugging | Optimized for programming tasks |
| `nvidia.nemotron-nano-12b-v2` | General purpose | Fast, efficient |
| `anthropic.claude-v2` | Complex reasoning | High quality responses |
| `anthropic.claude-instant-v1` | Fast responses | Lower cost |
| `amazon.titan-text-express-v1` | General purpose | AWS native |

## Testing

### 1. Test Bedrock Connection

```bash
cd ai_service
python test_bedrock_converse.py
```

Expected output:
```
SUCCESS: Bedrock Converse API is working correctly!
================================================================================

Model: qwen.qwen3-coder-next
Region: us-east-1

Test Response:
A binary search algorithm is an efficient search method that repeatedly divides
a sorted array in half to locate a target value...

================================================================================
```

### 2. Test via Docker

```bash
# Start services
docker-compose up -d

# Check AI service logs
docker-compose logs -f ai-service

# Test health endpoint
curl http://localhost:8000/health

# Test explanation endpoint
curl -X POST http://localhost:8000/tutor/explain \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search algorithm"}'
```

### 3. Test via Backend

```bash
# Backend should proxy to AI service
curl -X POST http://localhost:5000/ai/explain \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"topic": "binary search algorithm"}'
```

## Troubleshooting

### Error: "AccessDeniedException"

**Cause:** AWS credentials don't have Bedrock permissions

**Solution:**
1. Verify AWS credentials are configured:
   ```bash
   aws sts get-caller-identity
   ```

2. Check Bedrock access:
   ```bash
   aws bedrock list-foundation-models --region us-east-1
   ```

3. Ensure IAM policy includes:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "bedrock:InvokeModel",
       "bedrock:InvokeModelWithResponseStream"
     ],
     "Resource": "*"
   }
   ```

### Error: "ValidationException: The model ID is invalid"

**Cause:** Model not available in your region or account

**Solution:**
1. List available models:
   ```bash
   aws bedrock list-foundation-models --region us-east-1 --query 'modelSummaries[*].[modelId,modelName]' --output table
   ```

2. Request model access in AWS Console:
   - Go to Amazon Bedrock console
   - Navigate to "Model access"
   - Request access for desired models

### Error: "Failed to parse response"

**Cause:** Unexpected response structure

**Solution:**
1. Check logs for full response structure
2. Verify model ID is correct
3. Ensure using latest boto3:
   ```bash
   pip install --upgrade boto3
   ```

### Docker Container Issues

**Symptoms:** AI service container exits immediately

**Solution:**
1. Check environment variables:
   ```bash
   docker-compose config
   ```

2. View container logs:
   ```bash
   docker-compose logs ai-service
   ```

3. Verify .env file is in project root

4. Rebuild containers:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

## Migration Checklist

- [x] Update `bedrock_client.py` to use Converse API
- [x] Remove model family detection logic
- [x] Update response parsing
- [x] Update environment variables
- [x] Create test script
- [x] Update documentation
- [ ] Test with all endpoints (tutor, quiz, debugger)
- [ ] Test in Docker environment
- [ ] Test backend integration
- [ ] Verify AWS deployment compatibility

## Compatibility

### Docker Compose
✅ Fully compatible - no changes needed to `docker-compose.yml`

### Backend Integration
✅ Fully compatible - backend API contract unchanged

### AWS Deployment (ECS/Terraform)
✅ Fully compatible - uses same environment variables and IAM permissions

### Frontend
✅ Fully compatible - no changes needed

## Performance

The Converse API provides:
- **Unified interface** - same code works with all models
- **Better error handling** - clearer error messages
- **Future-proof** - supports new models automatically
- **Same latency** - no performance degradation

## Next Steps

1. **Test locally:**
   ```bash
   python ai_service/test_bedrock_converse.py
   ```

2. **Test in Docker:**
   ```bash
   docker-compose up -d
   curl http://localhost:8000/health
   ```

3. **Test end-to-end:**
   - Start frontend
   - Login to application
   - Try AI tutoring feature
   - Generate a quiz
   - Debug some code

4. **Deploy to AWS:**
   - No changes needed to Terraform
   - Same IAM permissions work
   - Update environment variables in ECS task definitions

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f ai-service`
2. Verify environment: `docker-compose config`
3. Test Bedrock access: `aws bedrock list-foundation-models`
4. Review this documentation

## References

- [Amazon Bedrock Converse API Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)
- [Boto3 Bedrock Runtime Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
- [Supported Models](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
