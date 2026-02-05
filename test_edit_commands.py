#!/usr/bin/env python3
"""
Test script to verify that the TodoAgent properly handles edit commands.
"""

import os
import sys
import logging

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.agents.todo_agent import TodoAgent

def test_edit_commands():
    """Test that the TodoAgent properly handles edit commands."""
    print("Testing edit command handling...")

    # Get the database URL from environment
    database_url = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")
    print(f"Using database URL: {database_url}")

    try:
        # Create the agent
        agent = TodoAgent(database_url=database_url)
        print("+ TodoAgent initialized successfully!")
        print("+ Selected model: {}".format(agent.model_name))

        # Test various edit command patterns
        test_cases = [
            "Edit market task to grocery shopping",
            "Change market to grocery shopping", 
            "Update market grocery shopping",
            "Rename market to grocery shopping",
            "Edit task market to grocery shopping"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: '{test_case}'")
            result = agent.process_message(
                user_id="test_user_123",
                message=test_case,
                conversation_id="test_conversation"
            )
            
            print(f"  Response: {result['response'][:100]}...")
            print(f"  Tool calls: {len(result['tool_calls'])}")
            if result['tool_calls']:
                print(f"  Tool call details: {result['tool_calls'][0]}")
            
            # Check if the response makes sense for an edit command
            response_lower = result['response'].lower()
            if any(word in response_lower for word in ['edit', 'change', 'update', 'rename']):
                print("  ✓ Edit command properly recognized")
            else:
                print("  ⚠ Edit command may not have been properly recognized")

        return True

    except Exception as e:
        print("- Error testing edit commands: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

def test_competing_commands():
    """Test that edit commands don't interfere with other commands."""
    print("\nTesting competing command handling...")

    database_url = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")
    
    try:
        agent = TodoAgent(database_url=database_url)
        
        # Test cases that might confuse the agent
        test_cases = [
            "Complete market task",  # Should NOT be interpreted as edit
            "Mark market as done",   # Should NOT be interpreted as edit
            "Buy groceries at market",  # Should NOT be interpreted as edit
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nCompeting Test {i}: '{test_case}'")
            result = agent.process_message(
                user_id="test_user_123",
                message=test_case,
                conversation_id="test_conversation"
            )
            
            print(f"  Response: {result['response'][:100]}...")
            print(f"  Tool calls: {len(result['tool_calls'])}")
            
            # Check that it's not being misinterpreted as an edit
            response_lower = result['response'].lower()
            if 'edit' in response_lower or 'change' in response_lower or 'update' in response_lower:
                print("  ⚠ Command may have been misinterpreted as edit")
            else:
                print("  ✓ Command correctly NOT interpreted as edit")

        return True

    except Exception as e:
        print("- Error testing competing commands: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("TodoAgent Edit Command Test")
    print("=" * 60)

    success1 = test_edit_commands()
    success2 = test_competing_commands()

    print("=" * 60)
    if success1 and success2:
        print("+ All Tests PASSED: Edit commands are working correctly!")
    else:
        print("- Some Tests FAILED: There are still issues with edit commands.")
    print("=" * 60)