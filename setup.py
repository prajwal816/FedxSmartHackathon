"""
Setup script for FedxSmart Platform
"""

import os
import sys
import json
import logging
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'cache',
        'data/exports',
        'tests/unit',
        'tests/integration',
        'docs/api',
        'docs/architecture'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_logging():
    """Setup logging configuration"""
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': 'logs/fedx_smart.log',
                'mode': 'a',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    # Save logging config
    with open('config/logging.json', 'w') as f:
        json.dump(log_config, f, indent=2)
    
    print("✓ Logging configuration created")

def create_env_file():
    """Create environment file template"""
    env_content = """# FedxSmart Platform Configuration

# Application Settings
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here

# Server Settings
HOST=0.0.0.0
PORT=5000

# External API Keys
TOMTOM_API_KEY=your-tomtom-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
OPENWEATHER_API_KEY=your-openweather-api-key

# Database Settings
DATABASE_URL=sqlite:///fedx_smart.db

# Redis Settings
REDIS_URL=redis://localhost:6379/0
CACHE_TIMEOUT=300

# Route Optimization Settings
MAX_STOPS_PER_ROUTE=50
OPTIMIZATION_TIMEOUT=30

# Logging Settings
LOG_LEVEL=INFO
LOG_FILE=logs/fedx_smart.log

# Traffic and Weather Update Intervals (seconds)
TRAFFIC_UPDATE_INTERVAL=300
WEATHER_UPDATE_INTERVAL=1800
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Environment file (.env) created")
    else:
        print("✓ Environment file already exists")

def create_docker_files():
    """Create Docker configuration files"""
    
    # Dockerfile
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs cache data/exports

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
"""
    
    # docker-compose.yml
    docker_compose_content = """version: '3.8'

services:
  fedx-smart:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DEBUG=False
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
      - ./cache:/app/cache
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - fedx-smart
    restart: unless-stopped

volumes:
  redis_data:
"""
    
    # nginx.conf
    nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream fedx_smart {
        server fedx-smart:5000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://fedx_smart;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/static/;
        }
    }
}
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose_content)
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✓ Docker configuration files created")

def create_test_files():
    """Create basic test structure"""
    
    # Test configuration
    test_config = """import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def app():
    from app import app
    app.config['TESTING'] = True
    app.config['DATABASE_URL'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def client(app):
    return app.test_client()
"""
    
    # Sample test
    sample_test = """import pytest
import json

def test_health_endpoint(client):
    \"\"\"Test health check endpoint\"\"\"
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_route_optimization_endpoint(client):
    \"\"\"Test route optimization endpoint\"\"\"
    test_data = {
        'origin': {'lat': 40.7128, 'lng': -74.0060},
        'destinations': [
            {'lat': 40.7589, 'lng': -73.9851},
            {'lat': 40.6892, 'lng': -74.0445}
        ],
        'vehicle_type': 'diesel_truck'
    }
    
    response = client.post('/api/optimize-route', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'route_id' in data
    assert 'optimized_route' in data
"""
    
    with open('tests/conftest.py', 'w') as f:
        f.write(test_config)
    
    with open('tests/test_api.py', 'w') as f:
        f.write(sample_test)
    
    print("✓ Test files created")

def create_documentation():
    """Create basic documentation structure"""
    
    api_docs = """# FedxSmart API Documentation

## Overview
The FedxSmart API provides endpoints for route optimization, emission calculation, and analytics.

## Authentication
Currently, no authentication is required for demo purposes. In production, implement API key authentication.

## Endpoints

### Route Optimization
- **POST** `/api/optimize-route`
- **GET** `/api/emissions/{route_id}`
- **POST** `/api/scenario-analysis`

### Analytics
- **GET** `/api/analytics/dashboard`
- **POST** `/api/analytics/comparison`

### Utilities
- **GET** `/api/vehicles`
- **GET** `/health`

## Rate Limits
- 100 requests per minute per IP
- 1000 requests per hour per IP

## Error Handling
All errors return JSON with error message and appropriate HTTP status code.
"""
    
    architecture_docs = """# FedxSmart Architecture

## System Overview
FedxSmart is a microservices-based platform for dynamic route optimization.

## Components

### Core Services
- Route Optimizer: Handles route calculation and optimization
- Emission Calculator: Calculates CO2 emissions and sustainability metrics
- Analytics Engine: Provides insights and reporting
- Scenario Analyzer: Performs what-if analysis

### External Integrations
- TomTom API: Traffic and routing data
- OpenWeather API: Weather conditions
- OSRM: Open-source routing engine

### Data Layer
- SQLite: Primary database (development)
- Redis: Caching layer
- File system: Route and analytics data

## Deployment
- Docker containers
- Nginx reverse proxy
- Redis for caching
- Horizontal scaling support
"""
    
    with open('docs/api/README.md', 'w') as f:
        f.write(api_docs)
    
    with open('docs/architecture/README.md', 'w') as f:
        f.write(architecture_docs)
    
    print("✓ Documentation created")

def main():
    """Main setup function"""
    print("🚚 Setting up FedxSmart Platform...")
    print("=" * 50)
    
    try:
        setup_directories()
        setup_logging()
        create_env_file()
        create_docker_files()
        create_test_files()
        create_documentation()
        
        print("=" * 50)
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your API keys")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the application: python app.py")
        print("4. Access dashboard: http://localhost:5000")
        print("\nFor Docker deployment:")
        print("1. docker-compose up --build")
        print("2. Access via: http://localhost")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()