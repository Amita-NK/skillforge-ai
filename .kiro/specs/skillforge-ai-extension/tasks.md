# Implementation Plan: SkillForge AI+ Platform Extension

## Overview

This implementation plan extends the existing SkillForge AI+ platform with comprehensive AI capabilities through a microservice architecture. The implementation is organized into phases that build incrementally, starting with the AI microservice foundation, then extending the backend, implementing RAG capabilities, adding frontend features, and finally containerizing and deploying to AWS.

Each task builds on previous work and includes validation through automated tests. The plan preserves existing authentication mechanisms and frontend structure while adding new AI-powered features.

## Tasks

- [x] 1. Set up AI Service foundation (Python FastAPI)
  - [x] 1.1 Create ai_service directory structure with main.py, config.py, models.py, and requirements.txt
    - Initialize FastAPI application with health check endpoint
    - Set up configuration management for environment variables
    - Define Pydantic models for API requests/responses
    - _Requirements: 1.1, 1.2_
  
  - [x] 1.2 Implement Bedrock client wrapper in bedrock_client.py
    - Create BedrockClient class with boto3 integration
    - Implement invoke_model method with retry logic
    - Support multiple model families (Claude, Titan, Llama)
    - _Requirements: 1.4, 1.5_
  
  - [x] 1.3 Create prompt template system in config.py
    - Define PromptTemplates class with TUTOR, QUIZ, and DEBUGGER templates
    - Load templates from configuration
    - _Requirements: 1.6, 2.2_
  
  - [x]* 1.4 Write property test for API input validation
    - **Property 1: API input validation**
    - **Validates: Requirements 1.7**
  
  - [x]* 1.5 Write unit tests for Bedrock client
    - Test successful model invocation
    - Test error handling for Bedrock failures
    - Test retry logic with exponential backoff
    - _Requirements: 1.8_

- [x] 2. Implement AI tutoring functionality
  - [x] 2.1 Create tutor.py module with explanation generation
    - Implement explain_concept function using Bedrock
    - Format responses with explanation, examples, and analogies
    - Add request/response logging
    - _Requirements: 2.1, 2.2, 2.3, 1.9_
  
  - [x] 2.2 Add POST /tutor/explain endpoint in main.py
    - Validate topic parameter
    - Call tutor module
    - Return structured explanation response
    - _Requirements: 2.4, 2.7_
  
  - [x]* 2.3 Write property test for explanation completeness
    - **Property 5: Explanation completeness**
    - **Validates: Requirements 2.3**
  
  - [ ]* 2.4 Write unit tests for tutor endpoint
    - Test successful explanation generation
    - Test empty topic validation
    - Test error handling
    - _Requirements: 2.7_

- [x] 3. Implement AI quiz generation
  - [x] 3.1 Create quiz.py module with quiz generation logic
    - Implement generate_quiz function using Bedrock
    - Parse and validate JSON responses from AI
    - Support difficulty levels (easy, medium, hard)
    - _Requirements: 3.2, 3.3, 3.4_
  
  - [x] 3.2 Add POST /quiz/generate endpoint in main.py
    - Validate topic, difficulty, and count parameters
    - Enforce count between 1 and 20
    - Return quiz in JSON format
    - _Requirements: 3.1, 3.8_
  
  - [x]* 3.3 Write property test for quiz structure completeness
    - **Property 6: Quiz structure completeness**
    - **Validates: Requirements 3.3**
  
  - [x]* 3.4 Write property test for quiz JSON format
    - **Property 8: Quiz JSON format**
    - **Validates: Requirements 3.4**
  
  - [ ]* 3.5 Write unit tests for quiz generation
    - Test quiz generation with different difficulties
    - Test count boundary validation (edge case)
    - Test JSON parsing errors
    - _Requirements: 3.8_

- [x] 4. Implement AI code debugging
  - [x] 4.1 Create debugger.py module with code analysis
    - Implement analyze_code function using Bedrock
    - Support multiple programming languages
    - Parse error detection and code correction from AI response
    - _Requirements: 4.2, 4.3, 4.6_
  
  - [x] 4.2 Add POST /debug/analyze endpoint in main.py
    - Validate language and code parameters
    - Call debugger module
    - Return errors, corrected code, and explanation
    - _Requirements: 4.1, 4.7_
  
  - [x]* 4.3 Write property test for debug response completeness
    - **Property 7: Debug response completeness**
    - **Validates: Requirements 4.4**
  
  - [ ]* 4.4 Write unit tests for debugger
    - Test code with known errors
    - Test valid code (no errors case)
    - Test multiple language support
    - _Requirements: 4.6, 4.7_

- [x] 5. Checkpoint - Ensure AI Service tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement RAG pipeline foundation
  - [x] 6.1 Create embeddings.py module for vector generation
    - Implement generate_embedding function using Bedrock Titan
    - Handle batch embedding generation
    - Add error handling for embedding failures
    - _Requirements: 6.4_
  
  - [x] 6.2 Create rag.py module with document processing
    - Implement text extraction from various file formats
    - Implement text chunking with configurable size and overlap
    - Implement OpenSearch client integration
    - _Requirements: 6.2, 6.3_
  
  - [x] 6.3 Implement embedding storage in OpenSearch
    - Create index with knn_vector mapping
    - Store embeddings with content and metadata
    - _Requirements: 6.5_
  
  - [ ]* 6.4 Write property test for text chunking consistency
    - **Property 12: Text chunking consistency**
    - **Validates: Requirements 6.3**
  
  - [ ]* 6.5 Write property test for embedding generation completeness
    - **Property 13: Embedding generation completeness**
    - **Validates: Requirements 6.4**
  
  - [ ]* 6.6 Write property test for embedding storage with metadata
    - **Property 14: Embedding storage with metadata**
    - **Validates: Requirements 6.5**

- [x] 7. Implement RAG retrieval and context-aware responses
  - [x] 7.1 Add vector search functionality to rag.py
    - Implement search method with knn query
    - Return top-k relevant chunks with scores
    - _Requirements: 6.6_
  
  - [x] 7.2 Integrate RAG with tutor module
    - Modify explain_concept to retrieve context
    - Include context in prompts sent to Bedrock
    - Add source citations to responses
    - _Requirements: 6.7, 6.8_
  
  - [x] 7.3 Add POST /rag/upload endpoint for document ingestion
    - Accept file URL or content
    - Process and store embeddings
    - Return processing status
    - _Requirements: 6.1_
  
  - [x] 7.4 Add GET /rag/search endpoint for testing
    - Accept query and top_k parameters
    - Return relevant chunks
    - _Requirements: 6.6_
  
  - [ ]* 7.5 Write property test for context retrieval
    - **Property 15: Context retrieval**
    - **Validates: Requirements 6.6**
  
  - [ ]* 7.6 Write property test for context inclusion in prompts
    - **Property 16: Context inclusion in prompts**
    - **Validates: Requirements 6.7**
  
  - [ ]* 7.7 Write property test for source citation
    - **Property 17: Source citation**
    - **Validates: Requirements 6.8**

- [x] 8. Checkpoint - Ensure RAG pipeline tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Extend Spring Boot backend with AI endpoints
  - [x] 9.1 Create AIController.java with endpoint stubs
    - Add POST /ai/explain endpoint
    - Add POST /ai/quiz endpoint
    - Add POST /ai/debug endpoint
    - Add GET /ai/recommendations endpoint
    - Apply existing authentication middleware
    - _Requirements: 7.1, 2.4, 3.1, 4.1, 5.6, 13.2_
  
  - [x] 9.2 Create AIServiceClient.java for HTTP communication
    - Implement RestTemplate configuration with timeouts
    - Implement explain, generateQuiz, and debugCode methods
    - Add error handling for service unavailability
    - Add retry logic with circuit breaker
    - _Requirements: 7.2, 7.5, 7.7_
  
  - [x] 9.3 Create request/response DTOs
    - ExplainRequest, ExplanationResponse
    - QuizRequest, QuizResponse, Question
    - DebugRequest, DebugResponse
    - _Requirements: 2.1, 3.1, 4.1_
  
  - [ ]* 9.4 Write property test for JWT token validation
    - **Property 3: JWT token validation**
    - **Validates: Requirements 7.3, 13.6**
  
  - [ ]* 9.5 Write property test for AI endpoint authentication enforcement
    - **Property 22: AI endpoint authentication enforcement**
    - **Validates: Requirements 13.2, 13.5**
  
  - [ ]* 9.6 Write unit tests for AIController
    - Test successful requests to AI service
    - Test JWT validation
    - Test AI service timeout handling
    - Test service unavailability (503 error)
    - _Requirements: 7.3, 7.5, 7.7_

- [x] 10. Implement database schema and adaptive learning
  - [x] 10.1 Create database migration for user_progress table
    - Define schema with user_id, topic, accuracy, attempts, time_spent
    - Add indexes for performance
    - _Requirements: 5.1, 14.1_
  
  - [x] 10.2 Create database migration for quiz_history table
    - Define schema with user_id, topic, difficulty, score, total_questions, completed_at
    - Add indexes for queries
    - _Requirements: 5.2, 14.2_
  
  - [x] 10.3 Create UserProgressService.java
    - Implement methods to update user progress
    - Calculate accuracy from quiz results
    - Use transactions for data consistency
    - _Requirements: 5.3, 5.4, 14.3, 14.4_
  
  - [x] 10.4 Create AdaptiveLearningEngine.java
    - Implement recommendation logic based on accuracy
    - accuracy < 50% → easier material
    - accuracy 50-80% → practice questions
    - accuracy > 80% → advance to next topic
    - _Requirements: 5.3, 5.4, 5.5_
  
  - [x] 10.5 Implement POST /api/quiz/complete endpoint
    - Accept quiz results
    - Calculate score and update user_progress
    - Store in quiz_history
    - _Requirements: 3.7, 5.3, 14.3_
  
  - [x] 10.6 Implement GET /api/progress endpoint
    - Return user progress data
    - _Requirements: 5.6, 14.5_
  
  - [ ]* 10.7 Write property test for quiz completion persistence
    - **Property 9: Quiz completion persistence**
    - **Validates: Requirements 3.7, 14.3**
  
  - [ ]* 10.8 Write property test for user progress calculation
    - **Property 10: User progress calculation**
    - **Validates: Requirements 5.3**
  
  - [ ]* 10.9 Write property test for transaction atomicity
    - **Property 11: Transaction atomicity**
    - **Validates: Requirements 5.4, 14.4**
  
  - [ ]* 10.10 Write unit tests for adaptive learning engine
    - Test recommendations for low accuracy
    - Test recommendations for medium accuracy
    - Test recommendations for high accuracy
    - _Requirements: 5.3, 5.4_

- [x] 11. Checkpoint - Ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Implement frontend TutorPage component
  - [x] 12.1 Create TutorPage.tsx with UI layout
    - Add input field for topic
    - Add "Explain" button
    - Add loading indicator
    - Add result display sections (explanation, analogy, examples)
    - _Requirements: 8.1, 8.6_
  
  - [x] 12.2 Integrate with backend API
    - Call POST /ai/explain with JWT token
    - Handle loading states
    - Handle errors gracefully
    - _Requirements: 8.5, 8.8_
  
  - [x] 12.3 Add authentication check
    - Redirect unauthenticated users to login
    - _Requirements: 8.4_
  
  - [ ]* 12.4 Write property test for code block formatting
    - **Property 26: Code block formatting**
    - **Validates: Requirements 2.6**
  
  - [ ]* 12.5 Write property test for unauthenticated page access
    - **Property 27: Unauthenticated page access**
    - **Validates: Requirements 8.4**
  
  - [ ]* 12.6 Write unit tests for TutorPage
    - Test loading indicator display
    - Test successful explanation display
    - Test error handling
    - Test authentication redirect
    - _Requirements: 8.4, 8.6, 8.8_

- [x] 13. Implement frontend QuizPage component
  - [x] 13.1 Create QuizPage.tsx with quiz setup UI
    - Add topic, difficulty, and count inputs
    - Add "Generate Quiz" button
    - _Requirements: 8.2_
  
  - [x] 13.2 Implement quiz taking interface
    - Display questions one at a time
    - Add selectable answer options
    - Add navigation (Next/Finish buttons)
    - _Requirements: 3.6_
  
  - [x] 13.3 Implement quiz results display
    - Calculate and display score
    - Show correct/incorrect answers
    - _Requirements: 3.7_
  
  - [x] 13.4 Integrate with backend APIs
    - Call POST /ai/quiz to generate quiz
    - Call POST /api/quiz/complete to submit results
    - Handle errors gracefully
    - _Requirements: 8.5, 8.8_
  
  - [ ]* 13.5 Write unit tests for QuizPage
    - Test quiz generation
    - Test question navigation
    - Test score calculation
    - Test authentication
    - _Requirements: 8.4, 8.8_

- [x] 14. Implement frontend DebuggerPage component
  - [x] 14.1 Create DebuggerPage.tsx with code input UI
    - Add language selector dropdown
    - Add code textarea
    - Add "Debug Code" button
    - Add loading indicator
    - _Requirements: 8.3, 8.6_
  
  - [x] 14.2 Implement results display
    - Show detected errors list
    - Display original and corrected code side-by-side
    - Show explanation
    - _Requirements: 4.5_
  
  - [x] 14.3 Integrate with backend API
    - Call POST /ai/debug with JWT token
    - Handle errors gracefully
    - _Requirements: 8.5, 8.8_
  
  - [ ]* 14.4 Write property test for frontend error handling
    - **Property 28: Frontend error handling**
    - **Validates: Requirements 8.8**
  
  - [ ]* 14.5 Write unit tests for DebuggerPage
    - Test code submission
    - Test side-by-side display
    - Test error handling
    - _Requirements: 8.8_

- [x] 15. Add progress dashboard integration
  - [x] 15.1 Create ProgressDashboard component
    - Display user progress statistics
    - Show adaptive learning recommendations
    - Add progress charts
    - _Requirements: 5.7, 14.6_
  
  - [x] 15.2 Integrate with GET /api/progress endpoint
    - Fetch user progress data
    - Display recommendations from adaptive engine
    - _Requirements: 5.6, 14.5_
  
  - [ ]* 15.3 Write unit tests for ProgressDashboard
    - Test data fetching
    - Test chart rendering
    - Test recommendations display
    - _Requirements: 5.7, 14.6_

- [x] 16. Checkpoint - Ensure frontend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 17. Create Docker containers
  - [x] 17.1 Create Dockerfile for AI Service
    - Use Python 3.11 slim base image
    - Install dependencies from requirements.txt
    - Expose port 8000
    - Set uvicorn as entrypoint
    - _Requirements: 9.3_
  
  - [x] 17.2 Create Dockerfile for Backend
    - Use multi-stage build with Maven and JRE
    - Build Spring Boot JAR
    - Expose port 8080
    - _Requirements: 9.2_
  
  - [x] 17.3 Create Dockerfile for Frontend
    - Use multi-stage build with Node and Nginx
    - Build React app
    - Serve with Nginx
    - Expose port 80
    - _Requirements: 9.1_
  
  - [x] 17.4 Create docker-compose.yml for local development
    - Define all services (frontend, backend, ai-service, db)
    - Configure networking and ports
    - Set up environment variables
    - Add volume for database persistence
    - _Requirements: 9.5, 9.6, 9.7, 12.7_
  
  - [ ]* 17.5 Write integration test for docker-compose
    - Test that all services start successfully
    - Test inter-service communication
    - _Requirements: 9.6_

- [x] 18. Implement environment configuration
  - [x] 18.1 Create .env.example file
    - Document all required environment variables
    - Include AWS_REGION, BEDROCK_MODEL_ID, DB credentials, etc.
    - _Requirements: 12.1_
  
  - [x] 18.2 Add environment variable validation to AI Service
    - Check required variables on startup
    - Fail with descriptive error if missing
    - _Requirements: 12.5, 12.6_
  
  - [x] 18.3 Add environment variable validation to Backend
    - Check required variables on startup
    - Load database credentials from environment
    - _Requirements: 12.3, 12.5, 12.6_
  
  - [ ]* 18.4 Write property test for environment variable usage
    - **Property 23: Environment variable usage**
    - **Validates: Requirements 10.9, 12.1**
  
  - [ ]* 18.5 Write property test for frontend credential absence
    - **Property 24: Frontend credential absence**
    - **Validates: Requirements 12.2**
  
  - [ ]* 18.6 Write property test for required environment validation
    - **Property 25: Required environment validation**
    - **Validates: Requirements 12.5**

- [x] 19. Create AWS infrastructure with Terraform
  - [x] 19.1 Create VPC and networking resources
    - Define VPC with public and private subnets
    - Create security groups for services
    - Set up NAT gateway
    - _Requirements: 10.1_
  
  - [x] 19.2 Create ECS cluster and task definitions
    - Define ECS cluster
    - Create task definitions for backend and AI service
    - Configure IAM roles for tasks
    - _Requirements: 10.2, 10.3_
  
  - [x] 19.3 Create RDS MySQL instance
    - Define database instance
    - Configure security groups
    - Set up backup retention
    - _Requirements: 10.4_
  
  - [x] 19.4 Create OpenSearch domain
    - Define OpenSearch cluster
    - Configure encryption
    - Set up access policies
    - _Requirements: 10.5_
  
  - [x] 19.5 Create S3 buckets and CloudFront distribution
    - Create S3 bucket for frontend
    - Create S3 bucket for documents
    - Set up CloudFront distribution
    - Configure origin access identity
    - _Requirements: 10.1, 10.6_
  
  - [x] 19.6 Create ECR repositories
    - Create repositories for backend, AI service, and frontend images
    - _Requirements: 10.6_
  
  - [x] 19.7 Set up CloudWatch log groups
    - Create log groups for all services
    - _Requirements: 10.8, 15.5_

- [x] 20. Create CI/CD pipeline with GitHub Actions
  - [x] 20.1 Create workflow file .github/workflows/deploy.yml
    - Define workflow triggers (push to main, pull requests)
    - _Requirements: 11.1, 11.2_
  
  - [x] 20.2 Add test job
    - Set up Python, Node.js, and Java environments
    - Run tests for all services
    - _Requirements: 11.3_
  
  - [x] 20.3 Add build-and-push job
    - Configure AWS credentials
    - Build Docker images for all services
    - Push images to ECR with tags
    - _Requirements: 11.4, 11.5_
  
  - [x] 20.4 Add deploy job
    - Update ECS services with new images
    - Wait for services to stabilize
    - _Requirements: 11.6_
  
  - [x] 20.5 Add deploy-frontend job
    - Build React app
    - Deploy to S3
    - Invalidate CloudFront cache
    - _Requirements: 11.7_
  
  - [x] 20.6 Add error handling to pipeline
    - Ensure pipeline stops on failures
    - Add notification on errors
    - _Requirements: 11.8_

- [x] 21. Implement comprehensive error handling and logging
  - [x] 21.1 Add structured logging to AI Service
    - Log all requests and responses
    - Log errors with context
    - Send logs to CloudWatch
    - _Requirements: 15.1, 15.5_
  
  - [x] 21.2 Add structured logging to Backend
    - Log all AI endpoint requests
    - Log errors with stack traces
    - Send logs to CloudWatch
    - _Requirements: 15.1, 15.5, 7.6_
  
  - [x] 21.3 Implement health check endpoints
    - Add /health endpoint to AI Service
    - Add /actuator/health endpoint to Backend
    - _Requirements: 15.6_
  
  - [x] 21.4 Add database retry logic to Backend
    - Implement exponential backoff for connection failures
    - _Requirements: 15.7_
  
  - [x] 21.5 Add rate limit handling to AI Service
    - Detect Bedrock rate limit errors
    - Implement exponential backoff
    - _Requirements: 15.3_
  
  - [ ]* 21.6 Write property test for error logging
    - **Property 18: Error logging**
    - **Validates: Requirements 15.1**
  
  - [ ]* 21.7 Write property test for HTTP status code correctness
    - **Property 19: HTTP status code correctness**
    - **Validates: Requirements 15.2**
  
  - [ ]* 21.8 Write property test for frontend error message safety
    - **Property 20: Frontend error message safety**
    - **Validates: Requirements 15.4**
  
  - [ ]* 21.9 Write property test for request logging
    - **Property 21: Request logging**
    - **Validates: Requirements 1.9, 7.6**
  
  - [ ]* 21.10 Write unit tests for error handling
    - Test Bedrock timeout handling
    - Test service unavailability
    - Test database retry logic
    - Test rate limit handling
    - _Requirements: 15.3, 15.7_

- [x] 22. Final integration testing and validation
  - [x] 22.1 Test complete AI tutoring flow
    - User authenticates and requests explanation
    - Backend validates JWT and forwards to AI Service
    - AI Service retrieves context from RAG and calls Bedrock
    - Response flows back to frontend
    - _Requirements: 2.1, 2.2, 2.3, 6.6, 6.7_
  
  - [x] 22.2 Test complete quiz flow
    - User generates quiz
    - User completes quiz
    - Backend calculates score and updates progress
    - Adaptive engine generates recommendations
    - _Requirements: 3.1, 3.2, 3.7, 5.3, 5.4_
  
  - [x] 22.3 Test complete debugging flow
    - User submits code
    - AI Service analyzes and returns corrections
    - Frontend displays side-by-side comparison
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 22.4 Test RAG pipeline end-to-end
    - Upload document to S3
    - Process and generate embeddings
    - Store in OpenSearch
    - Retrieve context during AI queries
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [x] 22.5 Verify authentication preservation
    - Confirm existing login/signup flows work
    - Confirm JWT validation on all AI endpoints
    - Confirm no modifications to user tables
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_
  
  - [x] 22.6 Test deployment to AWS
    - Deploy infrastructure with Terraform
    - Run CI/CD pipeline
    - Verify all services running on ECS
    - Verify frontend accessible via CloudFront
    - Verify database and OpenSearch connectivity
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_

- [x] 23. Final checkpoint - Complete system validation
  - Ensure all integration tests pass, verify deployment is successful, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples, edge cases, and error conditions
- Integration tests verify end-to-end flows across all services
- The implementation preserves existing authentication and does not modify user tables
- All services use environment variables for configuration (no hardcoded secrets)
- Docker containers enable consistent deployment across environments
- AWS infrastructure is defined as code using Terraform
- CI/CD pipeline automates testing, building, and deployment
