#!/usr/bin/env python3
"""
Demo Test Script for FedxSmart Platform
Tests all major functionality for hackathon demonstration
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
DEMO_ROUTES = {
    "manhattan": {
        "origin": {"lat": 40.7128, "lng": -74.0060},
        "destinations": [
            {"lat": 40.7589, "lng": -73.9851, "priority": 1},
            {"lat": 40.6892, "lng": -74.0445, "priority": 2},
            {"lat": 40.7505, "lng": -73.9934, "priority": 1},
            {"lat": 40.7282, "lng": -73.7949, "priority": 3}
        ],
        "vehicle_type": "diesel_truck"
    },
    "brooklyn": {
        "origin": {"lat": 40.6782, "lng": -73.9442},
        "destinations": [
            {"lat": 40.6591, "lng": -73.9442, "priority": 1},
            {"lat": 40.6403, "lng": -74.0099, "priority": 2},
            {"lat": 40.6928, "lng": -73.9903, "priority": 2}
        ],
        "vehicle_type": "hybrid_truck"
    }
}

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_health_check():
    """Test health check endpoint"""
    print_header("Health Check Test")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data.get('status', 'unknown')}")
            print_info(f"Version: {data.get('version', 'unknown')}")
            print_info(f"Services: {data.get('services', {})}")
            return True
        else:
            print_error(f"Health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Health check failed: {str(e)}")
        return False

def test_route_optimization(route_name, route_data):
    """Test route optimization endpoint"""
    print_header(f"Route Optimization Test - {route_name.title()}")
    
    try:
        # Prepare request data
        request_data = {
            "origin": route_data["origin"],
            "destinations": route_data["destinations"],
            "vehicle_type": route_data["vehicle_type"],
            "preferences": {"optimize_for": "time"}
        }
        
        print_info(f"Optimizing route with {len(route_data['destinations'])} stops...")
        print_info(f"Vehicle type: {route_data['vehicle_type']}")
        
        # Make API request
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/optimize-route",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract metrics
            metrics = data.get('optimization_metrics', {})
            emissions = data.get('emissions', {})
            
            print_success(f"Route optimized in {end_time - start_time:.2f} seconds")
            print_info(f"Route ID: {data.get('route_id', 'unknown')}")
            print_info(f"Total Distance: {metrics.get('total_distance_km', 0):.1f} km")
            print_info(f"Total Time: {metrics.get('total_time_minutes', 0):.0f} minutes")
            print_info(f"Fuel Consumed: {metrics.get('fuel_consumed_liters', 0):.1f} L")
            print_info(f"Estimated Cost: ${metrics.get('estimated_cost_usd', 0):.2f}")
            
            if emissions:
                print_info(f"CO₂ Emissions: {emissions.get('total_co2_kg', 0):.2f} kg")
                print_info(f"Green Score: {emissions.get('green_score', 0)}/100")
            
            return data.get('route_id')
            
        else:
            print_error(f"Route optimization failed: HTTP {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Route optimization failed: {str(e)}")
        return None

def test_emissions_endpoint(route_id):
    """Test emissions endpoint"""
    print_header("Emissions Analysis Test")
    
    if not route_id:
        print_error("No route ID provided, skipping emissions test")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/emissions/{route_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Emissions data retrieved successfully")
            print_info(f"Total CO₂: {data.get('total_co2_kg', 0):.3f} kg")
            print_info(f"CO₂ per km: {data.get('co2_per_km', 0):.3f} kg/km")
            print_info(f"Green Score: {data.get('green_score', 0)}/100")
            
            # Show breakdown if available
            breakdown = data.get('emission_breakdown', {})
            if breakdown:
                print_info("Emission Breakdown:")
                for source, amount in breakdown.items():
                    print_info(f"  - {source.replace('_', ' ').title()}: {amount:.3f} kg")
            
            return True
        else:
            print_error(f"Emissions retrieval failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Emissions retrieval failed: {str(e)}")
        return False

def test_scenario_analysis(route_id):
    """Test scenario analysis endpoint"""
    print_header("Scenario Analysis Test")
    
    if not route_id:
        print_error("No route ID provided, skipping scenario analysis")
        return False
    
    try:
        # Test peak traffic scenario
        scenario_data = {
            "base_route_id": route_id,
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
        
        print_info("Running scenario analysis...")
        response = requests.post(
            f"{BASE_URL}/api/scenario-analysis",
            json=scenario_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Scenario analysis completed")
            
            scenarios = data.get('scenarios', {})
            for scenario_name, scenario_result in scenarios.items():
                print_info(f"\nScenario: {scenario_name}")
                
                metrics = scenario_result.get('modified_metrics', {})
                impact = scenario_result.get('impact_analysis', {})
                
                print_info(f"  Time: {metrics.get('total_time_minutes', 0):.0f} minutes")
                print_info(f"  Distance: {metrics.get('total_distance_km', 0):.1f} km")
                print_info(f"  Emissions: {metrics.get('total_co2_kg', 0):.2f} kg CO₂")
                
                # Show impact vs baseline
                if 'total_time_minutes' in impact:
                    time_impact = impact['total_time_minutes']
                    print_info(f"  Time Impact: {time_impact.get('percentage_change', 0):+.1f}%")
            
            return True
        else:
            print_error(f"Scenario analysis failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Scenario analysis failed: {str(e)}")
        return False

def test_dashboard_analytics():
    """Test dashboard analytics endpoint"""
    print_header("Dashboard Analytics Test")
    
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Dashboard analytics retrieved")
            
            summary = data.get('summary', {})
            print_info(f"Total Routes: {summary.get('total_routes', 0)}")
            print_info(f"Total Distance: {summary.get('total_distance_km', 0):.1f} km")
            print_info(f"Total Emissions: {summary.get('total_emissions_kg', 0):.1f} kg")
            print_info(f"Average Green Score: {summary.get('average_green_score', 0):.1f}")
            
            return True
        else:
            print_error(f"Dashboard analytics failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Dashboard analytics failed: {str(e)}")
        return False

def test_vehicle_types():
    """Test vehicle types endpoint"""
    print_header("Vehicle Types Test")
    
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Vehicle types retrieved")
            
            vehicle_types = data.get('vehicle_types', {})
            print_info(f"Available vehicle types: {len(vehicle_types)}")
            
            for vehicle_type, specs in vehicle_types.items():
                print_info(f"  - {vehicle_type}: {specs.get('description', 'No description')}")
                print_info(f"    Emission Factor: {specs.get('emission_factor', 0):.3f} kg CO₂/km")
                print_info(f"    Efficiency Rating: {specs.get('efficiency_rating', 'Unknown')}")
            
            return True
        else:
            print_error(f"Vehicle types retrieval failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Vehicle types retrieval failed: {str(e)}")
        return False

def run_comprehensive_demo():
    """Run comprehensive demo test suite"""
    print_header("FedxSmart Platform Demo Test Suite")
    print_info(f"Testing against: {BASE_URL}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    route_ids = []
    
    # Test 1: Health Check
    test_results.append(("Health Check", test_health_check()))
    
    # Test 2: Vehicle Types
    test_results.append(("Vehicle Types", test_vehicle_types()))
    
    # Test 3: Route Optimization (Manhattan)
    route_id = test_route_optimization("manhattan", DEMO_ROUTES["manhattan"])
    test_results.append(("Manhattan Route Optimization", route_id is not None))
    if route_id:
        route_ids.append(route_id)
    
    # Test 4: Route Optimization (Brooklyn)
    route_id = test_route_optimization("brooklyn", DEMO_ROUTES["brooklyn"])
    test_results.append(("Brooklyn Route Optimization", route_id is not None))
    if route_id:
        route_ids.append(route_id)
    
    # Test 5: Emissions Analysis
    if route_ids:
        test_results.append(("Emissions Analysis", test_emissions_endpoint(route_ids[0])))
    
    # Test 6: Scenario Analysis
    if route_ids:
        test_results.append(("Scenario Analysis", test_scenario_analysis(route_ids[0])))
    
    # Test 7: Dashboard Analytics
    test_results.append(("Dashboard Analytics", test_dashboard_analytics()))
    
    # Summary
    print_header("Test Results Summary")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name}")
            passed_tests += 1
        else:
            print_error(f"{test_name}")
    
    print_header("Final Results")
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print_success("🎉 All tests passed! Platform is ready for demo.")
        return True
    else:
        print_error(f"⚠️  {total_tests - passed_tests} test(s) failed. Check the issues above.")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick health check only
        print_header("Quick Health Check")
        success = test_health_check()
        sys.exit(0 if success else 1)
    else:
        # Full demo test suite
        success = run_comprehensive_demo()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()