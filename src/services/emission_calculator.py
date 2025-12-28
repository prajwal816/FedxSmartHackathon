"""
Emission Calculator Service
Calculates CO2 emissions and sustainability metrics for routes
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

from ..utils.cache_manager import CacheManager
from ..models.emission_models import EmissionResult, VehicleSpec
from config.settings import Config

logger = logging.getLogger(__name__)

class EmissionCalculator:
    """Calculate CO2 emissions and sustainability metrics"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.emission_factors = Config.EMISSION_FACTORS
        self.vehicle_specs = self._load_vehicle_specifications()
    
    def calculate_route_emissions(self, route: Dict, vehicle_type: str) -> Dict:
        """
        Calculate comprehensive emissions for a route
        
        Args:
            route: Route data with stops and distances
            vehicle_type: Type of vehicle used
            
        Returns:
            Detailed emission analysis
        """
        try:
            logger.info(f"Calculating emissions for route with {len(route.get('stops', []))} stops")
            
            # Get vehicle specifications
            vehicle_spec = self.vehicle_specs.get(vehicle_type, self.vehicle_specs['diesel_truck'])
            
            # Calculate base emissions
            total_distance = route.get('total_distance_km', 0)
            base_emissions = total_distance * vehicle_spec['emission_factor']
            
            # Calculate traffic-adjusted emissions
            traffic_emissions = self._calculate_traffic_emissions(route, vehicle_spec)
            
            # Calculate idle emissions
            idle_emissions = self._calculate_idle_emissions(route, vehicle_spec)
            
            # Calculate cold start emissions
            cold_start_emissions = self._calculate_cold_start_emissions(vehicle_spec)
            
            # Total emissions
            total_emissions = base_emissions + traffic_emissions + idle_emissions + cold_start_emissions
            
            # Calculate green score (0-100, higher is better)
            green_score = self._calculate_green_score(total_emissions, total_distance, vehicle_type)
            
            # Generate recommendations
            recommendations = self._generate_emission_recommendations(
                total_emissions, vehicle_type, route
            )
            
            # Create detailed breakdown
            emission_breakdown = {
                'base_driving': round(base_emissions, 3),
                'traffic_congestion': round(traffic_emissions, 3),
                'idle_time': round(idle_emissions, 3),
                'cold_start': round(cold_start_emissions, 3),
                'total': round(total_emissions, 3)
            }
            
            result = {
                'total_co2_kg': round(total_emissions, 3),
                'co2_per_km': round(total_emissions / total_distance, 3) if total_distance > 0 else 0,
                'green_score': green_score,
                'emission_breakdown': emission_breakdown,
                'vehicle_type': vehicle_type,
                'distance_km': total_distance,
                'equivalent_metrics': self._calculate_equivalent_metrics(total_emissions),
                'recommendations': recommendations,
                'calculation_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Emissions calculated: {total_emissions:.3f} kg CO2")
            return result
            
        except Exception as e:
            logger.error(f"Emission calculation failed: {str(e)}")
            raise
    
    def _load_vehicle_specifications(self) -> Dict:
        """Load detailed vehicle specifications"""
        return {
            'diesel_truck': {
                'emission_factor': 0.162,  # kg CO2 per km
                'fuel_type': 'diesel',
                'idle_emission_rate': 0.8,  # kg CO2 per hour
                'cold_start_penalty': 0.5,  # kg CO2 per start
                'efficiency_rating': 'C',
                'description': 'Standard diesel delivery truck'
            },
            'petrol_truck': {
                'emission_factor': 0.184,
                'fuel_type': 'petrol',
                'idle_emission_rate': 0.9,
                'cold_start_penalty': 0.6,
                'efficiency_rating': 'D',
                'description': 'Petrol-powered delivery truck'
            },
            'electric_truck': {
                'emission_factor': 0.045,  # Considering electricity grid mix
                'fuel_type': 'electric',
                'idle_emission_rate': 0.0,  # No idle emissions
                'cold_start_penalty': 0.0,  # No cold start penalty
                'efficiency_rating': 'A+',
                'description': 'Battery electric delivery truck'
            },
            'hybrid_truck': {
                'emission_factor': 0.098,
                'fuel_type': 'hybrid',
                'idle_emission_rate': 0.3,  # Reduced idle emissions
                'cold_start_penalty': 0.2,  # Reduced cold start penalty
                'efficiency_rating': 'B+',
                'description': 'Hybrid electric-diesel truck'
            },
            'hydrogen_truck': {
                'emission_factor': 0.020,  # Considering hydrogen production
                'fuel_type': 'hydrogen',
                'idle_emission_rate': 0.0,
                'cold_start_penalty': 0.1,
                'efficiency_rating': 'A',
                'description': 'Hydrogen fuel cell truck'
            }
        }
    
    def _calculate_traffic_emissions(self, route: Dict, vehicle_spec: Dict) -> float:
        """Calculate additional emissions due to traffic congestion"""
        
        # Estimate traffic delay from route metrics
        total_time = route.get('total_time_minutes', 0)
        total_distance = route.get('total_distance_km', 0)
        
        if total_distance == 0:
            return 0
        
        # Calculate average speed
        average_speed = (total_distance / (total_time / 60)) if total_time > 0 else 50
        
        # Optimal speed for fuel efficiency is typically 50-60 km/h
        optimal_speed = 55
        
        if average_speed < optimal_speed:
            # Lower speeds due to traffic increase emissions
            speed_penalty = (optimal_speed - average_speed) / optimal_speed
            traffic_emissions = total_distance * vehicle_spec['emission_factor'] * speed_penalty * 0.3
            return max(0, traffic_emissions)
        
        return 0
    
    def _calculate_idle_emissions(self, route: Dict, vehicle_spec: Dict) -> float:
        """Calculate emissions from idle time at stops"""
        
        stops = route.get('stops', [])
        if len(stops) <= 1:
            return 0
        
        # Estimate 5 minutes idle time per stop (excluding origin)
        delivery_stops = len(stops) - 1
        idle_time_hours = (delivery_stops * 5) / 60  # Convert to hours
        
        idle_emissions = idle_time_hours * vehicle_spec['idle_emission_rate']
        return idle_emissions
    
    def _calculate_cold_start_emissions(self, vehicle_spec: Dict) -> float:
        """Calculate emissions from cold engine start"""
        return vehicle_spec['cold_start_penalty']
    
    def _calculate_green_score(self, total_emissions: float, distance: float, vehicle_type: str) -> int:
        """
        Calculate green score (0-100, higher is better)
        Based on emissions per km compared to benchmarks
        """
        if distance == 0:
            return 0
        
        emissions_per_km = total_emissions / distance
        
        # Benchmark values (kg CO2 per km)
        benchmarks = {
            'excellent': 0.05,   # Electric/Hydrogen
            'good': 0.10,        # Hybrid
            'average': 0.16,     # Efficient diesel
            'poor': 0.25         # Old/inefficient vehicles
        }
        
        # Calculate score based on performance vs benchmarks
        if emissions_per_km <= benchmarks['excellent']:
            score = 95 + (benchmarks['excellent'] - emissions_per_km) * 100
        elif emissions_per_km <= benchmarks['good']:
            score = 80 + (benchmarks['good'] - emissions_per_km) / (benchmarks['good'] - benchmarks['excellent']) * 15
        elif emissions_per_km <= benchmarks['average']:
            score = 60 + (benchmarks['average'] - emissions_per_km) / (benchmarks['average'] - benchmarks['good']) * 20
        elif emissions_per_km <= benchmarks['poor']:
            score = 30 + (benchmarks['poor'] - emissions_per_km) / (benchmarks['poor'] - benchmarks['average']) * 30
        else:
            score = max(0, 30 - (emissions_per_km - benchmarks['poor']) * 50)
        
        return min(100, max(0, int(score)))
    
    def _calculate_equivalent_metrics(self, total_emissions_kg: float) -> Dict:
        """Calculate equivalent environmental metrics for context"""
        
        # Conversion factors
        tree_absorption_per_year = 22  # kg CO2 per tree per year
        car_emissions_per_km = 0.12   # kg CO2 per km for average car
        
        return {
            'trees_needed_per_year': round(total_emissions_kg / tree_absorption_per_year, 2),
            'equivalent_car_km': round(total_emissions_kg / car_emissions_per_km, 1),
            'equivalent_gasoline_liters': round(total_emissions_kg / 2.31, 2),  # 2.31 kg CO2 per liter gasoline
            'carbon_offset_cost_usd': round(total_emissions_kg * 0.02, 2)  # $20 per ton CO2
        }
    
    def _generate_emission_recommendations(self, total_emissions: float, 
                                         vehicle_type: str, route: Dict) -> List[str]:
        """Generate actionable recommendations to reduce emissions"""
        
        recommendations = []
        
        # Vehicle-specific recommendations
        if vehicle_type in ['diesel_truck', 'petrol_truck']:
            recommendations.append("Consider upgrading to hybrid or electric vehicles for 60-80% emission reduction")
            recommendations.append("Implement eco-driving training to reduce fuel consumption by 10-15%")
        
        # Route optimization recommendations
        stops_count = len(route.get('stops', [])) - 1
        if stops_count > 10:
            recommendations.append("Consider splitting route into multiple smaller routes to reduce total distance")
        
        # Time-based recommendations
        total_time = route.get('total_time_minutes', 0)
        if total_time > 300:  # 5 hours
            recommendations.append("Schedule deliveries during off-peak hours to reduce traffic-related emissions")
        
        # Distance-based recommendations
        total_distance = route.get('total_distance_km', 0)
        if total_distance > 200:
            recommendations.append("Evaluate hub-and-spoke distribution model for long-distance routes")
        
        # General recommendations
        recommendations.extend([
            "Implement route consolidation to reduce number of trips",
            "Use telematics to monitor and improve driver behavior",
            "Consider alternative fuel options (biodiesel, CNG) as intermediate step"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def get_detailed_emissions(self, route_id: str) -> Optional[Dict]:
        """Get detailed emission data for a specific route"""
        try:
            # Try to get from cache first
            cached_data = self.cache.get_route(route_id)
            if cached_data and hasattr(cached_data, 'emissions'):
                return cached_data.emissions
            
            logger.warning(f"No emission data found for route: {route_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get emission data for route {route_id}: {str(e)}")
            return None
    
    def get_vehicle_specifications(self) -> Dict:
        """Get all available vehicle types and their specifications"""
        return {
            'vehicle_types': self.vehicle_specs,
            'emission_factors': self.emission_factors,
            'fuel_types': list(set(spec['fuel_type'] for spec in self.vehicle_specs.values())),
            'efficiency_ratings': list(set(spec['efficiency_rating'] for spec in self.vehicle_specs.values()))
        }
    
    def compare_vehicle_emissions(self, route: Dict, vehicle_types: List[str]) -> Dict:
        """Compare emissions across different vehicle types for the same route"""
        
        comparison_results = {}
        
        for vehicle_type in vehicle_types:
            if vehicle_type in self.vehicle_specs:
                emissions = self.calculate_route_emissions(route, vehicle_type)
                comparison_results[vehicle_type] = {
                    'total_co2_kg': emissions['total_co2_kg'],
                    'green_score': emissions['green_score'],
                    'co2_per_km': emissions['co2_per_km']
                }
        
        # Find best and worst options
        if comparison_results:
            best_option = min(comparison_results.items(), key=lambda x: x[1]['total_co2_kg'])
            worst_option = max(comparison_results.items(), key=lambda x: x[1]['total_co2_kg'])
            
            potential_savings = worst_option[1]['total_co2_kg'] - best_option[1]['total_co2_kg']
            
            return {
                'comparison': comparison_results,
                'best_option': best_option[0],
                'worst_option': worst_option[0],
                'potential_co2_savings_kg': round(potential_savings, 3),
                'savings_percentage': round((potential_savings / worst_option[1]['total_co2_kg']) * 100, 1)
            }
        
        return {'comparison': comparison_results}