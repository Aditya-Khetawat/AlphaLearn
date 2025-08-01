import requests
import json

# Test the backend API endpoints
BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    """Test user registration"""
    print("Testing registration...")
    
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.text}")
        
        if response.status_code == 200:
            return data
        else:
            print(f"Registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"Registration error: {e}")
        return None

def test_login(user_data):
    """Test user login"""
    if not user_data:
        print("No user data to test login")
        return None
        
    print("\nTesting login...")
    
    data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=data)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"Login error: {e}")
        return None

if __name__ == "__main__":
    # Test registration first
    user_data = test_register()
    
    # If registration successful, test login
    if user_data:
        login_result = test_login(user_data)
        
        if login_result:
            print(f"\nSuccess! Got access token: {login_result.get('access_token', 'N/A')[:20]}...")
