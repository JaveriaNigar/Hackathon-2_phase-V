import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    "Content-Type": "application/json"
}

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("[OK] API Health Check: Healthy")
            return True
        else:
            print(f"[ERROR] API Health Check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] API Health Check error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint with a dummy user ID"""
    # This is a simplified test that assumes we have a valid user ID
    # In a real scenario, we would need to authenticate first
    user_id = "test-user-id"  # This is just for testing purposes
    
    message_data = {
        "message": "Add a task to buy groceries",
        "conversation_id": None  # Will create a new conversation
    }
    
    try:
        response = requests.post(f"{BASE_URL}/{user_id}/chat", json=message_data, headers=HEADERS)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Chat endpoint working")
            print(f"  Response: {result['response'][:100]}...")
            if result.get('tool_calls'):
                print(f"  Tool calls: {len(result['tool_calls'])}")
            return True
        else:
            print(f"[ERROR] Chat endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Chat endpoint error: {e}")
        return False

def main():
    print("Testing agent functionality...")
    
    # Test API health
    if not test_health():
        print("Health check failed, stopping tests")
        return
    
    # Test chat functionality
    test_chat_endpoint()
    
    print("\nFunctionality test completed!")

if __name__ == "__main__":
    main()