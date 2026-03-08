# ECS Auto Scaling Module

Comprehensive auto-scaling module for Amazon ECS services with multiple scaling strategies.

## Features

- **CPU-based Scaling**: Scale based on average CPU utilization
- **Memory-based Scaling**: Scale based on average memory utilization
- **Request Count Scaling**: Scale based on ALB request count per target
- **Step Scaling**: Granular scaling with multiple thresholds
- **Scheduled Scaling**: Predictable scaling for known traffic patterns
- **CloudWatch Dashboard**: Visual monitoring of scaling metrics

## Usage

### Basic CPU and Memory Scaling

```hcl
module "backend_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = "skillforge-ai-cluster"
  service_name = "skillforge-ai-backend"
  
  min_capacity = 2
  max_capacity = 10
  
  cpu_target_value    = 70
  memory_target_value = 80
  
  tags = {
    Environment = "production"
  }
}
```

### With Request Count Scaling (for ALB)

```hcl
module "backend_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = "skillforge-ai-cluster"
  service_name = "skillforge-ai-backend"
  
  min_capacity = 2
  max_capacity = 10
  
  enable_request_count_scaling = true
  request_count_target_value   = 1000
  alb_target_group_arn         = aws_lb_target_group.backend.arn
  alb_resource_label           = "app/skillforge-alb/abc123/targetgroup/backend-tg/def456"
}
```

### With Step Scaling

```hcl
module "backend_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = "skillforge-ai-cluster"
  service_name = "skillforge-ai-backend"
  
  min_capacity = 2
  max_capacity = 10
  
  enable_step_scaling        = true
  step_scaling_cpu_threshold = 80
}
```

### With Scheduled Scaling

```hcl
module "backend_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = "skillforge-ai-cluster"
  service_name = "skillforge-ai-backend"
  
  min_capacity = 2
  max_capacity = 10
  
  enable_scheduled_scaling = true
  scale_up_schedule        = "cron(0 8 * * ? *)"   # 8 AM UTC
  scale_down_schedule      = "cron(0 20 * * ? *)"  # 8 PM UTC
  scheduled_min_capacity   = 5
  scheduled_max_capacity   = 15
}
```

### Cost-Optimized Configuration

```hcl
module "ai_service_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = "skillforge-ai-cluster"
  service_name = "skillforge-ai-ai-service"
  
  min_capacity = 1  # Minimal baseline
  max_capacity = 5  # Limited max
  
  cpu_target_value    = 80  # Higher threshold
  memory_target_value = 85  # Higher threshold
  
  scale_in_cooldown  = 600  # Longer cooldown to prevent flapping
  scale_out_cooldown = 120  # Moderate scale-out
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| cluster_name | Name of the ECS cluster | string | - | yes |
| service_name | Name of the ECS service | string | - | yes |
| min_capacity | Minimum number of tasks | number | 1 | no |
| max_capacity | Maximum number of tasks | number | 10 | no |
| enable_cpu_scaling | Enable CPU-based auto scaling | bool | true | no |
| cpu_target_value | Target CPU utilization percentage | number | 70 | no |
| enable_memory_scaling | Enable memory-based auto scaling | bool | true | no |
| memory_target_value | Target memory utilization percentage | number | 80 | no |
| enable_request_count_scaling | Enable request count-based scaling | bool | false | no |
| request_count_target_value | Target requests per target | number | 1000 | no |
| alb_target_group_arn | ARN of ALB target group | string | null | no |
| alb_resource_label | Resource label for ALB | string | null | no |
| scale_in_cooldown | Scale in cooldown (seconds) | number | 300 | no |
| scale_out_cooldown | Scale out cooldown (seconds) | number | 60 | no |
| enable_step_scaling | Enable step scaling policy | bool | false | no |
| step_scaling_cooldown | Step scaling cooldown | number | 60 | no |
| step_scaling_cpu_threshold | CPU threshold for step scaling | number | 80 | no |
| enable_scheduled_scaling | Enable scheduled scaling | bool | false | no |
| scale_up_schedule | Cron for scaling up | string | "cron(0 8 * * ? *)" | no |
| scale_down_schedule | Cron for scaling down | string | "cron(0 20 * * ? *)" | no |
| scheduled_min_capacity | Min capacity during scale up | number | 3 | no |
| scheduled_max_capacity | Max capacity during scale up | number | 10 | no |
| create_dashboard | Create CloudWatch dashboard | bool | true | no |
| tags | Tags for resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| autoscaling_target_id | ID of the Application Auto Scaling target |
| cpu_scaling_policy_arn | ARN of CPU-based scaling policy |
| memory_scaling_policy_arn | ARN of memory-based scaling policy |
| request_count_scaling_policy_arn | ARN of request count scaling policy |
| step_scaling_policy_arn | ARN of step scaling policy |
| dashboard_name | Name of CloudWatch dashboard |
| min_capacity | Minimum capacity configured |
| max_capacity | Maximum capacity configured |
| scaling_policies | Map of all policy ARNs |

## Scaling Strategies

### 1. Target Tracking (Recommended)
Automatically adjusts capacity to maintain target metric:
- **CPU**: Scales when average CPU crosses threshold
- **Memory**: Scales when average memory crosses threshold
- **Requests**: Scales based on requests per target

**Pros**: Simple, automatic, handles gradual changes well  
**Cons**: May not react fast enough to sudden spikes

### 2. Step Scaling
Scales in steps based on metric thresholds:
- 50% increase when CPU > 80%
- 100% increase when CPU > 90%

**Pros**: Fast reaction to sudden changes, granular control  
**Cons**: More complex to configure

### 3. Scheduled Scaling
Scales at specific times:
- Scale up before peak hours
- Scale down during off-hours

**Pros**: Predictable costs, handles known patterns  
**Cons**: Doesn't adapt to unexpected traffic

## Best Practices

1. **Start Conservative**: Begin with higher thresholds (70-80%)
2. **Monitor First**: Observe patterns before enabling aggressive scaling
3. **Use Cooldowns**: Prevent rapid scaling oscillations
4. **Combine Strategies**: Use target tracking + scheduled scaling
5. **Set Appropriate Limits**: Prevent runaway costs with max_capacity
6. **Test Scaling**: Simulate load to verify scaling behavior

## Cost Optimization

### Development Environment
```hcl
min_capacity = 1
max_capacity = 3
cpu_target_value = 80
scale_in_cooldown = 600  # Longer cooldown
```

### Production Environment
```hcl
min_capacity = 3
max_capacity = 10
cpu_target_value = 70
scale_in_cooldown = 300
scale_out_cooldown = 60
```

## Monitoring

The module creates a CloudWatch dashboard with:
- CPU and Memory utilization graphs
- Desired vs Running task count
- Scaling activity timeline

Access via: AWS Console → CloudWatch → Dashboards → `{service_name}-autoscaling`

## Troubleshooting

### Service Not Scaling

1. Check CloudWatch metrics are being published
2. Verify scaling policies are active
3. Check if at min/max capacity
4. Review cooldown periods

```bash
# Check scaling activities
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/cluster-name/service-name
```

### Scaling Too Aggressively

1. Increase target values (70 → 80)
2. Increase cooldown periods
3. Reduce max_capacity
4. Consider step scaling for more control

### Scaling Too Slowly

1. Decrease target values (80 → 70)
2. Decrease scale_out_cooldown
3. Enable step scaling for faster response
4. Check if hitting max_capacity

## Examples

See the `examples/` directory for complete configurations:
- `basic-autoscaling.tf` - Simple CPU/memory scaling
- `advanced-autoscaling.tf` - All features enabled
- `cost-optimized.tf` - Minimal cost configuration

## References

- [Application Auto Scaling](https://docs.aws.amazon.com/autoscaling/application/userguide/)
- [ECS Service Auto Scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html)
- [Target Tracking Policies](https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-target-tracking.html)
