# IAM Roles and Policies for ECS Tasks

# ECS Task Execution Role (for pulling images and writing logs)
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.project_name}-ecs-execution-role"
  
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
  
  tags = {
    Name        = "${var.project_name}-ecs-execution-role"
    Environment = var.environment
  }
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for accessing Secrets Manager
resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${var.project_name}-ecs-execution-secrets"
  role = aws_iam_role.ecs_execution_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "kms:Decrypt"
        ]
        Resource = [
          var.db_url_secret_arn,
          var.db_username_secret_arn,
          var.db_password_secret_arn,
          var.jwt_secret_arn
        ]
      }
    ]
  })
}

# ECS Task Role (for application permissions)
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ecs-task-role"
  
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
  
  tags = {
    Name        = "${var.project_name}-ecs-task-role"
    Environment = var.environment
  }
}

# Policy for AI Service to access Bedrock
resource "aws_iam_role_policy" "ai_service_bedrock" {
  name = "${var.project_name}-ai-service-bedrock"
  role = aws_iam_role.ecs_task_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-v2",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-v2:1",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-instant-v1",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v1",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/meta.llama2-*"
        ]
      }
    ]
  })
}

# Policy for AI Service to access S3 documents bucket
resource "aws_iam_role_policy" "ai_service_s3" {
  name = "${var.project_name}-ai-service-s3"
  role = aws_iam_role.ecs_task_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_documents_bucket_name}",
          "arn:aws:s3:::${var.s3_documents_bucket_name}/*"
        ]
      }
    ]
  })
}

# Policy for AI Service to access OpenSearch
resource "aws_iam_role_policy" "ai_service_opensearch" {
  name = "${var.project_name}-ai-service-opensearch"
  role = aws_iam_role.ecs_task_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPut",
          "es:ESHttpPost",
          "es:ESHttpDelete",
          "es:ESHttpHead"
        ]
        Resource = "arn:aws:es:${var.aws_region}:*:domain/${var.project_name}-vectors/*"
      }
    ]
  })
}

# Policy for CloudWatch Logs
resource "aws_iam_role_policy" "ecs_task_cloudwatch" {
  name = "${var.project_name}-ecs-task-cloudwatch"
  role = aws_iam_role.ecs_task_role.id
  
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
        Resource = [
          aws_cloudwatch_log_group.backend.arn,
          aws_cloudwatch_log_group.ai_service.arn,
          "${aws_cloudwatch_log_group.backend.arn}:*",
          "${aws_cloudwatch_log_group.ai_service.arn}:*"
        ]
      }
    ]
  })
}
