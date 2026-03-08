# SkillForge AI+ Terraform Infrastructure

This directory contains Terraform configuration files for deploying the SkillForge AI+ platform infrastructure on AWS.

## Architecture Overview

The infrastructure includes:

- **VPC**: Virtual Private Cloud with DNS support
- **Subnets**: 
  - Public subnets (2) for ALB and NAT Gateway
  - Private subnets (2) for ECS services (Backend, AI Service)
  - Database subnets (2) for RDS and OpenSearch
- **Internet Gateway**: For public subnet internet access
- **NAT Gateway**: For private subnet outbound internet access
- **Security Groups**: 
  - ALB (ports 80, 443)
  - Backend (port 8080)
  - AI Service (port 8000)
  - RDS MySQL (port 3306)
  - OpenSearch (port 443)
  - VPC Endpoints (port 443)
- **ECS Cluster**: Fargate cluster with Container Insights enabled
- **ECS Task Definitions**: Backend (1 vCPU, 2GB) and AI Service (2 vCPU, 4GB)
- **ECS Services**: Backend with ALB integration, AI Service with Service Discovery
- **Application Load Balancer**: Public-facing ALB for backend service
- **IAM Roles**: Execution role and task role with appropriate permissions
- **CloudWatch Log Groups**: Container logs for backend and AI service
- **Service Discovery**: AWS Cloud Map for internal service communication

## Prerequisites

1. **AWS Account**: Active AWS account with appropriate permissions
2. **Terraform**: Version >= 1.0 installed
3. **AWS CLI**: Configured with credentials
4. **IAM Permissions**: Ability to create VPC, subnets, security groups, etc.

## File Structure

```
terraform/
├── main.tf                    # Provider and Terraform configuration
├── variables.tf               # Input variables
├── vpc.tf                     # VPC, subnets, gateways, route tables
├── security_groups.tf         # Security groups for all services
├── ecs.tf                     # ECS cluster, task definitions, services, ALB
├── iam.tf                     # IAM roles and policies for ECS tasks
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example variable values
└── README.md                  # This file
```

## Getting Started

### 1. Configure Variables

Copy the example variables file and update with your values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` to set your desired configuration:

```hcl
aws_region   = "us-east-1"
environment  = "dev"
project_name = "skillforge-ai"

# ECS Configuration
backend_desired_count    = 2
ai_service_desired_count = 2

# ECR Repository URLs (update after creating ECR repositories)
ecr_backend_repository_url    = "123456789012.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend"
ecr_ai_service_repository_url = "123456789012.dkr.ecr.us-east-1.amazonaws.com/skillforge-ai-service"

# Secrets Manager ARNs (update after creating secrets)
db_url_secret_arn      = "arn:aws:secretsmanager:us-east-1:123456789012:secret:skillforge/db-url-xxxxx"
db_username_secret_arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:skillforge/db-username-xxxxx"
db_password_secret_arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:skillforge/db-password-xxxxx"
jwt_secret_arn         = "arn:aws:secretsmanager:us-east-1:123456789012:secret:skillforge/jwt-secret-xxxxx"

# OpenSearch and S3 (update after creating resources)
opensearch_endpoint      = "https://vpc-skillforge-vectors-xxxxx.us-east-1.es.amazonaws.com"
s3_documents_bucket_name = "skillforge-documents-dev"
```

### 2. Initialize Terraform

Initialize the Terraform working directory:

```bash
cd terraform
terraform init
```

### 3. Review the Plan

Preview the infrastructure changes:

```bash
terraform plan
```

### 4. Apply the Configuration

Create the infrastructure:

```bash
terraform apply
```

Type `yes` when prompted to confirm.

### 5. View Outputs

After successful deployment, view the outputs:

```bash
terraform output
```

## Network Architecture

### Subnet Layout

| Subnet Type | CIDR Block    | AZ         | Purpose                    |
|-------------|---------------|------------|----------------------------|
| Public 1    | 10.0.1.0/24   | us-east-1a | ALB, NAT Gateway          |
| Public 2    | 10.0.2.0/24   | us-east-1b | ALB (HA)                  |
| Private 1   | 10.0.10.0/24  | us-east-1a | ECS Services              |
| Private 2   | 10.0.11.0/24  | us-east-1b | ECS Services (HA)         |
| Database 1  | 10.0.20.0/24  | us-east-1a | RDS, OpenSearch           |
| Database 2  | 10.0.21.0/24  | us-east-1b | RDS, OpenSearch (HA)      |

### Traffic Flow

1. **Inbound Traffic**:
   - Internet → ALB (public subnet) → Backend (private subnet)
   - Backend → AI Service (private subnet)
   - Backend → RDS (database subnet)
   - AI Service → OpenSearch (database subnet)

2. **Outbound Traffic**:
   - Private subnets → NAT Gateway → Internet Gateway → Internet
   - Database subnets → No direct internet access

## ECS Architecture

### Task Definitions

**Backend Task:**
- **Family**: skillforge-ai-backend
- **CPU**: 1024 (1 vCPU)
- **Memory**: 2048 MB (2 GB)
- **Port**: 8080
- **Health Check**: /actuator/health (30s interval, 5s timeout, 3 retries, 60s start period)
- **Environment Variables**: 
  - SPRING_PROFILES_ACTIVE (from variable)
  - AI_SERVICE_URL (http://ai-service.local:8000)
- **Secrets** (from Secrets Manager):
  - SPRING_DATASOURCE_URL
  - SPRING_DATASOURCE_USERNAME
  - SPRING_DATASOURCE_PASSWORD
  - JWT_SECRET

**AI Service Task:**
- **Family**: skillforge-ai-ai-service
- **CPU**: 2048 (2 vCPU)
- **Memory**: 4096 MB (4 GB)
- **Port**: 8000
- **Health Check**: /health (30s interval, 5s timeout, 3 retries, 60s start period)
- **Environment Variables**:
  - AWS_REGION
  - BEDROCK_MODEL_ID
  - OPENSEARCH_ENDPOINT
  - S3_BUCKET_NAME
- **IAM Permissions**: Bedrock, OpenSearch, S3 access via task role

### ECS Services

**Backend Service:**
- **Launch Type**: Fargate
- **Desired Count**: 2 (configurable)
- **Network**: Private subnets, no public IP
- **Load Balancer**: Integrated with ALB target group
- **Deployment**: Rolling update (200% max, 100% min healthy)
- **Circuit Breaker**: Enabled with automatic rollback

**AI Service:**
- **Launch Type**: Fargate
- **Desired Count**: 2 (configurable)
- **Network**: Private subnets, no public IP
- **Service Discovery**: Registered as ai-service.local
- **Deployment**: Rolling update (200% max, 100% min healthy)
- **Circuit Breaker**: Enabled with automatic rollback

### Service Discovery

The AI Service uses AWS Cloud Map for service discovery:
- **Namespace**: local (private DNS namespace)
- **Service Name**: ai-service
- **DNS Name**: ai-service.local
- **Record Type**: A record with MULTIVALUE routing
- **TTL**: 10 seconds
- **Health Check**: Custom health check with failure threshold of 1

Backend services can reach the AI Service at `http://ai-service.local:8000`

### IAM Roles

**ECS Execution Role** (for ECS agent):
- Pull container images from ECR
- Write logs to CloudWatch
- Retrieve secrets from Secrets Manager
- Decrypt KMS-encrypted secrets

**ECS Task Role** (for application containers):
- **Backend**: CloudWatch Logs access
- **AI Service**: 
  - Invoke Bedrock models (Claude, Titan, Llama)
  - Access OpenSearch domain (read/write)
  - Access S3 documents bucket (read/write)
  - CloudWatch Logs access

### Load Balancer Configuration

**Application Load Balancer:**
- **Type**: Application Load Balancer
- **Scheme**: Internet-facing
- **Subnets**: Public subnets (multi-AZ)
- **Security Group**: ALB security group (ports 80, 443)
- **Deletion Protection**: Disabled (for dev/test)

**Target Group:**
- **Name**: skillforge-ai-backend-tg
- **Port**: 8080
- **Protocol**: HTTP
- **Target Type**: IP (for Fargate)
- **Health Check**:
  - Path: /actuator/health
  - Interval: 30s
  - Timeout: 5s
  - Healthy threshold: 2
  - Unhealthy threshold: 3
  - Matcher: 200
- **Deregistration Delay**: 30s

**Listener:**
- **Port**: 80 (HTTP)
- **Default Action**: Forward to backend target group
- **Note**: HTTPS (443) can be added with SSL certificate

### Monitoring and Logging

**CloudWatch Log Groups:**
- `/ecs/skillforge-ai-backend`: Backend container logs
- `/ecs/skillforge-ai-ai-service`: AI service container logs
- **Retention**: 7 days (configurable)
- **Log Driver**: awslogs

**Container Insights:**
- Enabled on ECS cluster
- Provides metrics for CPU, memory, network, and storage
- Available in CloudWatch console

**Deployment Circuit Breaker:**
- Automatically detects failed deployments
- Rolls back to previous task definition
- Prevents bad deployments from affecting service availability

### Security Group Rules

**ALB Security Group**:
- Inbound: 80 (HTTP), 443 (HTTPS) from 0.0.0.0/0
- Outbound: All traffic

**Backend Security Group**:
- Inbound: 8080 from ALB security group
- Outbound: All traffic

**AI Service Security Group**:
- Inbound: 8000 from Backend security group
- Outbound: All traffic

**RDS Security Group**:
- Inbound: 3306 from Backend security group
- Outbound: All traffic

**OpenSearch Security Group**:
- Inbound: 443 from AI Service security group
- Outbound: All traffic

## Customization

### Changing CIDR Blocks

Edit `variables.tf` or `terraform.tfvars`:

```hcl
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]
```

### Adding More Availability Zones

Update the `availability_zones` variable and add corresponding subnet CIDRs:

```hcl
availability_zones    = ["us-east-1a", "us-east-1b", "us-east-1c"]
public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs  = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
database_subnet_cidrs = ["10.0.20.0/24", "10.0.21.0/24", "10.0.22.0/24"]
```

### Changing AWS Region

Update the `aws_region` variable and ensure availability zones match:

```hcl
aws_region         = "us-west-2"
availability_zones = ["us-west-2a", "us-west-2b"]
```

## Outputs

After deployment, the following outputs are available:

**Network:**
- `vpc_id`: VPC identifier
- `public_subnet_ids`: List of public subnet IDs
- `private_subnet_ids`: List of private subnet IDs
- `database_subnet_ids`: List of database subnet IDs
- `nat_gateway_public_ip`: Public IP of NAT Gateway
- `*_security_group_id`: Security group IDs for all services

**ECS:**
- `ecs_cluster_id`, `ecs_cluster_name`, `ecs_cluster_arn`: ECS cluster identifiers
- `backend_task_definition_arn`: Backend task definition ARN
- `ai_service_task_definition_arn`: AI service task definition ARN
- `backend_service_name`: Backend ECS service name
- `ai_service_service_name`: AI service ECS service name

**Load Balancer:**
- `alb_dns_name`: DNS name of the Application Load Balancer
- `alb_arn`: ALB ARN
- `backend_target_group_arn`: Backend target group ARN

**IAM:**
- `ecs_execution_role_arn`: ECS execution role ARN
- `ecs_task_role_arn`: ECS task role ARN

**Monitoring:**
- `backend_log_group_name`: Backend CloudWatch log group
- `ai_service_log_group_name`: AI service CloudWatch log group
- `service_discovery_namespace_id`: Service discovery namespace ID

Use these outputs in subsequent Terraform configurations or CI/CD pipelines.

## Cost Considerations

The infrastructure created by this configuration has the following cost implications:

**Free Tier / No Cost:**
- VPC, Subnets, Route Tables
- Internet Gateway
- Security Groups
- Elastic IP (when attached to running NAT Gateway)

**Ongoing Costs:**
- **NAT Gateway**: ~$0.045/hour + data transfer costs (~$32/month + data)
- **ECS Fargate**: 
  - Backend: 1 vCPU, 2GB RAM × 2 tasks × $0.04048/vCPU-hour + $0.004445/GB-hour
  - AI Service: 2 vCPU, 4GB RAM × 2 tasks × $0.04048/vCPU-hour + $0.004445/GB-hour
  - Estimated: ~$150-200/month for ECS services
- **Application Load Balancer**: ~$0.0225/hour (~$16/month) + LCU charges
- **CloudWatch Logs**: $0.50/GB ingested + $0.03/GB stored

**Cost Optimization Tips**:
- Use a single NAT Gateway for dev/test environments
- Reduce ECS task counts for non-production (set desired_count = 1)
- Use Fargate Spot for non-critical workloads (up to 70% savings)
- Set appropriate CloudWatch log retention (currently 7 days)
- Monitor data transfer through NAT Gateway
- Consider VPC endpoints for AWS services to reduce NAT costs

## Cleanup

To destroy all resources created by this configuration:

```bash
terraform destroy
```

Type `yes` when prompted to confirm.

**Warning**: This will delete all networking infrastructure. Ensure no other resources depend on these resources before destroying.

## Next Steps

After deploying the VPC and ECS infrastructure:

1. ✅ VPC and networking (Task 19.1) - Complete
2. ✅ ECS cluster and task definitions (Task 19.2) - Complete
3. Deploy RDS MySQL instance (Task 19.3)
4. Deploy OpenSearch domain (Task 19.4)
5. Deploy S3 buckets and CloudFront (Task 19.5)
6. Set up ECR repositories (Task 19.6)
7. Configure CloudWatch logging (Task 19.7)
8. Build and push Docker images to ECR
9. Update terraform.tfvars with ECR URLs and resource ARNs
10. Deploy services with `terraform apply`

## Troubleshooting

### VPC and Networking Issues

**Issue: Terraform init fails**

**Solution**: Ensure AWS credentials are configured:
```bash
aws configure
```

**Issue: Insufficient permissions**

**Solution**: Ensure your IAM user/role has permissions for:
- ec2:CreateVpc, ec2:CreateSubnet, ec2:CreateSecurityGroup
- ec2:CreateInternetGateway, ec2:CreateNatGateway
- ec2:AllocateAddress, ec2:CreateRouteTable
- ecs:*, iam:*, logs:*, elasticloadbalancing:*

**Issue: CIDR block conflicts**

**Solution**: Ensure your VPC CIDR doesn't overlap with existing VPCs or on-premises networks.

### ECS Issues

**Issue: ECS service won't start**

**Solution**: 
1. Check CloudWatch logs for container errors:
   ```bash
   aws logs tail /ecs/skillforge-ai-backend --follow
   aws logs tail /ecs/skillforge-ai-ai-service --follow
   ```
2. Verify secrets are accessible in Secrets Manager
3. Ensure security groups allow required traffic
4. Check task definition environment variables

**Issue: Health checks failing**

**Solution**:
1. Verify health check endpoints are responding:
   - Backend: /actuator/health
   - AI Service: /health
2. Check container logs for application errors
3. Ensure sufficient startup time (startPeriod: 60s)
4. Verify security groups allow traffic from ALB/ECS

**Issue: Can't access backend via ALB**

**Solution**:
1. Verify ALB security group allows inbound traffic (ports 80, 443)
2. Check target group health status:
   ```bash
   aws elbv2 describe-target-health --target-group-arn <arn>
   ```
3. Ensure backend tasks are running and healthy:
   ```bash
   aws ecs describe-services --cluster skillforge-ai-cluster --services skillforge-ai-backend
   ```
4. Check ALB listener rules

**Issue: Backend can't reach AI Service**

**Solution**:
1. Verify service discovery is working:
   ```bash
   aws servicediscovery list-services
   ```
2. Check AI Service security group allows traffic from Backend
3. Verify AI Service tasks are running
4. Test DNS resolution from backend container:
   ```bash
   nslookup ai-service.local
   ```

**Issue: Tasks keep restarting**

**Solution**:
1. Check CloudWatch logs for errors
2. Verify sufficient CPU and memory allocation
3. Check for application crashes or OOM errors
4. Review task definition configuration

**Issue: Deployment fails with circuit breaker**

**Solution**:
1. Check CloudWatch logs for startup errors
2. Verify health check configuration
3. Ensure new task definition is valid
4. Check for resource constraints (CPU, memory)
5. Review recent code changes

### IAM Issues

**Issue: Tasks can't access Bedrock**

**Solution**:
1. Verify task role has Bedrock permissions
2. Check Bedrock model ARNs in IAM policy
3. Ensure Bedrock is available in your region
4. Verify AWS credentials are not hardcoded (use task role)

**Issue: Can't retrieve secrets**

**Solution**:
1. Verify execution role has secretsmanager:GetSecretValue permission
2. Check secret ARNs in task definition
3. Ensure KMS key permissions if secrets are encrypted
4. Verify secrets exist in Secrets Manager

### Monitoring Issues

**Issue: No logs in CloudWatch**

**Solution**:
1. Verify log groups exist
2. Check execution role has logs:CreateLogStream and logs:PutLogEvents permissions
3. Ensure log configuration in task definition is correct
4. Check container is actually running

**Issue: Container Insights not showing data**

**Solution**:
1. Verify Container Insights is enabled on cluster
2. Wait a few minutes for data to appear
3. Check IAM permissions for CloudWatch
4. Ensure tasks are running

## References

- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [SkillForge AI+ Design Document](../.kiro/specs/skillforge-ai-extension/design.md)
