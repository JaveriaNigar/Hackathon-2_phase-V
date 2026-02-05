import requests
import json
import time
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    "Content-Type": "application/json"
}

# Sample JWT token for testing (this would need to be a valid token in a real scenario)
# For testing purposes, we'll need to create a user and get a valid token
# But for now, let's assume we have a test user

def test_basic_functionality():
    print("Testing basic functionality...")

    # First, let's try to register a test user
    user_data = {
        "email": f"testuser_{uuid.uuid4()}@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=user_data, headers=HEADERS)
        if response.status_code in [200, 201, 400]:  # Allow for existing user
            print("[OK] User registration attempted")
        else:
            print(f"[ERROR] User registration failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Error registering user: {e}")
        return None

    # Try to login to get a token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data, headers=HEADERS)
        if response.status_code == 200:
            token = response.json().get("access_token")
            HEADERS["Authorization"] = f"Bearer {token}"
            print("[OK] User login successful")
        else:
            print(f"[ERROR] User login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Error logging in user: {e}")
        return None

    # Test creating a conversation
    try:
        response = requests.post(f"{BASE_URL}/conversations", headers=HEADERS)
        if response.status_code == 200:
            conversation_id = response.json()["id"]
            print(f"[OK] Conversation created: {conversation_id}")
        else:
            print(f"[ERROR] Conversation creation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Error creating conversation: {e}")
        return None

    # Test sending a message to the agent
    message_data = {
        "message": "Add a task to buy groceries",
        "conversation_id": str(conversation_id)
    }

    try:
        response = requests.post(f"{BASE_URL}/{conversation_id}/chat", json=message_data, headers=HEADERS)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Message sent successfully")
            print(f"  Response: {result['response'][:100]}...")
            if result.get('tool_calls'):
                print(f"  Tool calls: {len(result['tool_calls'])}")
        else:
            print(f"[ERROR] Message sending failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Error sending message: {e}")
        return None

    # Test getting tasks
    try:
        response = requests.get(f"{BASE_URL}/{conversation_id}/tasks", headers=HEADERS)
        if response.status_code in [200, 404]:  # 404 is OK if no tasks exist yet
            if response.status_code == 200:
                tasks = response.json()
                print(f"[OK] Retrieved tasks: {len(tasks)} found")
            else:
                print("[OK] Retrieved tasks: none found (OK)")
        else:
            print(f"[ERROR] Task retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error retrieving tasks: {e}")

    print("\nBasic functionality test completed!")
    return True

if __name__ == "__main__":
    print("Starting agent functionality test...")
    test_basic_functionality()