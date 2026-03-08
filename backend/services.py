"""
Business Logic Services for SkillForge Backend
"""
import logging
from typing import List, Dict, Any
from database import db
from models import User, UserProgress, QuizHistory
from sqlalchemy import func

logger = logging.getLogger(__name__)


class UserProgressService:
    """Service for managing user progress"""
    
    @staticmethod
    def update_progress(user_id: int, topic: str, score: float, total_questions: int, time_spent: int = 0):
        """
        Update user progress after quiz completion
        
        Args:
            user_id: User ID
            topic: Topic name
            score: Score achieved
            total_questions: Total questions in quiz
            time_spent: Time spent in seconds
        """
        try:
            # Calculate accuracy
            accuracy = (score / total_questions) * 100 if total_questions > 0 else 0
            
            # Get or create progress record
            progress = UserProgress.query.filter_by(
                user_id=user_id,
                topic=topic
            ).first()
            
            if progress:
                # Update existing record
                # Calculate weighted average accuracy
                total_attempts = progress.attempts + 1
                progress.accuracy = (
                    (progress.accuracy * progress.attempts + accuracy) / total_attempts
                )
                progress.attempts = total_attempts
                progress.time_spent += time_spent
            else:
                # Create new record
                progress = UserProgress(
                    user_id=user_id,
                    topic=topic,
                    accuracy=accuracy,
                    attempts=1,
                    time_spent=time_spent
                )
                db.session.add(progress)
            
            db.session.commit()
            logger.info(f"Updated progress for user {user_id}, topic {topic}")
            
            return progress
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update progress: {str(e)}")
            raise
    
    @staticmethod
    def get_user_progress(user_id: int) -> List[UserProgress]:
        """
        Get all progress records for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of UserProgress objects
        """
        return UserProgress.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_topic_progress(user_id: int, topic: str) -> UserProgress:
        """
        Get progress for a specific topic
        
        Args:
            user_id: User ID
            topic: Topic name
            
        Returns:
            UserProgress object or None
        """
        return UserProgress.query.filter_by(
            user_id=user_id,
            topic=topic
        ).first()


class QuizHistoryService:
    """Service for managing quiz history"""
    
    @staticmethod
    def record_quiz_completion(
        user_id: int,
        topic: str,
        difficulty: str,
        score: float,
        total_questions: int,
        time_spent: int = 0
    ) -> QuizHistory:
        """
        Record quiz completion
        
        Args:
            user_id: User ID
            topic: Topic name
            difficulty: Difficulty level
            score: Score achieved
            total_questions: Total questions
            time_spent: Time spent in seconds
            
        Returns:
            QuizHistory object
        """
        try:
            quiz_record = QuizHistory(
                user_id=user_id,
                topic=topic,
                difficulty=difficulty,
                score=score,
                total_questions=total_questions,
                time_spent=time_spent
            )
            
            db.session.add(quiz_record)
            db.session.commit()
            
            logger.info(f"Recorded quiz completion for user {user_id}, topic {topic}")
            
            return quiz_record
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record quiz completion: {str(e)}")
            raise
    
    @staticmethod
    def get_user_quiz_history(user_id: int, limit: int = 50) -> List[QuizHistory]:
        """
        Get quiz history for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List of QuizHistory objects
        """
        return QuizHistory.query.filter_by(user_id=user_id)\
            .order_by(QuizHistory.completed_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_topic_statistics(user_id: int, topic: str) -> Dict[str, Any]:
        """
        Get statistics for a specific topic
        
        Args:
            user_id: User ID
            topic: Topic name
            
        Returns:
            Dictionary with statistics
        """
        quizzes = QuizHistory.query.filter_by(
            user_id=user_id,
            topic=topic
        ).all()
        
        if not quizzes:
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'best_score': 0,
                'total_time': 0
            }
        
        total_score = sum(q.score for q in quizzes)
        total_questions = sum(q.total_questions for q in quizzes)
        
        return {
            'total_quizzes': len(quizzes),
            'average_score': (total_score / total_questions * 100) if total_questions > 0 else 0,
            'best_score': max((q.score / q.total_questions * 100) for q in quizzes),
            'total_time': sum(q.time_spent or 0 for q in quizzes)
        }


class AdaptiveLearningEngine:
    """Adaptive learning recommendation engine"""
    
    # Accuracy thresholds
    LOW_ACCURACY_THRESHOLD = 50.0
    HIGH_ACCURACY_THRESHOLD = 80.0
    
    @staticmethod
    def generate_recommendations(user_id: int) -> List[Dict[str, str]]:
        """
        Generate personalized learning recommendations
        
        Args:
            user_id: User ID
            
        Returns:
            List of recommendation dictionaries
        """
        progress_records = UserProgressService.get_user_progress(user_id)
        
        if not progress_records:
            return [{
                'topic': 'Getting Started',
                'type': 'START',
                'reason': 'Begin your learning journey'
            }]
        
        recommendations = []
        
        for progress in progress_records:
            accuracy = progress.accuracy
            topic = progress.topic
            
            if accuracy < AdaptiveLearningEngine.LOW_ACCURACY_THRESHOLD:
                # Low accuracy - recommend easier material
                recommendations.append({
                    'topic': topic,
                    'type': 'EASIER',
                    'reason': f'Review fundamentals of {topic} (current accuracy: {accuracy:.1f}%)'
                })
            
            elif accuracy <= AdaptiveLearningEngine.HIGH_ACCURACY_THRESHOLD:
                # Medium accuracy - recommend practice
                recommendations.append({
                    'topic': topic,
                    'type': 'PRACTICE',
                    'reason': f'Practice more questions on {topic} (current accuracy: {accuracy:.1f}%)'
                })
            
            else:
                # High accuracy - recommend advancing
                recommendations.append({
                    'topic': topic,
                    'type': 'ADVANCE',
                    'reason': f'Ready to move to next topic (mastered {topic} with {accuracy:.1f}% accuracy)'
                })
        
        # Sort by accuracy (lowest first - needs most attention)
        recommendations.sort(key=lambda x: {
            'EASIER': 0,
            'PRACTICE': 1,
            'ADVANCE': 2,
            'START': 3
        }.get(x['type'], 4))
        
        return recommendations
    
    @staticmethod
    def get_next_difficulty(user_id: int, topic: str, current_difficulty: str) -> str:
        """
        Suggest next difficulty level based on performance
        
        Args:
            user_id: User ID
            topic: Topic name
            current_difficulty: Current difficulty level
            
        Returns:
            Suggested difficulty level
        """
        progress = UserProgressService.get_topic_progress(user_id, topic)
        
        if not progress:
            return 'easy'
        
        accuracy = progress.accuracy
        
        # Difficulty progression logic
        if current_difficulty == 'easy':
            if accuracy >= AdaptiveLearningEngine.HIGH_ACCURACY_THRESHOLD:
                return 'medium'
            return 'easy'
        
        elif current_difficulty == 'medium':
            if accuracy >= AdaptiveLearningEngine.HIGH_ACCURACY_THRESHOLD:
                return 'hard'
            elif accuracy < AdaptiveLearningEngine.LOW_ACCURACY_THRESHOLD:
                return 'easy'
            return 'medium'
        
        else:  # hard
            if accuracy < AdaptiveLearningEngine.LOW_ACCURACY_THRESHOLD:
                return 'medium'
            return 'hard'
