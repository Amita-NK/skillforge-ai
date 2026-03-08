"""
AI Tutoring Module
Provides concept explanation functionality using Amazon Bedrock
"""
import logging
import re
from typing import Dict, List
from bedrock_client import BedrockClient
from config import PromptTemplates

logger = logging.getLogger(__name__)


class TutorService:
    """Service for generating educational explanations using AI"""
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize tutor service
        
        Args:
            bedrock_client: Configured BedrockClient instance
        """
        self.bedrock = bedrock_client
    
    def explain_concept(self, topic: str, context: str = "") -> Dict[str, any]:
        """
        Generate a comprehensive explanation for a given topic
        
        Args:
            topic: The concept or topic to explain
            context: Optional context from RAG pipeline (course materials)
            
        Returns:
            Dictionary containing:
                - explanation: Detailed step-by-step explanation
                - examples: List of code examples
                - analogy: Real-world analogy
                
        Raises:
            ValueError: If topic is empty or invalid
            BedrockClientError: If AI generation fails
        """
        # Validate input
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")
        
        topic = topic.strip()
        
        # Log request
        logger.info(f"Generating explanation for topic: {topic}")
        
        # Build prompt using template
        prompt = PromptTemplates.TUTOR.format(
            topic=topic,
            context=context if context else "No additional context available."
        )
        
        try:
            # Call Bedrock to generate explanation
            response = self.bedrock.invoke_model(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7,
                top_p=0.9
            )
            
            # Parse and structure the response
            structured_response = self._parse_explanation(response)
            
            # Log successful generation
            logger.info(f"Successfully generated explanation for topic: {topic}")
            logger.debug(f"Response structure: explanation={len(structured_response['explanation'])} chars, "
                        f"examples={len(structured_response['examples'])}, "
                        f"analogy={len(structured_response.get('analogy', ''))} chars")
            
            return structured_response
            
        except Exception as e:
            logger.error(f"Failed to generate explanation for topic '{topic}': {str(e)}")
            raise
    
    def _parse_explanation(self, response: str) -> Dict[str, any]:
        """
        Parse AI response into structured format
        
        Args:
            response: Raw text response from Bedrock
            
        Returns:
            Dictionary with explanation, examples, and analogy
        """
        # Initialize result structure
        result = {
            'explanation': '',
            'examples': [],
            'analogy': ''
        }
        
        # Extract code examples (anything in code blocks)
        code_pattern = r'```[\w]*\n(.*?)```'
        code_matches = re.findall(code_pattern, response, re.DOTALL)
        result['examples'] = [code.strip() for code in code_matches]
        
        # Remove code blocks from response for easier parsing
        response_without_code = re.sub(code_pattern, '[CODE_EXAMPLE]', response, flags=re.DOTALL)
        
        # Try to extract analogy section
        analogy_patterns = [
            r'(?:Analogy|Real-world analogy):\s*(.+?)(?:\n\n|\n[A-Z]|$)',
            r'(?:Think of it like|It\'s like|Similar to|Imagine)\s+(.+?)(?:\n\n|\n[A-Z]|$)'
        ]
        
        for pattern in analogy_patterns:
            analogy_match = re.search(pattern, response_without_code, re.IGNORECASE | re.DOTALL)
            if analogy_match:
                result['analogy'] = analogy_match.group(1).strip()
                break
        
        # The explanation is the main content
        # Remove the analogy section if found
        explanation_text = response_without_code
        if result['analogy']:
            explanation_text = re.sub(
                r'(?:Analogy|Real-world analogy|Think of it like|It\'s like|Similar to|Imagine).*',
                '',
                explanation_text,
                flags=re.IGNORECASE | re.DOTALL
            )
        
        result['explanation'] = explanation_text.strip()
        
        # If no structured parsing worked, use the full response as explanation
        if not result['explanation']:
            result['explanation'] = response.strip()
        
        return result


def create_tutor_service(bedrock_client: BedrockClient) -> TutorService:
    """
    Factory function to create a TutorService instance
    
    Args:
        bedrock_client: Configured BedrockClient instance
        
    Returns:
        TutorService instance
    """
    return TutorService(bedrock_client)
