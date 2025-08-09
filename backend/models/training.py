from datetime import datetime
from enum import Enum
import json
from . import db

class TrainingType(Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    HIIT = "hiit"
    AGILITY = "agility"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    SPORT_SPECIFIC = "sport_specific"

class ExerciseType(Enum):
    # Type 2 muscle fiber exercises
    EXPLOSIVE = "explosive"
    POWER = "power"
    SPRINT = "sprint"
    PLYOMETRIC = "plyometric"
    
    # Mitochondrial capacity exercises
    AEROBIC = "aerobic"
    TEMPO = "tempo"
    THRESHOLD = "threshold"
    
    # Sport-specific
    AGILITY_DRILL = "agility_drill"
    SKILL_BASED = "skill_based"

class IntensityLevel(Enum):
    LOW = "low"        # 50-60% max effort
    MODERATE = "moderate"  # 60-70% max effort
    HIGH = "high"      # 70-85% max effort
    VERY_HIGH = "very_high"  # 85-95% max effort
    MAXIMAL = "maximal"    # 95-100% max effort

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    target_muscle_groups = db.Column(db.Text)  # JSON string
    equipment_needed = db.Column(db.Text)      # JSON string
    instructions = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    difficulty_level = db.Column(db.Integer, default=1)  # 1-5 scale
    
    # Sport-specific targeting
    primary_sports = db.Column(db.Text)  # JSON string of sports this exercise benefits
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_target_muscles(self):
        """Get target muscle groups as list"""
        if self.target_muscle_groups:
            return json.loads(self.target_muscle_groups)
        return []
    
    def get_equipment(self):
        """Get equipment needed as list"""
        if self.equipment_needed:
            return json.loads(self.equipment_needed)
        return []
    
    def get_primary_sports(self):
        """Get primary sports as list"""
        if self.primary_sports:
            return json.loads(self.primary_sports)
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'exercise_type': self.exercise_type.value if self.exercise_type else None,
            'target_muscle_groups': self.get_target_muscles(),
            'equipment_needed': self.get_equipment(),
            'instructions': self.instructions,
            'video_url': self.video_url,
            'difficulty_level': self.difficulty_level,
            'primary_sports': self.get_primary_sports()
        }

class TrainingPlan(db.Model):
    __tablename__ = 'training_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Plan metadata
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    week_number = db.Column(db.Integer, nullable=False)
    training_type = db.Column(db.Enum(TrainingType), nullable=False)
    
    # AI-generated parameters
    target_adaptations = db.Column(db.Text)  # JSON: muscle fiber types, energy systems
    expected_duration = db.Column(db.Integer)  # minutes
    difficulty_score = db.Column(db.Float)     # 1-10 scale
    
    # Performance targets
    target_improvements = db.Column(db.Text)  # JSON: specific metrics to improve
    
    # Plan status
    is_active = db.Column(db.Boolean, default=True)
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime)
    
    # AI model version for tracking
    model_version = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('TrainingSession', backref='plan', lazy=True, cascade='all, delete-orphan')
    
    def get_target_adaptations(self):
        """Get target adaptations as dict"""
        if self.target_adaptations:
            return json.loads(self.target_adaptations)
        return {}
    
    def get_target_improvements(self):
        """Get target improvements as dict"""
        if self.target_improvements:
            return json.loads(self.target_improvements)
        return {}
    
    def calculate_completion_rate(self):
        """Calculate plan completion percentage"""
        if not self.sessions:
            return 0
        completed_sessions = sum(1 for session in self.sessions if session.is_completed)
        return round((completed_sessions / len(self.sessions)) * 100, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'week_number': self.week_number,
            'training_type': self.training_type.value if self.training_type else None,
            'target_adaptations': self.get_target_adaptations(),
            'expected_duration': self.expected_duration,
            'difficulty_score': self.difficulty_score,
            'target_improvements': self.get_target_improvements(),
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'completion_rate': self.calculate_completion_rate(),
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sessions_count': len(self.sessions) if self.sessions else 0
        }

class TrainingSession(db.Model):
    __tablename__ = 'training_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('training_plans.id'), nullable=False)
    
    # Session details
    session_name = db.Column(db.String(200), nullable=False)
    session_number = db.Column(db.Integer, nullable=False)  # Day of the week (1-7)
    scheduled_date = db.Column(db.Date)
    
    # Session parameters
    primary_focus = db.Column(db.String(100))  # Type 2 fibers, mitochondrial, sport-specific
    warm_up_duration = db.Column(db.Integer, default=10)  # minutes
    main_duration = db.Column(db.Integer, nullable=False)  # minutes
    cool_down_duration = db.Column(db.Integer, default=10)  # minutes
    
    # Execution tracking
    is_completed = db.Column(db.Boolean, default=False)
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    actual_duration = db.Column(db.Integer)  # minutes
    
    # User feedback
    perceived_exertion = db.Column(db.Integer)  # 1-10 RPE scale
    user_notes = db.Column(db.Text)
    session_rating = db.Column(db.Integer)  # 1-5 stars
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exercises = db.relationship('SessionExercise', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def calculate_total_duration(self):
        """Calculate total planned session duration"""
        return self.warm_up_duration + self.main_duration + self.cool_down_duration
    
    def calculate_actual_duration_minutes(self):
        """Calculate actual session duration if completed"""
        if self.actual_start_time and self.actual_end_time:
            delta = self.actual_end_time - self.actual_start_time
            return int(delta.total_seconds() / 60)
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'session_name': self.session_name,
            'session_number': self.session_number,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'primary_focus': self.primary_focus,
            'warm_up_duration': self.warm_up_duration,
            'main_duration': self.main_duration,
            'cool_down_duration': self.cool_down_duration,
            'total_duration': self.calculate_total_duration(),
            'is_completed': self.is_completed,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'actual_duration': self.calculate_actual_duration_minutes(),
            'perceived_exertion': self.perceived_exertion,
            'user_notes': self.user_notes,
            'session_rating': self.session_rating,
            'exercises_count': len(self.exercises) if self.exercises else 0
        }

class SessionExercise(db.Model):
    __tablename__ = 'session_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    
    # Exercise parameters
    order_in_session = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.String(50))  # Can be "12", "8-10", "30 seconds", etc.
    weight = db.Column(db.Float)     # kg
    rest_time = db.Column(db.Integer)  # seconds
    intensity = db.Column(db.Enum(IntensityLevel))
    
    # Special parameters for different exercise types
    distance = db.Column(db.Float)   # meters for running/cycling
    duration = db.Column(db.Integer) # seconds for time-based exercises
    tempo = db.Column(db.String(20)) # "3-1-2-1" for controlled movements
    
    # Performance tracking
    actual_sets = db.Column(db.Integer)
    actual_reps = db.Column(db.String(50))
    actual_weight = db.Column(db.Float)
    actual_duration = db.Column(db.Integer)
    
    # Exercise-specific notes
    form_notes = db.Column(db.Text)
    difficulty_rating = db.Column(db.Integer)  # 1-10 scale
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    exercise = db.relationship('Exercise', backref='session_uses')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'exercise_id': self.exercise_id,
            'exercise': self.exercise.to_dict() if self.exercise else None,
            'order_in_session': self.order_in_session,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'rest_time': self.rest_time,
            'intensity': self.intensity.value if self.intensity else None,
            'distance': self.distance,
            'duration': self.duration,
            'tempo': self.tempo,
            'actual_sets': self.actual_sets,
            'actual_reps': self.actual_reps,
            'actual_weight': self.actual_weight,
            'actual_duration': self.actual_duration,
            'form_notes': self.form_notes,
            'difficulty_rating': self.difficulty_rating
        }

# Training alias for backward compatibility
Training = TrainingPlan