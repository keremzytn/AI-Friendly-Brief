import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import json
from datetime import datetime, timedelta
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TrainingOptimizer:
    """AI-powered training program optimizer"""
    
    def __init__(self):
        self.progression_model = None
        self.exercise_selector = None
        self.load_balancer = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def generate_training_plan(self, user_profile, current_week=1, performance_history=None):
        """
        Generate AI-optimized training plan for user
        
        Args:
            user_profile: Dict containing user information
            current_week: Current training week number
            performance_history: List of previous performance test results
            
        Returns:
            Dict containing complete training plan
        """
        try:
            # Analyze user profile and needs
            user_analysis = self._analyze_user_profile(user_profile)
            
            # Determine training focus based on sport and week
            training_focus = self._determine_training_focus(
                user_profile['sport_type'],
                current_week,
                user_analysis
            )
            
            # Generate exercise selection
            exercises = self._select_exercises(user_profile, training_focus)
            
            # Optimize training parameters
            training_params = self._optimize_training_parameters(
                user_profile, 
                performance_history,
                current_week
            )
            
            # Create weekly plan structure
            weekly_plan = self._create_weekly_plan(
                exercises, 
                training_params, 
                user_profile['training_frequency']
            )
            
            # Generate specific adaptations
            target_adaptations = self._generate_target_adaptations(
                user_profile,
                training_focus,
                current_week
            )
            
            return {
                'plan_name': f"Week {current_week} - {training_focus['primary_type']} Focus",
                'week_number': current_week,
                'training_type': training_focus['primary_type'],
                'target_adaptations': target_adaptations,
                'expected_duration': training_params['total_duration'],
                'difficulty_score': training_params['difficulty_score'],
                'sessions': weekly_plan,
                'model_version': '1.0',
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error generating training plan: {str(e)}")
    
    def predict_performance_improvement(self, user_profile, training_plan, weeks_ahead=4):
        """
        Predict expected performance improvements
        
        Args:
            user_profile: User profile data
            training_plan: Training plan data
            weeks_ahead: Number of weeks to predict
            
        Returns:
            Dict with predicted improvements by metric
        """
        try:
            # Base improvement rates by age and fitness level
            base_rates = self._get_base_improvement_rates(
                user_profile['age'],
                user_profile['fitness_level']
            )
            
            # Training type multipliers
            training_multipliers = self._get_training_multipliers(
                training_plan['training_type']
            )
            
            # Sport-specific factors
            sport_factors = self._get_sport_factors(user_profile['sport_type'])
            
            predictions = {}
            
            for metric, base_rate in base_rates.items():
                multiplier = training_multipliers.get(metric, 1.0)
                sport_factor = sport_factors.get(metric, 1.0)
                
                # Calculate predicted improvement
                weekly_improvement = base_rate * multiplier * sport_factor
                total_improvement = weekly_improvement * weeks_ahead
                
                # Add some variation based on user characteristics
                if user_profile.get('years_experience', 0) > 5:
                    total_improvement *= 0.8  # Experienced athletes improve slower
                
                if user_profile.get('age', 25) > 30:
                    total_improvement *= 0.9  # Older athletes improve slower
                
                predictions[metric] = {
                    'expected_improvement_percentage': round(total_improvement, 2),
                    'confidence_score': self._calculate_confidence_score(user_profile, metric),
                    'weekly_rate': round(weekly_improvement, 2)
                }
            
            return predictions
            
        except Exception as e:
            raise Exception(f"Error predicting performance: {str(e)}")
    
    def optimize_exercise_load(self, exercise_type, user_profile, performance_history=None):
        """
        Optimize exercise load (sets, reps, intensity) based on user data
        
        Args:
            exercise_type: Type of exercise
            user_profile: User profile data
            performance_history: Recent performance data
            
        Returns:
            Dict with optimized exercise parameters
        """
        try:
            # Base parameters by fitness level
            base_params = self._get_base_exercise_parameters(
                exercise_type,
                user_profile['fitness_level']
            )
            
            # Adjust based on training experience
            experience_factor = min(user_profile.get('years_experience', 1) / 10, 1.0)
            
            # Adjust based on age
            age_factor = 1.0 if user_profile['age'] < 30 else 0.9
            
            # Adjust based on recent performance
            performance_factor = 1.0
            if performance_history:
                recent_trend = self._analyze_performance_trend(performance_history)
                if recent_trend > 0:
                    performance_factor = 1.1  # Increase load if improving
                elif recent_trend < -5:
                    performance_factor = 0.9  # Decrease load if declining
            
            # Calculate optimized parameters
            sets = max(1, int(base_params['sets'] * experience_factor * age_factor))
            
            if base_params['reps_type'] == 'range':
                min_reps = max(1, int(base_params['reps_min'] * performance_factor))
                max_reps = max(min_reps + 2, int(base_params['reps_max'] * performance_factor))
                reps = f"{min_reps}-{max_reps}"
            else:
                reps = str(max(1, int(base_params['reps'] * performance_factor)))
            
            intensity = min(100, base_params['intensity'] * performance_factor)
            
            return {
                'sets': sets,
                'reps': reps,
                'intensity': self._intensity_to_level(intensity),
                'rest_time': base_params['rest_time'],
                'load_factor': performance_factor,
                'progression_notes': self._generate_progression_notes(
                    exercise_type, performance_factor
                )
            }
            
        except Exception as e:
            raise Exception(f"Error optimizing exercise load: {str(e)}")
    
    # Private helper methods
    
    def _analyze_user_profile(self, profile):
        """Analyze user profile to determine training needs"""
        analysis = {
            'primary_weakness': None,
            'injury_considerations': profile.get('has_injuries', False),
            'training_capacity': 'moderate',
            'recovery_needs': 'standard'
        }
        
        # Determine training capacity based on experience and frequency
        experience = profile.get('years_experience', 0)
        frequency = profile.get('training_frequency', 3)
        
        if experience >= 5 and frequency >= 5:
            analysis['training_capacity'] = 'high'
        elif experience <= 2 or frequency <= 2:
            analysis['training_capacity'] = 'low'
        
        # Determine recovery needs based on age
        if profile.get('age', 25) > 35:
            analysis['recovery_needs'] = 'extended'
        elif profile.get('age', 25) < 25:
            analysis['recovery_needs'] = 'quick'
        
        return analysis
    
    def _determine_training_focus(self, sport_type, week, user_analysis):
        """Determine training focus for the week"""
        # Periodization model: alternate between different focuses
        week_cycle = (week - 1) % 4
        
        base_focuses = {
            0: {'primary_type': 'strength', 'secondary_type': 'power'},
            1: {'primary_type': 'hiit', 'secondary_type': 'agility'},
            2: {'primary_type': 'endurance', 'secondary_type': 'sport_specific'},
            3: {'primary_type': 'agility', 'secondary_type': 'flexibility'}
        }
        
        focus = base_focuses[week_cycle].copy()
        
        # Sport-specific adjustments
        sport_adjustments = {
            'football': {'strength': 1.2, 'agility': 1.3, 'power': 1.1},
            'basketball': {'agility': 1.3, 'hiit': 1.2, 'power': 1.1},
            'tennis': {'agility': 1.4, 'endurance': 1.1, 'flexibility': 1.2},
            'running': {'endurance': 1.4, 'hiit': 1.2, 'strength': 0.9},
            'cycling': {'endurance': 1.3, 'strength': 1.1, 'hiit': 1.1},
            'swimming': {'endurance': 1.3, 'flexibility': 1.2, 'strength': 1.1}
        }
        
        if sport_type in sport_adjustments:
            focus['sport_adjustments'] = sport_adjustments[sport_type]
        
        return focus
    
    def _select_exercises(self, user_profile, training_focus):
        """Select appropriate exercises based on profile and focus"""
        sport_type = user_profile['sport_type']
        fitness_level = user_profile['fitness_level']
        
        # Exercise database by type and sport
        exercise_db = {
            'strength': {
                'beginner': ['bodyweight_squats', 'push_ups', 'planks', 'lunges'],
                'intermediate': ['goblet_squats', 'deadlifts', 'bench_press', 'rows'],
                'advanced': ['back_squats', 'deadlifts', 'bench_press', 'clean_pulls'],
                'elite': ['back_squats', 'deadlifts', 'power_cleans', 'snatches']
            },
            'hiit': {
                'beginner': ['burpees', 'mountain_climbers', 'jumping_jacks', 'high_knees'],
                'intermediate': ['box_jumps', 'battle_ropes', 'kettlebell_swings', 'sprints'],
                'advanced': ['plyometric_jumps', 'medicine_ball_slams', 'sprint_intervals'],
                'elite': ['depth_jumps', 'reactive_jumps', 'olympic_lift_complexes']
            },
            'agility': {
                'all': ['ladder_drills', 't_test', 'cone_drills', '5_10_5_drill', 'reactive_drills']
            },
            'endurance': {
                'all': ['tempo_runs', 'bike_intervals', 'swimming_sets', 'rowing_intervals']
            },
            'sport_specific': {
                'football': ['40_yard_dash', 'position_drills', 'tackling_drills'],
                'basketball': ['suicide_drills', 'defensive_slides', 'shooting_drills'],
                'tennis': ['court_sprints', 'serve_practice', 'volley_drills'],
                'running': ['interval_training', 'hill_repeats', 'tempo_runs'],
                'cycling': ['hill_climbs', 'sprint_intervals', 'time_trials'],
                'swimming': ['stroke_technique', 'flip_turns', 'breathing_drills']
            }
        }
        
        selected_exercises = []
        
        # Select primary focus exercises
        primary_type = training_focus['primary_type']
        if primary_type in exercise_db:
            if fitness_level in exercise_db[primary_type]:
                selected_exercises.extend(exercise_db[primary_type][fitness_level][:3])
            elif 'all' in exercise_db[primary_type]:
                selected_exercises.extend(exercise_db[primary_type]['all'][:3])
        
        # Add sport-specific exercises
        if sport_type in exercise_db.get('sport_specific', {}):
            selected_exercises.extend(exercise_db['sport_specific'][sport_type][:2])
        
        return selected_exercises[:6]  # Limit to 6 exercises per session
    
    def _optimize_training_parameters(self, user_profile, performance_history, week):
        """Optimize training parameters based on user data"""
        base_duration = 45  # minutes
        base_difficulty = 5  # 1-10 scale
        
        # Adjust based on fitness level
        level_adjustments = {
            'beginner': {'duration': 0.8, 'difficulty': 0.7},
            'intermediate': {'duration': 1.0, 'difficulty': 1.0},
            'advanced': {'duration': 1.2, 'difficulty': 1.2},
            'elite': {'duration': 1.4, 'difficulty': 1.4}
        }
        
        fitness_level = user_profile.get('fitness_level', 'intermediate')
        adjustments = level_adjustments.get(fitness_level, level_adjustments['intermediate'])
        
        duration = int(base_duration * adjustments['duration'])
        difficulty = min(10, base_difficulty * adjustments['difficulty'])
        
        # Progressive overload based on week
        week_progression = 1 + ((week - 1) * 0.05)  # 5% increase per week
        difficulty *= min(week_progression, 1.5)  # Cap at 50% increase
        
        return {
            'total_duration': duration,
            'difficulty_score': round(difficulty, 1),
            'week_progression': week_progression
        }
    
    def _create_weekly_plan(self, exercises, training_params, frequency):
        """Create weekly training plan structure"""
        sessions = []
        
        for day in range(1, frequency + 1):
            session = {
                'session_number': day,
                'session_name': f"Training Day {day}",
                'primary_focus': self._get_daily_focus(day, frequency),
                'exercises': exercises,
                'warm_up_duration': 10,
                'main_duration': training_params['total_duration'] - 20,
                'cool_down_duration': 10,
                'difficulty_level': training_params['difficulty_score']
            }
            sessions.append(session)
        
        return sessions
    
    def _get_daily_focus(self, day, frequency):
        """Get daily training focus based on frequency"""
        if frequency <= 3:
            focuses = ['Full Body', 'Upper Body', 'Lower Body']
        elif frequency <= 5:
            focuses = ['Power', 'Strength', 'Endurance', 'Agility', 'Recovery']
        else:
            focuses = ['Power', 'Strength', 'Endurance', 'Agility', 'Sport-Specific', 'Recovery', 'Active Recovery']
        
        return focuses[(day - 1) % len(focuses)]
    
    def _generate_target_adaptations(self, user_profile, training_focus, week):
        """Generate target physiological adaptations"""
        adaptations = {
            'muscle_fiber_types': {
                'type_2_activation': 0.7,  # Focus on Type 2 fibers
                'type_1_endurance': 0.3
            },
            'energy_systems': {
                'phosphocreatine': 0.4,
                'glycolytic': 0.4,
                'oxidative': 0.2
            },
            'neuromuscular': {
                'power_output': 0.8,
                'coordination': 0.6,
                'reaction_time': 0.5
            },
            'mitochondrial': {
                'density_increase': 0.3,
                'enzyme_activity': 0.4
            }
        }
        
        # Adjust based on training focus
        if training_focus['primary_type'] == 'strength':
            adaptations['muscle_fiber_types']['type_2_activation'] = 0.9
            adaptations['neuromuscular']['power_output'] = 0.9
        elif training_focus['primary_type'] == 'endurance':
            adaptations['mitochondrial']['density_increase'] = 0.8
            adaptations['energy_systems']['oxidative'] = 0.6
        elif training_focus['primary_type'] == 'hiit':
            adaptations['energy_systems']['glycolytic'] = 0.7
            adaptations['muscle_fiber_types']['type_2_activation'] = 0.8
        
        return adaptations
    
    def _get_base_improvement_rates(self, age, fitness_level):
        """Get base weekly improvement rates by metric"""
        base_rates = {
            'power': 2.0,      # % per week
            'speed': 1.5,
            'agility': 1.8,
            'endurance': 2.5,
            'strength': 2.2,
            'flexibility': 1.0
        }
        
        # Age adjustments
        if age > 30:
            for metric in base_rates:
                base_rates[metric] *= 0.9
        if age > 40:
            for metric in base_rates:
                base_rates[metric] *= 0.8
        
        # Fitness level adjustments
        level_multipliers = {
            'beginner': 1.5,
            'intermediate': 1.0,
            'advanced': 0.7,
            'elite': 0.5
        }
        
        multiplier = level_multipliers.get(fitness_level, 1.0)
        for metric in base_rates:
            base_rates[metric] *= multiplier
        
        return base_rates
    
    def _get_training_multipliers(self, training_type):
        """Get training type multipliers for different metrics"""
        multipliers = {
            'strength': {
                'power': 1.3,
                'strength': 1.5,
                'speed': 1.1,
                'agility': 0.9,
                'endurance': 0.8
            },
            'hiit': {
                'power': 1.4,
                'speed': 1.3,
                'agility': 1.2,
                'endurance': 1.2,
                'strength': 1.0
            },
            'endurance': {
                'endurance': 1.5,
                'speed': 1.1,
                'power': 0.8,
                'agility': 0.9,
                'strength': 0.9
            },
            'agility': {
                'agility': 1.5,
                'speed': 1.2,
                'power': 1.1,
                'endurance': 0.9,
                'strength': 0.9
            }
        }
        
        return multipliers.get(training_type, {})
    
    def _get_sport_factors(self, sport_type):
        """Get sport-specific improvement factors"""
        factors = {
            'football': {
                'power': 1.2,
                'strength': 1.3,
                'agility': 1.2,
                'speed': 1.1
            },
            'basketball': {
                'agility': 1.3,
                'power': 1.2,
                'endurance': 1.1,
                'speed': 1.1
            },
            'tennis': {
                'agility': 1.4,
                'speed': 1.2,
                'endurance': 1.1,
                'flexibility': 1.2
            },
            'running': {
                'endurance': 1.4,
                'speed': 1.2,
                'power': 0.9
            },
            'cycling': {
                'endurance': 1.3,
                'power': 1.1,
                'strength': 1.1
            },
            'swimming': {
                'endurance': 1.3,
                'flexibility': 1.2,
                'strength': 1.1
            }
        }
        
        return factors.get(sport_type, {})
    
    def _calculate_confidence_score(self, user_profile, metric):
        """Calculate confidence score for prediction"""
        base_confidence = 0.7
        
        # Higher confidence for experienced users
        experience = user_profile.get('years_experience', 0)
        if experience >= 3:
            base_confidence += 0.1
        
        # Lower confidence for older athletes (more variable)
        age = user_profile.get('age', 25)
        if age > 35:
            base_confidence -= 0.1
        
        # Metric-specific adjustments
        metric_confidence = {
            'strength': 0.8,
            'endurance': 0.75,
            'power': 0.7,
            'agility': 0.65,
            'speed': 0.7,
            'flexibility': 0.6
        }
        
        final_confidence = base_confidence * metric_confidence.get(metric, 0.7)
        return round(min(max(final_confidence, 0.3), 0.95), 2)
    
    def _get_base_exercise_parameters(self, exercise_type, fitness_level):
        """Get base exercise parameters"""
        parameters = {
            'strength': {
                'beginner': {'sets': 2, 'reps': 12, 'reps_type': 'fixed', 'intensity': 60, 'rest_time': 90},
                'intermediate': {'sets': 3, 'reps_min': 8, 'reps_max': 12, 'reps_type': 'range', 'intensity': 70, 'rest_time': 120},
                'advanced': {'sets': 4, 'reps_min': 6, 'reps_max': 10, 'reps_type': 'range', 'intensity': 80, 'rest_time': 150},
                'elite': {'sets': 5, 'reps_min': 4, 'reps_max': 8, 'reps_type': 'range', 'intensity': 85, 'rest_time': 180}
            },
            'power': {
                'beginner': {'sets': 3, 'reps': 8, 'reps_type': 'fixed', 'intensity': 70, 'rest_time': 120},
                'intermediate': {'sets': 4, 'reps_min': 6, 'reps_max': 8, 'reps_type': 'range', 'intensity': 80, 'rest_time': 150},
                'advanced': {'sets': 5, 'reps_min': 4, 'reps_max': 6, 'reps_type': 'range', 'intensity': 85, 'rest_time': 180},
                'elite': {'sets': 6, 'reps_min': 3, 'reps_max': 5, 'reps_type': 'range', 'intensity': 90, 'rest_time': 200}
            },
            'endurance': {
                'all': {'sets': 3, 'reps': 20, 'reps_type': 'fixed', 'intensity': 60, 'rest_time': 60}
            }
        }
        
        if exercise_type in parameters:
            if fitness_level in parameters[exercise_type]:
                return parameters[exercise_type][fitness_level]
            elif 'all' in parameters[exercise_type]:
                return parameters[exercise_type]['all']
        
        # Default parameters
        return {'sets': 3, 'reps': 10, 'reps_type': 'fixed', 'intensity': 70, 'rest_time': 90}
    
    def _intensity_to_level(self, intensity_percent):
        """Convert intensity percentage to level"""
        if intensity_percent >= 90:
            return 'maximal'
        elif intensity_percent >= 80:
            return 'very_high'
        elif intensity_percent >= 70:
            return 'high'
        elif intensity_percent >= 60:
            return 'moderate'
        else:
            return 'low'
    
    def _analyze_performance_trend(self, performance_history):
        """Analyze recent performance trend"""
        if not performance_history or len(performance_history) < 2:
            return 0
        
        # Calculate simple trend over last few tests
        values = [test.get('primary_value', 0) for test in performance_history[-3:]]
        if len(values) < 2:
            return 0
        
        # Calculate percentage change
        initial_value = values[0]
        final_value = values[-1]
        
        if initial_value == 0:
            return 0
        
        change_percent = ((final_value - initial_value) / initial_value) * 100
        return round(change_percent, 2)
    
    def _generate_progression_notes(self, exercise_type, load_factor):
        """Generate progression notes for exercises"""
        if load_factor > 1.05:
            return f"Increase load by {round((load_factor - 1) * 100, 1)}% based on recent improvements"
        elif load_factor < 0.95:
            return f"Reduce load by {round((1 - load_factor) * 100, 1)}% to allow for recovery"
        else:
            return "Maintain current load and focus on form"