# Outputs for ECS Auto Scaling Module

output "autoscaling_target_id" {
  description = "ID of the Application Auto Scaling target"
  value       = aws_appautoscaling_target.ecs_target.id
}

output "cpu_scaling_policy_arn" {
  description = "ARN of the CPU-based scaling policy"
  value       = var.enable_cpu_scaling ? aws_appautoscaling_policy.cpu_scaling[0].arn : null
}

output "memory_scaling_policy_arn" {
  description = "ARN of the memory-based scaling policy"
  value       = var.enable_memory_scaling ? aws_appautoscaling_policy.memory_scaling[0].arn : null
}

output "request_count_scaling_policy_arn" {
  description = "ARN of the request count-based scaling policy"
  value       = var.enable_request_count_scaling ? aws_appautoscaling_policy.request_count_scaling[0].arn : null
}

output "step_scaling_policy_arn" {
  description = "ARN of the step scaling policy"
  value       = var.enable_step_scaling ? aws_appautoscaling_policy.step_scaling[0].arn : null
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = var.create_dashboard ? aws_cloudwatch_dashboard.autoscaling[0].dashboard_name : null
}

output "min_capacity" {
  description = "Minimum capacity configured"
  value       = var.min_capacity
}

output "max_capacity" {
  description = "Maximum capacity configured"
  value       = var.max_capacity
}

output "scaling_policies" {
  description = "Map of all scaling policy ARNs"
  value = {
    cpu           = var.enable_cpu_scaling ? aws_appautoscaling_policy.cpu_scaling[0].arn : null
    memory        = var.enable_memory_scaling ? aws_appautoscaling_policy.memory_scaling[0].arn : null
    request_count = var.enable_request_count_scaling ? aws_appautoscaling_policy.request_count_scaling[0].arn : null
    step          = var.enable_step_scaling ? aws_appautoscaling_policy.step_scaling[0].arn : null
  }
}
