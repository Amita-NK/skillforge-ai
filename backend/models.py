"""
Database Models for SkillForge Backend
"""
from database import db
from datetime import datetime


class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    quiz_history = db.relationship('QuizHistory', backref='user', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserProgress(db.Model):
    """User progress tracking"""
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    accuracy = db.Column(db.Float, default=0.0)
    attempts = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Integer, default=0)  # in seconds
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite index for efficient queries
    __table_args__ = (
        db.Index('idx_user_topic', 'user_id', 'topic'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'accuracy': self.accuracy,
            'attempts': self.attempts,
            'time_spent': self.time_spent,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class QuizHistory(db.Model):
    """Quiz completion history"""
    __tablename__ = 'quiz_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    time_spent = db.Column(db.Integer)  # in seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index for efficient queries
    __table_args__ = (
        db.Index('idx_user_completed', 'user_id', 'completed_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'score': self.score,
            'total_questions': self.total_questions,
            'time_spent': self.time_spent,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @property
    def accuracy(self):
        """Calculate accuracy percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.score / self.total_questions) * 100
