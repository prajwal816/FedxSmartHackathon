"""
Configuration settings for FedxSmart Platform
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'fedx-smart-hackathon-2024')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # External API Keys
    TOMTOM_API_KEY = os.getenv('TOMTOM_API_KEY', '')
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///fedx_smart.db')
    
    # Redis settings
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))  # 5 minutes
    
    # Route optimization settings
    MAX_STOPS_PER_ROUTE = int(os.getenv('MAX_STOPS_PER_ROUTE', 50))
    OPTIMIZATION_TIMEOUT = int(os.getenv('OPTIMIZATION_TIMEOUT', 30))  # seconds
    
    # Emission calculation settings
    DEFAULT_VEHICLE_TYPE = os.getenv('DEFAULT_VEHICLE_TYPE', 'diesel_truck')
    EMISSION_FACTORS = {
        'diesel_truck': 0.162,  # kg CO2 per km
        'petrol_truck': 0.184,  # kg CO2 per km
        'electric_truck': 0.045,  # kg CO2 per km (considering electricity source)
        'hybrid_truck': 0.098   # kg CO2 per km
    }
    
    # Traffic and weather update intervals
    TRAFFIC_UPDATE_INTERVAL = int(os.getenv('TRAFFIC_UPDATE_INTERVAL', 300))  # 5 minutes
    WEATHER_UPDATE_INTERVAL = int(os.getenv('WEATHER_UPDATE_INTERVAL', 1800))  # 30 minutes
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/fedx_smart.log')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}