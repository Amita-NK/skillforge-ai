# Terraform Environment Configurations

This directory contains environment-specific Terraform variable files for deploying SkillForge AI+ to different environments.

## Available Environments

### 1. Development (`dev/`)
**Purpose**: Development and testing  
**Cost**: ~$305/month  
**Characteristics**:
- Single instance per service
- Smaller instance sizes
- Single AZ deployment
- Short log retention (3 days)
- No auto-scaling
- Fargate Spot enabled

**Use Cases**:
- Feature development
- Integration testing
- Developer sandboxes
- CI/CD testing

### 2. Production (`prod/`)
**Purpose**: Production workloads  
**Cost**: ~$600-800/month  
**Characteristics**:
- Multiple instances (3+) per service
- Production-grade instance sizes
- Multi-AZ deployment (3 AZs)
- Long log retention (30 days)
- Auto-scaling enabled
- High availability
- Enhanced monitoring
- Automated backups

**Use Cases**:
- Live production traffic
- Customer-facing applications
- Mission-critical workloads
- High availability requirements

### 3. Cost-Optimized (`cost-optimized/`)
**Purpose**: Minimal cost deployment  
**Cost**: ~$150-180/month (50% savings)  
**Characteristics**:
- Single instance per service
- Smallest possible instance sizes
- Single AZ deployment
- Minimal log retention (1 day)
- No auto-scaling
- Fargate Spot enabled
- No CloudFront
- Cheaper Bedrock models

**Use Cases**:
- Proof of concepts
- Demos
- Learning and experimentation
- Budget-constrained projects

## Quick Start

### Deploy Development Environment

```bash
cd terraform

# Initialize Terraform
terraform init

# Create dev workspace
terraform workspace new dev

# Deploy with dev configuration
terraform apply -var-file=environments/dev/terraform.tfvars
```

### Deploy Production Environment

```bash
cd terraform

# Create prod workspace
terraform workspace new prod

# Deploy with prod configuration
terraform apply -var-file=environments/prod/terraform.tfvars
```

### Deploy Cost-Optimized Environment

```bash
cd terraform

# Create cost-optimized workspace
terraform workspace new cost-optimized

# Deploy with cost-optimized configuration
terraform apply -var-file=environments/cost-optimized/terraform.tfvars
```

## Environment Comparison

| Feature | Cost-Optimized | Development | Production |
|---------|----------------|-------------|------------|
| **Monthly Cost** | ~$160 | ~$305 | ~$790 |
| **Availability Zones** | 1 | 2 | 3 |
| **Backend Tasks** | 1 | 1 | 3 |
| **AI Service Tasks** | 1 | 1 | 3 |
| **Backend CPU/Memory** | 0.25 vCPU / 0.5 GB | 0.5 vCPU / 1 GB | 1 vCPU / 2 GB |
| **AI Service CPU/Memory** | 0.5 vCPU / 1 GB | 1 vCPU / 2 GB | 2 vCPU / 4 GB |
| **RDS Instance** | db.t3.micro | db.t3.micro | db.r5.large |
| **RDS Multi-AZ** | No | No | Yes |
| **OpenSearch Nodes** | 1 | 1 | 3 |
| **OpenSearch Instance** | t3.small | t3.small | r5.large |
| **NAT Gateways** | 1 | 1 | 3 |
| **Auto Scaling** | No | No | Yes |
| **Fargate Spot** | Yes | Yes | No |
| **Log Retention** | 1 day | 3 days | 30 days |
| **CloudFront** | No | Yes | Yes |
| **Enhanced Monitoring** | No | No | Yes |
| **Deletion Protection** | No | No | Yes |

## Configuration Files

Each environment directory contains:

- `terraform.tfvars` - Variable values for the environment
- `README.md` - Environment-specific documentation (optional)

## Customization

### Create Custom Environment

1. Copy an existing environment:
   ```bash
   cp -r environments/dev environments/staging
   ```

2. Edit `environments/staging/terraform.tfvars`:
   ```hcl
   environment = "staging"
   # Adjust other values as needed
   ```

3. Deploy:
   ```bash
   terraform workspace new staging
   terraform apply -var-file=environments/staging/terraform.tfvars
   ```

### Override Specific Values

You can override individual values at apply time:

```bash
terraform apply \
  -var-file=environments/dev/terraform.tfvars \
  -var="backend_desired_count=2" \
  -var="enable_autoscaling=true"
```

## Secrets Management

Each environment requires its own secrets in AWS Secrets Manager:

### Development
```bash
aws secretsmanager create-secret \
  --name skillforge/dev/db-password \
  --secret-string "$(openssl rand -base64 32)"

aws secretsmanager create-secret \
  --name skillforge/dev/jwt-secret \
  --secret-string "$(openssl rand -base64 64)"
```

### Production
```bash
aws secretsmanager create-secret \
  --name skillforge/prod/db-password \
  --secret-string "$(openssl rand -base64 32)"

aws secretsmanager create-secret \
  --name skillforge/prod/jwt-secret \
  --secret-string "$(openssl rand -base64 64)"
```

### Cost-Optimized
```bash
aws secretsmanager create-secret \
  --name skillforge/cost/db-password \
  --secret-string "$(openssl rand -base64 32)"

aws secretsmanager create-secret \
  --name skillforge/cost/jwt-secret \
  --secret-string "$(openssl rand -base64 64)"
```

## Workspace Management

Terraform workspaces isolate state for different environments:

```bash
# List workspaces
terraform workspace list

# Switch workspace
terraform workspace select dev

# Show current workspace
terraform workspace show

# Delete workspace (after destroying resources)
terraform workspace delete dev
```

## Cost Optimization Tips

### For Development
1. Stop services outside business hours
2. Use Fargate Spot (already enabled)
3. Reduce log retention to 1 day
4. Use smaller instance sizes

### For Production
1. Enable auto-scaling to match demand
2. Use Reserved Instances for predictable workloads
3. Implement CloudWatch alarms to detect waste
4. Review and optimize regularly

### For Cost-Optimized
1. Already optimized for minimal cost
2. Consider stopping when not in use
3. Use AWS Budgets to track spending
4. Monitor Fargate Spot interruptions

## Migration Between Environments

### Promote Dev to Prod

1. Test thoroughly in dev
2. Update prod configuration if needed
3. Build and tag Docker images:
   ```bash
   docker tag skillforge-backend:latest skillforge-backend:v1.0.0
   docker push <ecr-url>/skillforge-backend:v1.0.0
   ```
4. Update prod task definitions to use new tag
5. Deploy to prod:
   ```bash
   terraform workspace select prod
   terraform apply -var-file=environments/prod/terraform.tfvars
   ```

### Downgrade Prod to Dev

Not recommended, but if needed:
1. Backup production data
2. Export important configurations
3. Destroy prod environment
4. Deploy dev environment
5. Restore data if needed

## Monitoring

### View Environment Costs

```bash
# Get cost for specific environment
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-08 \
  --granularity DAILY \
  --metrics BlendedCost \
  --filter file://cost-filter.json

# cost-filter.json
{
  "Tags": {
    "Key": "Environment",
    "Values": ["dev"]
  }
}
```

### View Resource Usage

```bash
# ECS service metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=skillforge-ai-backend Name=ClusterName,Value=skillforge-ai-cluster \
  --start-time 2026-03-07T00:00:00Z \
  --end-time 2026-03-08T00:00:00Z \
  --period 3600 \
  --statistics Average
```

## Troubleshooting

### Environment Not Deploying

1. Check workspace:
   ```bash
   terraform workspace show
   ```

2. Verify variable file path:
   ```bash
   ls -la environments/dev/terraform.tfvars
   ```

3. Validate configuration:
   ```bash
   terraform validate
   ```

### Wrong Environment Deployed

1. Check current workspace:
   ```bash
   terraform workspace show
   ```

2. Switch to correct workspace:
   ```bash
   terraform workspace select <correct-env>
   ```

3. Verify state:
   ```bash
   terraform show
   ```

### Cost Higher Than Expected

1. Check running resources:
   ```bash
   aws ecs list-tasks --cluster skillforge-ai-cluster
   aws rds describe-db-instances
   aws es describe-elasticsearch-domains
   ```

2. Review CloudWatch metrics
3. Check for orphaned resources
4. Verify Fargate Spot is enabled

## Best Practices

1. **Always Use Workspaces**: Isolate state for each environment
2. **Tag Everything**: Use consistent tagging for cost tracking
3. **Version Control**: Commit environment configs to git
4. **Test Changes**: Test in dev before applying to prod
5. **Backup State**: Enable S3 backend with versioning
6. **Document Changes**: Update README when modifying configs
7. **Review Costs**: Monitor spending regularly
8. **Secure Secrets**: Never commit secrets to git
9. **Use Variables**: Parameterize environment-specific values
10. **Plan Before Apply**: Always review `terraform plan` output

## Security Considerations

1. **Secrets**: Store in AWS Secrets Manager, not in tfvars
2. **State Files**: Use S3 backend with encryption
3. **Access Control**: Use IAM roles with least privilege
4. **Network**: Use private subnets for services
5. **Encryption**: Enable encryption at rest for all data stores
6. **Monitoring**: Enable CloudTrail for audit logging
7. **Updates**: Keep Terraform and providers up to date

## Support

For issues or questions:
1. Check the main [terraform/README.md](../README.md)
2. Review [PROJECT_STATUS_AND_DEPLOYMENT.md](../../PROJECT_STATUS_AND_DEPLOYMENT.md)
3. Consult AWS documentation
4. Review Terraform logs: `TF_LOG=DEBUG terraform apply`

## References

- [Terraform Workspaces](https://www.terraform.io/docs/language/state/workspaces.html)
- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
