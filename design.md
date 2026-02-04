# Design Overview

## 1. Architecture Overview

Frontend → Backend → AI Engine → Database

---

## 2. AWS Cloud Architecture

- CloudFront → S3  
- API Gateway → Lambda/EC2  
- Database → RDS  
- AI → SageMaker  
- Auth → Cognito  

---

## 3. Modules

- Learning Studio
- Code Debugger
- Gamification Engine
- Analytics Engine
- Security Layer

---

## 4. Database Schema

- Users  
- Skills  
- Sessions  
- Challenges  
- Notes  
- CodeAnalysis  

---

## 5. Workflow

Login → Dashboard → Learn/Debug → AI → Update Score → Recommendation

---

## 6. Security Design

- sandbox execution
- encryption
- RBAC
- audit logging

---

## 7. Scalability

Serverless architecture enables automatic scaling and cost efficiency.

---

## 8. Deployment

AWS deployment using S3 + Lambda + RDS.

