# ECS Deployment Guide

This guide walks through deploying the SkillForge AI+ ECS infrastructure.

## Prerequisites

Before deploying the ECS infrastructure, ensure you have:

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 installed
3. **AWS CLI** configured with credentials
4. **Docker images** built and ready to push to ECR
5. **Secrets** created in AWS Secrets Manager:
   - Database URL
   - Database username
   - Database password
   - JWT secret

## Step-by-Step Deployment

### Step 1: Create Secrets in AWS Secrets Manager

Create the required secrets before deploying:

```bash
# Database URL
aws secretsmanager create-secret \
  --name skillforge/db-url \
  --description "Database connection URL" \
  --secret-string "jdbc:mysql://your-rds-endpoint:3306/skillforge"

# Database Username
aws secretsmanager create-secret \
  --name skillforge/db-username \
  --description "Database username" \
  --secret-string "admin"

# Database Password
aws secretsmanager create-secret \
  --name skillforge/db-password \
  --description "Database password" \
  --secret-string "your-secure-password"

# JWT Secret
aws secretsmanager create-secret \
  --name skillforge/jwt-secret \
  --description "JWT signing secret" \
  --secret-string "your-jwt-secret-key"
```

Note the ARNs returned by these commands - you'll need them for terraform.tfvars.

### Step 2: Create ECR Repositories

Create ECR repositories for your Docker images:

```bash
# Create backend repository
aws ecr create-repository \
  --repository-name skillforge-backend \
  --region us-east-1

# Create AI service repository
aws ecr create-repository \
  --repository-name skillforge-ai-service \
  --region us-east-1
```

Note the repository URLs - you'll need them for terraform.tfvars.

### Step 3: Build and Push Docker Images

Build and push your Docker images to ECR:

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend image
cd backend
docker build -t skillforge-backend .
docker tag skillforge-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend:latest

# Build and push AI service image
cd ../ai_service
docker build -t skillforge-ai-service .
docker tag skillforge-ai-service:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillforge-ai-service:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillforge-ai-service:latest
```

### Step 4: Configure Terraform Variables

Copy the example variables file and update with your values:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your actual values:

```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "dev"
project_name = "skillforge-ai"

# ECS Configuration
backend_desired_count    = 2
ai_service_desired_count = 2

# ECR Repository URLs (from Step 2)
ecr_backend_repository_url    = "123456789012.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend"
ecr_ai_service_repository_url = "123456789012.dkr.ecr.us-east-1.amazonaws.com/skillforge-ai-service"

# Secrets Manager ARNs (from Step 1)
db_url_secret_arn      = "arn:aws:secretsmanager:us-east-1:123456789012:secret:skillforge/db-url-xxxxx"
db_username_secret_arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:skillforge/db-username-xxxxx"
db_password_secret_arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:skillforge/db-password-xxxxx"
jwt_secret_arn         = "arn:aws:secretsmanager:us-east-1:123456789012:secret:skillforge/jwt-secret-xxxxx"

# Bedrock Configuration
bedrock_model_id = "anthropic.claude-v2"

# OpenSearch Configuration (update after creating OpenSearch domain)
opensearch_endpoint = "https://vpc-skillforge-vectors-xxxxx.us-east-1.es.amazonaws.com"

# S3 Configuration (update after creating S3 bucket)
s3_documents_bucket_name = "skillforge-documents-dev"
```

### Step 5: Initialize Terraform

Initialize the Terraform working directory:

```bash
terraform init
```

### Step 6: Review the Plan

Preview the infrastructure changes:

```bash
terraform plan
```

Review the output carefully. You should see resources being created for:
- ECS Cluster
- ECS Task Definitions (2)
- ECS Services (2)
- Application Load Balancer
- Target Group
- ALB Listener
- IAM Roles (2)
- IAM Policies (5)
- CloudWatch Log Groups (2)
- Service Discovery Namespace
- Service Discovery Service

### Step 7: Apply the Configuration

Create the infrastructure:

```bash
terraform apply
```

Type `yes` when prompted to confirm.

The deployment will take approximately 5-10 minutes. Terraform will:
1. Create the ECS cluster
2. Create IAM roles and policies
3. Create CloudWatch log groups
4. Create the Application Load Balancer
5. Create task definitions
6. Create and start ECS services
7. Register services with service discovery

### Step 8: Verify Deployment

After deployment completes, verify the services are running:

```bash
# Check ECS cluster
aws ecs describe-clusters --clusters skillforge-ai-cluster

# Check backend service
aws ecs describe-services \
  --cluster skillforge-ai-cluster \
  --services skillforge-ai-backend

# Check AI service
aws ecs describe-services \
  --cluster skillforge-ai-cluster \
  --services skillforge-ai-ai-service

# Check running tasks
aws ecs list-tasks --cluster skillforge-ai-cluster

# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn $(terraform output -raw backend_target_group_arn)
```

### Step 9: Test the Deployment

Get the ALB DNS name:

```bash
terraform output alb_dns_name
```

Test the backend health endpoint:

```bash
curl http://<alb-dns-name>/actuator/health
```

You should receive a JSON response indicating the service is healthy.

### Step 10: View Logs

Monitor container logs in CloudWatch:

```bash
# Backend logs
aws logs tail /ecs/skillforge-ai-backend --follow

# AI service logs
aws logs tail /ecs/skillforge-ai-ai-service --follow
```

## Post-Deployment Configuration

### Configure Auto Scaling (Optional)

Add auto-scaling to handle variable load:

```bash
# Register scalable target for backend
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/skillforge-ai-cluster/skillforge-ai-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/skillforge-ai-cluster/skillforge-ai-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

Example `scaling-policy.json`:

```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleInCooldown": 300,
  "ScaleOutCooldown": 60
}
```

### Configure HTTPS (Recommended for Production)

1. Request an SSL certificate in AWS Certificate Manager
2. Add HTTPS listener to the ALB:

```bash
aws elbv2 create-listener \
  --load-balancer-arn $(terraform output -raw alb_arn) \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=<your-certificate-arn> \
  --default-actions Type=forward,TargetGroupArn=$(terraform output -raw backend_target_group_arn)
```

3. Update HTTP listener to redirect to HTTPS

### Set Up CloudWatch Alarms

Create alarms for monitoring:

```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name skillforge-backend-high-cpu \
  --alarm-description "Backend CPU utilization is too high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=ServiceName,Value=skillforge-ai-backend Name=ClusterName,Value=skillforge-ai-cluster

# Unhealthy target alarm
aws cloudwatch put-metric-alarm \
  --alarm-name skillforge-backend-unhealthy-targets \
  --alarm-description "Backend has unhealthy targets" \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 60 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 2 \
  --dimensions Name=TargetGroup,Value=<target-group-name> Name=LoadBalancer,Value=<alb-name>
```

## Updating Services

### Deploy New Container Images

To deploy new versions of your services:

1. Build and push new Docker images with a new tag:

```bash
docker build -t skillforge-backend:v2 .
docker tag skillforge-backend:v2 <ecr-url>/skillforge-backend:v2
docker push <ecr-url>/skillforge-backend:v2
```

2. Update the task definition to use the new image tag
3. Force a new deployment:

```bash
aws ecs update-service \
  --cluster skillforge-ai-cluster \
  --service skillforge-ai-backend \
  --force-new-deployment
```

Or update the Terraform configuration and apply:

```bash
# Update ecr_backend_repository_url in terraform.tfvars to include :v2 tag
terraform apply
```

### Update Task Configuration

To change CPU, memory, or environment variables:

1. Update the task definition in `ecs.tf`
2. Apply the changes:

```bash
terraform apply
```

ECS will automatically perform a rolling update.

### Scale Services

To change the number of running tasks:

```bash
# Via AWS CLI
aws ecs update-service \
  --cluster skillforge-ai-cluster \
  --service skillforge-ai-backend \
  --desired-count 4

# Via Terraform
# Update backend_desired_count in terraform.tfvars
terraform apply
```

## Troubleshooting

### Services Won't Start

1. Check CloudWatch logs for errors
2. Verify secrets are accessible
3. Check security group rules
4. Ensure sufficient resources (CPU, memory)

### Health Checks Failing

1. Verify health check endpoints are responding
2. Check application logs
3. Ensure sufficient startup time
4. Test health endpoint manually from within VPC

### Can't Access via ALB

1. Check ALB security group
2. Verify target group health
3. Check listener rules
4. Ensure tasks are running

### High Costs

1. Reduce task counts for non-production
2. Use Fargate Spot
3. Optimize container resource allocation
4. Review CloudWatch log retention
5. Monitor NAT Gateway data transfer

## Rollback

If you need to rollback a deployment:

```bash
# Rollback to previous task definition
aws ecs update-service \
  --cluster skillforge-ai-cluster \
  --service skillforge-ai-backend \
  --task-definition skillforge-ai-backend:1

# Or use Terraform to revert changes
git revert <commit-hash>
terraform apply
```

## Cleanup

To destroy all ECS resources:

```bash
terraform destroy
```

**Warning**: This will delete all ECS services, tasks, and related resources. Ensure you have backups of any important data.

## Next Steps

1. Set up CI/CD pipeline for automated deployments
2. Configure custom domain with Route 53
3. Implement WAF rules for security
4. Set up X-Ray for distributed tracing
5. Configure backup and disaster recovery
6. Implement cost optimization strategies

## References

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Fargate Documentation](https://docs.aws.amazon.com/fargate/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [SkillForge AI+ Design Document](../.kiro/specs/skillforge-ai-extension/design.md)
