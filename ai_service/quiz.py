"""
AI Quiz Generation Module
Provides quiz generation functionality using Amazon Bedrock
"""
import logging
import json
import re
from typing import Dict, List, Any
from bedrock_client import BedrockClient, BedrockClientError
from config import PromptTemplates

logger = logging.getLogger(__name__)


class QuizGenerationError(Exception):
    """Custom exception for quiz generation errors"""
    pass


class QuizService:
    """Service for generating quizzes using AI"""
    
    # Valid difficulty levels
    VALID_DIFFICULTIES = {'easy', 'medium', 'hard'}
    
    # Count boundaries
    MIN_QUESTIONS = 1
    MAX_QUESTIONS = 20
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize quiz service
        
        Args:
            bedrock_client: Configured BedrockClient instance
        """
        self.bedrock = bedrock_client
    
    def generate_quiz(
        self,
        topic: str,
        difficulty: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        Generate a quiz with multiple choice questions
        
        Args:
            topic: The topic for the quiz
            difficulty: Difficulty level ('easy', 'medium', or 'hard')
            count: Number of questions to generate (1-20)
            
        Returns:
            List of question dictionaries, each containing:
                - question: Question text
                - options: List of answer options
                - correct: Index of correct answer
                - explanation: Explanation of the answer
                
        Raises:
            ValueError: If parameters are invalid
            QuizGenerationError: If quiz generation or parsing fails
        """
        # Validate inputs
        self._validate_inputs(topic, difficulty, count)
        
        # Log request
        logger.info(f"Generating quiz: topic='{topic}', difficulty={difficulty}, count={count}")
        
        # Build prompt using template
        prompt = PromptTemplates.QUIZ.format(
            topic=topic,
            difficulty=difficulty,
            count=count
        )
        
        try:
            # Call Bedrock to generate quiz
            response = self.bedrock.invoke_model(
                prompt=prompt,
                max_tokens=3000,  # More tokens for multiple questions
                temperature=0.7,
                top_p=0.9
            )
            
            # Parse and validate JSON response
            questions = self._parse_quiz_response(response, count)
            
            # Log successful generation
            logger.info(f"Successfully generated {len(questions)} questions for topic: {topic}")
            
            return questions
            
        except BedrockClientError as e:
            logger.error(f"Bedrock API error during quiz generation: {str(e)}")
            raise QuizGenerationError(f"Failed to generate quiz: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error during quiz generation: {str(e)}")
            raise QuizGenerationError(f"Failed to generate quiz: {str(e)}")
    
    def _validate_inputs(self, topic: str, difficulty: str, count: int) -> None:
        """
        Validate quiz generation inputs
        
        Args:
            topic: Quiz topic
            difficulty: Difficulty level
            count: Number of questions
            
        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate topic
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")
        
        # Validate difficulty
        if difficulty not in self.VALID_DIFFICULTIES:
            raise ValueError(
                f"Difficulty must be one of {self.VALID_DIFFICULTIES}, got '{difficulty}'"
            )
        
        # Validate count
        if not isinstance(count, int):
            raise ValueError(f"Count must be an integer, got {type(count).__name__}")
        
        if count < self.MIN_QUESTIONS or count > self.MAX_QUESTIONS:
            raise ValueError(
                f"Count must be between {self.MIN_QUESTIONS} and {self.MAX_QUESTIONS}, got {count}"
            )
    
    def _parse_quiz_response(self, response: str, expected_count: int) -> List[Dict[str, Any]]:
        """
        Parse and validate quiz response from AI
        
        Args:
            response: Raw text response from Bedrock
            expected_count: Expected number of questions
            
        Returns:
            List of validated question dictionaries
            
        Raises:
            QuizGenerationError: If parsing or validation fails
        """
        # Try to extract JSON from response
        json_str = self._extract_json(response)
        
        if not json_str:
            logger.error("No JSON found in response")
            raise QuizGenerationError("AI response did not contain valid JSON")
        
        try:
            # Parse JSON
            questions = json.loads(json_str)
            
            # Validate structure
            if not isinstance(questions, list):
                raise QuizGenerationError("Response must be a JSON array of questions")
            
            if len(questions) == 0:
                raise QuizGenerationError("No questions were generated")
            
            # Validate each question
            validated_questions = []
            for i, q in enumerate(questions):
                try:
                    validated_q = self._validate_question(q, i)
                    validated_questions.append(validated_q)
                except ValueError as e:
                    logger.warning(f"Question {i} validation failed: {str(e)}")
                    # Continue with other questions instead of failing completely
                    continue
            
            if len(validated_questions) == 0:
                raise QuizGenerationError("No valid questions could be parsed")
            
            # Log if we got fewer questions than expected
            if len(validated_questions) < expected_count:
                logger.warning(
                    f"Generated {len(validated_questions)} valid questions, "
                    f"expected {expected_count}"
                )
            
            return validated_questions
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.debug(f"Failed JSON string: {json_str[:500]}")
            raise QuizGenerationError(f"Failed to parse JSON response: {str(e)}")
    
    def _extract_json(self, response: str) -> str:
        """
        Extract JSON array from response text
        
        Args:
            response: Raw response text
            
        Returns:
            Extracted JSON string or empty string if not found
        """
        # Try to find JSON array in response
        # Look for patterns like [...] with proper nesting
        
        # First, try to find JSON between code blocks
        code_block_pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
        match = re.search(code_block_pattern, response, re.DOTALL)
        if match:
            return match.group(1)
        
        # Try to find raw JSON array
        # Find the first '[' and matching ']'
        start_idx = response.find('[')
        if start_idx == -1:
            # No array found
            return ""
        
        # Find matching closing bracket
        bracket_count = 0
        for i in range(start_idx, len(response)):
            if response[i] == '[':
                bracket_count += 1
            elif response[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    return response[start_idx:i+1]
        
        # No matching bracket found
        return ""
    
    def _validate_question(self, question: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Validate a single question structure
        
        Args:
            question: Question dictionary to validate
            index: Question index for error messages
            
        Returns:
            Validated and normalized question dictionary
            
        Raises:
            ValueError: If question structure is invalid
        """
        if not isinstance(question, dict):
            raise ValueError(f"Question {index} must be a dictionary")
        
        # Validate required fields
        required_fields = ['question', 'options', 'correct']
        for field in required_fields:
            if field not in question:
                raise ValueError(f"Question {index} missing required field: {field}")
        
        # Validate question text
        if not isinstance(question['question'], str) or not question['question'].strip():
            raise ValueError(f"Question {index} has invalid question text")
        
        # Validate options
        if not isinstance(question['options'], list):
            raise ValueError(f"Question {index} options must be a list")
        
        if len(question['options']) < 2:
            raise ValueError(f"Question {index} must have at least 2 options")
        
        if len(question['options']) > 6:
            raise ValueError(f"Question {index} has too many options (max 6)")
        
        for i, option in enumerate(question['options']):
            if not isinstance(option, str) or not option.strip():
                raise ValueError(f"Question {index} option {i} is invalid")
        
        # Validate correct answer index
        if not isinstance(question['correct'], int):
            raise ValueError(f"Question {index} correct answer must be an integer")
        
        if question['correct'] < 0 or question['correct'] >= len(question['options']):
            raise ValueError(
                f"Question {index} correct answer index {question['correct']} "
                f"out of range (0-{len(question['options'])-1})"
            )
        
        # Explanation is optional but should be a string if present
        if 'explanation' in question:
            if not isinstance(question['explanation'], str):
                question['explanation'] = str(question['explanation'])
        else:
            question['explanation'] = ""
        
        # Return normalized question
        return {
            'question': question['question'].strip(),
            'options': [opt.strip() for opt in question['options']],
            'correct': question['correct'],
            'explanation': question['explanation'].strip()
        }


def create_quiz_service(bedrock_client: BedrockClient) -> QuizService:
    """
    Factory function to create a QuizService instance
    
    Args:
        bedrock_client: Configured BedrockClient instance
        
    Returns:
        QuizService instance
    """
    return QuizService(bedrock_client)
