#!/usr/bin/env python3
"""
Simple test script to demonstrate the JWT authentication system.
Run this after starting the FastAPI server.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test the complete authentication flow."""
    
    # Test data
    test_email = "test@example.com"
    test_password = "testpassword123"
    
    print("🔐 Testing JWT Authentication System")
    print("=" * 50)
    
    # 1. Register a new user
    print("\n1. Registering new user...")
    register_data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User registered successfully!")
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the FastAPI server is running.")
        return
    
    # 2. Login
    print("\n2. Logging in...")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"✅ Login successful!")
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Access token: {access_token[:50]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    # 3. Get current user info
    print("\n3. Getting current user info...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ User info retrieved successfully!")
        print(f"   User ID: {user_info['id']}")
        print(f"   Email: {user_info['email']}")
        print(f"   Active: {user_info['is_active']}")
    else:
        print(f"❌ Failed to get user info: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # 4. Test protected endpoint (without token)
    print("\n4. Testing protected endpoint without token...")
    response = requests.post(f"{BASE_URL}/api/query", json={"q": "test query"})
    if response.status_code == 401:
        print("✅ Protected endpoint correctly rejected request without token")
    else:
        print(f"❌ Protected endpoint should have rejected request: {response.status_code}")
    
    # 5. Test protected endpoint (with token)
    print("\n5. Testing protected endpoint with token...")
    response = requests.post(
        f"{BASE_URL}/api/query", 
        json={"q": "test query"},
        headers=headers
    )
    if response.status_code == 200:
        print("✅ Protected endpoint accepted request with valid token")
        result = response.json()
        print(f"   Query result: {result.get('answer', 'No answer')[:100]}...")
    else:
        print(f"❌ Protected endpoint failed with valid token: {response.status_code}")
        print(f"   Response: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system test completed!")

if __name__ == "__main__":
    test_authentication()
