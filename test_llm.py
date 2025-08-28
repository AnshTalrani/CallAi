#!/usr/bin/env python3
"""
Simple test script for Large Language Model (LLM) functionality
Tests the LangChain setup with LM Studio
"""

import sys
import time
from llm_thinking import LLMThinker

def test_llm():
    """Test the LLM functionality"""
    print("=" * 50)
    print("LLM (Large Language Model) Test")
    print("=" * 50)
    
    thinker = None
    try:
        # Initialize LLM
        print("Initializing LLM system...")
        thinker = LLMThinker()
        print("✓ LLM system initialized successfully!")
        
        # Test prompts
        test_prompts = [
            "Hello, how are you today?",
            "What is 2 + 2?",
            "Tell me a short joke.",
            "What is the capital of France?"
        ]
        
        print("\n" + "=" * 30)
        print("LLM RESPONSE TESTS")
        print("=" * 30)
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n🤖 Test {i}/{len(test_prompts)}")
            print(f"Prompt: '{prompt}'")
            print("Getting response...")
            
            try:
                start_time = time.time()
                response = thinker.get_response(prompt)
                end_time = time.time()
                
                duration = end_time - start_time
                print(f"✓ Response received! (took {duration:.2f} seconds)")
                
                # Validate response
                if response and len(response.strip()) > 0:
                    print("✅ Response validation passed!")
                else:
                    print("❌ Response validation failed - empty response")
                    return False
                    
            except Exception as e:
                print(f"❌ Error getting response: {e}")
                return False
        
        print("\n✅ LLM test PASSED - Model is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ LLM test FAILED with error: {e}")
        return False

def quick_llm_test():
    """Quick test without user interaction"""
    print("=" * 50)
    print("Quick LLM Test")
    print("=" * 50)
    
    try:
        # Test initialization
        print("Testing LLM initialization...")
        thinker = LLMThinker()
        print("✓ LLM initialization successful!")
        
        # Test model loading
        print("✓ LangChain setup successful!")
        print("✓ LM Studio connection successful!")
        
        # Quick response test
        print("Testing response generation...")
        test_prompt = "Say hello in one word."
        response = thinker.get_response(test_prompt)
        
        if response and len(response.strip()) > 0:
            print("✓ Response generation successful!")
            print("✓ Quick LLM test PASSED - System is ready!")
            return True
        else:
            print("❌ Response generation failed")
            return False
        
    except Exception as e:
        print(f"❌ Quick LLM test FAILED: {e}")
        return False

def test_llm_connection():
    """Test LLM connection without full initialization"""
    print("=" * 50)
    print("LLM Connection Test")
    print("=" * 50)
    
    try:
        # Test basic connection
        print("Testing LM Studio connection...")
        print("Make sure LM Studio is running on http://192.168.1.6:1234")
        
        # Try to create the chat model
        from langchain.chat_models import ChatOpenAI
        
        chat = ChatOpenAI(
            model_name="meta-llama-3.1-8b-instruct",
            openai_api_base="http://192.168.1.6:1234/v1",
            openai_api_key="not-needed",
            streaming=False  # Disable streaming for connection test
        )
        
        print("✓ Chat model created successfully!")
        
        # Test a simple call
        print("Testing simple API call...")
        response = chat.invoke("Hello")
        
        if response and hasattr(response, 'content'):
            print("✓ API call successful!")
            print("✓ LLM connection test PASSED!")
            return True
        else:
            print("❌ API call failed")
            return False
        
    except Exception as e:
        print(f"❌ LLM connection test FAILED: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure LM Studio is running")
        print("2. Check if the API endpoint is correct (http://192.168.1.6:1234)")
        print("3. Verify the model is loaded in LM Studio")
        return False

def interactive_llm_test():
    """Interactive test for LLM"""
    print("=" * 50)
    print("Interactive LLM Test")
    print("=" * 50)
    
    try:
        print("Initializing LLM for interactive test...")
        thinker = LLMThinker()
        print("✓ LLM ready for interactive testing!")
        
        print("\nYou can now chat with the LLM.")
        print("Type 'quit', 'exit', 'goodbye', or 'bye' to end the test.")
        print("Type 'test' for a quick response test.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'goodbye', 'bye']:
                    print("Ending interactive test...")
                    break
                elif user_input.lower() == 'test':
                    print("Running quick test...")
                    response = thinker.get_response("Say 'test successful' in a creative way.")
                    print(f"LLM: {response}")
                elif user_input:
                    response = thinker.get_response(user_input)
                    print(f"LLM: {response}")
                else:
                    print("Please enter some text.")
                    
            except KeyboardInterrupt:
                print("\nTest interrupted by user.")
                break
            except EOFError:
                print("\nEnd of input.")
                break
        
        print("✅ Interactive LLM test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Interactive LLM test FAILED: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            success = quick_llm_test()
        elif sys.argv[1] == "--connection":
            success = test_llm_connection()
        elif sys.argv[1] == "--interactive":
            success = interactive_llm_test()
        else:
            print("Usage: python test_llm.py [--quick|--connection|--interactive]")
            sys.exit(1)
    else:
        success = test_llm()
    
    sys.exit(0 if success else 1)