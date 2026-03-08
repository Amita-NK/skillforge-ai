"""
Database initialization and configuration
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()


def init_db(app):
    """
    Initialize database with Flask app
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")


def create_tables():
    """Create all database tables"""
    db.create_all()
    logger.info("All tables created")


def drop_tables():
    """Drop all database tables (use with caution!)"""
    db.drop_all()
    logger.warning("All tables dropped")


def reset_database():
    """Reset database by dropping and recreating all tables"""
    drop_tables()
    create_tables()
    logger.info("Database reset complete")


def check_connection():
    """
    Check database connection
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db.session.execute(text('SELECT 1'))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
