from datetime import datetime
from enum import Enum
import bcrypt
from . import db

class SportType(Enum):
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    TENNIS = "tennis"
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    VOLLEYBALL = "volleyball"
    BADMINTON = "badminton"
    OTHER = "other"

class FitnessLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    
    # Physical characteristics
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)  # cm
    weight = db.Column(db.Float, nullable=False)  # kg
    gender = db.Column(db.String(10), nullable=False)
    
    # Sports information
    sport_type = db.Column(db.Enum(SportType), nullable=False)
    years_experience = db.Column(db.Integer, nullable=False)
    fitness_level = db.Column(db.Enum(FitnessLevel), nullable=False)
    training_frequency = db.Column(db.Integer, nullable=False)  # days per week
    
    # Health information
    has_injuries = db.Column(db.Boolean, default=False)
    injury_description = db.Column(db.Text)
    medical_conditions = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    trainings = db.relationship('Training', backref='user', lazy=True, cascade='all, delete-orphan')
    performances = db.relationship('Performance', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def calculate_bmi(self):
        """Calculate Body Mass Index"""
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 2)
    
    def get_profile_completeness(self):
        """Calculate profile completeness percentage"""
        total_fields = 15
        completed_fields = 0
        
        required_fields = [
            self.email, self.first_name, self.last_name, self.age,
            self.height, self.weight, self.gender, self.sport_type,
            self.years_experience, self.fitness_level, self.training_frequency
        ]
        
        for field in required_fields:
            if field is not None:
                completed_fields += 1
                
        return round((completed_fields / total_fields) * 100, 2)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'gender': self.gender,
            'sport_type': self.sport_type.value if self.sport_type else None,
            'years_experience': self.years_experience,
            'fitness_level': self.fitness_level.value if self.fitness_level else None,
            'training_frequency': self.training_frequency,
            'has_injuries': self.has_injuries,
            'injury_description': self.injury_description,
            'medical_conditions': self.medical_conditions,
            'bmi': self.calculate_bmi(),
            'profile_completeness': self.get_profile_completeness(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'