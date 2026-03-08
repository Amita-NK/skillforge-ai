# SkillForge AI+ Deployment Guide

The system must deploy fully on AWS.

---

# AWS Services Required

Amazon S3  
Amazon CloudFront  
Amazon ECS  
Amazon ECR  
Amazon RDS  
Amazon Bedrock  
Amazon OpenSearch  

---

# Containerization

Create Dockerfiles for:

frontend  
backend  
ai-service  

Each service must be containerized.

---

# Container Registry

Push images to Amazon ECR.

---

# Deployment

Deploy containers using ECS Fargate.

Services:

skillforge-backend  
skillforge-ai-service

---

# Frontend Deployment

Build React app.

Upload build folder to S3.

Enable CloudFront CDN.

---

# Database

Create RDS MySQL instance.

---

# AI Models

Use Amazon Bedrock.

Supported models:

Claude  
Titan  
Llama

---

# Environment Variables

AWS_REGION  
BEDROCK_MODEL_ID  
DB_URL  
DB_USER  
DB_PASSWORD  

---

# Monitoring

Use CloudWatch logs.