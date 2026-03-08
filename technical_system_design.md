# SkillForge AI+ Technical System Design

## 🗄️ Database Schema Design

### 1. Amazon DynamoDB (Learner Session Store)
*Purpose: Sub-millisecond state management for personalization.*

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `PK` | String | `USER#[UserId]` |
| `SK` | String | `STATE#[SessionId]` |
| `PersonalizationVector` | Map | JSON blob of learning style, strengths, weaknesses |
| `CurrentModule` | String | ID of the module the user is currently studying |
| `LastInteraction` | Number | Epoch timestamp for fatigue monitoring |
| `LQ_Score` | Number | Current Learning Quotient index |
| `CPS_Score` | Number | Current Coding Productivity Score |

### 2. Amazon RDS (Academic & Scored Records)
*Purpose: Structured, ACID-compliant records for exams and certifications.*

```sql
CREATE TABLE courses (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    syllabus_meta JSONB, -- Links to S3 PDFs/OpenSearch IDs
    difficulty_level INT
);

CREATE TABLE assessments (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    course_id UUID REFERENCES courses(id),
    score DECIMAL(5,2),
    ai_feedback TEXT,
    completed_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Amazon S3 (Large Scale Storage)
*Purpose: Content delivery and audit logs.*

*   `s3://skillforge-assets/content/`: PDF/Video/Audio files indexed by Bedrock.
*   `s3://skillforge-assets/roadmaps/`: User-specific adaptive roadmap JSONs.
*   `s3://skillforge-logs/fargate/`: Secure sandbox execution logs (Lifecycle: Move to Glacier after 30 days).

## 🤖 GenAI Metric Engineering

### Learning Quotient (LQ)
Calculated via Lambda using interaction frequency, correct answer ratio, and time-to-concept-grasp.
`LQ = (Correct_Answers / Total_Attempts) * (k / Avg_Time_Per_Module)`

### Fatigue Recovery Index (FRI)
Analyzes `LastInteraction` timestamps and response latency. If latency increases by >25% over 1 hour, **Bedrock Agent** triggers a "Micro-break" recommendation.

## 🛡️ Sandbox Isolation Strategy (ECS Fargate)
- **Networking**: `awsvpc` mode with security groups blocking all outbound traffic except S3 (for logs).
- **Hardness**: Containers run in read-only root FS.
- **Persistence**: User files (`/workspace`) mounted via **Amazon EFS** to allow resumption of work across container restarts.
