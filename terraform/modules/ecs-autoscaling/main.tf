# ECS Auto Scaling Module
# Provides comprehensive auto-scaling policies for ECS services

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Application Auto Scaling Target
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${var.cluster_name}/${var.service_name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
  
  tags = var.tags
}

# CPU-based Auto Scaling Policy
resource "aws_appautoscaling_policy" "cpu_scaling" {
  count = var.enable_cpu_scaling ? 1 : 0
  
  name               = "${var.service_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  
  target_tracking_scaling_policy_configuration {
    target_value       = var.cpu_target_value
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
    
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

# Memory-based Auto Scaling Policy
resource "aws_appautoscaling_policy" "memory_scaling" {
  count = var.enable_memory_scaling ? 1 : 0
  
  name               = "${var.service_name}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  
  target_tracking_scaling_policy_configuration {
    target_value       = var.memory_target_value
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
    
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
  }
}

# Request Count-based Auto Scaling Policy (for services behind ALB)
resource "aws_appautoscaling_policy" "request_count_scaling" {
  count = var.enable_request_count_scaling && var.alb_target_group_arn != null ? 1 : 0
  
  name               = "${var.service_name}-request-count-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  
  target_tracking_scaling_policy_configuration {
    target_value       = var.request_count_target_value
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
    
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = var.alb_resource_label
    }
  }
}

# Step Scaling Policy (for more granular control)
resource "aws_appautoscaling_policy" "step_scaling" {
  count = var.enable_step_scaling ? 1 : 0
  
  name               = "${var.service_name}-step-scaling"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  
  step_scaling_policy_configuration {
    adjustment_type         = "PercentChangeInCapacity"
    cooldown                = var.step_scaling_cooldown
    metric_aggregation_type = "Average"
    
    # Scale out: Add 50% capacity when CPU > 80%
    step_adjustment {
      metric_interval_lower_bound = 0
      metric_interval_upper_bound = 10
      scaling_adjustment          = 50
    }
    
    # Scale out: Add 100% capacity when CPU > 90%
    step_adjustment {
      metric_interval_lower_bound = 10
      scaling_adjustment          = 100
    }
  }
}

# CloudWatch Alarm for Step Scaling (Scale Out)
resource "aws_cloudwatch_metric_alarm" "step_scaling_out" {
  count = var.enable_step_scaling ? 1 : 0
  
  alarm_name          = "${var.service_name}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = var.step_scaling_cpu_threshold
  alarm_description   = "Triggers step scaling when CPU is high"
  alarm_actions       = [aws_appautoscaling_policy.step_scaling[0].arn]
  
  dimensions = {
    ClusterName = var.cluster_name
    ServiceName = var.service_name
  }
  
  tags = var.tags
}

# Scheduled Scaling (for predictable traffic patterns)
resource "aws_appautoscaling_scheduled_action" "scale_up_morning" {
  count = var.enable_scheduled_scaling ? 1 : 0
  
  name               = "${var.service_name}-scale-up-morning"
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  schedule           = var.scale_up_schedule
  
  scalable_target_action {
    min_capacity = var.scheduled_min_capacity
    max_capacity = var.scheduled_max_capacity
  }
}

resource "aws_appautoscaling_scheduled_action" "scale_down_evening" {
  count = var.enable_scheduled_scaling ? 1 : 0
  
  name               = "${var.service_name}-scale-down-evening"
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  schedule           = var.scale_down_schedule
  
  scalable_target_action {
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
  }
}

# CloudWatch Dashboard for Auto Scaling Metrics
resource "aws_cloudwatch_dashboard" "autoscaling" {
  count = var.create_dashboard ? 1 : 0
  
  dashboard_name = "${var.service_name}-autoscaling"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", { stat = "Average", label = "CPU %" }],
            [".", "MemoryUtilization", { stat = "Average", label = "Memory %" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Service Utilization"
          dimensions = {
            ClusterName = var.cluster_name
            ServiceName = var.service_name
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ECS", "DesiredTaskCount", { stat = "Average", label = "Desired" }],
            [".", "RunningTaskCount", { stat = "Average", label = "Running" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Task Count"
          dimensions = {
            ClusterName = var.cluster_name
            ServiceName = var.service_name
          }
        }
      }
    ]
  })
}
