# SkillForge AI+ Architecture

The system must follow a microservice architecture.

---

# System Overview

Frontend:

React

Backend:

Spring Boot

AI Service:

Python FastAPI

AI Models:

Amazon Bedrock

---

# Architecture Diagram

React Frontend  
↓  
CloudFront CDN  
↓  
API Gateway  
↓  
Spring Boot Backend  
↓  
AI Microservice  
↓  
Amazon Bedrock  

Supporting Services:

Amazon RDS  
Amazon OpenSearch  
Amazon S3  

---

# AI Microservice

Create directory:

ai_service/

Files:

main.py  
tutor.py  
quiz.py  
debugger.py  
rag.py  

This service communicates with Bedrock.

---

# Data Layer

Database:

Amazon RDS MySQL

Tables:

users  
user_progress  
quiz_history  

---

# Vector Database

Use Amazon OpenSearch for embeddings.

---

# Infrastructure

Frontend hosting → S3 + CloudFront  
Backend → ECS Fargate  
AI Service → ECS Fargate  
Database → RDS  

---

# Communication

Frontend → Backend REST APIs  
Backend → AI Service HTTP  
AI Service → Bedrock API