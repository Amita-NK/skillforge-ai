# SkillForge AI+ Terraform Modules & Configurations Guide

## Overview

This guide covers the additional Terraform configurations and modules created for flexible, environment-specific, and cost-optimized deployments of SkillForge AI+.

## 📁 Directory Structure

```
terraform/
├── main.tf                          # Provider configuration
├── variables.tf                     # Input variables
├── vpc.tf                           # VPC and networking
├── security_groups.tf               # Security groups
├── ecs.tf                           # ECS cluster and services
├── iam.tf                           # IAM roles and policies
├── outputs.tf                       # Output values
├── terraform.tfvars.example         # Example configuration
├── README.md                        # Main documentation
├── DEPLOYMENT.md                    # Deployment guide
│
├── environments/                    # Environment-specific configs
│   ├── README.md                    # Environment guide
│   ├── dev/
│   │   └── terraform.tfvars         # Development config
│   ├── prod/
│   │   └── terraform.tfvars         # Production config
│   └── cost-optimized/
│       └── terraform.tfvars         # Cost-optimized config
│
└── modules/                         # Reusable modules
    ├── bedrock-iam/                 # Bedrock IAM policies
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── README.md
    └── ecs-autoscaling/             # ECS auto-scaling
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── README.md
```

## 🌍 Environment Configurations

### 1. Development Environment

**File**: `terraform/environments/dev/terraform.tfvars`

**Characteristics**:
- **Cost**: ~$305/month
- **Purpose**: Development and testing
- **Configuration**:
  - 1 task per service
  - Smaller instances (0.5-1 vCPU)
  - 2 availability zones
  - db.t3.micro RDS
  - Single OpenSearch node
  - 3-day log retention
  - Fargate Spot enabled

**Deploy**:
```bash
cd terraform
terraform workspace new dev
terraform apply -var-file=environments/dev/terraform.tfvars
```

### 2. Production Environment

**File**: `terraform/environments/prod/terraform.tfvars`

**Characteristics**:
- **Cost**: ~$600-800/month
- **Purpose**: Production workloads
- **Configuration**:
  - 3 tasks per service
  - Production instances (1-2 vCPU)
  - 3 availability zones
  - db.r5.large RDS Multi-AZ
  - 3-node OpenSearch cluster
  - 30-day log retention
  - Auto-scaling enabled
  - Enhanced monitoring
  - Deletion protection

**Deploy**:
```bash
cd terraform
terraform workspace new prod
terraform apply -var-file=environments/prod/terraform.tfvars
```

### 3. Cost-Optimized Environment

**File**: `terraform/environments/cost-optimized/terraform.tfvars`

**Characteristics**:
- **Cost**: ~$150-180/month (50% savings!)
- **Purpose**: Minimal cost deployment
- **Configuration**:
  - 1 task per service
  - Smallest instances (0.25-0.5 vCPU)
  - Single availability zone
  - db.t3.micro RDS
  - Single OpenSearch node
  - 1-day log retention
  - Fargate Spot enabled
  - No CloudFront
  - Cheaper Bedrock models (Claude Instant)

**Deploy**:
```bash
cd terraform
terraform workspace new cost-optimized
terraform apply -var-file=environments/cost-optimized/terraform.tfvars
```

## 🔐 Bedrock IAM Module

**Location**: `terraform/modules/bedrock-iam/`

### Features

- **Least-privilege IAM policies** for Bedrock access
- **Separate policies** for model invocation, embeddings, and listing
- **Pre-configured ECS task role** with Bedrock permissions
- **CloudWatch Logs integration**
- **Customizable model ARNs**

### Usage

```hcl
module "bedrock_iam" {
  source = "./modules/bedrock-iam"
  
  project_name = "skillforge-ai"
  aws_region   = "us-east-1"
  
  allowed_model_arns = [
    "arn:aws:bedrock:*::foundation-model/anthropic.claude-v2",
    "arn:aws:bedrock:*::foundation-model/anthropic.claude-instant-v1"
  ]
  
  embedding_model_arns = [
    "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1"
  ]
  
  enable_model_listing = true
  create_task_role     = true
  
  tags = {
    Environment = "production"
  }
}
```

### Outputs

- `bedrock_invoke_policy_arn` - Policy for model invocation
- `bedrock_embeddings_policy_arn` - Policy for embeddings
- `bedrock_task_role_arn` - ECS task role ARN
- `policy_arns` - Map of all policy ARNs

### Security Best Practices

1. Only grant access to specific models needed
2. Use separate policies for fine-grained control
3. Avoid wildcards in resource ARNs
4. Enable CloudTrail to monitor Bedrock API calls
5. Regularly review and update allowed models

## 📈 ECS Auto Scaling Module

**Location**: `terraform/modules/ecs-autoscaling/`

### Features

- **CPU-based scaling** - Scale on CPU utilization
- **Memory-based scaling** - Scale on memory utilization
- **Request count scaling** - Scale on ALB requests per target
- **Step scaling** - Granular scaling with multiple thresholds
- **Scheduled scaling** - Predictable scaling for known patterns
- **CloudWatch dashboard** - Visual monitoring

### Usage

#### Basic CPU and Memory Scaling

```hcl
module "backend_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = "skillforge-ai-cluster"
  service_name = "skillforge-ai-backend"
  
  min_capacity = 2
  max_capacity = 10
  
  cpu_target_value    = 70
  memory_target_value = 80
  
  scale_in_cooldown  = 300
  scale_out_cooldown = 60
}
```

#### With Request Count Scaling

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
  alb_resource_label           = "app/skillforge-alb/abc/targetgroup/backend-tg/def"
}
```

#### With Scheduled Scaling

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

#### Cost-Optimized Configuration

```hcl
module "ai_service_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = "skillforge-ai-cluster"
  service_name = "skillforge-ai-ai-service"
  
  min_capacity = 1
  max_capacity = 3
  
  cpu_target_value    = 80  # Higher threshold
  memory_target_value = 85  # Higher threshold
  
  scale_in_cooldown  = 600  # Longer cooldown
  scale_out_cooldown = 120
}
```

### Scaling Strategies

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| **Target Tracking** | Gradual traffic changes | Simple, automatic | Slower reaction |
| **Step Scaling** | Sudden traffic spikes | Fast, granular | Complex config |
| **Scheduled** | Predictable patterns | Cost-effective | Not adaptive |

### Outputs

- `autoscaling_target_id` - Auto Scaling target ID
- `cpu_scaling_policy_arn` - CPU policy ARN
- `memory_scaling_policy_arn` - Memory policy ARN
- `dashboard_name` - CloudWatch dashboard name

## 💰 Cost Comparison

| Environment | Monthly Cost | Use Case | Savings |
|-------------|--------------|----------|---------|
| **Cost-Optimized** | ~$160 | POC, demos, learning | 80% vs prod |
| **Development** | ~$305 | Dev, testing, CI/CD | 60% vs prod |
| **Production** | ~$790 | Live traffic, HA | Baseline |

### Cost Breakdown (Cost-Optimized)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| ECS Fargate Spot | 2 tasks (0.25-0.5 vCPU) | $15-20 |
| RDS MySQL | db.t3.micro, Single AZ | $15 |
| OpenSearch | t3.small, 1 node | $40 |
| NAT Gateway | 1 gateway | $32 |
| ALB | Standard | $20 |
| S3 + Logs | Minimal | $7 |
| Bedrock | Usage-based | $20-30 |
| **Total** | | **~$160** |

## 🚀 Quick Start Guide

### 1. Choose Your Environment

```bash
# For development
ENVIRONMENT="dev"

# For production
ENVIRONMENT="prod"

# For cost-optimized
ENVIRONMENT="cost-optimized"
```

### 2. Create Secrets

```bash
aws secretsmanager create-secret \
  --name skillforge/$ENVIRONMENT/db-password \
  --secret-string "$(openssl rand -base64 32)"

aws secretsmanager create-secret \
  --name skillforge/$ENVIRONMENT/jwt-secret \
  --secret-string "$(openssl rand -base64 64)"
```

### 3. Update Configuration

Edit `terraform/environments/$ENVIRONMENT/terraform.tfvars`:
- Update secret ARNs
- Adjust instance sizes if needed
- Set your AWS account ID

### 4. Deploy

```bash
cd terraform

# Initialize
terraform init

# Create workspace
terraform workspace new $ENVIRONMENT

# Deploy
terraform apply -var-file=environments/$ENVIRONMENT/terraform.tfvars
```

### 5. Verify

```bash
# Check resources
terraform output

# Test backend
curl http://$(terraform output -raw alb_dns_name)/actuator/health
```

## 🔧 Using Modules in Your Configuration

### Integrate Bedrock IAM Module

Add to your `main.tf`:

```hcl
module "bedrock_iam" {
  source = "./modules/bedrock-iam"
  
  project_name = var.project_name
  aws_region   = var.aws_region
  
  tags = var.tags
}

# Use the task role in ECS task definition
resource "aws_ecs_task_definition" "ai_service" {
  # ... other configuration ...
  task_role_arn = module.bedrock_iam.bedrock_task_role_arn
}
```

### Integrate Auto Scaling Module

Add to your `main.tf`:

```hcl
module "backend_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = aws_ecs_cluster.main.name
  service_name = aws_ecs_service.backend.name
  
  min_capacity = var.backend_min_capacity
  max_capacity = var.backend_max_capacity
  
  cpu_target_value    = var.autoscaling_target_cpu
  memory_target_value = var.autoscaling_target_memory
  
  tags = var.tags
}

module "ai_service_autoscaling" {
  source = "./modules/ecs-autoscaling"
  
  cluster_name = aws_ecs_cluster.main.name
  service_name = aws_ecs_service.ai_service.name
  
  min_capacity = var.ai_service_min_capacity
  max_capacity = var.ai_service_max_capacity
  
  cpu_target_value    = var.autoscaling_target_cpu
  memory_target_value = var.autoscaling_target_memory
  
  tags = var.tags
}
```

## 📊 Monitoring and Optimization

### View Auto Scaling Activity

```bash
aws application-autoscaling describe-scaling-activities \
  --service-namespace ecs \
  --resource-id service/skillforge-ai-cluster/skillforge-ai-backend
```

### Check Current Capacity

```bash
aws ecs describe-services \
  --cluster skillforge-ai-cluster \
  --services skillforge-ai-backend \
  --query 'services[0].[desiredCount,runningCount]'
```

### View Cost by Environment

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-08 \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=TAG,Key=Environment
```

## 🛠️ Troubleshooting

### Module Not Found

```bash
# Ensure you're in the terraform directory
cd terraform

# Re-initialize
terraform init
```

### Auto Scaling Not Working

```bash
# Check scaling policies
aws application-autoscaling describe-scaling-policies \
  --service-namespace ecs

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=skillforge-ai-backend \
  --start-time 2026-03-07T00:00:00Z \
  --end-time 2026-03-08T00:00:00Z \
  --period 300 \
  --statistics Average
```

### Bedrock Access Denied

```bash
# Verify Bedrock is enabled
aws bedrock list-foundation-models --region us-east-1

# Check IAM role permissions
aws iam get-role-policy \
  --role-name skillforge-ai-ecs-task-role \
  --policy-name skillforge-ai-bedrock-invoke-policy
```

## 📚 Additional Resources

### Documentation
- [Main Deployment Guide](PROJECT_STATUS_AND_DEPLOYMENT.md)
- [Quick Deployment Checklist](QUICK_DEPLOYMENT_CHECKLIST.md)
- [AWS Deployment Guide](AWS_DEPLOYMENT_GUIDE.md)
- [Terraform README](terraform/README.md)
- [Environment Guide](terraform/environments/README.md)

### Module Documentation
- [Bedrock IAM Module](terraform/modules/bedrock-iam/README.md)
- [ECS Auto Scaling Module](terraform/modules/ecs-autoscaling/README.md)

### AWS Documentation
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)
- [ECS Auto Scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html)
- [Application Auto Scaling](https://docs.aws.amazon.com/autoscaling/application/userguide/)

## 🎯 Best Practices

1. **Start Small**: Begin with cost-optimized or dev environment
2. **Test Thoroughly**: Test in dev before deploying to prod
3. **Monitor Costs**: Set up AWS Budgets and Cost Anomaly Detection
4. **Use Workspaces**: Isolate state for each environment
5. **Tag Everything**: Consistent tagging for cost tracking
6. **Enable Auto Scaling**: Let services scale with demand
7. **Review Regularly**: Optimize based on actual usage patterns
8. **Backup State**: Use S3 backend with versioning
9. **Secure Secrets**: Never commit secrets to version control
10. **Document Changes**: Keep README files up to date

## 🎉 Summary

You now have:

✅ **3 Environment Configurations**
- Development (~$305/month)
- Production (~$790/month)
- Cost-Optimized (~$160/month)

✅ **2 Reusable Modules**
- Bedrock IAM (security)
- ECS Auto Scaling (performance)

✅ **Complete Documentation**
- Environment guides
- Module documentation
- Deployment instructions
- Troubleshooting tips

✅ **Cost Savings**
- Up to 80% savings with cost-optimized
- Flexible scaling options
- Usage-based optimization

**Ready to deploy!** Choose your environment and follow the Quick Start Guide above.
