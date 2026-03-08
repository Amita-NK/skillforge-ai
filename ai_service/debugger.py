"""
AI Code Debugging Module
Provides code analysis and debugging functionality using Amazon Bedrock
"""
import logging
import json
import re
from typing import Dict, List, Any
from bedrock_client import BedrockClient, BedrockClientError
from config import PromptTemplates

logger = logging.getLogger(__name__)


class DebuggerError(Exception):
    """Custom exception for debugger errors"""
    pass


class DebuggerService:
    """Service for analyzing and debugging code using AI"""
    
    # Supported programming languages
    SUPPORTED_LANGUAGES = {'python', 'javascript', 'java', 'cpp', 'c++', 'typescript', 'go', 'rust'}
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        Initialize debugger service
        
        Args:
            bedrock_client: Configured BedrockClient instance
        """
        self.bedrock = bedrock_client
    
    def analyze_code(
        self,
        language: str,
        code: str
    ) -> Dict[str, Any]:
        """
        Analyze code and provide debugging assistance
        
        Args:
            language: Programming language of the code
            code: Source code to analyze
            
        Returns:
            Dictionary containing:
                - errors: List of detected errors with line numbers and messages
                - corrected_code: Corrected version of the code
                - explanation: Explanation of the issues and fixes
                
        Raises:
            ValueError: If parameters are invalid
            DebuggerError: If code analysis fails
        """
        # Validate inputs
        self._validate_inputs(language, code)
        
        # Log request
        logger.info(f"Analyzing {language} code ({len(code)} characters)")
        
        # Build prompt using template
        prompt = PromptTemplates.DEBUGGER.format(
            language=language,
            code=code
        )
        
        try:
            # Call Bedrock to analyze code
            response = self.bedrock.invoke_model(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.3,  # Lower temperature for more deterministic debugging
                top_p=0.9
            )
            
            # Parse and validate response
            result = self._parse_debug_response(response)
            
            # Log successful analysis
            logger.info(f"Successfully analyzed code, found {len(result['errors'])} issues")
            
            return result
            
        except BedrockClientError as e:
            logger.error(f"Bedrock API error during code analysis: {str(e)}")
            raise DebuggerError(f"Failed to analyze code: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error during code analysis: {str(e)}")
            raise DebuggerError(f"Failed to analyze code: {str(e)}")
    
    def _validate_inputs(self, language: str, code: str) -> None:
        """
        Validate debugger inputs
        
        Args:
            language: Programming language
            code: Source code
            
        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate language
        if not language or not language.strip():
            raise ValueError("Language cannot be empty")
        
        language_lower = language.lower().strip()
        if language_lower not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{language}' is not supported. "
                f"Supported languages: {', '.join(sorted(self.SUPPORTED_LANGUAGES))}"
            )
        
        # Validate code
        if not code or not code.strip():
            raise ValueError("Code cannot be empty")
        
        # Check code length (max 10000 characters as per design)
        if len(code) > 10000:
            raise ValueError("Code is too long (maximum 10000 characters)")
    
    def _parse_debug_response(self, response: str) -> Dict[str, Any]:
        """
        Parse and validate debug response from AI
        
        Args:
            response: Raw text response from Bedrock
            
        Returns:
            Dictionary with errors, corrected_code, and explanation
            
        Raises:
            DebuggerError: If parsing or validation fails
        """
        # Try to extract JSON from response
        json_str = self._extract_json(response)
        
        if json_str:
            try:
                # Parse JSON
                result = json.loads(json_str)
                
                # Validate and normalize structure
                return self._validate_debug_result(result)
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed: {str(e)}, falling back to text parsing")
        
        # Fallback: parse as text if JSON extraction fails
        return self._parse_text_response(response)
    
    def _extract_json(self, response: str) -> str:
        """
        Extract JSON object from response text
        
        Args:
            response: Raw response text
            
        Returns:
            Extracted JSON string or empty string if not found
        """
        # Try to find JSON in code blocks
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(code_block_pattern, response, re.DOTALL)
        if match:
            return match.group(1)
        
        # Try to find raw JSON object
        start_idx = response.find('{')
        if start_idx == -1:
            return ""
        
        # Find matching closing brace
        brace_count = 0
        for i in range(start_idx, len(response)):
            if response[i] == '{':
                brace_count += 1
            elif response[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return response[start_idx:i+1]
        
        return ""
    
    def _validate_debug_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize debug result structure
        
        Args:
            result: Parsed result dictionary
            
        Returns:
            Validated and normalized result
            
        Raises:
            DebuggerError: If structure is invalid
        """
        if not isinstance(result, dict):
            raise DebuggerError("Response must be a JSON object")
        
        # Ensure required fields exist
        normalized = {
            'errors': [],
            'corrected_code': '',
            'explanation': ''
        }
        
        # Validate errors array
        if 'errors' in result:
            if isinstance(result['errors'], list):
                for error in result['errors']:
                    if isinstance(error, dict):
                        normalized['errors'].append({
                            'line': error.get('line', 0),
                            'message': str(error.get('message', 'Unknown error'))
                        })
            elif isinstance(result['errors'], str):
                # Single error as string
                normalized['errors'].append({
                    'line': 0,
                    'message': result['errors']
                })
        
        # Get corrected code
        if 'corrected_code' in result:
            normalized['corrected_code'] = str(result['corrected_code']).strip()
        elif 'corrected' in result:
            normalized['corrected_code'] = str(result['corrected']).strip()
        elif 'fixed_code' in result:
            normalized['corrected_code'] = str(result['fixed_code']).strip()
        
        # Get explanation
        if 'explanation' in result:
            normalized['explanation'] = str(result['explanation']).strip()
        elif 'description' in result:
            normalized['explanation'] = str(result['description']).strip()
        
        return normalized
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """
        Parse response as plain text when JSON parsing fails
        
        Args:
            response: Raw text response
            
        Returns:
            Dictionary with parsed errors, corrected_code, and explanation
        """
        result = {
            'errors': [],
            'corrected_code': '',
            'explanation': ''
        }
        
        # Extract code blocks (corrected code)
        code_pattern = r'```[\w]*\n(.*?)```'
        code_matches = re.findall(code_pattern, response, re.DOTALL)
        if code_matches:
            result['corrected_code'] = code_matches[0].strip()
        
        # Try to extract errors
        error_patterns = [
            r'(?:Error|Issue|Problem).*?line\s+(\d+).*?:\s*(.+?)(?:\n|$)',
            r'Line\s+(\d+):\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                result['errors'].append({
                    'line': int(match[0]),
                    'message': match[1].strip()
                })
        
        # If no specific errors found but response indicates issues
        if not result['errors'] and any(word in response.lower() for word in ['error', 'issue', 'problem', 'bug']):
            result['errors'].append({
                'line': 0,
                'message': 'Code has issues (see explanation for details)'
            })
        
        # Use full response as explanation if no specific explanation found
        result['explanation'] = response.strip()
        
        return result


def create_debugger_service(bedrock_client: BedrockClient) -> DebuggerService:
    """
    Factory function to create a DebuggerService instance
    
    Args:
        bedrock_client: Configured BedrockClient instance
        
    Returns:
        DebuggerService instance
    """
    return DebuggerService(bedrock_client)
