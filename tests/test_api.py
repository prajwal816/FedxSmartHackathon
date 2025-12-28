import pytest
import json

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_route_optimization_endpoint(client):
    """Test route optimization endpoint"""
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
