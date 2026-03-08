# Bedrock IAM Policy Module
# Provides least-privilege IAM policies for Amazon Bedrock access

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# IAM Policy for Bedrock Model Invocation
resource "aws_iam_policy" "bedrock_invoke" {
  name        = "${var.project_name}-bedrock-invoke-policy"
  description = "Allow invocation of specific Bedrock foundation models"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockModelInvocation"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = var.allowed_model_arns
      }
    ]
  })
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-bedrock-invoke-policy"
    }
  )
}

# IAM Policy for Bedrock Embeddings
resource "aws_iam_policy" "bedrock_embeddings" {
  name        = "${var.project_name}-bedrock-embeddings-policy"
  description = "Allow generation of embeddings using Bedrock Titan"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockEmbeddingsGeneration"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = var.embedding_model_arns
      }
    ]
  })
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-bedrock-embeddings-policy"
    }
  )
}

# IAM Policy for Bedrock Model Listing (for monitoring/debugging)
resource "aws_iam_policy" "bedrock_list" {
  count = var.enable_model_listing ? 1 : 0
  
  name        = "${var.project_name}-bedrock-list-policy"
  description = "Allow listing of available Bedrock models"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockModelListing"
        Effect = "Allow"
        Action = [
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-bedrock-list-policy"
    }
  )
}

# Combined IAM Policy for full Bedrock access
resource "aws_iam_policy" "bedrock_full" {
  count = var.create_combined_policy ? 1 : 0
  
  name        = "${var.project_name}-bedrock-full-policy"
  description = "Full Bedrock access for AI service"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockModelInvocation"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = concat(var.allowed_model_arns, var.embedding_model_arns)
      },
      {
        Sid    = "BedrockModelListing"
        Effect = "Allow"
        Action = [
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-bedrock-full-policy"
    }
  )
}

# IAM Role for ECS Task with Bedrock access
resource "aws_iam_role" "bedrock_task_role" {
  count = var.create_task_role ? 1 : 0
  
  name = "${var.project_name}-bedrock-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-bedrock-task-role"
    }
  )
}

# Attach Bedrock policies to task role
resource "aws_iam_role_policy_attachment" "bedrock_invoke_attachment" {
  count = var.create_task_role ? 1 : 0
  
  role       = aws_iam_role.bedrock_task_role[0].name
  policy_arn = aws_iam_policy.bedrock_invoke.arn
}

resource "aws_iam_role_policy_attachment" "bedrock_embeddings_attachment" {
  count = var.create_task_role ? 1 : 0
  
  role       = aws_iam_role.bedrock_task_role[0].name
  policy_arn = aws_iam_policy.bedrock_embeddings.arn
}

resource "aws_iam_role_policy_attachment" "bedrock_list_attachment" {
  count = var.create_task_role && var.enable_model_listing ? 1 : 0
  
  role       = aws_iam_role.bedrock_task_role[0].name
  policy_arn = aws_iam_policy.bedrock_list[0].arn
}

# CloudWatch Logs policy for task role
resource "aws_iam_role_policy" "cloudwatch_logs" {
  count = var.create_task_role && var.enable_cloudwatch_logs ? 1 : 0
  
  name = "${var.project_name}-cloudwatch-logs-policy"
  role = aws_iam_role.bedrock_task_role[0].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/ecs/${var.project_name}-*"
      }
    ]
  })
}
