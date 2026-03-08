# Variables for Bedrock IAM Module

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "allowed_model_arns" {
  description = "List of Bedrock model ARNs allowed for invocation"
  type        = list(string)
  default = [
    "arn:aws:bedrock:*::foundation-model/anthropic.claude-v2",
    "arn:aws:bedrock:*::foundation-model/anthropic.claude-v2:1",
    "arn:aws:bedrock:*::foundation-model/anthropic.claude-instant-v1",
    "arn:aws:bedrock:*::foundation-model/meta.llama2-13b-chat-v1",
    "arn:aws:bedrock:*::foundation-model/meta.llama2-70b-chat-v1"
  ]
}

variable "embedding_model_arns" {
  description = "List of Bedrock embedding model ARNs"
  type        = list(string)
  default = [
    "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1",
    "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0"
  ]
}

variable "enable_model_listing" {
  description = "Enable permissions to list Bedrock models"
  type        = bool
  default     = false
}

variable "create_combined_policy" {
  description = "Create a single combined policy instead of separate policies"
  type        = bool
  default     = false
}

variable "create_task_role" {
  description = "Create an IAM role for ECS tasks with Bedrock access"
  type        = bool
  default     = true
}

variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch Logs permissions for the task role"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
