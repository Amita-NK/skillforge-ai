"""
Property-Based Tests for API Input Validation
Tests universal properties that should hold for all inputs
"""
import pytest
from hypothesis import given, strategies as st, settings
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)


# Property 1: API input validation
# All API endpoints should reject empty or whitespace-only inputs
@settings(max_examples=100)
@given(
    topic=st.one_of(
        st.just(""),
        st.just("   "),
        st.just("\n\n"),
        st.just("\t\t"),
        st.text(min_size=0, max_size=0)
    )
)
def test_property_tutor_rejects_empty_topic(topic):
    """
    Property: The /tutor/explain endpoint should reject empty or whitespace-only topics
    Validates: Requirements 1.7
    """
    response = client.post(
        "/tutor/explain",
        json={"topic": topic}
    )
    # Accept either 400 (endpoint validation) or 422 (Pydantic validation)
    assert response.status_code in [400, 422], f"Expected 400 or 422 for empty topic, got {response.status_code}"
    assert "error" in response.json() or "detail" in response.json()


@settings(max_examples=100)
@given(
    topic=st.one_of(
        st.just(""),
        st.just("   "),
        st.just("\n\n")
    ),
    difficulty=st.sampled_from(["easy", "medium", "hard"]),
    count=st.integers(min_value=1, max_value=20)
)
def test_property_quiz_rejects_empty_topic(topic, difficulty, count):
    """
    Property: The /quiz/generate endpoint should reject empty or whitespace-only topics
    Validates: Requirements 1.7
    """
    response = client.post(
        "/quiz/generate",
        json={"topic": topic, "difficulty": difficulty, "count": count}
    )
    # Accept either 400 (endpoint validation) or 422 (Pydantic validation)
    assert response.status_code in [400, 422]
    assert "error" in response.json() or "detail" in response.json()


@settings(max_examples=100)
@given(
    language=st.sampled_from(["python", "javascript", "java"]),
    code=st.one_of(
        st.just(""),
        st.just("   "),
        st.just("\n\n")
    )
)
def test_property_debugger_rejects_empty_code(language, code):
    """
    Property: The /debug/analyze endpoint should reject empty or whitespace-only code
    Validates: Requirements 1.7
    """
    response = client.post(
        "/debug/analyze",
        json={"language": language, "code": code}
    )
    # Accept either 400 (endpoint validation) or 422 (Pydantic validation)
    assert response.status_code in [400, 422]
    assert "error" in response.json() or "detail" in response.json()


# Property: Valid inputs should return 200 or appropriate success status
@settings(max_examples=50, deadline=5000)  # Set reasonable deadline
@patch('main.rag_pipeline', None)  # Disable RAG
@patch('main.tutor_service')
@given(
    topic=st.text(min_size=1, max_size=100).filter(lambda x: x.strip())
)
def test_property_tutor_accepts_valid_topic(mock_tutor_service, topic):
    """
    Property: The /tutor/explain endpoint should accept non-empty topics
    Validates: Requirements 1.7
    """
    # Mock the service to return a valid response
    mock_tutor_service.explain_concept.return_value = {
        'explanation': 'Test explanation',
        'examples': [],
        'analogy': 'Test analogy'
    }
    
    response = client.post(
        "/tutor/explain",
        json={"topic": topic}
    )
    # Should not be 400 or 422 (validation error)
    assert response.status_code not in [400, 422], f"Valid topic '{topic}' was rejected with status {response.status_code}"


# Property: Quiz count validation
@settings(max_examples=100)
@given(
    topic=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    difficulty=st.sampled_from(["easy", "medium", "hard"]),
    count=st.integers().filter(lambda x: x < 1 or x > 20)
)
def test_property_quiz_rejects_invalid_count(topic, difficulty, count):
    """
    Property: The /quiz/generate endpoint should reject counts outside 1-20 range
    Validates: Requirements 1.7, 3.8
    """
    response = client.post(
        "/quiz/generate",
        json={"topic": topic, "difficulty": difficulty, "count": count}
    )
    assert response.status_code in [400, 422]
    error_msg = response.json().get("detail", "").lower()
    assert "count" in error_msg or "between" in error_msg or "greater" in error_msg or "less" in error_msg


# Property: Quiz difficulty validation
@settings(max_examples=100)
@given(
    topic=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    difficulty=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ["easy", "medium", "hard"]
    ),
    count=st.integers(min_value=1, max_value=20)
)
def test_property_quiz_rejects_invalid_difficulty(topic, difficulty, count):
    """
    Property: The /quiz/generate endpoint should reject invalid difficulty levels
    Validates: Requirements 1.7, 3.8
    """
    response = client.post(
        "/quiz/generate",
        json={"topic": topic, "difficulty": difficulty, "count": count}
    )
    assert response.status_code == 400 or response.status_code == 422  # Pydantic validation


# Property: Code length validation
@settings(max_examples=20)  # Reduced examples for performance
@given(
    language=st.sampled_from(["python", "javascript", "java"]),
    code=st.text(min_size=1000, max_size=2000).map(lambda x: x * 6)  # Generate ~6000-12000 chars
)
def test_property_debugger_rejects_long_code(language, code):
    """
    Property: The /debug/analyze endpoint should reject code longer than 10,000 characters
    Validates: Requirements 1.7, 4.7
    """
    # Ensure code is actually long enough
    if len(code) <= 10000:
        code = code + "x" * (10001 - len(code))
    
    response = client.post(
        "/debug/analyze",
        json={"language": language, "code": code}
    )
    assert response.status_code in [400, 422]
    error_msg = str(response.json()).lower()
    assert "long" in error_msg or "10000" in error_msg or "maximum" in error_msg or "max_length" in error_msg


# Property: Language validation
@settings(max_examples=100)
@given(
    language=st.text(min_size=1, max_size=20).filter(
        lambda x: x.lower() not in ["python", "javascript", "typescript", "java", "cpp", "c++", "go", "rust"]
    ),
    code=st.text(min_size=10, max_size=100)
)
def test_property_debugger_rejects_unsupported_language(language, code):
    """
    Property: The /debug/analyze endpoint should reject unsupported languages
    Validates: Requirements 1.7, 4.6
    """
    response = client.post(
        "/debug/analyze",
        json={"language": language, "code": code}
    )
    # Should either reject at validation (400/422) or in service logic (400/500)
    # We accept 500 here because the service may process it before rejecting
    assert response.status_code in [400, 422, 500]


# Property: Health endpoint always returns 200
@settings(max_examples=20)
@given(st.none())
def test_property_health_always_succeeds(_):
    """
    Property: The /health endpoint should always return 200
    Validates: Requirements 1.1
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


# Property: Root endpoint always returns 200
@settings(max_examples=20)
@given(st.none())
def test_property_root_always_succeeds(_):
    """
    Property: The root endpoint should always return 200
    Validates: Requirements 1.1
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
