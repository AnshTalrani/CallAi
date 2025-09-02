#!/usr/bin/env python3
"""
Test script for LLM integration with Ollama.
"""
import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.llm_thinking import LLMThinker

def test_simple_response():
    """Test getting a simple response from the LLM."""
    print("Testing simple response...")
    thinker = LLMThinker()
    response = thinker.get_response("Hello, how are you?")
    print(f"Response: {response}")
    return response is not None and len(response) > 0

def test_contextual_response():
    """Test getting a response with context."""
    print("\nTesting response with context...")
    thinker = LLMThinker()
    
    context = {
        "campaign": {
            "name": "Test Campaign",
            "purpose": "DEMO",
            "description": "A test campaign for LLM integration"
        },
        "template": {
            "llm_personality": {
                "name": "Test Assistant",
                "personality_traits": ["helpful", "knowledgeable", "friendly"]
            }
        }
    }
    
    response = thinker.get_response_with_context(
        "Tell me about this campaign",
        campaign_context=context
    )
    print(f"Response with context: {response}")
    return response is not None and len(response) > 0

def main():
    """Run all tests."""
    print("=== Starting LLM Integration Tests ===\n")
    
    # Wait a moment to ensure Ollama is ready
    print("Waiting for Ollama to be ready...")
    time.sleep(2)
    
    # Run tests
    success = True
    
    print("\n--- Test 1: Simple Response ---")
    if not test_simple_response():
        print("❌ Simple response test failed")
        success = False
    else:
        print("✅ Simple response test passed")
    
    print("\n--- Test 2: Contextual Response ---")
    if not test_contextual_response():
        print("❌ Contextual response test failed")
        success = False
    else:
        print("✅ Contextual response test passed")
    
    # Print final result
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
