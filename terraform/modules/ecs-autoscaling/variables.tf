# Variables for ECS Auto Scaling Module

variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "service_name" {
  description = "Name of the ECS service"
  type        = string
}

variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 10
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# CPU Scaling
variable "enable_cpu_scaling" {
  description = "Enable CPU-based auto scaling"
  type        = bool
  default     = true
}

variable "cpu_target_value" {
  description = "Target CPU utilization percentage"
  type        = number
  default     = 70
}

# Memory Scaling
variable "enable_memory_scaling" {
  description = "Enable memory-based auto scaling"
  type        = bool
  default     = true
}

variable "memory_target_value" {
  description = "Target memory utilization percentage"
  type        = number
  default     = 80
}

# Request Count Scaling
variable "enable_request_count_scaling" {
  description = "Enable request count-based auto scaling"
  type        = bool
  default     = false
}

variable "request_count_target_value" {
  description = "Target number of requests per target"
  type        = number
  default     = 1000
}

variable "alb_target_group_arn" {
  description = "ARN of the ALB target group (required for request count scaling)"
  type        = string
  default     = null
}

variable "alb_resource_label" {
  description = "Resource label for ALB target group (format: app/load-balancer-name/id/targetgroup/target-group-name/id)"
  type        = string
  default     = null
}

# Cooldown Periods
variable "scale_in_cooldown" {
  description = "Cooldown period (seconds) before allowing another scale in"
  type        = number
  default     = 300
}

variable "scale_out_cooldown" {
  description = "Cooldown period (seconds) before allowing another scale out"
  type        = number
  default     = 60
}

# Step Scaling
variable "enable_step_scaling" {
  description = "Enable step scaling policy"
  type        = bool
  default     = false
}

variable "step_scaling_cooldown" {
  description = "Cooldown period for step scaling"
  type        = number
  default     = 60
}

variable "step_scaling_cpu_threshold" {
  description = "CPU threshold for step scaling alarm"
  type        = number
  default     = 80
}

# Scheduled Scaling
variable "enable_scheduled_scaling" {
  description = "Enable scheduled scaling actions"
  type        = bool
  default     = false
}

variable "scale_up_schedule" {
  description = "Cron expression for scaling up (e.g., 'cron(0 8 * * ? *)')"
  type        = string
  default     = "cron(0 8 * * ? *)"  # 8 AM UTC
}

variable "scale_down_schedule" {
  description = "Cron expression for scaling down (e.g., 'cron(0 20 * * ? *)')"
  type        = string
  default     = "cron(0 20 * * ? *)"  # 8 PM UTC
}

variable "scheduled_min_capacity" {
  description = "Minimum capacity during scheduled scale up"
  type        = number
  default     = 3
}

variable "scheduled_max_capacity" {
  description = "Maximum capacity during scheduled scale up"
  type        = number
  default     = 10
}

# Dashboard
variable "create_dashboard" {
  description = "Create CloudWatch dashboard for auto scaling metrics"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
