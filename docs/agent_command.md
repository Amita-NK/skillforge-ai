# Kiro Autonomous Development Command — SkillForge AI+

You are an autonomous software engineering agent tasked with transforming this repository into a fully functional AI-powered adaptive learning platform.

Before generating any code, you must first analyze the repository and understand the existing project structure.

The repository currently contains:

* React frontend
* Spring Boot backend
* authentication system with JWT

Do not remove or break existing authentication logic.

Your task is to extend the system according to the following specification files located in the repository root:

* usecases.md
* architecture.md
* deployment.md
* prompts.md

You must read and follow these documents before making any modifications.

---

## Phase 1 — Repository Analysis

Perform a full repository scan.

Identify:

* frontend framework and structure
* backend controllers and services
* authentication implementation
* existing API endpoints
* configuration files

Produce an internal plan for extending the system while preserving current functionality.

Do not hallucinate files that do not exist.

---

## Phase 2 — System Design

Implement the architecture defined in architecture.md.

The final system must contain:

Frontend
React application with AI feature pages.

Backend
Spring Boot API with AI endpoints.

AI Microservice
Python FastAPI service responsible for interacting with Amazon Bedrock.

Data Layer
Amazon RDS MySQL database.

Vector Database
Amazon OpenSearch for knowledge retrieval.

Cloud Infrastructure
AWS services defined in deployment.md.

---

## Phase 3 — Backend Extension

Extend the Spring Boot backend.

Add a new controller:

AIController

Implement endpoints:

POST /ai/explain
POST /ai/quiz
POST /ai/debug

These endpoints must communicate with the AI microservice via HTTP.

Do not modify existing authentication routes.

---

## Phase 4 — AI Microservice Creation

Create a new service directory:

ai_service

Structure:

ai_service/
main.py
tutor.py
quiz.py
debugger.py
rag.py
embeddings.py
requirements.txt

Technology stack:

Python
FastAPI
boto3
Amazon Bedrock runtime API

The service must use prompt templates defined in prompts.md.

---

## Phase 5 — Retrieval Augmented Generation

Implement RAG pipeline.

Process:

1. upload course material to S3
2. extract text
3. split into chunks
4. generate embeddings
5. store embeddings in OpenSearch

During user queries:

search vector database
retrieve context
send context to Bedrock model
generate response.

---

## Phase 6 — Frontend Features

Add React pages:

TutorPage
QuizPage
DebuggerPage

Each page must communicate with backend APIs.

Reuse existing authentication tokens.

---

## Phase 7 — Containerization

Create Dockerfiles for:

frontend
backend
ai-service

Ensure containers can run independently.

---

## Phase 8 — AWS Deployment

Deploy the system according to deployment.md.

Infrastructure must include:

Amazon S3 for frontend hosting
Amazon CloudFront CDN
Amazon ECS Fargate for backend and AI services
Amazon ECR for container images
Amazon RDS for database
Amazon OpenSearch for vector database
Amazon Bedrock for AI models
Amazon CloudWatch for monitoring

---

## Phase 9 — Environment Configuration

Use environment variables for all secrets.

Required variables:

AWS_REGION
BEDROCK_MODEL_ID
DB_URL
DB_USER
DB_PASSWORD

Never expose secrets in frontend code.

---

## Phase 10 — CI/CD

Create GitHub Actions pipeline.

Pipeline stages:

1. build
2. test
3. docker build
4. push images to ECR
5. deploy to ECS
6. invalidate CloudFront cache

---

## Phase 11 — Validation

Before finishing, ensure the system can:

* register and login users
* call AI tutor endpoint
* generate quizzes
* debug code
* retrieve knowledge using RAG
* run AI inference through Amazon Bedrock
* deploy successfully on AWS

---

## Final Deliverables

The repository must contain:

AI microservice
extended backend controllers
new frontend AI pages
Dockerfiles
AWS infrastructure configuration
CI/CD pipeline

The final platform must run entirely on AWS using Amazon Bedrock models.
