# SkillForge AI+ AWS Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the SkillForge AI+ platform to AWS. The platform uses a microservice architecture with the following components:

- **Frontend**: Next.js application served via CloudFront CDN
- **Backend**: Spring Boot API on ECS Fargate
- **AI Service**: Python FastAPI service on ECS Fargate
- **Database**: RDS MySQL
- **Vector Store**: Amazon OpenSearch
- **AI Models**: Amazon Bedrock (Claude, Titan)
- **Storage**: S3 for documents and static assets

## Architecture

```
Internet → CloudFront → S3 (Frontend)
Internet → ALB → Backend (ECS) → AI Service (ECS) → Bedrock
                    ↓                    ↓
                  RDS MySQL         OpenSearch
```

## Prerequisites

Before starting the deployment, ensure you have:

1. **AWS Account** with administrator access
2. **AWS CLI** installed and configured (`aws configure`)
3. **Terraform** >= 1.0 installed
4. **Docker** installed for building images
5. **Node.js** >= 18 for frontend build
6. **Python** >= 3.11 for AI service
7. **Java** >= 17 for backend

## Cost Estimate

Approximate monthly costs for a development environment:

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| ECS Fargate | 2 tasks (Backend) + 2 tasks (AI Service) | ~$100 |
| RDS MySQL | db.t3.medium | ~$60 |
| OpenSearch | t3.small.search (2 nodes) | ~$80 |
| NAT Gateway | 1 gateway + data transfer | ~$35 |
| ALB | Application Load Balancer | ~$20 |
| S3 + CloudFront | Storage + CDN | ~$10 |
| **Total** | | **~$305/month** |

Production costs will be higher with auto-scaling, larger instances, and increased traffic.

## Deployment Steps

### Phase 1: AWS Account Setup

#### 1.1 Enable Required AWS Services

```bash
# Enable Bedrock in your region
aws bedrock list-foundation-models --region us-east-1

# If you get an error, request access via AWS Console:
# https://console.aws.amazon.com/bedrock/
```

#### 1.2 Create IAM User for Deployment

```bash
# Create deployment user
aws iam create-user --user-name skillforge-deployer

# Attach required policies
aws iam attach-user-policy \
  --user-name skillforge-deployer \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create access keys
aws iam create-access-key --user-name skillforge-deployer
```

Save the access key ID and secret access key for later use.

### Phase 2: Infrastructure Deployment

#### 2.1 Clone Repository and Navigate to Terraform

```bash
cd terraform
```

#### 2.2 Create Secrets in AWS Secrets Manager

```bash
# Database credentials
aws secretsmanager create-secret \
  --name skillforge/db-password \
  --description "RDS MySQL password" \
  --secret-string "$(openssl rand -base64 32)"

# JWT secret
aws secretsmanager create-secret \
  --name skillforge/jwt-secret \
  --description "JWT signing secret" \
  --secret-string "$(openssl rand -base64 64)"

# Get the ARNs (you'll need these)
aws secretsmanager describe-secret --secret-id skillforge/db-password --query ARN
aws secretsmanager describe-secret --secret-id skillforge/jwt-secret --query ARN
```

#### 2.3 Configure Terraform Variables

Create `terraform/terraform.tfvars`:

```hcl
# AWS Configuration
aws_region   = "us-east-1"
environment  = "production"
project_name = "skillforge-ai"

# Network Configuration
vpc_cidr             = "10.0.0.0/16"
availability_zones   = ["us-east-1a", "us-east-1b"]
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]
database_subnet_cidrs = ["10.0.20.0/24", "10.0.21.0/24"]

# ECS Configuration
backend_desired_count    = 2
ai_service_desired_count = 2

# Database Configuration
db_instance_class = "db.t3.medium"
db_name          = "skillforge"
db_username      = "admin"

# OpenSearch Configuration
opensearch_instance_type  = "t3.small.search"
opensearch_instance_count = 2

# Bedrock Configuration
bedrock_model_id = "anthropic.claude-v2"

# Secrets Manager ARNs (from step 2.2)
db_password_secret_arn = "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:skillforge/db-password-XXXXX"
jwt_secret_arn         = "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:skillforge/jwt-secret-XXXXX"
```

#### 2.4 Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

This will create:
- VPC with public, private, and database subnets
- Security groups for all services
- RDS MySQL database
- OpenSearch domain
- S3 buckets for frontend and documents
- CloudFront distribution
- ECR repositories
- ECS cluster
- IAM roles and policies

**Note**: This will take approximately 20-30 minutes.

#### 2.5 Save Terraform Outputs

```bash
# Save all outputs to a file
terraform output -json > ../terraform-outputs.json

# View specific outputs
terraform output alb_dns_name
terraform output rds_endpoint
terraform output opensearch_endpoint
terraform output ecr_backend_repository_url
terraform output ecr_ai_service_repository_url
terraform output s3_frontend_bucket_name
terraform output cloudfront_distribution_id
```

### Phase 3: Build and Push Docker Images

#### 3.1 Login to ECR

```bash
# Get ECR login command
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(terraform output -raw ecr_backend_repository_url | cut -d'/' -f1)
```

#### 3.2 Build and Push Backend Image

```bash
cd ../backend

# Build the image
docker build -t skillforge-backend .

# Tag the image
docker tag skillforge-backend:latest $(terraform output -raw ecr_backend_repository_url):latest

# Push to ECR
docker push $(terraform output -raw ecr_backend_repository_url):latest
```

#### 3.3 Build and Push AI Service Image

```bash
cd ../ai_service

# Build the image
docker build -t skillforge-ai-service .

# Tag the image
docker tag skillforge-ai-service:latest $(terraform output -raw ecr_ai_service_repository_url):latest

# Push to ECR
docker push $(terraform output -raw ecr_ai_service_repository_url):latest
```

### Phase 4: Deploy ECS Services

#### 4.1 Update ECS Task Definitions

The task definitions are already created by Terraform, but we need to force a deployment with the new images:

```bash
# Update backend service
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw backend_service_name) \
  --force-new-deployment

# Update AI service
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw ai_service_name) \
  --force-new-deployment
```

#### 4.2 Monitor Deployment

```bash
# Watch backend service
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw backend_service_name) \
  --query 'services[0].deployments'

# Watch AI service
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw ai_service_name) \
  --query 'services[0].deployments'

# View logs
aws logs tail /ecs/skillforge-ai-backend --follow
aws logs tail /ecs/skillforge-ai-ai-service --follow
```

### Phase 5: Deploy Frontend

#### 5.1 Build Frontend

```bash
cd ../src/web

# Install dependencies
npm install

# Build for production
npm run build
```

#### 5.2 Deploy to S3

```bash
# Sync build to S3
aws s3 sync out/ s3://$(terraform output -raw s3_frontend_bucket_name)/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id $(terraform output -raw cloudfront_distribution_id) \
  --paths "/*"
```

### Phase 6: Database Initialization

#### 6.1 Connect to RDS

```bash
# Get RDS endpoint
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Get database password
DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id skillforge/db-password \
  --query SecretString \
  --output text)

# Connect via MySQL client (from a machine with access)
mysql -h $RDS_ENDPOINT -u admin -p skillforge
```

#### 6.2 Run Migrations

The Spring Boot backend will automatically run migrations on startup using Flyway/Liquibase. Verify by checking the logs:

```bash
aws logs tail /ecs/skillforge-ai-backend --follow | grep -i migration
```

### Phase 7: Verification and Testing

#### 7.1 Test Backend Health

```bash
ALB_DNS=$(terraform output -raw alb_dns_name)

# Test health endpoint
curl http://$ALB_DNS/actuator/health

# Expected response:
# {"status":"UP"}
```

#### 7.2 Test Frontend

```bash
CLOUDFRONT_URL=$(terraform output -raw cloudfront_distribution_url)

# Open in browser
echo "Frontend URL: https://$CLOUDFRONT_URL"
```

#### 7.3 Test AI Service (via Backend)

```bash
# Test explanation endpoint
curl -X POST http://$ALB_DNS/ai/explain \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"topic": "binary search"}'
```

#### 7.4 Test RAG Pipeline

```bash
# Upload a test document
curl -X POST http://$ALB_DNS/ai/rag/upload \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "content": "Python is a high-level programming language...",
    "metadata": {"source": "test-doc", "topic": "python"}
  }'

# Search for context
curl -X POST http://$ALB_DNS/ai/rag/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"query": "What is Python?", "top_k": 3}'
```

### Phase 8: Configure Custom Domain (Optional)

#### 8.1 Create Route 53 Hosted Zone

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name skillforge.example.com \
  --caller-reference $(date +%s)
```

#### 8.2 Request SSL Certificate

```bash
# Request certificate
aws acm request-certificate \
  --domain-name skillforge.example.com \
  --subject-alternative-names "*.skillforge.example.com" \
  --validation-method DNS \
  --region us-east-1
```

#### 8.3 Update CloudFront and ALB

Update your Terraform configuration to use the custom domain and certificate, then apply:

```bash
terraform apply
```

### Phase 9: Set Up Monitoring and Alerts

#### 9.1 Create CloudWatch Dashboard

```bash
aws cloudwatch put-dashboard \
  --dashboard-name SkillForge-AI \
  --dashboard-body file://cloudwatch-dashboard.json
```

#### 9.2 Create Alarms

```bash
# High CPU alarm for backend
aws cloudwatch put-metric-alarm \
  --alarm-name skillforge-backend-high-cpu \
  --alarm-description "Backend CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=ServiceName,Value=skillforge-ai-backend Name=ClusterName,Value=skillforge-ai-cluster

# Unhealthy targets alarm
aws cloudwatch put-metric-alarm \
  --alarm-name skillforge-unhealthy-targets \
  --alarm-description "ALB has unhealthy targets" \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 60 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 2
```

### Phase 10: Set Up CI/CD (Optional)

#### 10.1 Configure GitHub Secrets

In your GitHub repository, add the following secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_BACKEND_REPOSITORY`
- `ECR_AI_SERVICE_REPOSITORY`
- `ECS_CLUSTER_NAME`
- `ECS_BACKEND_SERVICE_NAME`
- `ECS_AI_SERVICE_NAME`
- `S3_FRONTEND_BUCKET`
- `CLOUDFRONT_DISTRIBUTION_ID`

#### 10.2 Enable GitHub Actions

The workflow file is already in `.github/workflows/deploy.yml`. Push to the main branch to trigger deployment:

```bash
git push origin main
```

## Post-Deployment Configuration

### Enable Auto Scaling

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
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

### Configure Backup

```bash
# Enable automated RDS backups (already configured in Terraform)
# Enable S3 versioning for documents bucket
aws s3api put-bucket-versioning \
  --bucket $(terraform output -raw s3_documents_bucket_name) \
  --versioning-configuration Status=Enabled
```

## Troubleshooting

### Services Won't Start

1. Check CloudWatch logs:
   ```bash
   aws logs tail /ecs/skillforge-ai-backend --follow
   aws logs tail /ecs/skillforge-ai-ai-service --follow
   ```

2. Verify secrets are accessible:
   ```bash
   aws secretsmanager get-secret-value --secret-id skillforge/db-password
   ```

3. Check security group rules:
   ```bash
   aws ec2 describe-security-groups --filters "Name=tag:Name,Values=skillforge-ai-*"
   ```

### Health Checks Failing

1. Test health endpoint from within VPC
2. Check application logs for errors
3. Verify database connectivity
4. Ensure sufficient startup time (increase `startPeriod` in task definition)

### High Costs

1. Reduce task counts for non-production environments
2. Use Fargate Spot for cost savings
3. Optimize container resource allocation
4. Review CloudWatch log retention
5. Monitor NAT Gateway data transfer

### Bedrock Access Denied

1. Verify Bedrock is enabled in your region
2. Check IAM role permissions
3. Request model access in Bedrock console

## Maintenance

### Update Services

```bash
# Build new images
docker build -t skillforge-backend:v2 ./backend
docker tag skillforge-backend:v2 $(terraform output -raw ecr_backend_repository_url):v2
docker push $(terraform output -raw ecr_backend_repository_url):v2

# Update task definition and force deployment
aws ecs update-service \
  --cluster skillforge-ai-cluster \
  --service skillforge-ai-backend \
  --force-new-deployment
```

### Scale Services

```bash
# Scale backend
aws ecs update-service \
  --cluster skillforge-ai-cluster \
  --service skillforge-ai-backend \
  --desired-count 4
```

### Backup Database

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier skillforge-ai-db \
  --db-snapshot-identifier skillforge-backup-$(date +%Y%m%d)
```

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

**Warning**: This will delete all data. Ensure you have backups before proceeding.

## Support and Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [SkillForge AI+ Design Document](.kiro/specs/skillforge-ai-extension/design.md)
- [Terraform Configuration](terraform/README.md)

## Security Best Practices

1. **Rotate Secrets Regularly**: Use AWS Secrets Manager rotation
2. **Enable MFA**: For all IAM users with console access
3. **Use VPC Endpoints**: For AWS services to avoid NAT Gateway costs
4. **Enable CloudTrail**: For audit logging
5. **Configure WAF**: For ALB and CloudFront
6. **Enable GuardDuty**: For threat detection
7. **Regular Security Scans**: Use AWS Inspector
8. **Least Privilege IAM**: Review and minimize permissions

## Next Steps

1. Set up monitoring dashboards
2. Configure alerting and notifications
3. Implement backup and disaster recovery
4. Set up staging environment
5. Configure custom domain
6. Enable HTTPS with SSL certificate
7. Implement rate limiting
8. Set up log aggregation and analysis
9. Configure cost optimization strategies
10. Document runbooks for common operations

---

**Congratulations!** Your SkillForge AI+ platform is now deployed on AWS and ready for use.
