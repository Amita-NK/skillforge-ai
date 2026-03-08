# Variables for SkillForge AI+ Infrastructure

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "skillforge-ai"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for subnets"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.20.0/24", "10.0.21.0/24"]
}

# ECS Configuration
variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 2
}

variable "ai_service_desired_count" {
  description = "Desired number of AI service tasks"
  type        = number
  default     = 2
}

# ECR Repository URLs
variable "ecr_backend_repository_url" {
  description = "URL of the ECR repository for backend images"
  type        = string
  default     = ""
}

variable "ecr_ai_service_repository_url" {
  description = "URL of the ECR repository for AI service images"
  type        = string
  default     = ""
}

# Secrets Manager ARNs
variable "db_url_secret_arn" {
  description = "ARN of the secret containing database URL"
  type        = string
  default     = ""
}

variable "db_username_secret_arn" {
  description = "ARN of the secret containing database username"
  type        = string
  default     = ""
}

variable "db_password_secret_arn" {
  description = "ARN of the secret containing database password"
  type        = string
  default     = ""
}

variable "jwt_secret_arn" {
  description = "ARN of the secret containing JWT secret"
  type        = string
  default     = ""
}

# Bedrock Configuration
variable "bedrock_model_id" {
  description = "Bedrock model ID to use"
  type        = string
  default     = "anthropic.claude-v2"
}

# OpenSearch Configuration
variable "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  type        = string
  default     = ""
}

# S3 Configuration
variable "s3_documents_bucket_name" {
  description = "Name of the S3 bucket for documents"
  type        = string
  default     = ""
}
