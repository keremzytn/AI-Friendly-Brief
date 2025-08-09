from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys
import os

from models.user import User
from models import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Get user dashboard data"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user statistics
        dashboard_data = {
            'user_profile': user.to_dict(),
            'stats': {
                'total_trainings': len(user.trainings) if user.trainings else 0,
                'total_performances': len(user.performances) if user.performances else 0,
                'current_week': get_current_training_week(user),
                'profile_completeness': user.get_profile_completeness(),
                'bmi': user.calculate_bmi(),
                'bmi_category': get_bmi_category(user.calculate_bmi())
            },
            'recent_activity': get_recent_activity(user),
            'upcoming_sessions': get_upcoming_sessions(user)
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get detailed user statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        stats = {
            'training_stats': get_training_statistics(user),
            'performance_stats': get_performance_statistics(user),
            'health_metrics': get_health_metrics(user),
            'achievements': get_user_achievements(user)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/goals', methods=['GET'])
@jwt_required()
def get_user_goals():
    """Get user goals and targets"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        from models.performance import PerformanceBaseline
        
        baselines = PerformanceBaseline.query.filter_by(user_id=user.id).all()
        goals = [baseline.to_dict() for baseline in baselines]
        
        return jsonify({
            'goals': goals,
            'summary': {
                'total_goals': len(goals),
                'achieved_goals': len([g for g in goals if g['short_term_progress'] >= 100]),
                'in_progress_goals': len([g for g in goals if 0 < g['short_term_progress'] < 100])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_user_preferences():
    """Get user preferences and settings"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        preferences = {
            'training_preferences': {
                'training_frequency': user.training_frequency,
                'fitness_level': user.fitness_level.value if user.fitness_level else None,
                'sport_type': user.sport_type.value if user.sport_type else None,
                'has_injuries': user.has_injuries,
                'injury_description': user.injury_description
            },
            'notifications': {
                'email_notifications': True,  # Default settings
                'workout_reminders': True,
                'progress_updates': True,
                'weekly_reports': True
            },
            'privacy': {
                'data_sharing': False,
                'public_profile': False,
                'leaderboard_participation': True
            }
        }
        
        return jsonify(preferences)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_user_preferences():
    """Update user preferences"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update training preferences
        if 'training_preferences' in data:
            tp = data['training_preferences']
            if 'training_frequency' in tp:
                user.training_frequency = tp['training_frequency']
            if 'fitness_level' in tp:
                user.fitness_level = tp['fitness_level']
            if 'has_injuries' in tp:
                user.has_injuries = tp['has_injuries']
            if 'injury_description' in tp:
                user.injury_description = tp['injury_description']
        
        # Note: In a real application, you'd store notification and privacy preferences
        # in separate tables or JSON fields. For now, we'll just return success.
        
        db.session.commit()
        
        return jsonify({'message': 'Preferences updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Helper functions

def get_current_training_week(user):
    """Get current training week number"""
    from models.training import TrainingPlan
    
    active_plan = TrainingPlan.query.filter_by(
        user_id=user.id, 
        is_active=True
    ).first()
    
    return active_plan.week_number if active_plan else 0

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_recent_activity(user):
    """Get recent user activity"""
    from models.training import TrainingSession
    from models.performance import Performance
    
    # Get recent training sessions
    recent_sessions = TrainingSession.query.join(
        TrainingSession.plan
    ).filter_by(user_id=user.id).order_by(
        TrainingSession.created_at.desc()
    ).limit(5).all()
    
    # Get recent performance tests
    recent_tests = Performance.query.filter_by(
        user_id=user.id
    ).order_by(Performance.test_date.desc()).limit(3).all()
    
    activity = []
    
    for session in recent_sessions:
        activity.append({
            'type': 'training_session',
            'title': session.session_name,
            'date': session.created_at.isoformat() if session.created_at else None,
            'status': 'completed' if session.is_completed else 'pending',
            'data': session.to_dict()
        })
    
    for test in recent_tests:
        activity.append({
            'type': 'performance_test',
            'title': f"{test.test_type.value} Test",
            'date': test.test_date.isoformat() if test.test_date else None,
            'status': 'completed',
            'data': test.to_dict()
        })
    
    # Sort by date
    activity.sort(key=lambda x: x['date'], reverse=True)
    
    return activity[:10]  # Return last 10 activities

def get_upcoming_sessions(user):
    """Get upcoming training sessions"""
    from models.training import TrainingSession
    from datetime import datetime, timedelta
    
    upcoming = TrainingSession.query.join(
        TrainingSession.plan
    ).filter_by(user_id=user.id).filter(
        TrainingSession.is_completed == False,
        TrainingSession.scheduled_date >= datetime.now().date(),
        TrainingSession.scheduled_date <= (datetime.now() + timedelta(days=7)).date()
    ).order_by(TrainingSession.scheduled_date).limit(5).all()
    
    return [session.to_dict() for session in upcoming]

def get_training_statistics(user):
    """Get training statistics"""
    from models.training import TrainingSession, TrainingPlan
    
    total_plans = TrainingPlan.query.filter_by(user_id=user.id).count()
    completed_plans = TrainingPlan.query.filter_by(user_id=user.id, is_completed=True).count()
    
    total_sessions = TrainingSession.query.join(
        TrainingSession.plan
    ).filter_by(user_id=user.id).count()
    
    completed_sessions = TrainingSession.query.join(
        TrainingSession.plan
    ).filter_by(user_id=user.id).filter(
        TrainingSession.is_completed == True
    ).count()
    
    return {
        'total_plans': total_plans,
        'completed_plans': completed_plans,
        'plan_completion_rate': round((completed_plans / total_plans) * 100, 2) if total_plans > 0 else 0,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'session_completion_rate': round((completed_sessions / total_sessions) * 100, 2) if total_sessions > 0 else 0
    }

def get_performance_statistics(user):
    """Get performance statistics"""
    from models.performance import Performance, TestType
    
    total_tests = Performance.query.filter_by(user_id=user.id).count()
    
    # Get test counts by type
    test_counts = {}
    for test_type in TestType:
        count = Performance.query.filter_by(user_id=user.id, test_type=test_type).count()
        if count > 0:
            test_counts[test_type.value] = count
    
    # Get improvement statistics
    improved_tests = Performance.query.filter_by(user_id=user.id).filter(
        Performance.improvement_from_baseline > 0
    ).count()
    
    return {
        'total_tests': total_tests,
        'test_types': test_counts,
        'improved_tests': improved_tests,
        'improvement_rate': round((improved_tests / total_tests) * 100, 2) if total_tests > 0 else 0
    }

def get_health_metrics(user):
    """Get health metrics"""
    return {
        'bmi': user.calculate_bmi(),
        'bmi_category': get_bmi_category(user.calculate_bmi()),
        'age': user.age,
        'years_experience': user.years_experience,
        'training_frequency': user.training_frequency,
        'has_injuries': user.has_injuries,
        'fitness_level': user.fitness_level.value if user.fitness_level else None
    }

def get_user_achievements(user):
    """Get user achievements"""
    achievements = []
    
    # Basic achievements based on activity
    if user.trainings and len(user.trainings) >= 1:
        achievements.append({
            'title': 'First Training Plan',
            'description': 'Completed your first training plan',
            'icon': 'trophy',
            'date_earned': user.trainings[0].created_at.isoformat() if user.trainings[0].created_at else None
        })
    
    if user.performances and len(user.performances) >= 1:
        achievements.append({
            'title': 'First Performance Test',
            'description': 'Completed your first performance test',
            'icon': 'chart-line',
            'date_earned': user.performances[0].test_date.isoformat() if user.performances[0].test_date else None
        })
    
    # Streak achievements
    training_count = len(user.trainings) if user.trainings else 0
    if training_count >= 10:
        achievements.append({
            'title': 'Training Enthusiast',
            'description': 'Completed 10 training plans',
            'icon': 'fire',
            'date_earned': None
        })
    
    return achievements