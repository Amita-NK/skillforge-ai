# Use Cases

Student
- Learn concepts
- Track progress
- Solve challenges

Developer
- Debug code
- Optimize performance

Institution
- Monitor analytics
- Assign modules


# SkillForge AI+ — Functional Use Cases

This document defines the core capabilities of the SkillForge AI platform.

The AI coding agent must extend the existing repository to support the following features.

---

# AI Tutor

Users can request explanations of technical topics.

Example:

Explain binary search.

Endpoint:

POST /ai/explain

Response:

- explanation
- examples
- analogy

The explanation must be beginner friendly.

---

# AI Quiz Generator

Users can generate quizzes.

Endpoint:

POST /ai/quiz

Input:

topic  
difficulty  
count

Output:

multiple choice questions with answers.

---

# AI Code Debugger

Users submit code for debugging.

Endpoint:

POST /ai/debug

Input:

language  
code

Output:

- detected errors
- corrected code
- explanation

---

# Adaptive Learning Engine

Track user progress.

Create table:

user_progress

Fields:

user_id  
topic  
accuracy  
attempts  
time_spent  

Adaptive rules:

accuracy < 50 → easier material  
accuracy 50–80 → practice questions  
accuracy > 80 → next topic

---

# Knowledge Retrieval (RAG)

The system must retrieve knowledge from learning materials.

Process:

1 upload course material to S3  
2 extract text  
3 create embeddings  
4 store in vector database  
5 retrieve relevant context during AI queries

Vector database:

OpenSearch.

---

# System Requirements

The platform must support:

AI tutoring  
AI quizzes  
AI debugging  
adaptive learning  
knowledge retrieval