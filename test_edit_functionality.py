import requests
import json
import time
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api"
HEADERS = {
    "Content-Type": "application/json"
}

def test_edit_functionality():
    print("Testing edit functionality...")
    
    # Test user ID for testing
    user_id = "test-user-id"
    
    # Test 1: Add a task first
    print("\n1. Adding a task...")
    message_data = {
        "message": "Add a task called market",
        "conversation_id": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/{user_id}/chat", json=message_data, headers=HEADERS)
        if response.status_code == 200:
            result = response.json()
            print(f"   [OK] Task added: {result['response'][:100]}...")
        else:
            print(f"   [ERROR] Task addition failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   [ERROR] Error adding task: {e}")
        return False
    
    time.sleep(1)  # Brief pause to ensure task is processed
    
    # Test 2: Edit the task
    print("\n2. Editing the task...")
    edit_message_data = {
        "message": "Edit market task to grocery shopping",
        "conversation_id": response.json()['conversation_id']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/{user_id}/chat", json=edit_message_data, headers=HEADERS)
        if response.status_code == 200:
            result = response.json()
            print(f"   [OK] Task edited: {result['response'][:150]}...")

            # Check if the response indicates the edit was successful
            response_text = result['response'].lower()
            if 'grocery shopping' in response_text and ('edit' in response_text or 'change' in response_text or 'update' in response_text):
                print("   [OK] Edit command properly interpreted")
            else:
                print(f"   [WARN] Edit may not have been properly interpreted: {result['response']}")

        else:
            print(f"   [ERROR] Task edit failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   [ERROR] Error editing task: {e}")
        return False
    
    time.sleep(1)  # Brief pause to ensure edit is processed
    
    # Test 3: List tasks to verify the edit
    print("\n3. Listing tasks to verify edit...")
    list_message_data = {
        "message": "Show my tasks",
        "conversation_id": response.json()['conversation_id']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/{user_id}/chat", json=list_message_data, headers=HEADERS)
        if response.status_code == 200:
            result = response.json()
            print(f"   [OK] Tasks listed: {result['response'][:200]}...")

            # Check if the updated task appears in the response
            response_text = result['response'].lower()
            if 'grocery shopping' in response_text:
                print("   [OK] Updated task appears in task list")
            else:
                print(f"   [WARN] Updated task may not appear in list: {result['response']}")

        else:
            print(f"   [ERROR] Task listing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   [ERROR] Error listing tasks: {e}")
        return False
    
    print("\nEdit functionality test completed!")
    return True

def test_various_edit_patterns():
    print("\nTesting various edit command patterns...")
    
    user_id = "test-user-id"
    
    patterns = [
        "Edit market task to grocery shopping",
        "Change market to grocery shopping", 
        "Update market grocery shopping",
        "Rename market to grocery shopping"
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"\n{i+1}. Testing pattern: '{pattern}'")
        
        message_data = {
            "message": pattern,
            "conversation_id": None
        }
        
        try:
            response = requests.post(f"{BASE_URL}/{user_id}/chat", json=message_data, headers=HEADERS)
            if response.status_code == 200:
                result = response.json()
                print(f"   [OK] Pattern processed: {result['response'][:100]}...")
            else:
                print(f"   [ERROR] Pattern failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   [ERROR] Error with pattern: {e}")
    
    print("\nPattern testing completed!")

if __name__ == "__main__":
    print("Starting edit functionality tests...")
    
    success = test_edit_functionality()
    test_various_edit_patterns()
    
    print("\nAll tests completed!")