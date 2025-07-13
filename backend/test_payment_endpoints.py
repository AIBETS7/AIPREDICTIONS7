#!/usr/bin/env python3
"""
Test payment endpoints
"""

import requests
import json

def test_payment_endpoints():
    """Test payment endpoints"""
    base_url = "https://myfootballpredictions.onrender.com"
    
    print("Testing payment endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test payment status endpoint
    try:
        response = requests.get(f"{base_url}/api/payment-status")
        print(f"✅ Payment status endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Payment status endpoint error: {e}")
    
    # Test check access endpoint (should work without payment)
    try:
        response = requests.post(f"{base_url}/api/check-access", 
                               json={"email": "test@example.com"})
        print(f"✅ Check access endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Check access endpoint error: {e}")

if __name__ == "__main__":
    test_payment_endpoints() 