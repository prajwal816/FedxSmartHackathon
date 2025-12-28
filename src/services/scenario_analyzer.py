"""
Scenario Analyzer Service
Performs what-if analysis for different route conditions and parameters
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import copy

from ..services.route_optimizer import RouteOptimizer
from ..services.emission_calculator import EmissionCalculator
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class ScenarioAnalyzer:
    """Advanced scenario analysis for route optimization"""
    
    def __init__(self):
        self.route_optimizer = RouteOptimizer()
        self.emission_calculator = EmissionCalculator()
        self.cache = CacheManager()
    
    def analyze_scenarios(self, base_route_id: str, scenarios: List[Dict]) -> Dict:
        """
        Analyze multiple what-if scenarios against a base route
        
        Args:
            base_route_id: ID of the base route for comparison
            scenarios: List of scenario configurations
            
        Returns:
            Comprehensive scenario analysis results
        """
        try:
            logger.info(f"Starting scenario analysis for route {base_route_id}")
            
            # Get base route data
            base_route = self.cache.get_route(base_route_id)
            if not base_route:
                return {'error': f'Base route {base_route_id} not found'}
            
            # Initialize results
            analysis_results = {
                'base_route_id': base_route_id,
                'base_metrics': self._extract_base_metrics(base_route),
                'scenarios': {},
                'comparison_summary': {},
                'recommendations': [],
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Analyze each scenario
            for scenario in scenarios:
                scenario_name = scenario.get('name', f'scenario_{len(analysis_results["scenarios"])}')
                logger.info(f"Analyzing scenario: {scenario_name}")
                
                scenario_result = self._analyze_single_scenario(base_route, scenario)
                analysis_results['scenarios'][scenario_name] = scenario_result
            
            # Generate comparison summary
            analysis_results['comparison_summary'] = self._generate_comparison_summary(
                analysis_results['base_metrics'], 
                analysis_results['scenarios']
            )
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_scenario_recommendations(
                analysis_results['scenarios'],
                analysis_results['comparison_summary']
            )
            
            logger.info("Scenario analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Scenario analysis failed: {str(e)}")
            return {'error': 'Scenario analysis failed'}
    
    def _extract_base_metrics(self, base_route) -> Dict:
        """Extract key metrics from base route"""
        if hasattr(base_route, 'metrics'):
            return {
                'total_distance_km': base_route.metrics.get('total_distance_km', 0),
                'total_time_minutes': base_route.metrics.get('total_time_minutes', 0),
                'fuel_consumed_liters': base_route.metrics.get('fuel_consumed_liters', 0),
                'estimated_cost_usd': base_route.metrics.get('estimated_cost_usd', 0)
            }
        
        # Fallback for demo data
        return {
            'total_distance_km': 150.0,
            'total_time_minutes': 240.0,
            'fuel_consumed_liters': 45.0,
            'estimated_cost_usd': 120.0
        }
    
    def _analyze_single_scenario(self, base_route, scenario: Dict) -> Dict:
        """Analyze a single scenario configuration"""
        try:
            scenario_conditions = scenario.get('conditions', {})
            scenario_name = scenario.get('name', 'unnamed_scenario')
            
            # Create modified route parameters
            modified_params = self._apply_scenario_conditions(base_route, scenario_conditions)
            
            # Calculate scenario-specific results
            scenario_results = {
                'conditions': scenario_conditions,
                'modified_metrics': self._calculate_scenario_metrics(modified_params, scenario_conditions),
                'impact_analysis': {},
                'feasibility': 'feasible'
            }
            
            # Calculate impact vs base route
            base_metrics = self._extract_base_metrics(base_route)
            scenario_results['impact_analysis'] = self._calculate_impact_analysis(
                base_metrics, 
                scenario_results['modified_metrics']
            )
            
            # Assess feasibility
            scenario_results['feasibility'] = self._assess_scenario_feasibility(
                scenario_results['modified_metrics'], 
                scenario_conditions
            )
            
            return scenario_results
            
        except Exception as e:
            logger.error(f"Single scenario analysis failed: {str(e)}")
            return {'error': f'Failed to analyze scenario: {scenario.get("name", "unknown")}'}
    
    def _apply_scenario_conditions(self, base_route, conditions: Dict) -> Dict:
        """Apply scenario conditions to base route parameters"""
        
        # Start with base route data
        base_metrics = self._extract_base_metrics(base_route)
        modified_params = copy.deepcopy(base_metrics)
        
        # Apply traffic conditions
        if 'traffic_multiplier' in conditions:
            traffic_multiplier = conditions['traffic_multiplier']
            modified_params['total_time_minutes'] *= traffic_multiplier
            # Traffic also affects fuel consumption
            modified_params['fuel_consumed_liters'] *= (1 + (traffic_multiplier - 1) * 0.3)
        
        # Apply weather conditions
        if 'weather_impact' in conditions:
            weather_impact = conditions['weather_impact']
            weather_multipliers = {
                'clear': 1.0,
                'light_rain': 1.1,
                'heavy_rain': 1.3,
                'snow': 1.5,
                'fog': 1.2
            }
            multiplier = weather_multipliers.get(weather_impact, 1.0)
            modified_params['total_time_minutes'] *= multiplier
            modified_params['fuel_consumed_liters'] *= multiplier
        
        # Apply vehicle type changes
        if 'vehicle_type' in conditions:
            new_vehicle_type = conditions['vehicle_type']
            modified_params = self._recalculate_for_vehicle_type(modified_params, new_vehicle_type)
        
        # Apply time of day effects
        if 'time_of_day' in conditions:
            time_multiplier = self._get_time_of_day_multiplier(conditions['time_of_day'])
            modified_params['total_time_minutes'] *= time_multiplier
        
        # Apply route modifications
        if 'route_modification' in conditions:
            modification = conditions['route_modification']
            if modification == 'avoid_highways':
                modified_params['total_distance_km'] *= 1.15
                modified_params['total_time_minutes'] *= 1.1
            elif modification == 'avoid_tolls':
                modified_params['total_distance_km'] *= 1.08
                modified_params['total_time_minutes'] *= 1.05
        
        return modified_params
    
    def _recalculate_for_vehicle_type(self, params: Dict, vehicle_type: str) -> Dict:
        """Recalculate metrics for different vehicle type"""
        
        # Vehicle efficiency factors (relative to diesel truck)
        efficiency_factors = {
            'diesel_truck': 1.0,
            'petrol_truck': 1.15,  # Less efficient
            'electric_truck': 0.0,  # No fuel consumption
            'hybrid_truck': 0.7,   # More efficient
            'hydrogen_truck': 0.3  # Very efficient
        }
        
        # Recalculate fuel consumption
        base_fuel = params['fuel_consumed_liters']
        efficiency_factor = efficiency_factors.get(vehicle_type, 1.0)
        
        if vehicle_type == 'electric_truck':
            params['fuel_consumed_liters'] = 0
            params['energy_consumed_kwh'] = base_fuel * 3.5  # Rough conversion
        else:
            params['fuel_consumed_liters'] = base_fuel * efficiency_factor
        
        # Recalculate cost (electric vehicles have different cost structure)
        if vehicle_type == 'electric_truck':
            # Electricity cost vs fuel cost
            params['estimated_cost_usd'] = params['estimated_cost_usd'] * 0.4
        elif vehicle_type == 'hybrid_truck':
            params['estimated_cost_usd'] = params['estimated_cost_usd'] * 0.8
        
        return params
    
    def _get_time_of_day_multiplier(self, time_of_day: str) -> float:
        """Get traffic multiplier based on time of day"""
        time_multipliers = {
            '06:00': 1.0,   # Early morning
            '08:00': 1.4,   # Morning rush
            '10:00': 1.1,   # Mid morning
            '12:00': 1.2,   # Lunch time
            '14:00': 1.1,   # Early afternoon
            '17:00': 1.5,   # Evening rush
            '19:00': 1.2,   # Evening
            '22:00': 1.0    # Night
        }
        
        return time_multipliers.get(time_of_day, 1.1)
    
    def _calculate_scenario_metrics(self, modified_params: Dict, conditions: Dict) -> Dict:
        """Calculate comprehensive metrics for scenario"""
        
        # Start with modified parameters
        metrics = copy.deepcopy(modified_params)
        
        # Calculate derived metrics
        if metrics['total_time_minutes'] > 0:
            metrics['average_speed_kmh'] = round(
                (metrics['total_distance_km'] / (metrics['total_time_minutes'] / 60)), 2
            )
        else:
            metrics['average_speed_kmh'] = 0
        
        # Calculate emissions based on vehicle type
        vehicle_type = conditions.get('vehicle_type', 'diesel_truck')
        distance = metrics['total_distance_km']
        
        # Simplified emission calculation
        emission_factors = {
            'diesel_truck': 0.162,
            'petrol_truck': 0.184,
            'electric_truck': 0.045,
            'hybrid_truck': 0.098,
            'hydrogen_truck': 0.020
        }
        
        emission_factor = emission_factors.get(vehicle_type, 0.162)
        metrics['total_co2_kg'] = round(distance * emission_factor, 3)
        
        # Calculate green score
        metrics['green_score'] = self._calculate_scenario_green_score(metrics, vehicle_type)
        
        return metrics
    
    def _calculate_scenario_green_score(self, metrics: Dict, vehicle_type: str) -> int:
        """Calculate green score for scenario"""
        
        distance = metrics.get('total_distance_km', 0)
        if distance == 0:
            return 0
        
        co2_per_km = metrics.get('total_co2_kg', 0) / distance
        
        # Score based on emissions per km
        if co2_per_km <= 0.05:
            return 95
        elif co2_per_km <= 0.10:
            return 85
        elif co2_per_km <= 0.16:
            return 70
        elif co2_per_km <= 0.25:
            return 50
        else:
            return 30
    
    def _calculate_impact_analysis(self, base_metrics: Dict, scenario_metrics: Dict) -> Dict:
        """Calculate impact of scenario vs base route"""
        
        impact = {}
        
        for metric in ['total_distance_km', 'total_time_minutes', 'fuel_consumed_liters', 'estimated_cost_usd']:
            if metric in base_metrics and metric in scenario_metrics:
                base_value = base_metrics[metric]
                scenario_value = scenario_metrics[metric]
                
                if base_value > 0:
                    change_absolute = scenario_value - base_value
                    change_percentage = (change_absolute / base_value) * 100
                    
                    impact[metric] = {
                        'absolute_change': round(change_absolute, 2),
                        'percentage_change': round(change_percentage, 1),
                        'direction': 'increase' if change_absolute > 0 else 'decrease'
                    }
        
        # Add CO2 impact if available
        if 'total_co2_kg' in scenario_metrics:
            # Estimate base CO2 (assuming diesel truck)
            base_co2 = base_metrics.get('total_distance_km', 0) * 0.162
            scenario_co2 = scenario_metrics['total_co2_kg']
            
            co2_change = scenario_co2 - base_co2
            impact['total_co2_kg'] = {
                'absolute_change': round(co2_change, 3),
                'percentage_change': round((co2_change / base_co2) * 100, 1) if base_co2 > 0 else 0,
                'direction': 'increase' if co2_change > 0 else 'decrease'
            }
        
        return impact
    
    def _assess_scenario_feasibility(self, metrics: Dict, conditions: Dict) -> str:
        """Assess feasibility of scenario"""
        
        # Check time constraints
        if metrics.get('total_time_minutes', 0) > 600:  # 10 hours
            return 'challenging'
        
        # Check distance constraints
        if metrics.get('total_distance_km', 0) > 500:  # 500 km
            return 'challenging'
        
        # Check vehicle availability
        vehicle_type = conditions.get('vehicle_type')
        if vehicle_type in ['electric_truck', 'hydrogen_truck']:
            return 'requires_infrastructure'
        
        return 'feasible'
    
    def _generate_comparison_summary(self, base_metrics: Dict, scenarios: Dict) -> Dict:
        """Generate summary comparison across all scenarios"""
        
        summary = {
            'best_scenarios': {},
            'worst_scenarios': {},
            'average_impacts': {},
            'feasibility_summary': {}
        }
        
        # Find best and worst scenarios for each metric
        metrics_to_compare = ['total_time_minutes', 'total_distance_km', 'fuel_consumed_liters', 'estimated_cost_usd']
        
        for metric in metrics_to_compare:
            best_scenario = None
            worst_scenario = None
            best_value = float('inf')
            worst_value = float('-inf')
            
            for scenario_name, scenario_data in scenarios.items():
                if 'modified_metrics' in scenario_data and metric in scenario_data['modified_metrics']:
                    value = scenario_data['modified_metrics'][metric]
                    
                    if value < best_value:
                        best_value = value
                        best_scenario = scenario_name
                    
                    if value > worst_value:
                        worst_value = value
                        worst_scenario = scenario_name
            
            summary['best_scenarios'][metric] = best_scenario
            summary['worst_scenarios'][metric] = worst_scenario
        
        # Feasibility summary
        feasibility_counts = {}
        for scenario_data in scenarios.values():
            feasibility = scenario_data.get('feasibility', 'unknown')
            feasibility_counts[feasibility] = feasibility_counts.get(feasibility, 0) + 1
        
        summary['feasibility_summary'] = feasibility_counts
        
        return summary
    
    def _generate_scenario_recommendations(self, scenarios: Dict, comparison_summary: Dict) -> List[str]:
        """Generate actionable recommendations based on scenario analysis"""
        
        recommendations = []
        
        # Vehicle type recommendations
        vehicle_scenarios = [name for name, data in scenarios.items() 
                           if 'vehicle_type' in data.get('conditions', {})]
        
        if vehicle_scenarios:
            recommendations.append("Consider vehicle type optimization for significant emission reductions")
        
        # Traffic timing recommendations
        traffic_scenarios = [name for name, data in scenarios.items() 
                           if 'time_of_day' in data.get('conditions', {})]
        
        if traffic_scenarios:
            recommendations.append("Schedule deliveries during off-peak hours to reduce travel time by 20-30%")
        
        # Weather contingency recommendations
        weather_scenarios = [name for name, data in scenarios.items() 
                           if 'weather_impact' in data.get('conditions', {})]
        
        if weather_scenarios:
            recommendations.append("Develop weather contingency plans to maintain service levels")
        
        # Infrastructure recommendations
        challenging_scenarios = [name for name, data in scenarios.items() 
                               if data.get('feasibility') == 'requires_infrastructure']
        
        if challenging_scenarios:
            recommendations.append("Evaluate infrastructure requirements for advanced vehicle technologies")
        
        # General optimization recommendations
        recommendations.extend([
            "Implement dynamic routing to adapt to real-time conditions",
            "Consider multi-modal transportation for long-distance routes",
            "Develop KPI monitoring for continuous optimization"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations