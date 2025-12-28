"""
Data models for route optimization
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Stop:
    """Represents a delivery stop"""
    lat: float
    lng: float
    stop_id: str
    sequence: int
    priority: int = 1
    service_time_minutes: int = 10
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    special_instructions: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Route:
    """Represents a complete delivery route"""
    route_id: str
    origin: Stop
    stops: List[Stop]
    vehicle_type: str
    total_distance_km: float
    total_time_minutes: float
    optimization_sequence: List[int]
    created_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            'route_id': self.route_id,
            'origin': self.origin.to_dict(),
            'stops': [stop.to_dict() for stop in self.stops],
            'vehicle_type': self.vehicle_type,
            'total_distance_km': self.total_distance_km,
            'total_time_minutes': self.total_time_minutes,
            'optimization_sequence': self.optimization_sequence,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class OptimizationConstraints:
    """Constraints for route optimization"""
    max_capacity: Optional[int] = None
    max_duration_minutes: Optional[int] = None
    max_distance_km: Optional[int] = None
    vehicle_restrictions: Optional[List[str]] = None
    time_windows_required: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class OptimizationPreferences:
    """Preferences for route optimization"""
    optimize_for: str = 'time'  # 'time', 'distance', 'fuel', 'emissions'
    avoid_tolls: bool = False
    avoid_highways: bool = False
    prefer_main_roads: bool = True
    consider_traffic: bool = True
    consider_weather: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class RouteMetrics:
    """Comprehensive metrics for a route"""
    total_distance_km: float
    total_time_minutes: float
    fuel_consumed_liters: float
    estimated_cost_usd: float
    average_speed_kmh: float
    traffic_impact: float
    weather_impact: float
    optimization_quality: str
    stops_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class OptimizationResult:
    """Complete result of route optimization"""
    route_id: str
    optimized_route: Dict
    metrics: RouteMetrics
    emissions: Optional[Dict] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        result = {
            'route_id': self.route_id,
            'optimized_route': self.optimized_route,
            'metrics': self.metrics.to_dict() if isinstance(self.metrics, RouteMetrics) else self.metrics
        }
        
        if self.emissions:
            result['emissions'] = self.emissions
        
        if self.timestamp:
            result['timestamp'] = self.timestamp.isoformat()
        
        return result

@dataclass
class TrafficCondition:
    """Real-time traffic condition data"""
    location: Dict  # lat, lng
    congestion_level: str  # 'light', 'moderate', 'heavy', 'severe'
    speed_kmh: float
    delay_minutes: float
    incident_type: Optional[str] = None
    incident_description: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        if self.timestamp:
            result['timestamp'] = self.timestamp.isoformat()
        return result

@dataclass
class WeatherCondition:
    """Weather condition affecting route"""
    location: Dict  # lat, lng
    condition: str  # 'clear', 'rain', 'snow', 'fog', etc.
    temperature_celsius: float
    precipitation_mm: float
    wind_speed_kmh: float
    visibility_km: float
    impact_multiplier: float  # Effect on travel time
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        if self.timestamp:
            result['timestamp'] = self.timestamp.isoformat()
        return result

@dataclass
class VehicleSpecification:
    """Vehicle specifications for optimization"""
    vehicle_type: str
    fuel_type: str
    capacity_kg: int
    fuel_efficiency_l_per_100km: float
    emission_factor_kg_co2_per_km: float
    max_range_km: int
    average_speed_kmh: float
    cost_per_km: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class RouteSegment:
    """Individual segment of a route between two stops"""
    from_stop: Stop
    to_stop: Stop
    distance_km: float
    time_minutes: float
    traffic_conditions: Optional[TrafficCondition] = None
    weather_conditions: Optional[WeatherCondition] = None
    road_type: Optional[str] = None
    toll_cost: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'from_stop': self.from_stop.to_dict(),
            'to_stop': self.to_stop.to_dict(),
            'distance_km': self.distance_km,
            'time_minutes': self.time_minutes,
            'traffic_conditions': self.traffic_conditions.to_dict() if self.traffic_conditions else None,
            'weather_conditions': self.weather_conditions.to_dict() if self.weather_conditions else None,
            'road_type': self.road_type,
            'toll_cost': self.toll_cost
        }