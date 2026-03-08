# SkillForge AI+ Deployment Guide

Complete guide for deploying SkillForge AI+ platform.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Production Checklist](#production-checklist)

---

## Local Development

### Prerequisites

- Python 3.11+
- AWS Account with Bedrock access
- OpenSearch instance (optional)

### Setup

1. **Clone repository**
```bash
git clone <repository-url>
cd skillforge-ai
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Install dependencies**
```bash
# AI Service
cd ai_service
pip install -r requirements.txt

# Backend
cd ../backend
pip install -r requirements.txt
```

4. **Run services**
```bash
# Terminal 1: AI Service
cd ai_service
python main.py

# Terminal 2: Backend
cd backend
python app.py
```

5. **Verify**
```bash
curl http://localhost:8000/health  # AI Service
curl http://localhost:5000/health  # Backend
```

---

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- AWS credentials configured

### Quick Start

1. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

2. **Build and run**
```bash
docker-compose up --build
```

3. **Verify**
```bash
curl http://localhost:8000/health  # AI Service
curl http://localhost:5000/health  # Backend
```

### Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# Remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Using MySQL Database

1. **Uncomment MySQL service in docker-compose.yml**

2. **Update .env**
```env
DATABASE_URL=mysql+pymysql://skillforge:password@db:3306/skillforge
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=skillforge
MYSQL_USER=skillforge
MYSQL_PASSWORD=password
```

3. **Restart services**
```bash
docker-compose down
docker-compose up -d
```

---

## AWS Deployment

### Architecture

```
┌─────────────┐
│ CloudFront  │ (Frontend CDN)
└──────┬──────┘
       │
┌──────▼──────┐
│     ALB     │ (Load Balancer)
└──────┬──────┘
       │
┌──────▼──────────────────┐
│      ECS Cluster        │
│  ┌────────┐  ┌────────┐│
│  │Backend │  │AI Svc  ││
│  │(Flask) │  │(FastAPI││
│  └────┬───┘  └───┬────┘│
└───────┼──────────┼─────┘
        │          │
   ┌────▼────┐ ┌──▼──────┐
   │   RDS   │ │ Bedrock │
   │ (MySQL) │ │OpenSearch│
   └─────────┘ └─────────┘
```

### Prerequisites

- AWS CLI configured
- Terraform 1.0+
- AWS account with appropriate permissions
- Domain name (optional)

### Step 1: Prepare AWS Resources

1. **Enable Bedrock**
   - Go to AWS Bedrock console
   - Request model access for Claude/Titan
   - Wait for approval (usually instant)

2. **Create OpenSearch domain** (optional)
   - Go to OpenSearch Service
   - Create domain
   - Note endpoint and credentials

3. **Create ECR repositories**
```bash
aws ecr create-repository --repository-name skillforge-ai-service
aws ecr create-repository --repository-name skillforge-backend
```

### Step 2: Build and Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag AI Service
cd ai_service
docker build -t skillforge-ai-service .
docker tag skillforge-ai-service:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillforge-ai-service:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillforge-ai-service:latest

# Build and tag Backend
cd ../backend
docker build -t skillforge-backend .
docker tag skillforge-backend:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/skillforge-backend:latest
```

### Step 3: Deploy Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Apply infrastructure
terraform apply
```

### Step 4: Configure Secrets

Store sensitive values in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name skillforge/backend/secrets \
  --secret-string '{
    "SECRET_KEY": "your-secret-key",
    "JWT_SECRET_KEY": "your-jwt-secret",
    "DATABASE_URL": "mysql+pymysql://user:pass@rds-endpoint/skillforge"
  }'

aws secretsmanager create-secret \
  --name skillforge/ai-service/secrets \
  --secret-string '{
    "AWS_ACCESS_KEY_ID": "your-key",
    "AWS_SECRET_ACCESS_KEY": "your-secret",
    "OPENSEARCH_PASSWORD": "your-password"
  }'
```

### Step 5: Deploy ECS Services

```bash
# Update ECS services with new images
aws ecs update-service \
  --cluster skillforge-cluster \
  --service skillforge-ai-service \
  --force-new-deployment

aws ecs update-service \
  --cluster skillforge-cluster \
  --service skillforge-backend \
  --force-new-deployment
```

### Step 6: Configure DNS (Optional)

1. **Create Route 53 hosted zone**
2. **Add A record pointing to ALB**
3. **Configure SSL certificate in ACM**
4. **Update ALB listener to use HTTPS**

---

## Production Checklist

### Security

- [ ] Change all default passwords and secrets
- [ ] Enable HTTPS/TLS for all services
- [ ] Configure VPC with private subnets
- [ ] Set up security groups with minimal access
- [ ] Enable AWS WAF on ALB
- [ ] Rotate credentials regularly
- [ ] Enable MFA for AWS accounts
- [ ] Use IAM roles instead of access keys where possible
- [ ] Enable CloudTrail for audit logging
- [ ] Configure CORS properly

### Database

- [ ] Use RDS Multi-AZ for high availability
- [ ] Enable automated backups
- [ ] Configure backup retention (7-30 days)
- [ ] Set up read replicas if needed
- [ ] Enable encryption at rest
- [ ] Use parameter groups for optimization
- [ ] Monitor slow queries
- [ ] Set up connection pooling

### Monitoring

- [ ] Configure CloudWatch alarms
  - CPU utilization > 80%
  - Memory utilization > 80%
  - Error rate > 1%
  - Response time > 2s
- [ ] Set up CloudWatch Logs
- [ ] Enable X-Ray tracing
- [ ] Configure SNS notifications
- [ ] Set up dashboards
- [ ] Monitor Bedrock usage and costs

### Performance

- [ ] Enable CloudFront CDN
- [ ] Configure auto-scaling policies
- [ ] Set up Application Load Balancer
- [ ] Enable ECS service auto-scaling
- [ ] Optimize Docker images (multi-stage builds)
- [ ] Configure connection pooling
- [ ] Enable caching where appropriate
- [ ] Use ElastiCache for session storage

### Reliability

- [ ] Deploy across multiple AZs
- [ ] Configure health checks
- [ ] Set up automatic failover
- [ ] Test disaster recovery procedures
- [ ] Document runbooks
- [ ] Set up automated backups
- [ ] Configure retry logic
- [ ] Implement circuit breakers

### Cost Optimization

- [ ] Use Reserved Instances for predictable workloads
- [ ] Configure auto-scaling to scale down during low usage
- [ ] Use Spot Instances for non-critical workloads
- [ ] Monitor Bedrock API costs
- [ ] Set up billing alarms
- [ ] Review and optimize resource sizes
- [ ] Use S3 lifecycle policies
- [ ] Clean up unused resources

### Compliance

- [ ] Enable encryption at rest and in transit
- [ ] Configure data retention policies
- [ ] Set up audit logging
- [ ] Document data flows
- [ ] Implement access controls
- [ ] Regular security audits
- [ ] GDPR compliance (if applicable)
- [ ] Data backup and recovery procedures

---

## Troubleshooting

### Docker Issues

**Problem**: Container fails to start
```bash
# Check logs
docker-compose logs <service-name>

# Check container status
docker ps -a

# Rebuild image
docker-compose build --no-cache <service-name>
```

**Problem**: Cannot connect to services
```bash
# Check network
docker network ls
docker network inspect skillforge-network

# Verify ports
docker-compose ps
```

### AWS Issues

**Problem**: ECS task fails to start
```bash
# Check task logs in CloudWatch
aws logs tail /ecs/skillforge-ai-service --follow

# Check task definition
aws ecs describe-task-definition --task-definition skillforge-ai-service

# Check service events
aws ecs describe-services --cluster skillforge-cluster --services skillforge-ai-service
```

**Problem**: Cannot access Bedrock
- Verify IAM role has bedrock:InvokeModel permission
- Check model is available in your region
- Verify model access is granted in Bedrock console

**Problem**: Database connection fails
- Check security group allows traffic from ECS tasks
- Verify RDS endpoint is correct
- Check database credentials in Secrets Manager
- Ensure VPC configuration allows connectivity

### Performance Issues

**Problem**: Slow response times
- Check CloudWatch metrics for CPU/memory
- Review application logs for errors
- Check database query performance
- Verify network latency
- Consider scaling up resources

**Problem**: High costs
- Review CloudWatch billing dashboard
- Check Bedrock API usage
- Verify auto-scaling policies
- Look for unused resources
- Consider Reserved Instances

---

## Maintenance

### Regular Tasks

**Daily**
- Monitor CloudWatch alarms
- Review error logs
- Check service health

**Weekly**
- Review performance metrics
- Check backup status
- Update dependencies (security patches)

**Monthly**
- Review and optimize costs
- Update documentation
- Test disaster recovery
- Security audit
- Rotate credentials

### Updating Services

1. **Build new images**
```bash
docker build -t <service>:v2 .
docker push <ecr-repo>/<service>:v2
```

2. **Update task definition**
```bash
aws ecs register-task-definition --cli-input-json file://task-def.json
```

3. **Deploy update**
```bash
aws ecs update-service \
  --cluster skillforge-cluster \
  --service <service-name> \
  --task-definition <service>:v2 \
  --force-new-deployment
```

4. **Monitor deployment**
```bash
aws ecs describe-services \
  --cluster skillforge-cluster \
  --services <service-name>
```

---

## Support

For deployment issues:
- Check CloudWatch Logs
- Review ECS service events
- Consult AWS documentation
- Contact AWS Support (if applicable)

For application issues:
- Check application logs
- Review IMPLEMENTATION_STATUS.md
- Test locally with Docker
- Check GitHub issues

---

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Docker Documentation](https://docs.docker.com/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
