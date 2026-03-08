"""
Property-based tests for quiz service
Tests quiz structure completeness and JSON format
**Validates: Requirements 3.3, 3.4**
"""
import pytest
import json
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock
from quiz import QuizService


# Strategies for generating valid inputs
# Use alphanumeric topics to avoid JSON escaping issues in tests
topics_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip())
difficulty_strategy = st.sampled_from(['easy', 'medium', 'hard'])
count_strategy = st.integers(min_value=1, max_value=20)


@given(topic=topics_strategy, difficulty=difficulty_strategy, count=count_strategy)
@settings(max_examples=100)
def test_property_quiz_structure_completeness(topic, difficulty, count):
    """
    Property 6: Quiz structure completeness
    
    For all valid inputs, each question in the quiz must contain:
    - question: non-empty string
    - options: list with 2-6 items
    - correct: integer index within options range
    - explanation: string (may be empty)
    
    **Validates: Requirements 3.3**
    """
    # Setup mock Bedrock client with valid JSON response
    mock_bedrock = Mock()
    questions_json = []
    for i in range(count):
        questions_json.append({
            "question": f"Question {i+1} about the topic?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": i % 4,
            "explanation": f"Explanation for question {i+1}"
        })
    
    # Return JSON in a format that the parser can extract
    json_response = json.dumps(questions_json)
    mock_bedrock.invoke_model.return_value = f"Here is the quiz:\n{json_response}"
    
    # Create service and generate quiz
    service = QuizService(mock_bedrock)
    result = service.generate_quiz(topic, difficulty, count)
    
    # Property: Result must be a list
    assert isinstance(result, list), "Quiz must be a list of questions"
    assert len(result) > 0, "Quiz must contain at least one question"
    
    # Property: Each question must have complete structure
    for i, question in enumerate(result):
        assert isinstance(question, dict), f"Question {i} must be a dictionary"
        
        # Check required fields exist
        assert 'question' in question, f"Question {i} missing 'question' field"
        assert 'options' in question, f"Question {i} missing 'options' field"
        assert 'correct' in question, f"Question {i} missing 'correct' field"
        assert 'explanation' in question, f"Question {i} missing 'explanation' field"
        
        # Validate question text
        assert isinstance(question['question'], str), f"Question {i} text must be string"
        assert len(question['question']) > 0, f"Question {i} text must not be empty"
        
        # Validate options
        assert isinstance(question['options'], list), f"Question {i} options must be list"
        assert 2 <= len(question['options']) <= 6, \
            f"Question {i} must have 2-6 options, got {len(question['options'])}"
        for j, option in enumerate(question['options']):
            assert isinstance(option, str), f"Question {i} option {j} must be string"
            assert len(option) > 0, f"Question {i} option {j} must not be empty"
        
        # Validate correct answer index
        assert isinstance(question['correct'], int), f"Question {i} correct must be integer"
        assert 0 <= question['correct'] < len(question['options']), \
            f"Question {i} correct index {question['correct']} out of range"
        
        # Validate explanation
        assert isinstance(question['explanation'], str), \
            f"Question {i} explanation must be string"


@given(topic=topics_strategy, difficulty=difficulty_strategy, count=count_strategy)
@settings(max_examples=100)
def test_property_quiz_json_format(topic, difficulty, count):
    """
    Property 8: Quiz JSON format
    
    For all valid inputs, the AI response must be parseable as JSON
    and conform to the expected quiz structure.
    
    **Validates: Requirements 3.4**
    """
    # Setup mock with valid JSON
    mock_bedrock = Mock()
    questions = []
    for i in range(count):
        questions.append({
            "question": f"Q{i+1}",
            "options": ["A", "B", "C"],
            "correct": 0,
            "explanation": "Exp"
        })
    
    mock_bedrock.invoke_model.return_value = f"```json\n{json.dumps(questions)}\n```"
    
    # Create service and generate quiz
    service = QuizService(mock_bedrock)
    result = service.generate_quiz(topic, difficulty, count)
    
    # Property: Result must be valid and parseable
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Property: Result must be JSON-serializable
    try:
        json_str = json.dumps(result)
        reparsed = json.loads(json_str)
        assert reparsed == result
    except (TypeError, ValueError) as e:
        pytest.fail(f"Quiz result is not JSON-serializable: {e}")


@given(
    topic=st.text(max_size=10).filter(lambda x: not x.strip()),
    difficulty=difficulty_strategy,
    count=count_strategy
)
@settings(max_examples=50)
def test_property_empty_topic_rejection(topic, difficulty, count):
    """
    Property: Empty topic rejection
    
    For all empty or whitespace-only topics, the service must raise ValueError.
    
    **Validates: Requirements 3.8**
    """
    mock_bedrock = Mock()
    service = QuizService(mock_bedrock)
    
    with pytest.raises(ValueError, match="Topic cannot be empty"):
        service.generate_quiz(topic, difficulty, count)


@given(
    topic=topics_strategy,
    difficulty=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in {'easy', 'medium', 'hard'}
    ),
    count=count_strategy
)
@settings(max_examples=50)
def test_property_invalid_difficulty_rejection(topic, difficulty, count):
    """
    Property: Invalid difficulty rejection
    
    For all invalid difficulty values, the service must raise ValueError.
    
    **Validates: Requirements 3.8**
    """
    mock_bedrock = Mock()
    service = QuizService(mock_bedrock)
    
    with pytest.raises(ValueError, match="Difficulty must be one of"):
        service.generate_quiz(topic, difficulty, count)


@given(
    topic=topics_strategy,
    difficulty=difficulty_strategy,
    count=st.one_of(
        st.integers(max_value=0),
        st.integers(min_value=21, max_value=100)
    )
)
@settings(max_examples=50)
def test_property_count_boundary_validation(topic, difficulty, count):
    """
    Property: Count boundary validation
    
    For all counts outside the range [1, 20], the service must raise ValueError.
    
    **Validates: Requirements 3.8**
    """
    mock_bedrock = Mock()
    service = QuizService(mock_bedrock)
    
    with pytest.raises(ValueError, match="Count must be between 1 and 20"):
        service.generate_quiz(topic, difficulty, count)
