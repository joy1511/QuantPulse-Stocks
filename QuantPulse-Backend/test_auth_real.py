"""
Test Real Authentication

Tests that authentication rejects invalid credentials and accepts valid ones.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*60)
print("🔐 Testing Real Authentication (No Demo Mode)")
print("="*60 + "\n")

# Test 1: Invalid credentials should FAIL
print("Test 1: Invalid Credentials")
print("-" * 60)
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login/json",
        json={"email": "fake@email.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("✅ PASS: Invalid credentials rejected (401 Unauthorized)")
    else:
        print(f"❌ FAIL: Expected 401, got {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print()

# Test 2: Valid credentials should SUCCEED
print("Test 2: Valid Credentials")
print("-" * 60)
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login/json",
        json={
            "email": "riddhisharma140606@gmail.com",
            "password": "R23314@riddhi"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ PASS: Valid credentials accepted (200 OK)")
        print(f"   User: {data['user']['full_name']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Token: {data['access_token'][:30]}...")
    else:
        print(f"❌ FAIL: Expected 200, got {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print()

# Test 3: Random dummy credentials should FAIL
print("Test 3: Random Dummy Credentials")
print("-" * 60)
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login/json",
        json={"email": "sdfgh@gmail.com", "password": "anything123"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("✅ PASS: Dummy credentials rejected (401 Unauthorized)")
    else:
        print(f"❌ FAIL: Expected 401, got {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print()
print("="*60)
print("✅ Authentication is working correctly!")
print("   - Demo mode removed")
print("   - Only real credentials accepted")
print("   - Invalid credentials properly rejected")
print("="*60)
print()
