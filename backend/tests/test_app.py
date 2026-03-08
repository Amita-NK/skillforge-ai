"""
Unit tests for Flask backend application
"""
import pytest
import json
from app import app, db
from models import User, UserProgress, QuizHistory
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def test_user(client):
    """Create a test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            name='Test User'
        )
        db.session.add(user)
        db.session.commit()
        return user


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'skillforge-backend'


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['service'] == 'SkillForge Backend API'
    assert 'endpoints' in data


def test_register_success(client):
    """Test successful user registration"""
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'name': 'New User'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully'
    assert data['user']['username'] == 'newuser'


def test_register_missing_fields(client):
    """Test registration with missing fields"""
    response = client.post('/auth/register', json={
        'username': 'newuser'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_register_duplicate_user(client, test_user):
    """Test registration with duplicate username"""
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'another@example.com',
        'password': 'password123'
    })
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['user']['username'] == 'testuser'


def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_login_missing_fields(client):
    """Test login with missing fields"""
    response = client.post('/auth/login', json={
        'username': 'testuser'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def get_auth_token(client, username='testuser', password='password123'):
    """Helper function to get JWT token"""
    response = client.post('/auth/login', json={
        'username': username,
        'password': password
    })
    data = json.loads(response.data)
    return data['access_token']


def test_progress_endpoint_requires_auth(client):
    """Test that progress endpoint requires authentication"""
    response = client.get('/api/progress')
    assert response.status_code == 401


def test_get_progress_empty(client, test_user):
    """Test getting progress with no data"""
    token = get_auth_token(client)
    response = client.get('/api/progress', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'progress' in data
    assert len(data['progress']) == 0


def test_complete_quiz_requires_auth(client):
    """Test that quiz completion requires authentication"""
    response = client.post('/api/quiz/complete', json={
        'topic': 'Python',
        'score': 8,
        'total_questions': 10
    })
    assert response.status_code == 401


def test_complete_quiz_success(client, test_user):
    """Test successful quiz completion"""
    token = get_auth_token(client)
    response = client.post('/api/quiz/complete', 
        json={
            'topic': 'Python Basics',
            'difficulty': 'medium',
            'score': 8,
            'total_questions': 10,
            'time_spent': 300
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Quiz completion recorded'
    assert data['score'] == 8
    assert 'accuracy' in data


def test_complete_quiz_missing_fields(client, test_user):
    """Test quiz completion with missing fields"""
    token = get_auth_token(client)
    response = client.post('/api/quiz/complete',
        json={'topic': 'Python'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_recommendations_requires_auth(client):
    """Test that recommendations endpoint requires authentication"""
    response = client.get('/ai/recommendations')
    assert response.status_code == 401


def test_recommendations_empty(client, test_user):
    """Test recommendations with no progress data"""
    token = get_auth_token(client)
    response = client.get('/ai/recommendations', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'recommendations' in data
