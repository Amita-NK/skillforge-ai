# Bedrock IAM Policy Module

This Terraform module creates IAM policies and roles for Amazon Bedrock access with least-privilege permissions.

## Features

- **Separate Policies**: Individual policies for model invocation, embeddings, and listing
- **Combined Policy**: Optional single policy for simplified management
- **Task Role**: Pre-configured ECS task role with Bedrock access
- **CloudWatch Integration**: Optional CloudWatch Logs permissions
- **Customizable Models**: Specify which Bedrock models to allow

## Usage

### Basic Usage

```hcl
module "bedrock_iam" {
  source = "./modules/bedrock-iam"
  
  project_name = "skillforge-ai"
  aws_region   = "us-east-1"
  
  tags = {
    Environment = "production"
    Project     = "SkillForge-AI"
  }
}
```

### Custom Model ARNs

```hcl
module "bedrock_iam" {
  source = "./modules/bedrock-iam"
  
  project_name = "skillforge-ai"
  
  allowed_model_arns = [
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2",
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1"
  ]
  
  embedding_model_arns = [
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
  ]
}
```

### With Model Listing Enabled

```hcl
module "bedrock_iam" {
  source = "./modules/bedrock-iam"
  
  project_name         = "skillforge-ai"
  enable_model_listing = true  # Allow listing available models
}
```

### Combined Policy Mode

```hcl
module "bedrock_iam" {
  source = "./modules/bedrock-iam"
  
  project_name           = "skillforge-ai"
  create_combined_policy = true  # Single policy instead of separate
}
```

### Without Task Role

```hcl
module "bedrock_iam" {
  source = "./modules/bedrock-iam"
  
  project_name    = "skillforge-ai"
  create_task_role = false  # Only create policies, not role
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | Project name for resource naming | string | - | yes |
| aws_region | AWS region | string | "us-east-1" | no |
| allowed_model_arns | List of Bedrock model ARNs allowed for invocation | list(string) | See variables.tf | no |
| embedding_model_arns | List of Bedrock embedding model ARNs | list(string) | See variables.tf | no |
| enable_model_listing | Enable permissions to list Bedrock models | bool | false | no |
| create_combined_policy | Create a single combined policy | bool | false | no |
| create_task_role | Create an IAM role for ECS tasks | bool | true | no |
| enable_cloudwatch_logs | Enable CloudWatch Logs permissions | bool | true | no |
| tags | Tags to apply to all resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| bedrock_invoke_policy_arn | ARN of the Bedrock model invocation policy |
| bedrock_embeddings_policy_arn | ARN of the Bedrock embeddings policy |
| bedrock_list_policy_arn | ARN of the Bedrock model listing policy |
| bedrock_full_policy_arn | ARN of the combined Bedrock policy |
| bedrock_task_role_arn | ARN of the ECS task role with Bedrock access |
| bedrock_task_role_name | Name of the ECS task role |
| policy_arns | Map of all policy ARNs |

## IAM Policies Created

### 1. Bedrock Invoke Policy
Allows invocation of specified foundation models:
- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`

### 2. Bedrock Embeddings Policy
Allows generation of embeddings:
- `bedrock:InvokeModel` (for embedding models only)

### 3. Bedrock List Policy (Optional)
Allows listing available models:
- `bedrock:ListFoundationModels`
- `bedrock:GetFoundationModel`

### 4. CloudWatch Logs Policy (Optional)
Allows writing logs:
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`
- `logs:DescribeLogStreams`

## Security Best Practices

1. **Least Privilege**: Only grant access to specific models needed
2. **Separate Policies**: Use individual policies for fine-grained control
3. **No Wildcards**: Avoid using `*` in resource ARNs
4. **Regular Audits**: Review and update allowed models periodically
5. **CloudTrail**: Enable CloudTrail to monitor Bedrock API calls

## Example: Attach to Existing Role

```hcl
module "bedrock_iam" {
  source = "./modules/bedrock-iam"
  
  project_name    = "skillforge-ai"
  create_task_role = false  # Don't create role
}

resource "aws_iam_role_policy_attachment" "attach_bedrock" {
  role       = aws_iam_role.my_existing_role.name
  policy_arn = module.bedrock_iam.bedrock_invoke_policy_arn
}
```

## Supported Bedrock Models

### Text Generation Models
- `anthropic.claude-v2`
- `anthropic.claude-v2:1`
- `anthropic.claude-instant-v1`
- `meta.llama2-13b-chat-v1`
- `meta.llama2-70b-chat-v1`

### Embedding Models
- `amazon.titan-embed-text-v1`
- `amazon.titan-embed-text-v2:0`

## Cost Considerations

- IAM policies and roles are free
- Bedrock charges are based on:
  - Input tokens processed
  - Output tokens generated
  - Embedding dimensions

## Troubleshooting

### Access Denied Errors

1. Verify Bedrock is enabled in your region
2. Check model ARNs are correct
3. Ensure role is attached to ECS task
4. Review CloudTrail logs for detailed error

### Model Not Available

1. Check model availability in your region
2. Request access in Bedrock console
3. Verify model ARN format

## References

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Bedrock Model IDs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)
