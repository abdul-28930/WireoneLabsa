#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Pricing Module

This script tests all available API endpoints and demonstrates
how to use the pricing module APIs.

Usage:
    python test_api.py
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n--- {title} ---")

def make_request(method, url, data=None, expected_status=200):
    """Make an API request and handle the response"""
    try:
        headers = {'Content-Type': 'application/json'}
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return None
        
        print(f"{method.upper()} {url}")
        if data:
            print(f"Request data: {json.dumps(data, indent=2)}")
        
        print(f"Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response text: {response.text}")
        
        if response.status_code != expected_status:
            print(f"⚠️  Expected status {expected_status}, got {response.status_code}")
        else:
            print("✅ Success")
        
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed to {url}")
        print("Make sure the Django server is running: python manage.py runserver")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_api_root():
    """Test the API root endpoint"""
    print_section("API ROOT ENDPOINT")
    make_request('GET', f"{API_BASE}/")

def test_calculate_price():
    """Test price calculation endpoint"""
    print_section("PRICE CALCULATION TESTS")
    
    # Test 1: Basic calculation
    print_subsection("Basic Price Calculation")
    data = {
        "distance": 5.5,
        "duration": 45,
        "waiting_time": 5
    }
    make_request('POST', f"{API_BASE}/calculate-price/", data)
    
    # Test 2: Edge case - exact base distance
    print_subsection("Edge Case - Exact Base Distance")
    data = {
        "distance": 3.0,
        "duration": 30,
        "waiting_time": 0
    }
    make_request('POST', f"{API_BASE}/calculate-price/", data)
    
    # Test 3: Long duration with time multiplier
    print_subsection("Long Duration with Time Multiplier")
    data = {
        "distance": 10.0,
        "duration": 150,  # 2.5 hours
        "waiting_time": 15
    }
    make_request('POST', f"{API_BASE}/calculate-price/", data)
    
    # Test 4: Invalid input (negative values)
    print_subsection("Invalid Input Test")
    data = {
        "distance": -1.0,
        "duration": 30,
        "waiting_time": 5
    }
    make_request('POST', f"{API_BASE}/calculate-price/", data, expected_status=400)
    
    # Test 5: Get documentation
    print_subsection("API Documentation")
    make_request('GET', f"{API_BASE}/calculate-price/")

def test_pricing_configs():
    """Test pricing configuration endpoints"""
    print_section("PRICING CONFIGURATION TESTS")
    
    # Test 1: List all configurations
    print_subsection("List All Configurations")
    response = make_request('GET', f"{API_BASE}/pricing-configs/")
    
    # Test 2: Get active configurations only
    print_subsection("Get Active Configurations")
    make_request('GET', f"{API_BASE}/pricing-configs/active/")
    
    # Test 3: Create new configuration
    print_subsection("Create New Configuration")
    new_config = {
        "name": "Test API Config",
        "base_distance": "4.0",
        "base_price": "90.0",
        "additional_km_price": "30.0",
        "time_multiplier_1": "1.0",
        "time_multiplier_2": "1.3",
        "time_multiplier_3": "2.0",
        "free_waiting_time": 4,
        "waiting_charge_per_min": "6.0",
        "applicable_days": "0,1,2,3,4",
        "is_active": False
    }
    create_response = make_request('POST', f"{API_BASE}/pricing-configs/", new_config, expected_status=201)
    
    # Test 4: Activate the created configuration (if creation was successful)
    if create_response and create_response.status_code == 201:
        try:
            config_id = create_response.json()['id']
            print_subsection(f"Activate Configuration {config_id}")
            make_request('POST', f"{API_BASE}/pricing-configs/{config_id}/activate/")
            
            # Test 5: Deactivate the configuration
            print_subsection(f"Deactivate Configuration {config_id}")
            make_request('POST', f"{API_BASE}/pricing-configs/{config_id}/deactivate/")
            
            # Test 6: Get specific configuration
            print_subsection(f"Get Specific Configuration {config_id}")
            make_request('GET', f"{API_BASE}/pricing-configs/{config_id}/")
            
        except Exception as e:
            print(f"Could not test activate/deactivate: {e}")

def test_configuration_logs():
    """Test configuration logs endpoint"""
    print_section("CONFIGURATION LOGS TESTS")
    make_request('GET', f"{API_BASE}/configuration-logs/")

def test_admin_interface():
    """Test admin interface accessibility"""
    print_section("ADMIN INTERFACE TEST")
    try:
        response = requests.get(f"{BASE_URL}/admin/")
        print(f"GET {BASE_URL}/admin/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Admin interface is accessible")
        else:
            print("⚠️  Admin interface returned unexpected status")
    except Exception as e:
        print(f"❌ Error accessing admin: {e}")

def run_performance_test():
    """Run a simple performance test"""
    print_section("PERFORMANCE TEST")
    print("Running 10 concurrent price calculations...")
    
    import time
    import threading
    
    results = []
    
    def single_request():
        data = {
            "distance": 5.0,
            "duration": 40,
            "waiting_time": 3
        }
        start_time = time.time()
        response = requests.post(f"{API_BASE}/calculate-price/", json=data)
        end_time = time.time()
        results.append({
            'status': response.status_code,
            'time': end_time - start_time
        })
    
    # Run 10 concurrent requests
    threads = []
    start_time = time.time()
    
    for i in range(10):
        thread = threading.Thread(target=single_request)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    successful_requests = len([r for r in results if r['status'] == 200])
    avg_response_time = sum(r['time'] for r in results) / len(results)
    
    print(f"Total requests: 10")
    print(f"Successful requests: {successful_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average response time: {avg_response_time:.3f} seconds")
    print(f"Requests per second: {10/total_time:.2f}")

def main():
    """Main test runner"""
    print(f"Pricing Module API Testing Script")
    print(f"Testing server at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test all endpoints
    test_api_root()
    test_calculate_price()
    test_pricing_configs()
    test_configuration_logs()
    test_admin_interface()
    
    # Performance test
    try:
        run_performance_test()
    except Exception as e:
        print(f"Performance test failed: {e}")
    
    print_section("TESTING COMPLETED")
    print("✅ All API tests completed!")
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/api/ to explore the browsable API")
    print("2. Visit http://localhost:8000/admin/ to manage configurations")
    print("3. Run automated tests with: python manage.py test")
    print("4. Check the sample data with: python manage.py populate_sample_data")

if __name__ == "__main__":
    main() 