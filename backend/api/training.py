from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
import sys
import os

from models.user import User
from models import db
from models.training import TrainingPlan, TrainingSession, SessionExercise, Exercise
from ai.training_optimizer import TrainingOptimizer

training_bp = Blueprint('training', __name__)

@training_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_training_plan():
    """Generate AI-powered training plan for user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        current_week = data.get('week_number', 1)
        
        # Get user profile for AI
        user_profile = {
            'age': user.age,
            'height': user.height,
            'weight': user.weight,
            'gender': user.gender,
            'sport_type': user.sport_type.value if user.sport_type else 'other',
            'years_experience': user.years_experience,
            'fitness_level': user.fitness_level.value if user.fitness_level else 'intermediate',
            'training_frequency': user.training_frequency,
            'has_injuries': user.has_injuries,
            'injury_description': user.injury_description
        }
        
        # Get performance history
        from models.performance import Performance
        performance_tests = Performance.query.filter_by(user_id=user.id).order_by(
            Performance.test_date.desc()
        ).limit(10).all()
        
        performance_history = [test.to_dict() for test in performance_tests]
        
        # Generate training plan using AI
        optimizer = TrainingOptimizer()
        ai_plan = optimizer.generate_training_plan(
            user_profile, 
            current_week, 
            performance_history
        )
        
        # Create training plan in database
        training_plan = TrainingPlan(
            user_id=user.id,
            name=ai_plan['plan_name'],
            description=f"AI-generated training plan focusing on {ai_plan['training_type']}",
            week_number=current_week,
            training_type=ai_plan['training_type'],
            target_adaptations=json.dumps(ai_plan['target_adaptations']),
            expected_duration=ai_plan['expected_duration'],
            difficulty_score=ai_plan['difficulty_score'],
            target_improvements=json.dumps({}),  # To be filled with performance predictions
            model_version=ai_plan['model_version']
        )
        
        db.session.add(training_plan)
        db.session.flush()  # Get the ID
        
        # Create training sessions
        for session_data in ai_plan['sessions']:
            session = TrainingSession(
                plan_id=training_plan.id,
                session_name=session_data['session_name'],
                session_number=session_data['session_number'],
                primary_focus=session_data['primary_focus'],
                warm_up_duration=session_data['warm_up_duration'],
                main_duration=session_data['main_duration'],
                cool_down_duration=session_data['cool_down_duration']
            )
            db.session.add(session)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Training plan generated successfully',
            'plan': training_plan.to_dict(),
            'ai_analysis': ai_plan
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@training_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_training_plans():
    """Get user's training plans"""
    try:
        current_user_id = get_jwt_identity()
        
        # Query parameters
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 10))
        
        query = TrainingPlan.query.filter_by(user_id=current_user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        plans = query.order_by(TrainingPlan.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans],
            'total_count': len(plans)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/plans/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_training_plan(plan_id):
    """Get specific training plan with sessions"""
    try:
        current_user_id = get_jwt_identity()
        
        plan = TrainingPlan.query.filter_by(
            id=plan_id, 
            user_id=current_user_id
        ).first()
        
        if not plan:
            return jsonify({'error': 'Training plan not found'}), 404
        
        plan_dict = plan.to_dict()
        plan_dict['sessions'] = [session.to_dict() for session in plan.sessions]
        
        return jsonify(plan_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_training_session(session_id):
    """Get specific training session with exercises"""
    try:
        current_user_id = get_jwt_identity()
        
        session = TrainingSession.query.join(TrainingPlan).filter(
            TrainingSession.id == session_id,
            TrainingPlan.user_id == current_user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Training session not found'}), 404
        
        session_dict = session.to_dict()
        session_dict['exercises'] = [exercise.to_dict() for exercise in session.exercises]
        
        return jsonify(session_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/sessions/<int:session_id>/start', methods=['POST'])
@jwt_required()
def start_training_session(session_id):
    """Start a training session"""
    try:
        current_user_id = get_jwt_identity()
        
        session = TrainingSession.query.join(TrainingPlan).filter(
            TrainingSession.id == session_id,
            TrainingPlan.user_id == current_user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Training session not found'}), 404
        
        if session.is_completed:
            return jsonify({'error': 'Session already completed'}), 400
        
        session.actual_start_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Training session started',
            'session': session.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@training_bp.route('/sessions/<int:session_id>/complete', methods=['POST'])
@jwt_required()
def complete_training_session(session_id):
    """Complete a training session"""
    try:
        current_user_id = get_jwt_identity()
        
        session = TrainingSession.query.join(TrainingPlan).filter(
            TrainingSession.id == session_id,
            TrainingPlan.user_id == current_user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Training session not found'}), 404
        
        data = request.get_json()
        
        session.actual_end_time = datetime.utcnow()
        session.is_completed = True
        session.perceived_exertion = data.get('perceived_exertion')
        session.user_notes = data.get('user_notes')
        session.session_rating = data.get('session_rating')
        
        # Calculate actual duration
        if session.actual_start_time:
            duration = session.actual_end_time - session.actual_start_time
            session.actual_duration = int(duration.total_seconds() / 60)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Training session completed',
            'session': session.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@training_bp.route('/exercises', methods=['GET'])
def get_exercises():
    """Get exercise library"""
    try:
        # Query parameters
        exercise_type = request.args.get('type')
        sport = request.args.get('sport')
        difficulty = request.args.get('difficulty')
        limit = int(request.args.get('limit', 50))
        
        query = Exercise.query
        
        if exercise_type:
            query = query.filter_by(exercise_type=exercise_type)
        
        if sport:
            # Filter by primary sports (stored as JSON)
            query = query.filter(Exercise.primary_sports.contains(sport))
        
        if difficulty:
            query = query.filter_by(difficulty_level=int(difficulty))
        
        exercises = query.limit(limit).all()
        
        return jsonify({
            'exercises': [exercise.to_dict() for exercise in exercises],
            'total_count': len(exercises)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/exercises/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """Get specific exercise details"""
    try:
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            return jsonify({'error': 'Exercise not found'}), 404
        
        return jsonify(exercise.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/optimize-load', methods=['POST'])
@jwt_required()
def optimize_exercise_load():
    """Optimize exercise load using AI"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        exercise_type = data.get('exercise_type')
        
        if not exercise_type:
            return jsonify({'error': 'Exercise type required'}), 400
        
        # Get user profile
        user_profile = {
            'age': user.age,
            'height': user.height,
            'weight': user.weight,
            'sport_type': user.sport_type.value if user.sport_type else 'other',
            'years_experience': user.years_experience,
            'fitness_level': user.fitness_level.value if user.fitness_level else 'intermediate',
            'training_frequency': user.training_frequency
        }
        
        # Get recent performance history
        from models.performance import Performance
        recent_tests = Performance.query.filter_by(user_id=user.id).order_by(
            Performance.test_date.desc()
        ).limit(5).all()
        
        performance_history = [test.to_dict() for test in recent_tests]
        
        # Optimize using AI
        optimizer = TrainingOptimizer()
        optimized_params = optimizer.optimize_exercise_load(
            exercise_type,
            user_profile,
            performance_history
        )
        
        return jsonify({
            'exercise_type': exercise_type,
            'optimized_parameters': optimized_params,
            'user_factors': {
                'age_factor': 1.0 if user.age < 30 else 0.9,
                'experience_factor': min(user.years_experience / 10, 1.0),
                'fitness_level': user.fitness_level.value if user.fitness_level else 'intermediate'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/predict-improvement', methods=['POST'])
@jwt_required()
def predict_performance_improvement():
    """Predict performance improvements using AI"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        weeks_ahead = data.get('weeks_ahead', 4)
        
        # Get training plan
        plan = TrainingPlan.query.filter_by(
            id=plan_id,
            user_id=user.id
        ).first()
        
        if not plan:
            return jsonify({'error': 'Training plan not found'}), 404
        
        # Get user profile
        user_profile = {
            'age': user.age,
            'sport_type': user.sport_type.value if user.sport_type else 'other',
            'years_experience': user.years_experience,
            'fitness_level': user.fitness_level.value if user.fitness_level else 'intermediate'
        }
        
        # Get training plan data
        training_plan = {
            'training_type': plan.training_type.value if plan.training_type else 'strength'
        }
        
        # Predict improvements
        optimizer = TrainingOptimizer()
        predictions = optimizer.predict_performance_improvement(
            user_profile,
            training_plan,
            weeks_ahead
        )
        
        return jsonify({
            'plan_id': plan_id,
            'weeks_ahead': weeks_ahead,
            'predictions': predictions,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_training_stats():
    """Get training statistics for user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Total plans and sessions
        total_plans = TrainingPlan.query.filter_by(user_id=current_user_id).count()
        completed_plans = TrainingPlan.query.filter_by(
            user_id=current_user_id, 
            is_completed=True
        ).count()
        
        # Session statistics
        total_sessions = db.session.query(TrainingSession).join(TrainingPlan).filter(
            TrainingPlan.user_id == current_user_id
        ).count()
        
        completed_sessions = db.session.query(TrainingSession).join(TrainingPlan).filter(
            TrainingPlan.user_id == current_user_id,
            TrainingSession.is_completed == True
        ).count()
        
        # Recent activity
        recent_sessions = db.session.query(TrainingSession).join(TrainingPlan).filter(
            TrainingPlan.user_id == current_user_id,
            TrainingSession.is_completed == True
        ).order_by(TrainingSession.actual_end_time.desc()).limit(10).all()
        
        # Training frequency analysis
        if recent_sessions:
            total_duration = sum([s.actual_duration or 0 for s in recent_sessions])
            avg_duration = total_duration / len(recent_sessions) if recent_sessions else 0
            avg_rating = sum([s.session_rating or 0 for s in recent_sessions if s.session_rating]) / len([s for s in recent_sessions if s.session_rating]) if recent_sessions else 0
        else:
            avg_duration = 0
            avg_rating = 0
        
        stats = {
            'totals': {
                'plans': total_plans,
                'completed_plans': completed_plans,
                'sessions': total_sessions,
                'completed_sessions': completed_sessions
            },
            'completion_rates': {
                'plans': round((completed_plans / total_plans) * 100, 2) if total_plans > 0 else 0,
                'sessions': round((completed_sessions / total_sessions) * 100, 2) if total_sessions > 0 else 0
            },
            'averages': {
                'session_duration': round(avg_duration, 1),
                'session_rating': round(avg_rating, 1)
            },
            'recent_activity': [session.to_dict() for session in recent_sessions]
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500