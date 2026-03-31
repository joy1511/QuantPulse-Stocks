"""
Test Login Script

Tests the login functionality with the created user account.
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"

# User credentials
email = "riddhisharma140606@gmail.com"
password = "R23314@riddhi"

print("\n" + "="*60)
print("🔐 Testing Login")
print("="*60 + "\n")

# Test login
print(f"📧 Email: {email}")
print(f"🔑 Password: {'*' * len(password)}")
print()

print("🔌 Attempting login...")

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login/json",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("="*60)
        print("🎉 LOGIN SUCCESSFUL!")
        print("="*60)
        print()
        print(f"🎫 Access Token: {data['access_token'][:50]}...")
        print(f"📝 Token Type: {data['token_type']}")
        print()
        print("👤 User Info:")
        print(f"   ID: {data['user']['id']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Name: {data['user']['full_name']}")
        print(f"   Active: {data['user']['is_active']}")
        print(f"   Verified: {data['user']['is_verified']}")
        print()
        print("✅ Authentication is working perfectly!")
        print()
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server")
    print("   Make sure the server is running: python run.py")
except Exception as e:
    print(f"❌ Error: {e}")
