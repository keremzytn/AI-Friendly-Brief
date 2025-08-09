from datetime import datetime
from enum import Enum
import json
from . import db

class TestType(Enum):
    VERTICAL_JUMP = "vertical_jump"      # Patlayıcı güç
    SPRINT_20M = "sprint_20m"            # Hız
    T_TEST = "t_test"                    # Çeviklik
    HEART_RATE_RECOVERY = "heart_rate_recovery"  # Kardiyorespiratuar kapasite
    VO2_MAX = "vo2_max"                  # Maksimal oksijen tüketimi
    FLEXIBILITY = "flexibility"          # Esneklik
    STRENGTH_1RM = "strength_1rm"        # Maksimal güç
    ENDURANCE = "endurance"              # Dayanıklılık
    SPORT_SPECIFIC = "sport_specific"    # Spor branşına özel testler

class PerformanceMetric(Enum):
    # Physical metrics
    POWER = "power"
    SPEED = "speed"
    AGILITY = "agility"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    
    # Physiological metrics
    HEART_RATE = "heart_rate"
    RECOVERY_RATE = "recovery_rate"
    VO2_MAX = "vo2_max"
    LACTATE_THRESHOLD = "lactate_threshold"
    
    # Sport-specific metrics
    REACTION_TIME = "reaction_time"
    COORDINATION = "coordination"
    BALANCE = "balance"
    TECHNIQUE_SCORE = "technique_score"

class Performance(db.Model):
    __tablename__ = 'performances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Test information
    test_type = db.Column(db.Enum(TestType), nullable=False)
    test_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    week_number = db.Column(db.Integer)  # Training week when test was performed
    
    # Test results
    primary_metric = db.Column(db.Enum(PerformanceMetric), nullable=False)
    primary_value = db.Column(db.Float, nullable=False)
    primary_unit = db.Column(db.String(20), nullable=False)  # cm, seconds, bpm, etc.
    
    # Additional metrics (JSON format)
    secondary_metrics = db.Column(db.Text)  # JSON: {metric: {value: x, unit: y}}
    
    # Test conditions
    test_conditions = db.Column(db.Text)  # JSON: weather, equipment, etc.
    pre_test_state = db.Column(db.Text)   # JSON: fatigue level, sleep, nutrition
    
    # Performance analysis
    improvement_from_baseline = db.Column(db.Float)  # Percentage improvement
    improvement_from_last_test = db.Column(db.Float) # Percentage improvement
    percentile_rank = db.Column(db.Float)  # Ranking among similar athletes
    
    # AI analysis
    ai_analysis = db.Column(db.Text)      # JSON: AI insights about performance
    recommendations = db.Column(db.Text)  # JSON: AI recommendations
    
    # Notes and observations
    tester_notes = db.Column(db.Text)
    user_feedback = db.Column(db.Text)
    video_url = db.Column(db.String(500))  # Recording of the test
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_secondary_metrics(self):
        """Get secondary metrics as dict"""
        if self.secondary_metrics:
            return json.loads(self.secondary_metrics)
        return {}
    
    def get_test_conditions(self):
        """Get test conditions as dict"""
        if self.test_conditions:
            return json.loads(self.test_conditions)
        return {}
    
    def get_pre_test_state(self):
        """Get pre-test state as dict"""
        if self.pre_test_state:
            return json.loads(self.pre_test_state)
        return {}
    
    def get_ai_analysis(self):
        """Get AI analysis as dict"""
        if self.ai_analysis:
            return json.loads(self.ai_analysis)
        return {}
    
    def get_recommendations(self):
        """Get recommendations as dict"""
        if self.recommendations:
            return json.loads(self.recommendations)
        return {}
    
    def calculate_improvement_trend(self, previous_tests):
        """Calculate improvement trend over time"""
        if not previous_tests:
            return None
        
        # Calculate trend over last 4-6 tests
        values = [test.primary_value for test in previous_tests[-6:]]
        values.append(self.primary_value)
        
        if len(values) < 3:
            return None
        
        # Simple linear trend calculation
        x_values = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Return percentage trend per test
        avg_value = sum_y / n
        trend_percentage = (slope / avg_value) * 100 if avg_value != 0 else 0
        
        return round(trend_percentage, 2)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'test_type': self.test_type.value if self.test_type else None,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'week_number': self.week_number,
            'primary_metric': self.primary_metric.value if self.primary_metric else None,
            'primary_value': self.primary_value,
            'primary_unit': self.primary_unit,
            'secondary_metrics': self.get_secondary_metrics(),
            'test_conditions': self.get_test_conditions(),
            'pre_test_state': self.get_pre_test_state(),
            'improvement_from_baseline': self.improvement_from_baseline,
            'improvement_from_last_test': self.improvement_from_last_test,
            'percentile_rank': self.percentile_rank,
            'ai_analysis': self.get_ai_analysis(),
            'recommendations': self.get_recommendations(),
            'tester_notes': self.tester_notes,
            'user_feedback': self.user_feedback,
            'video_url': self.video_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PerformanceBaseline(db.Model):
    __tablename__ = 'performance_baselines'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Baseline information
    test_type = db.Column(db.Enum(TestType), nullable=False)
    metric = db.Column(db.Enum(PerformanceMetric), nullable=False)
    baseline_value = db.Column(db.Float, nullable=False)
    baseline_unit = db.Column(db.String(20), nullable=False)
    
    # Baseline context
    baseline_date = db.Column(db.DateTime, nullable=False)
    user_age_at_baseline = db.Column(db.Integer)
    fitness_level_at_baseline = db.Column(db.String(20))
    
    # Target setting
    short_term_target = db.Column(db.Float)    # 4-6 weeks
    medium_term_target = db.Column(db.Float)   # 3 months
    long_term_target = db.Column(db.Float)     # 6-12 months
    
    # Tracking
    current_best = db.Column(db.Float)
    current_best_date = db.Column(db.DateTime)
    tests_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_current_improvement(self):
        """Calculate current improvement from baseline"""
        if not self.current_best:
            return 0
        
        # Different calculation for metrics where lower is better (time-based)
        time_based_metrics = [TestType.SPRINT_20M, TestType.T_TEST]
        
        if self.test_type in time_based_metrics:
            # For time-based: improvement = (baseline - current) / baseline * 100
            improvement = ((self.baseline_value - self.current_best) / self.baseline_value) * 100
        else:
            # For distance/power-based: improvement = (current - baseline) / baseline * 100
            improvement = ((self.current_best - self.baseline_value) / self.baseline_value) * 100
        
        return round(improvement, 2)
    
    def calculate_target_progress(self, target_type='short_term'):
        """Calculate progress towards target"""
        targets = {
            'short_term': self.short_term_target,
            'medium_term': self.medium_term_target,
            'long_term': self.long_term_target
        }
        
        target = targets.get(target_type)
        if not target or not self.current_best:
            return 0
        
        # Calculate progress percentage
        total_improvement_needed = abs(target - self.baseline_value)
        current_improvement = abs(self.current_best - self.baseline_value)
        
        if total_improvement_needed == 0:
            return 100
        
        progress = (current_improvement / total_improvement_needed) * 100
        return min(round(progress, 2), 100)  # Cap at 100%
    
    def update_current_best(self, new_value, test_date):
        """Update current best if new value is better"""
        time_based_metrics = [TestType.SPRINT_20M, TestType.T_TEST]
        
        should_update = False
        
        if self.current_best is None:
            should_update = True
        elif self.test_type in time_based_metrics:
            # For time-based metrics, lower is better
            should_update = new_value < self.current_best
        else:
            # For other metrics, higher is better
            should_update = new_value > self.current_best
        
        if should_update:
            self.current_best = new_value
            self.current_best_date = test_date
            self.updated_at = datetime.utcnow()
        
        self.tests_count += 1
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'test_type': self.test_type.value if self.test_type else None,
            'metric': self.metric.value if self.metric else None,
            'baseline_value': self.baseline_value,
            'baseline_unit': self.baseline_unit,
            'baseline_date': self.baseline_date.isoformat() if self.baseline_date else None,
            'user_age_at_baseline': self.user_age_at_baseline,
            'fitness_level_at_baseline': self.fitness_level_at_baseline,
            'short_term_target': self.short_term_target,
            'medium_term_target': self.medium_term_target,
            'long_term_target': self.long_term_target,
            'current_best': self.current_best,
            'current_best_date': self.current_best_date.isoformat() if self.current_best_date else None,
            'tests_count': self.tests_count,
            'current_improvement': self.calculate_current_improvement(),
            'short_term_progress': self.calculate_target_progress('short_term'),
            'medium_term_progress': self.calculate_target_progress('medium_term'),
            'long_term_progress': self.calculate_target_progress('long_term'),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PerformanceReport(db.Model):
    __tablename__ = 'performance_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Report metadata
    report_type = db.Column(db.String(50), nullable=False)  # weekly, monthly, quarterly
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    
    # Performance summary (JSON)
    overall_progress = db.Column(db.Text)  # JSON: overall performance summary
    metric_improvements = db.Column(db.Text)  # JSON: improvements by metric
    training_effectiveness = db.Column(db.Text)  # JSON: training program effectiveness
    
    # AI insights
    ai_insights = db.Column(db.Text)  # JSON: AI-generated insights
    recommendations = db.Column(db.Text)  # JSON: recommendations for next period
    risk_factors = db.Column(db.Text)  # JSON: identified risk factors
    
    # Goals and targets
    next_period_goals = db.Column(db.Text)  # JSON: goals for next period
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_overall_progress(self):
        if self.overall_progress:
            return json.loads(self.overall_progress)
        return {}
    
    def get_metric_improvements(self):
        if self.metric_improvements:
            return json.loads(self.metric_improvements)
        return {}
    
    def get_training_effectiveness(self):
        if self.training_effectiveness:
            return json.loads(self.training_effectiveness)
        return {}
    
    def get_ai_insights(self):
        if self.ai_insights:
            return json.loads(self.ai_insights)
        return {}
    
    def get_recommendations(self):
        if self.recommendations:
            return json.loads(self.recommendations)
        return {}
    
    def get_risk_factors(self):
        if self.risk_factors:
            return json.loads(self.risk_factors)
        return {}
    
    def get_next_period_goals(self):
        if self.next_period_goals:
            return json.loads(self.next_period_goals)
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'overall_progress': self.get_overall_progress(),
            'metric_improvements': self.get_metric_improvements(),
            'training_effectiveness': self.get_training_effectiveness(),
            'ai_insights': self.get_ai_insights(),
            'recommendations': self.get_recommendations(),
            'risk_factors': self.get_risk_factors(),
            'next_period_goals': self.get_next_period_goals(),
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }