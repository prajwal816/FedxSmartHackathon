"""
API routes for FedxSmart Platform
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from ..services.route_optimizer import RouteOptimizer
from ..services.emission_calculator import EmissionCalculator
from ..services.analytics_engine import AnalyticsEngine
from ..services.scenario_analyzer import ScenarioAnalyzer

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Initialize services
route_optimizer = RouteOptimizer()
emission_calculator = EmissionCalculator()
analytics_engine = AnalyticsEngine()
scenario_analyzer = ScenarioAnalyzer()

@api_bp.route('/optimize-route', methods=['POST'])
def optimize_route():
    """
    Optimize delivery route with real-time data
    
    Expected payload:
    {
        "origin": {"lat": 40.7128, "lng": -74.0060},
        "destinations": [
            {"lat": 40.7589, "lng": -73.9851, "priority": 1},
            {"lat": 40.6892, "lng": -74.0445, "priority": 2}
        ],
        "vehicle_type": "diesel_truck",
        "constraints": {
            "max_capacity": 1000,
            "max_duration": 480
        },
        "preferences": {
            "optimize_for": "time", // "time", "fuel", "emissions"
            "avoid_tolls": false,
            "avoid_highways": false
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'origin' not in data or 'destinations' not in data:
            return jsonify({'error': 'Missing required fields: origin, destinations'}), 400
        
        # Optimize route
        result = route_optimizer.optimize(
            origin=data['origin'],
            destinations=data['destinations'],
            vehicle_type=data.get('vehicle_type', 'diesel_truck'),
            constraints=data.get('constraints', {}),
            preferences=data.get('preferences', {})
        )
        
        # Calculate emissions for optimized route
        emissions = emission_calculator.calculate_route_emissions(
            route=result['optimized_route'],
            vehicle_type=data.get('vehicle_type', 'diesel_truck')
        )
        
        # Combine results
        response = {
            'route_id': result['route_id'],
            'optimized_route': result['optimized_route'],
            'optimization_metrics': result['metrics'],
            'emissions': emissions,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Route optimized successfully: {result['route_id']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Route optimization failed: {str(e)}")
        return jsonify({'error': 'Route optimization failed'}), 500

@api_bp.route('/emissions/<route_id>', methods=['GET'])
def get_emissions(route_id):
    """Get detailed emission data for a specific route"""
    try:
        emissions_data = emission_calculator.get_detailed_emissions(route_id)
        
        if not emissions_data:
            return jsonify({'error': 'Route not found'}), 404
            
        return jsonify(emissions_data)
        
    except Exception as e:
        logger.error(f"Failed to get emissions for route {route_id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve emissions data'}), 500

@api_bp.route('/scenario-analysis', methods=['POST'])
def scenario_analysis():
    """
    Run what-if scenario analysis
    
    Expected payload:
    {
        "base_route_id": "route_123",
        "scenarios": [
            {
                "name": "peak_traffic",
                "conditions": {
                    "traffic_multiplier": 1.5,
                    "time_of_day": "08:00"
                }
            },
            {
                "name": "electric_vehicle",
                "conditions": {
                    "vehicle_type": "electric_truck"
                }
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'base_route_id' not in data or 'scenarios' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        analysis_results = scenario_analyzer.analyze_scenarios(
            base_route_id=data['base_route_id'],
            scenarios=data['scenarios']
        )
        
        return jsonify(analysis_results)
        
    except Exception as e:
        logger.error(f"Scenario analysis failed: {str(e)}")
        return jsonify({'error': 'Scenario analysis failed'}), 500

@api_bp.route('/analytics/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard analytics data"""
    try:
        # Get query parameters
        time_range = request.args.get('time_range', '24h')
        
        dashboard_data = analytics_engine.get_dashboard_metrics(time_range)
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        return jsonify({'error': 'Failed to retrieve dashboard data'}), 500

@api_bp.route('/analytics/comparison', methods=['POST'])
def route_comparison():
    """
    Compare multiple routes
    
    Expected payload:
    {
        "route_ids": ["route_1", "route_2", "route_3"],
        "metrics": ["time", "distance", "fuel", "emissions"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'route_ids' not in data:
            return jsonify({'error': 'Missing route_ids'}), 400
        
        comparison_data = analytics_engine.compare_routes(
            route_ids=data['route_ids'],
            metrics=data.get('metrics', ['time', 'distance', 'fuel', 'emissions'])
        )
        
        return jsonify(comparison_data)
        
    except Exception as e:
        logger.error(f"Route comparison failed: {str(e)}")
        return jsonify({'error': 'Route comparison failed'}), 500

@api_bp.route('/vehicles', methods=['GET'])
def get_vehicle_types():
    """Get available vehicle types and their specifications"""
    try:
        vehicle_data = emission_calculator.get_vehicle_specifications()
        return jsonify(vehicle_data)
        
    except Exception as e:
        logger.error(f"Failed to get vehicle types: {str(e)}")
        return jsonify({'error': 'Failed to retrieve vehicle data'}), 500