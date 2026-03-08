# SkillForge AI+ Quick Deployment Checklist

**Use this checklist to deploy SkillForge AI+ to AWS in ~2-3 hours**

---

## ✅ Pre-Deployment Checklist

- [ ] AWS Account with administrator access
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Terraform >= 1.0 installed
- [ ] Docker installed
- [ ] Node.js >= 18 installed
- [ ] Python >= 3.11 installed
- [ ] Bedrock access enabled in AWS Console

---

## 📋 Deployment Steps

### Phase 1: AWS Setup (15 minutes)

- [ ] **Enable Bedrock**
  ```bash
  aws bedrock list-foundation-models --region us-east-1
  ```

- [ ] **Create Secrets**
  ```bash
  aws secretsmanager create-secret --name skillforge/db-password --secret-string "$(openssl rand -base64 32)"
  aws secretsmanager create-secret --name skillforge/jwt-secret --secret-string "$(openssl rand -base64 64)"
  ```

- [ ] **Save Secret ARNs**
  ```bash
  aws secretsmanager describe-secret --secret-id skillforge/db-password --query ARN
  aws secretsmanager describe-secret --secret-id skillforge/jwt-secret --query ARN
  ```

### Phase 2: Infrastructure (30 minutes)

- [ ] **Configure Terraform**
  ```bash
  cd terraform
  cp terraform.tfvars.example terraform.tfvars
  nano terraform.tfvars  # Edit with your values
  ```

- [ ] **Deploy Infrastructure**
  ```bash
  terraform init
  terraform plan
  terraform apply  # Type 'yes'
  ```

- [ ] **Save Outputs**
  ```bash
  terraform output -json > ../terraform-outputs.json
  ```

### Phase 3: Docker Images (20 minutes)

- [ ] **Login to ECR**
  ```bash
  aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
  ```

- [ ] **Build and Push Backend**
  ```bash
  cd ../backend
  docker build -t skillforge-backend .
  docker tag skillforge-backend:latest <ecr-url>/skillforge-backend:latest
  docker push <ecr-url>/skillforge-backend:latest
  ```

- [ ] **Build and Push AI Service**
  ```bash
  cd ../ai_service
  docker build -t skillforge-ai-service .
  docker tag skillforge-ai-service:latest <ecr-url>/skillforge-ai-service:latest
  docker push <ecr-url>/skillforge-ai-service:latest
  ```

### Phase 4: Deploy Services (15 minutes)

- [ ] **Deploy ECS Services**
  ```bash
  aws ecs update-service --cluster <cluster-name> --service <backend-service> --force-new-deployment
  aws ecs update-service --cluster <cluster-name> --service <ai-service> --force-new-deployment
  ```

- [ ] **Wait for Stability**
  ```bash
  aws ecs wait services-stable --cluster <cluster-name> --services <backend-service> <ai-service>
  ```

### Phase 5: Frontend (10 minutes)

- [ ] **Build Frontend**
  ```bash
  cd ../src/web
  npm install
  npm run build
  ```

- [ ] **Deploy to S3**
  ```bash
  aws s3 sync out/ s3://<bucket-name>/ --delete
  aws cloudfront create-invalidation --distribution-id <dist-id> --paths "/*"
  ```

### Phase 6: Verification (10 minutes)

- [ ] **Test Backend Health**
  ```bash
  curl http://<alb-dns>/actuator/health
  ```
  Expected: `{"status":"UP"}`

- [ ] **Test Frontend**
  ```bash
  echo "https://<cloudfront-url>"
  ```
  Open in browser and verify it loads

- [ ] **Test AI Features**
  - Log in to the platform
  - Try AI Tutor with a topic
  - Generate a quiz
  - Test code debugger

### Phase 7: Post-Deployment (30 minutes)

- [ ] **Configure Auto Scaling**
  ```bash
  aws application-autoscaling register-scalable-target --service-namespace ecs --resource-id service/<cluster>/<service> --scalable-dimension ecs:service:DesiredCount --min-capacity 2 --max-capacity 10
  ```

- [ ] **Set Up Alarms**
  ```bash
  aws cloudwatch put-metric-alarm --alarm-name skillforge-backend-high-cpu --metric-name CPUUtilization --namespace AWS/ECS --threshold 80
  ```

- [ ] **Enable Backups**
  ```bash
  aws s3api put-bucket-versioning --bucket <docs-bucket> --versioning-configuration Status=Enabled
  ```

- [ ] **Review Logs**
  ```bash
  aws logs tail /ecs/skillforge-ai-backend --follow
  aws logs tail /ecs/skillforge-ai-ai-service --follow
  ```

---

## 🎯 Success Criteria

Your deployment is complete when all these are true:

- [ ] Terraform apply completed without errors
- [ ] All ECS services show "RUNNING" status
- [ ] Backend health endpoint returns 200 OK
- [ ] Frontend loads in browser
- [ ] Users can log in
- [ ] AI Tutor generates explanations
- [ ] Quiz generation works
- [ ] Code debugger analyzes code
- [ ] No critical errors in CloudWatch logs
- [ ] All ALB targets are healthy

---

## 💰 Expected Costs

**Development**: ~$305/month  
**Production**: ~$600-800/month

---

## 🆘 Quick Troubleshooting

### Services Won't Start
```bash
aws logs tail /ecs/skillforge-ai-backend --follow
aws ecs describe-tasks --cluster <cluster> --tasks <task-id>
```

### Health Checks Failing
```bash
curl http://<alb-dns>/actuator/health
aws elbv2 describe-target-health --target-group-arn <tg-arn>
```

### Bedrock Access Denied
```bash
aws bedrock list-foundation-models --region us-east-1
# If fails, enable in AWS Console: https://console.aws.amazon.com/bedrock/
```

### High Costs
```bash
aws ce get-cost-and-usage --time-period Start=2026-03-01,End=2026-03-08 --granularity DAILY --metrics BlendedCost
```

---

## 📚 Full Documentation

For detailed information, see:
- **PROJECT_STATUS_AND_DEPLOYMENT.md** - Complete deployment guide
- **AWS_DEPLOYMENT_GUIDE.md** - AWS-specific instructions
- **terraform/README.md** - Infrastructure documentation
- **.kiro/specs/skillforge-ai-extension/** - Requirements and design

---

## 🎉 You're Done!

Once all checkboxes are complete, your SkillForge AI+ platform is live on AWS!

**Total Time**: ~2-3 hours  
**Monthly Cost**: ~$305 (dev) or ~$600-800 (prod)

**Next Steps**:
1. Configure custom domain
2. Set up CI/CD with GitHub Actions
3. Implement monitoring dashboards
4. Configure backup strategy
5. Review security settings
