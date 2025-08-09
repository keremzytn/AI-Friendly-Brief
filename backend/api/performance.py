from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json
import sys
import os

from models.user import User
from models import db
from models.performance import Performance, PerformanceBaseline, PerformanceReport, TestType, PerformanceMetric

performance_bp = Blueprint('performance', __name__)

@performance_bp.route('/tests', methods=['POST'])
@jwt_required()
def record_performance_test():
    """Record a new performance test result"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['test_type', 'primary_metric', 'primary_value', 'primary_unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create performance record
        performance = Performance(
            user_id=user.id,
            test_type=data['test_type'],
            test_date=datetime.fromisoformat(data.get('test_date', datetime.utcnow().isoformat())),
            week_number=data.get('week_number'),
            primary_metric=data['primary_metric'],
            primary_value=data['primary_value'],
            primary_unit=data['primary_unit'],
            secondary_metrics=json.dumps(data.get('secondary_metrics', {})),
            test_conditions=json.dumps(data.get('test_conditions', {})),
            pre_test_state=json.dumps(data.get('pre_test_state', {})),
            tester_notes=data.get('tester_notes'),
            user_feedback=data.get('user_feedback'),
            video_url=data.get('video_url')
        )
        
        # Calculate improvements
        previous_tests = Performance.query.filter_by(
            user_id=user.id,
            test_type=data['test_type'],
            primary_metric=data['primary_metric']
        ).order_by(Performance.test_date.desc()).all()
        
        if previous_tests:
            last_test = previous_tests[0]
            performance.improvement_from_last_test = calculate_improvement(
                data['primary_value'], 
                last_test.primary_value, 
                data['test_type']
            )
        
        # Get or create baseline
        baseline = PerformanceBaseline.query.filter_by(
            user_id=user.id,
            test_type=data['test_type'],
            metric=data['primary_metric']
        ).first()
        
        if not baseline:
            # Create new baseline
            baseline = PerformanceBaseline(
                user_id=user.id,
                test_type=data['test_type'],
                metric=data['primary_metric'],
                baseline_value=data['primary_value'],
                baseline_unit=data['primary_unit'],
                baseline_date=performance.test_date,
                user_age_at_baseline=user.age,
                fitness_level_at_baseline=user.fitness_level.value if user.fitness_level else None
            )
            db.session.add(baseline)
            performance.improvement_from_baseline = 0
        else:
            # Calculate improvement from baseline
            performance.improvement_from_baseline = calculate_improvement(
                data['primary_value'],
                baseline.baseline_value,
                data['test_type']
            )
            # Update baseline current best
            baseline.update_current_best(data['primary_value'], performance.test_date)
        
        # Calculate percentile rank (simplified)
        performance.percentile_rank = calculate_percentile_rank(
            user, data['test_type'], data['primary_value']
        )
        
        # Generate AI analysis
        performance.ai_analysis = json.dumps(generate_ai_analysis(performance, previous_tests))
        performance.recommendations = json.dumps(generate_recommendations(performance, user))
        
        db.session.add(performance)
        db.session.commit()
        
        return jsonify({
            'message': 'Performance test recorded successfully',
            'performance': performance.to_dict(),
            'baseline_updated': baseline.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/tests', methods=['GET'])
@jwt_required()
def get_performance_tests():
    """Get user's performance test history"""
    try:
        current_user_id = get_jwt_identity()
        
        # Query parameters
        test_type = request.args.get('test_type')
        metric = request.args.get('metric')
        limit = int(request.args.get('limit', 20))
        weeks = int(request.args.get('weeks', 0))  # Filter by recent weeks
        
        query = Performance.query.filter_by(user_id=current_user_id)
        
        if test_type:
            query = query.filter_by(test_type=test_type)
        
        if metric:
            query = query.filter_by(primary_metric=metric)
        
        if weeks > 0:
            cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)
            query = query.filter(Performance.test_date >= cutoff_date)
        
        tests = query.order_by(Performance.test_date.desc()).limit(limit).all()
        
        return jsonify({
            'tests': [test.to_dict() for test in tests],
            'total_count': len(tests)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/tests/<int:test_id>', methods=['GET'])
@jwt_required()
def get_performance_test(test_id):
    """Get specific performance test details"""
    try:
        current_user_id = get_jwt_identity()
        
        test = Performance.query.filter_by(
            id=test_id,
            user_id=current_user_id
        ).first()
        
        if not test:
            return jsonify({'error': 'Performance test not found'}), 404
        
        return jsonify(test.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/baselines', methods=['GET'])
@jwt_required()
def get_performance_baselines():
    """Get user's performance baselines"""
    try:
        current_user_id = get_jwt_identity()
        
        baselines = PerformanceBaseline.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'baselines': [baseline.to_dict() for baseline in baselines],
            'total_count': len(baselines)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/baselines/<int:baseline_id>/targets', methods=['PUT'])
@jwt_required()
def update_performance_targets(baseline_id):
    """Update performance targets for a baseline"""
    try:
        current_user_id = get_jwt_identity()
        
        baseline = PerformanceBaseline.query.filter_by(
            id=baseline_id,
            user_id=current_user_id
        ).first()
        
        if not baseline:
            return jsonify({'error': 'Baseline not found'}), 404
        
        data = request.get_json()
        
        if 'short_term_target' in data:
            baseline.short_term_target = data['short_term_target']
        if 'medium_term_target' in data:
            baseline.medium_term_target = data['medium_term_target']
        if 'long_term_target' in data:
            baseline.long_term_target = data['long_term_target']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Targets updated successfully',
            'baseline': baseline.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/analysis', methods=['GET'])
@jwt_required()
def get_performance_analysis():
    """Get comprehensive performance analysis"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent tests (last 12 weeks)
        cutoff_date = datetime.utcnow() - timedelta(weeks=12)
        recent_tests = Performance.query.filter_by(user_id=current_user_id).filter(
            Performance.test_date >= cutoff_date
        ).order_by(Performance.test_date.desc()).all()
        
        # Get all baselines
        baselines = PerformanceBaseline.query.filter_by(user_id=current_user_id).all()
        
        # Analyze trends by test type
        trends = {}
        for test_type in TestType:
            type_tests = [t for t in recent_tests if t.test_type == test_type]
            if len(type_tests) >= 2:
                trends[test_type.value] = analyze_performance_trend(type_tests)
        
        # Overall performance score
        overall_score = calculate_overall_performance_score(baselines)
        
        # Strengths and weaknesses
        strengths, weaknesses = identify_strengths_weaknesses(baselines)
        
        # Recommendations
        recommendations = generate_comprehensive_recommendations(user, baselines, trends)
        
        analysis = {
            'overall_score': overall_score,
            'trends': trends,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': recommendations,
            'test_summary': {
                'total_tests': len(recent_tests),
                'test_types': len(set([t.test_type.value for t in recent_tests])),
                'improvement_rate': calculate_improvement_rate(recent_tests)
            },
            'baselines_summary': {
                'total_baselines': len(baselines),
                'targets_met': len([b for b in baselines if b.calculate_target_progress() >= 100]),
                'average_progress': round(sum([b.calculate_target_progress() for b in baselines]) / len(baselines), 2) if baselines else 0
            }
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/reports', methods=['POST'])
@jwt_required()
def generate_performance_report():
    """Generate comprehensive performance report"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        report_type = data.get('report_type', 'weekly')  # weekly, monthly, quarterly
        
        # Calculate period dates
        end_date = datetime.utcnow()
        if report_type == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif report_type == 'monthly':
            start_date = end_date - timedelta(days=30)
        elif report_type == 'quarterly':
            start_date = end_date - timedelta(days=90)
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        # Get tests in period
        period_tests = Performance.query.filter_by(user_id=current_user_id).filter(
            Performance.test_date >= start_date,
            Performance.test_date <= end_date
        ).all()
        
        # Get training sessions in period
        from models.training import TrainingSession, TrainingPlan
        period_sessions = db.session.query(TrainingSession).join(TrainingPlan).filter(
            TrainingPlan.user_id == current_user_id,
            TrainingSession.actual_end_time >= start_date,
            TrainingSession.actual_end_time <= end_date
        ).all()
        
        # Generate report content
        overall_progress = analyze_overall_progress(period_tests, period_sessions)
        metric_improvements = analyze_metric_improvements(period_tests)
        training_effectiveness = analyze_training_effectiveness(period_sessions, period_tests)
        ai_insights = generate_ai_insights(user, period_tests, period_sessions)
        recommendations = generate_period_recommendations(user, period_tests, period_sessions)
        risk_factors = identify_risk_factors(user, period_tests, period_sessions)
        next_period_goals = suggest_next_period_goals(user, period_tests)
        
        # Create report
        report = PerformanceReport(
            user_id=user.id,
            report_type=report_type,
            period_start=start_date,
            period_end=end_date,
            overall_progress=json.dumps(overall_progress),
            metric_improvements=json.dumps(metric_improvements),
            training_effectiveness=json.dumps(training_effectiveness),
            ai_insights=json.dumps(ai_insights),
            recommendations=json.dumps(recommendations),
            risk_factors=json.dumps(risk_factors),
            next_period_goals=json.dumps(next_period_goals)
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Performance report generated successfully',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_performance_reports():
    """Get user's performance reports"""
    try:
        current_user_id = get_jwt_identity()
        
        report_type = request.args.get('report_type')
        limit = int(request.args.get('limit', 10))
        
        query = PerformanceReport.query.filter_by(user_id=current_user_id)
        
        if report_type:
            query = query.filter_by(report_type=report_type)
        
        reports = query.order_by(PerformanceReport.generated_at.desc()).limit(limit).all()
        
        return jsonify({
            'reports': [report.to_dict() for report in reports],
            'total_count': len(reports)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@performance_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_performance_stats():
    """Get performance statistics summary"""
    try:
        current_user_id = get_jwt_identity()
        
        # Total tests
        total_tests = Performance.query.filter_by(user_id=current_user_id).count()
        
        # Tests by type
        test_counts = {}
        for test_type in TestType:
            count = Performance.query.filter_by(
                user_id=current_user_id, 
                test_type=test_type
            ).count()
            if count > 0:
                test_counts[test_type.value] = count
        
        # Recent improvements
        recent_tests = Performance.query.filter_by(user_id=current_user_id).filter(
            Performance.test_date >= datetime.utcnow() - timedelta(weeks=4)
        ).all()
        
        improved_tests = len([t for t in recent_tests if t.improvement_from_last_test and t.improvement_from_last_test > 0])
        
        # Baselines overview
        baselines = PerformanceBaseline.query.filter_by(user_id=current_user_id).all()
        targets_achieved = len([b for b in baselines if b.calculate_target_progress() >= 100])
        
        stats = {
            'totals': {
                'tests': total_tests,
                'test_types': len(test_counts),
                'baselines': len(baselines)
            },
            'test_distribution': test_counts,
            'recent_performance': {
                'total_recent_tests': len(recent_tests),
                'improved_tests': improved_tests,
                'improvement_rate': round((improved_tests / len(recent_tests)) * 100, 2) if recent_tests else 0
            },
            'goals': {
                'total_targets': len(baselines),
                'achieved_targets': targets_achieved,
                'achievement_rate': round((targets_achieved / len(baselines)) * 100, 2) if baselines else 0
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions

def calculate_improvement(current_value, previous_value, test_type):
    """Calculate improvement percentage"""
    if previous_value == 0:
        return 0
    
    # Time-based tests: lower is better
    time_based_tests = ['sprint_20m', 't_test', 'heart_rate_recovery']
    
    if test_type in time_based_tests:
        improvement = ((previous_value - current_value) / previous_value) * 100
    else:
        improvement = ((current_value - previous_value) / previous_value) * 100
    
    return round(improvement, 2)

def calculate_percentile_rank(user, test_type, value):
    """Calculate percentile rank (simplified implementation)"""
    # In a real implementation, this would compare against a database of similar athletes
    # For now, return a mock percentile based on user characteristics
    
    base_percentile = 50  # Average
    
    # Adjust based on fitness level
    if user.fitness_level and user.fitness_level.value == 'elite':
        base_percentile = 85
    elif user.fitness_level and user.fitness_level.value == 'advanced':
        base_percentile = 70
    elif user.fitness_level and user.fitness_level.value == 'intermediate':
        base_percentile = 55
    
    # Add some randomness for realism
    import random
    adjustment = random.randint(-10, 10)
    
    return max(5, min(95, base_percentile + adjustment))

def generate_ai_analysis(performance, previous_tests):
    """Generate AI analysis of performance test"""
    analysis = {
        'performance_category': 'good',
        'trend_analysis': 'stable',
        'key_insights': [],
        'technical_notes': []
    }
    
    # Analyze improvement
    if performance.improvement_from_last_test:
        if performance.improvement_from_last_test > 5:
            analysis['performance_category'] = 'excellent'
            analysis['key_insights'].append('Significant improvement from last test')
        elif performance.improvement_from_last_test > 0:
            analysis['performance_category'] = 'good'
            analysis['key_insights'].append('Positive improvement trend')
        elif performance.improvement_from_last_test < -5:
            analysis['performance_category'] = 'concerning'
            analysis['key_insights'].append('Performance decline noted')
    
    # Analyze trend over multiple tests
    if len(previous_tests) >= 3:
        values = [t.primary_value for t in previous_tests[-3:]]
        if all(values[i] <= values[i+1] for i in range(len(values)-1)):
            analysis['trend_analysis'] = 'improving'
        elif all(values[i] >= values[i+1] for i in range(len(values)-1)):
            analysis['trend_analysis'] = 'declining'
        else:
            analysis['trend_analysis'] = 'variable'
    
    return analysis

def generate_recommendations(performance, user):
    """Generate personalized recommendations"""
    recommendations = {
        'immediate_actions': [],
        'training_focus': [],
        'lifestyle_factors': [],
        'next_test_timeline': '1-2 weeks'
    }
    
    # Based on performance category
    if performance.improvement_from_last_test and performance.improvement_from_last_test > 0:
        recommendations['immediate_actions'].append('Continue current training approach')
        recommendations['training_focus'].append('Maintain intensity and progression')
    else:
        recommendations['immediate_actions'].append('Review and adjust training program')
        recommendations['training_focus'].append('Focus on technique refinement')
    
    # Based on user characteristics
    if user.age > 35:
        recommendations['lifestyle_factors'].append('Ensure adequate recovery between sessions')
        recommendations['next_test_timeline'] = '2-3 weeks'
    
    if user.has_injuries:
        recommendations['training_focus'].append('Prioritize injury prevention exercises')
    
    return recommendations

def analyze_performance_trend(tests):
    """Analyze trend in performance tests"""
    if len(tests) < 2:
        return {'trend': 'insufficient_data', 'slope': 0}
    
    values = [test.primary_value for test in sorted(tests, key=lambda x: x.test_date)]
    
    # Simple linear trend
    n = len(values)
    x_values = list(range(n))
    
    sum_x = sum(x_values)
    sum_y = sum(values)
    sum_xy = sum(x * y for x, y in zip(x_values, values))
    sum_x2 = sum(x * x for x in x_values)
    
    if n * sum_x2 - sum_x * sum_x == 0:
        return {'trend': 'stable', 'slope': 0}
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    
    if slope > 0.1:
        trend = 'improving'
    elif slope < -0.1:
        trend = 'declining'
    else:
        trend = 'stable'
    
    return {'trend': trend, 'slope': round(slope, 3)}

def calculate_overall_performance_score(baselines):
    """Calculate overall performance score"""
    if not baselines:
        return 0
    
    total_progress = sum([baseline.calculate_target_progress() for baseline in baselines])
    average_progress = total_progress / len(baselines)
    
    # Convert to 0-100 scale
    return round(min(average_progress, 100), 2)

def identify_strengths_weaknesses(baselines):
    """Identify performance strengths and weaknesses"""
    strengths = []
    weaknesses = []
    
    for baseline in baselines:
        progress = baseline.calculate_target_progress()
        metric_name = baseline.metric.value if baseline.metric else 'unknown'
        
        if progress >= 80:
            strengths.append({
                'metric': metric_name,
                'progress': progress,
                'improvement': baseline.calculate_current_improvement()
            })
        elif progress < 30:
            weaknesses.append({
                'metric': metric_name,
                'progress': progress,
                'improvement': baseline.calculate_current_improvement()
            })
    
    return strengths, weaknesses

def generate_comprehensive_recommendations(user, baselines, trends):
    """Generate comprehensive training recommendations"""
    recommendations = {
        'priority_areas': [],
        'training_adjustments': [],
        'recovery_recommendations': [],
        'testing_schedule': []
    }
    
    # Identify priority areas from weaknesses
    for baseline in baselines:
        if baseline.calculate_target_progress() < 50:
            recommendations['priority_areas'].append({
                'metric': baseline.metric.value if baseline.metric else 'unknown',
                'current_deficit': 100 - baseline.calculate_target_progress(),
                'suggested_focus': f"Increase {baseline.metric.value} training frequency"
            })
    
    # Training adjustments based on trends
    declining_trends = [k for k, v in trends.items() if v['trend'] == 'declining']
    if declining_trends:
        recommendations['training_adjustments'].append(
            f"Address declining performance in: {', '.join(declining_trends)}"
        )
    
    # Recovery recommendations based on age
    if user.age > 35:
        recommendations['recovery_recommendations'].extend([
            'Ensure 48-72h recovery between high-intensity sessions',
            'Include active recovery days',
            'Monitor sleep quality and duration'
        ])
    
    return recommendations

def calculate_improvement_rate(tests):
    """Calculate overall improvement rate"""
    if len(tests) < 2:
        return 0
    
    improved_tests = [t for t in tests if t.improvement_from_last_test and t.improvement_from_last_test > 0]
    return round((len(improved_tests) / len(tests)) * 100, 2)

def analyze_overall_progress(tests, sessions):
    """Analyze overall progress for report period"""
    return {
        'tests_completed': len(tests),
        'sessions_completed': len([s for s in sessions if s.is_completed]),
        'average_improvement': round(sum([t.improvement_from_last_test or 0 for t in tests]) / len(tests), 2) if tests else 0,
        'consistency_score': calculate_consistency_score(sessions)
    }

def analyze_metric_improvements(tests):
    """Analyze improvements by metric"""
    improvements = {}
    
    for test in tests:
        metric = test.primary_metric.value if test.primary_metric else 'unknown'
        if metric not in improvements:
            improvements[metric] = []
        
        if test.improvement_from_last_test:
            improvements[metric].append(test.improvement_from_last_test)
    
    # Calculate averages
    for metric, values in improvements.items():
        improvements[metric] = {
            'average_improvement': round(sum(values) / len(values), 2),
            'test_count': len(values),
            'best_improvement': max(values),
            'consistency': calculate_metric_consistency(values)
        }
    
    return improvements

def analyze_training_effectiveness(sessions, tests):
    """Analyze training effectiveness"""
    if not sessions:
        return {'effectiveness_score': 0, 'notes': 'No training data available'}
    
    completed_sessions = [s for s in sessions if s.is_completed]
    completion_rate = (len(completed_sessions) / len(sessions)) * 100
    
    avg_rating = sum([s.session_rating or 0 for s in completed_sessions if s.session_rating]) / len([s for s in completed_sessions if s.session_rating]) if completed_sessions else 0
    
    # Correlate with performance improvements
    improvements = [t.improvement_from_last_test or 0 for t in tests]
    avg_improvement = sum(improvements) / len(improvements) if improvements else 0
    
    effectiveness_score = (completion_rate * 0.4) + (avg_rating * 10 * 0.3) + (max(0, avg_improvement) * 0.3)
    
    return {
        'effectiveness_score': round(effectiveness_score, 2),
        'completion_rate': round(completion_rate, 2),
        'average_rating': round(avg_rating, 2),
        'average_improvement': round(avg_improvement, 2)
    }

def generate_ai_insights(user, tests, sessions):
    """Generate AI insights for the period"""
    insights = []
    
    if len(tests) >= 2:
        improvements = [t.improvement_from_last_test or 0 for t in tests]
        avg_improvement = sum(improvements) / len(improvements)
        
        if avg_improvement > 2:
            insights.append("Excellent performance improvements observed this period")
        elif avg_improvement > 0:
            insights.append("Positive performance trend maintained")
        else:
            insights.append("Performance plateaued - consider training adjustments")
    
    if sessions:
        completed_rate = (len([s for s in sessions if s.is_completed]) / len(sessions)) * 100
        if completed_rate > 90:
            insights.append("Outstanding training consistency")
        elif completed_rate < 70:
            insights.append("Training consistency could be improved")
    
    return insights

def generate_period_recommendations(user, tests, sessions):
    """Generate recommendations for next period"""
    recommendations = []
    
    # Based on performance trends
    if tests:
        avg_improvement = sum([t.improvement_from_last_test or 0 for t in tests]) / len(tests)
        if avg_improvement < 0:
            recommendations.append("Consider deload week or training modification")
        elif avg_improvement > 5:
            recommendations.append("Maintain current training intensity")
    
    # Based on training consistency
    if sessions:
        completion_rate = (len([s for s in sessions if s.is_completed]) / len(sessions)) * 100
        if completion_rate < 80:
            recommendations.append("Focus on improving training consistency")
    
    return recommendations

def identify_risk_factors(user, tests, sessions):
    """Identify potential risk factors"""
    risks = []
    
    # Performance decline risk
    if tests:
        declining_tests = [t for t in tests if t.improvement_from_last_test and t.improvement_from_last_test < -5]
        if len(declining_tests) > len(tests) * 0.5:
            risks.append({
                'type': 'performance_decline',
                'severity': 'high',
                'description': 'Multiple performance metrics showing decline'
            })
    
    # Overtraining risk
    if sessions:
        high_exertion_sessions = [s for s in sessions if s.perceived_exertion and s.perceived_exertion > 8]
        if len(high_exertion_sessions) > len(sessions) * 0.7:
            risks.append({
                'type': 'overtraining',
                'severity': 'medium',
                'description': 'High perceived exertion in most sessions'
            })
    
    return risks

def suggest_next_period_goals(user, tests):
    """Suggest goals for next period"""
    goals = []
    
    if tests:
        # Suggest improvement targets based on recent performance
        for test in tests[-3:]:  # Last 3 tests
            metric = test.primary_metric.value if test.primary_metric else 'unknown'
            current_value = test.primary_value
            
            # Suggest 2-5% improvement
            improvement_target = current_value * 1.03  # 3% improvement
            
            goals.append({
                'metric': metric,
                'current_value': current_value,
                'target_value': round(improvement_target, 2),
                'target_timeframe': '4 weeks'
            })
    
    return goals

def calculate_consistency_score(sessions):
    """Calculate training consistency score"""
    if not sessions:
        return 0
    
    completed_sessions = [s for s in sessions if s.is_completed]
    completion_rate = len(completed_sessions) / len(sessions)
    
    # Factor in rating consistency
    ratings = [s.session_rating for s in completed_sessions if s.session_rating]
    if ratings:
        rating_variance = sum([(r - sum(ratings)/len(ratings))**2 for r in ratings]) / len(ratings)
        consistency_factor = max(0, 1 - rating_variance/10)  # Normalize variance
    else:
        consistency_factor = 1
    
    return round(completion_rate * consistency_factor * 100, 2)

def calculate_metric_consistency(values):
    """Calculate consistency score for a metric"""
    if len(values) < 2:
        return 100
    
    mean_val = sum(values) / len(values)
    variance = sum([(v - mean_val)**2 for v in values]) / len(values)
    
    # Convert to consistency score (lower variance = higher consistency)
    consistency = max(0, 100 - (variance * 10))
    return round(consistency, 2)