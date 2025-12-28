"""
FedxSmart: Dynamic Route Optimization & Emission Reduction Platform
Main application entry point
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import logging
from datetime import datetime

from src.api.routes import api_bp
from src.services.route_optimizer import RouteOptimizer
from src.services.emission_calculator import EmissionCalculator
from src.services.analytics_engine import AnalyticsEngine
from config.settings import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
route_optimizer = RouteOptimizer()
emission_calculator = EmissionCalculator()
analytics_engine = AnalyticsEngine()

# Register API blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': {
            'route_optimizer': 'active',
            'emission_calculator': 'active',
            'analytics_engine': 'active'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting FedxSmart Platform...")
    logger.info(f"Environment: {Config.ENVIRONMENT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )