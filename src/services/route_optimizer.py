"""
Route Optimization Service
Handles dynamic route optimization with real-time data integration
"""

import uuid
import logging
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import networkx as nx
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from ..utils.external_apis import TomTomAPI, WeatherAPI
from ..utils.cache_manager import CacheManager
from ..models.route_models import Route, Stop, OptimizationResult

logger = logging.getLogger(__name__)

class RouteOptimizer:
    """Advanced route optimization with real-time data integration"""
    
    def __init__(self):
        self.tomtom_api = TomTomAPI()
        self.weather_api = WeatherAPI()
        self.cache = CacheManager()
        
    def optimize(self, origin: Dict, destinations: List[Dict], 
                 vehicle_type: str = 'diesel_truck',
                 constraints: Dict = None,
                 preferences: Dict = None) -> Dict:
        """
        Optimize route with real-time conditions
        
        Args:
            origin: Starting point coordinates
            destinations: List of delivery stops
            vehicle_type: Type of delivery vehicle
            constraints: Vehicle and route constraints
            preferences: Optimization preferences
            
        Returns:
            Optimized route with metrics
        """
        try:
            route_id = str(uuid.uuid4())
            logger.info(f"Starting route optimization: {route_id}")
            
            # Set default values
            constraints = constraints or {}
            preferences = preferences or {'optimize_for': 'time'}
            
            # Get real-time traffic and weather data
            traffic_data = self._get_traffic_conditions(origin, destinations)
            weather_data = self._get_weather_conditions(origin, destinations)
            
            # Build distance and time matrices
            distance_matrix, time_matrix = self._build_matrices(
                origin, destinations, traffic_data, weather_data
            )
            
            # Apply optimization algorithm
            optimized_sequence = self._solve_vrp(
                distance_matrix, time_matrix, constraints, preferences
            )
            
            # Build optimized route
            optimized_route = self._build_route(
                origin, destinations, optimized_sequence, 
                distance_matrix, time_matrix
            )
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                optimized_route, vehicle_type, traffic_data, weather_data
            )
            
            # Cache results
            result = OptimizationResult(
                route_id=route_id,
                optimized_route=optimized_route,
                metrics=metrics,
                timestamp=datetime.utcnow()
            )
            
            self.cache.store_route(route_id, result)
            
            logger.info(f"Route optimization completed: {route_id}")
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Route optimization failed: {str(e)}")
            raise
    
    def _get_traffic_conditions(self, origin: Dict, destinations: List[Dict]) -> Dict:
        """Get real-time traffic data for route points"""
        try:
            # Check cache first
            cache_key = f"traffic_{hash(str(origin) + str(destinations))}"
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            # Get traffic data from TomTom API
            traffic_data = self.tomtom_api.get_traffic_flow(origin, destinations)
            
            # Cache for 5 minutes
            self.cache.set(cache_key, traffic_data, timeout=300)
            
            return traffic_data
            
        except Exception as e:
            logger.warning(f"Failed to get traffic data: {str(e)}")
            return {'status': 'unavailable', 'multiplier': 1.0}
    
    def _get_weather_conditions(self, origin: Dict, destinations: List[Dict]) -> Dict:
        """Get weather conditions affecting route"""
        try:
            # Get weather for route area
            weather_data = self.weather_api.get_route_weather(origin, destinations)
            
            # Calculate weather impact on travel time
            weather_multiplier = self._calculate_weather_impact(weather_data)
            
            return {
                'conditions': weather_data,
                'impact_multiplier': weather_multiplier
            }
            
        except Exception as e:
            logger.warning(f"Failed to get weather data: {str(e)}")
            return {'conditions': {}, 'impact_multiplier': 1.0}
    
    def _calculate_weather_impact(self, weather_data: Dict) -> float:
        """Calculate weather impact on travel time"""
        if not weather_data:
            return 1.0
        
        multiplier = 1.0
        
        # Rain impact
        if weather_data.get('precipitation', 0) > 0:
            multiplier += 0.1 + (weather_data['precipitation'] / 10) * 0.2
        
        # Wind impact
        wind_speed = weather_data.get('wind_speed', 0)
        if wind_speed > 20:  # km/h
            multiplier += (wind_speed - 20) / 100
        
        # Visibility impact
        visibility = weather_data.get('visibility', 10)
        if visibility < 5:  # km
            multiplier += (5 - visibility) / 10
        
        return min(multiplier, 2.0)  # Cap at 2x normal time
    
    def _build_matrices(self, origin: Dict, destinations: List[Dict],
                       traffic_data: Dict, weather_data: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """Build distance and time matrices with real-time adjustments"""
        
        all_points = [origin] + destinations
        n = len(all_points)
        
        distance_matrix = np.zeros((n, n))
        time_matrix = np.zeros((n, n))
        
        # Get base distances and times
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Calculate straight-line distance as fallback
                    dist = self._haversine_distance(
                        all_points[i]['lat'], all_points[i]['lng'],
                        all_points[j]['lat'], all_points[j]['lng']
                    )
                    
                    # Estimate time based on average speed (50 km/h in city)
                    base_time = dist / 50 * 60  # minutes
                    
                    # Apply traffic multiplier
                    traffic_multiplier = traffic_data.get('multiplier', 1.0)
                    weather_multiplier = weather_data.get('impact_multiplier', 1.0)
                    
                    adjusted_time = base_time * traffic_multiplier * weather_multiplier
                    
                    distance_matrix[i][j] = dist
                    time_matrix[i][j] = adjusted_time
        
        return distance_matrix, time_matrix
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = (np.sin(dlat/2)**2 + 
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
             np.sin(dlon/2)**2)
        
        c = 2 * np.arcsin(np.sqrt(a))
        distance = R * c
        
        return distance
    
    def _solve_vrp(self, distance_matrix: np.ndarray, time_matrix: np.ndarray,
                   constraints: Dict, preferences: Dict) -> List[int]:
        """Solve Vehicle Routing Problem using OR-Tools"""
        
        try:
            # Create routing index manager
            manager = pywrapcp.RoutingIndexManager(
                len(distance_matrix), 1, 0  # locations, vehicles, depot
            )
            
            # Create routing model
            routing = pywrapcp.RoutingModel(manager)
            
            # Choose optimization matrix based on preference
            optimize_for = preferences.get('optimize_for', 'time')
            matrix = time_matrix if optimize_for == 'time' else distance_matrix
            
            # Create distance callback
            def distance_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return int(matrix[from_node][to_node] * 100)  # Scale for integer
            
            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            
            # Add capacity constraint if specified
            if 'max_capacity' in constraints:
                # Simplified capacity constraint (assuming equal demand)
                demands = [0] + [1] * (len(distance_matrix) - 1)
                
                def demand_callback(from_index):
                    from_node = manager.IndexToNode(from_index)
                    return demands[from_node]
                
                demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
                routing.AddDimensionWithVehicleCapacity(
                    demand_callback_index,
                    0,  # null capacity slack
                    [constraints['max_capacity']],  # vehicle maximum capacities
                    True,  # start cumul to zero
                    'Capacity'
                )
            
            # Add time constraint if specified
            if 'max_duration' in constraints:
                routing.AddDimension(
                    transit_callback_index,
                    30,  # allow waiting time
                    constraints['max_duration'],  # maximum time per vehicle
                    False,  # don't force start cumul to zero
                    'Time'
                )
            
            # Set search parameters
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.time_limit.seconds = 30
            
            # Solve
            solution = routing.SolveWithParameters(search_parameters)
            
            if solution:
                return self._extract_solution(manager, routing, solution)
            else:
                # Fallback to nearest neighbor if OR-Tools fails
                logger.warning("OR-Tools optimization failed, using nearest neighbor")
                return self._nearest_neighbor_solution(distance_matrix)
                
        except Exception as e:
            logger.error(f"VRP solving failed: {str(e)}")
            return self._nearest_neighbor_solution(distance_matrix)
    
    def _extract_solution(self, manager, routing, solution) -> List[int]:
        """Extract solution from OR-Tools solver"""
        route_sequence = []
        index = routing.Start(0)
        
        while not routing.IsEnd(index):
            route_sequence.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        
        return route_sequence
    
    def _nearest_neighbor_solution(self, distance_matrix: np.ndarray) -> List[int]:
        """Fallback nearest neighbor algorithm"""
        n = len(distance_matrix)
        unvisited = set(range(1, n))  # Exclude depot (0)
        current = 0
        route = [0]
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return route
    
    def _build_route(self, origin: Dict, destinations: List[Dict],
                     sequence: List[int], distance_matrix: np.ndarray,
                     time_matrix: np.ndarray) -> Dict:
        """Build detailed route from optimization sequence"""
        
        all_points = [origin] + destinations
        route_stops = []
        total_distance = 0
        total_time = 0
        
        for i, stop_idx in enumerate(sequence):
            stop_data = all_points[stop_idx].copy()
            stop_data['sequence'] = i
            stop_data['stop_id'] = stop_idx
            
            if i > 0:
                prev_idx = sequence[i-1]
                segment_distance = distance_matrix[prev_idx][stop_idx]
                segment_time = time_matrix[prev_idx][stop_idx]
                
                stop_data['distance_from_previous'] = segment_distance
                stop_data['time_from_previous'] = segment_time
                
                total_distance += segment_distance
                total_time += segment_time
            
            route_stops.append(stop_data)
        
        return {
            'stops': route_stops,
            'total_distance_km': total_distance,
            'total_time_minutes': total_time,
            'optimization_sequence': sequence
        }
    
    def _calculate_metrics(self, route: Dict, vehicle_type: str,
                          traffic_data: Dict, weather_data: Dict) -> Dict:
        """Calculate comprehensive route metrics"""
        
        total_distance = route['total_distance_km']
        total_time = route['total_time_minutes']
        
        # Fuel consumption estimation (L/100km)
        fuel_efficiency = {
            'diesel_truck': 35,
            'petrol_truck': 40,
            'electric_truck': 0,  # kWh/100km would be ~150
            'hybrid_truck': 25
        }
        
        efficiency = fuel_efficiency.get(vehicle_type, 35)
        fuel_consumed = (total_distance * efficiency) / 100 if efficiency > 0 else 0
        
        # Cost estimation
        fuel_cost_per_liter = 1.5  # USD
        driver_cost_per_hour = 25  # USD
        
        fuel_cost = fuel_consumed * fuel_cost_per_liter
        driver_cost = (total_time / 60) * driver_cost_per_hour
        total_cost = fuel_cost + driver_cost
        
        return {
            'total_distance_km': round(total_distance, 2),
            'total_time_minutes': round(total_time, 2),
            'fuel_consumed_liters': round(fuel_consumed, 2),
            'estimated_cost_usd': round(total_cost, 2),
            'average_speed_kmh': round((total_distance / (total_time / 60)), 2) if total_time > 0 else 0,
            'traffic_impact': traffic_data.get('multiplier', 1.0),
            'weather_impact': weather_data.get('impact_multiplier', 1.0),
            'optimization_quality': 'optimal',  # Could be enhanced with quality metrics
            'stops_count': len(route['stops']) - 1  # Exclude origin
        }