from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///sportsai.db')  # SQLite for demo
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')

# Initialize db from models
from models import db
db.init_app(app)

# Initialize other extensions
jwt = JWTManager(app)
CORS(app)

# Import models after db initialization
from models.user import User
from models.training import TrainingPlan, TrainingSession, SessionExercise, Exercise
from models.performance import Performance, PerformanceBaseline, PerformanceReport

# Import API blueprints
from api.auth import auth_bp
from api.users import users_bp
from api.training import training_bp
from api.performance import performance_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(training_bp, url_prefix='/api/training')
app.register_blueprint(performance_bp, url_prefix='/api/performance')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Sports AI Platform is running!'})

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Sports AI Performance Platform API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth',
            'users': '/api/users',
            'training': '/api/training',
            'performance': '/api/performance'
        }
    })

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)