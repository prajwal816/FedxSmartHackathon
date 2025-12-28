"""
External API integrations for real-time data
"""

import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
import time

from config.settings import Config

logger = logging.getLogger(__name__)

class TomTomAPI:
    """TomTom API integration for traffic and routing data"""
    
    def __init__(self):
        self.api_key = Config.TOMTOM_API_KEY
        self.base_url = "https://api.tomtom.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_traffic_flow(self, origin: Dict, destinations: List[Dict]) -> Dict:
        """Get real-time traffic flow data"""
        try:
            if not self.api_key:
                logger.warning("TomTom API key not configured, using mock data")
                return self._get_mock_traffic_data()
            
            # For demo purposes, we'll simulate traffic data
            # In production, this would make actual API calls
            traffic_data = {
                'status': 'active',
                'multiplier': self._calculate_traffic_multiplier(),
                'congestion_level': 'moderate',
                'incidents': [],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("Traffic data retrieved successfully")
            return traffic_data
            
        except Exception as e:
            logger.error(f"Failed to get traffic data: {str(e)}")
            return self._get_mock_traffic_data()
    
    def get_route_matrix(self, locations: List[Dict]) -> Dict:
        """Get distance and time matrix between locations"""
        try:
            if not self.api_key:
                return self._get_mock_matrix_data(locations)
            
            # Simulate matrix calculation
            n = len(locations)
            matrix_data = {
                'distances': [[0 for _ in range(n)] for _ in range(n)],
                'durations': [[0 for _ in range(n)] for _ in range(n)]
            }
            
            # Fill with estimated values
            for i in range(n):
                for j in range(n):
                    if i != j:
                        # Calculate approximate distance using coordinates
                        distance = self._calculate_distance(locations[i], locations[j])
                        duration = distance / 50 * 60  # Assume 50 km/h average speed
                        
                        matrix_data['distances'][i][j] = distance
                        matrix_data['durations'][i][j] = duration
            
            return matrix_data
            
        except Exception as e:
            logger.error(f"Failed to get route matrix: {str(e)}")
            return self._get_mock_matrix_data(locations)
    
    def _calculate_traffic_multiplier(self) -> float:
        """Calculate traffic multiplier based on current time"""
        current_hour = datetime.now().hour
        
        # Peak hours have higher multipliers
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            return 1.4  # 40% increase during rush hours
        elif 10 <= current_hour <= 16:
            return 1.1  # 10% increase during day
        else:
            return 1.0  # Normal traffic
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate approximate distance between two locations"""
        import math
        
        lat1, lon1 = loc1['lat'], loc1['lng']
        lat2, lon2 = loc2['lat'], loc2['lng']
        
        # Haversine formula
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def _get_mock_traffic_data(self) -> Dict:
        """Return mock traffic data for demo purposes"""
        return {
            'status': 'mock',
            'multiplier': 1.2,
            'congestion_level': 'light',
            'incidents': [],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_mock_matrix_data(self, locations: List[Dict]) -> Dict:
        """Return mock matrix data for demo purposes"""
        n = len(locations)
        return {
            'distances': [[0 if i == j else 25.0 for j in range(n)] for i in range(n)],
            'durations': [[0 if i == j else 30.0 for j in range(n)] for i in range(n)]
        }

class WeatherAPI:
    """OpenWeather API integration for weather data"""
    
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = requests.Session()
    
    def get_route_weather(self, origin: Dict, destinations: List[Dict]) -> Dict:
        """Get weather conditions for route area"""
        try:
            if not self.api_key:
                logger.warning("OpenWeather API key not configured, using mock data")
                return self._get_mock_weather_data()
            
            # Get weather for origin (representative of route area)
            weather_data = self._get_location_weather(origin)
            
            logger.info("Weather data retrieved successfully")
            return weather_data
            
        except Exception as e:
            logger.error(f"Failed to get weather data: {str(e)}")
            return self._get_mock_weather_data()
    
    def _get_location_weather(self, location: Dict) -> Dict:
        """Get weather for specific location"""
        try:
            # For demo purposes, return simulated weather data
            # In production, this would make actual API calls
            
            weather_conditions = ['clear', 'partly_cloudy', 'cloudy', 'light_rain', 'rain']
            import random
            
            return {
                'condition': random.choice(weather_conditions),
                'temperature': random.uniform(15, 25),  # Celsius
                'precipitation': random.uniform(0, 5),  # mm
                'wind_speed': random.uniform(5, 20),    # km/h
                'visibility': random.uniform(8, 15),    # km
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get location weather: {str(e)}")
            return self._get_mock_weather_data()
    
    def _get_mock_weather_data(self) -> Dict:
        """Return mock weather data for demo purposes"""
        return {
            'condition': 'clear',
            'temperature': 20.0,
            'precipitation': 0.0,
            'wind_speed': 10.0,
            'visibility': 15.0,
            'timestamp': datetime.utcnow().isoformat()
        }

class OSRMApi:
    """Open Source Routing Machine API for routing calculations"""
    
    def __init__(self):
        self.base_url = "http://router.project-osrm.org"
        self.session = requests.Session()
    
    def get_route(self, coordinates: List[Dict]) -> Dict:
        """Get route between multiple coordinates"""
        try:
            # Format coordinates for OSRM
            coord_string = ";".join([f"{coord['lng']},{coord['lat']}" for coord in coordinates])
            
            url = f"{self.base_url}/route/v1/driving/{coord_string}"
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_osrm_response(data)
            else:
                logger.warning(f"OSRM API returned status {response.status_code}")
                return self._get_fallback_route_data(coordinates)
                
        except Exception as e:
            logger.error(f"OSRM API request failed: {str(e)}")
            return self._get_fallback_route_data(coordinates)
    
    def _process_osrm_response(self, data: Dict) -> Dict:
        """Process OSRM API response"""
        if 'routes' not in data or not data['routes']:
            return self._get_fallback_route_data([])
        
        route = data['routes'][0]
        
        return {
            'distance_meters': route.get('distance', 0),
            'duration_seconds': route.get('duration', 0),
            'geometry': route.get('geometry', {}),
            'steps': route.get('legs', [{}])[0].get('steps', []) if route.get('legs') else []
        }
    
    def _get_fallback_route_data(self, coordinates: List[Dict]) -> Dict:
        """Return fallback route data when API is unavailable"""
        # Estimate distance and duration
        total_distance = 0
        if len(coordinates) > 1:
            for i in range(len(coordinates) - 1):
                distance = self._calculate_distance(coordinates[i], coordinates[i + 1])
                total_distance += distance
        
        estimated_duration = total_distance / 50 * 3600  # 50 km/h in seconds
        
        return {
            'distance_meters': total_distance * 1000,
            'duration_seconds': estimated_duration,
            'geometry': {},
            'steps': []
        }
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate distance between two coordinates"""
        import math
        
        lat1, lon1 = loc1['lat'], loc1['lng']
        lat2, lon2 = loc2['lat'], loc2['lng']
        
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        
        c = 2 * math.asin(math.sqrt(a))
        return R * c

class AirQualityAPI:
    """Air Quality API for environmental data"""
    
    def __init__(self):
        self.base_url = "https://api.waqi.info"
        self.session = requests.Session()
    
    def get_air_quality(self, location: Dict) -> Dict:
        """Get air quality data for location"""
        try:
            # For demo purposes, return simulated air quality data
            import random
            
            aqi_value = random.randint(20, 150)
            
            if aqi_value <= 50:
                category = "Good"
            elif aqi_value <= 100:
                category = "Moderate"
            elif aqi_value <= 150:
                category = "Unhealthy for Sensitive Groups"
            else:
                category = "Unhealthy"
            
            return {
                'aqi': aqi_value,
                'category': category,
                'pollutants': {
                    'pm25': random.uniform(10, 50),
                    'pm10': random.uniform(15, 80),
                    'no2': random.uniform(20, 100),
                    'o3': random.uniform(30, 120)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get air quality data: {str(e)}")
            return {
                'aqi': 50,
                'category': 'Good',
                'pollutants': {},
                'timestamp': datetime.utcnow().isoformat()
            }