#!/usr/bin/env python3
"""
Test script to verify authentication flow works correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test the complete authentication flow"""
    print("🧪 Testing Authentication Flow")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("1. Registering test user...")
    register_data = {
        "username": "test_employee",
        "email": "employee@test.com",
        "password": "testpassword123",
        "role": "employee",
        "skills": ["Python", "FastAPI", "SQLAlchemy"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        print(f"   Registration status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Registration successful")
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return False
    
    # Step 2: Login to get token
    print("\n2. Logging in...")
    login_data = {
        "email": "employee@test.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"   Login status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("   ✅ Login successful")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Step 3: Test protected endpoint
    print("\n3. Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/tasks/my", headers=headers)
        print(f"   Protected endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Protected endpoint accessible")
            tasks = response.json()
            print(f"   Found {len(tasks)} tasks")
        elif response.status_code == 403:
            print("   ❌ 403 Forbidden - Authentication issue")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Protected endpoint error: {e}")
        return False
    
    # Step 4: Test task creation
    print("\n4. Testing task creation...")
    task_data = {
        "title": "Test Task",
        "description": "This is a test task for authentication"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks/auto-assign", json=task_data, headers=headers)
        print(f"   Task creation status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Task creation successful")
            result = response.json()
            print(f"   Task ID: {result.get('task_id')}")
        elif response.status_code == 403:
            print("   ❌ 403 Forbidden - Authentication issue")
            return False
        else:
            print(f"   ❌ Task creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Task creation error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Authentication flow test completed successfully!")
    return True

def test_role_validation():
    """Test role-based access control"""
    print("\n🔐 Testing Role-Based Access Control")
    print("=" * 50)
    
    # Register different user roles
    users = [
        {
            "username": "test_admin",
            "email": "admin@test.com",
            "password": "testpassword123",
            "role": "admin",
            "skills": ["Management", "Leadership"]
        },
        {
            "username": "test_manager",
            "email": "manager@test.com",
            "password": "testpassword123",
            "role": "manager",
            "skills": ["Project Management", "Team Leadership"]
        }
    ]
    
    tokens = {}
    
    for user in users:
        print(f"\nTesting {user['role']} role...")
        
        # Register user
        try:
            response = requests.post(f"{BASE_URL}/register", json=user)
            if response.status_code != 200:
                print(f"   ⚠️  User may already exist: {response.text}")
        except Exception as e:
            print(f"   ⚠️  Registration error: {e}")
        
        # Login user
        try:
            login_response = requests.post(f"{BASE_URL}/login", json={
                "email": user["email"],
                "password": user["password"]
            })
            if login_response.status_code == 200:
                token = login_response.json().get("access_token")
                tokens[user["role"]] = token
                print(f"   ✅ {user['role']} login successful")
            else:
                print(f"   ❌ {user['role']} login failed: {login_response.text}")
        except Exception as e:
            print(f"   ❌ {user['role']} login error: {e}")
    
    # Test role-based endpoints
    if "admin" in tokens:
        print(f"\nTesting admin access...")
        headers = {"Authorization": f"Bearer {tokens['admin']}"}
        try:
            response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
            print(f"   Admin access to /tasks/: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Admin access error: {e}")
    
    if "manager" in tokens:
        print(f"\nTesting manager access...")
        headers = {"Authorization": f"Bearer {tokens['manager']}"}
        try:
            response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
            print(f"   Manager access to /tasks/: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Manager access error: {e}")
    
    if "employee" in tokens:
        print(f"\nTesting employee access...")
        headers = {"Authorization": f"Bearer {tokens['employee']}"}
        try:
            response = requests.get(f"{BASE_URL}/tasks/my", headers=headers)
            print(f"   Employee access to /tasks/my: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Employee access error: {e}")

def main():
    """Run all authentication tests"""
    print("🔐 Authentication Flow Testing")
    print("=" * 50)
    
    # Test basic auth flow
    auth_success = test_auth_flow()
    
    if auth_success:
        # Test role validation
        test_role_validation()
        
        print("\n" + "=" * 50)
        print("✅ All authentication tests completed!")
    else:
        print("\n" + "=" * 50)
        print("❌ Authentication flow test failed!")

if __name__ == "__main__":
    main() 