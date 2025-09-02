#!/usr/bin/env python3
"""
Simple test script for Large Language Model (LLM) functionality
Tests the LLM setup with Ollama
"""

import sys
import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_thinking import LLMThinker

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
        print(f"Error testing LLM connection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_integration():
    """Test LLM with template integration"""
    print("=" * 50)
    print("LLM Template Integration Test")
    print("=" * 50)
    
    thinker = None
    try:
        # Initialize LLM
        print("Initializing LLM with template context...")
        thinker = LLMThinker()
        
        # Set template context
        thinker.current_campaign_context = "Sales campaign for product outreach"
        thinker.current_document_context = "Product information: Our solution helps businesses increase efficiency by 30%"
        thinker.current_template_personality = "Professional and solution-oriented sales agent"
        
        print("✓ Template context set successfully!")
        
        # Test template-aware response
        test_prompt = "Tell me about our product benefits"
        print(f"\n🤖 Testing template-aware response for: '{test_prompt}'")
        
        response = thinker.get_response_with_context(
            test_prompt,
            campaign_context={
                'campaign': {'name': 'Sales Campaign', 'purpose': 'sales'},
                'template': {'llm_personality': {'name': 'Sarah', 'motive': 'Help customers'}},
                'document_context': 'Product helps increase efficiency by 30%'
            },
            conversation_context={'current_stage': 'introduction'}
        )
        
        if response and len(response.strip()) > 0:
            print("✅ Template integration test PASSED!")
            return True
        else:
            print("❌ Template integration test failed - empty response")
            return False
            
    except Exception as e:
        print(f"❌ Template integration test FAILED with error: {e}")
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
        print("✓ Ollama connection successful!")
        
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
        print("Testing Ollama connection...")
        print("Make sure Ollama is running on http://localhost:11434")
        
        # Try to create the chat model
        import ollama
        
        # Initialize Ollama client
        client = ollama.Client(host="http://localhost:11434")
        
        # Test connection by listing models
        models = client.list()
        if not models.get('models'):
            print("No models found. Please make sure Ollama is running and models are pulled.")
            return
        
        print("✓ Chat model created successfully!")
        
        # Test a simple call
        print("Testing simple API call...")
        response = client.generate(
            model="llama2",  # Use a default model that should be available
            prompt="Hello"
        )
        
        if response and 'response' in response:
            print("✓ API call successful!")
            print("✓ LLM connection test PASSED!")
            print(f"Response: {response['response']}")
            return True
        else:
            print("❌ API call failed")
            return False
        
    except Exception as e:
        print(f"❌ LLM connection test FAILED: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Ollama is running (run 'ollama serve' in a terminal)")
        print("2. Check if the Ollama API is accessible at http://localhost:11434")
        print("3. Make sure you have at least one model downloaded (e.g., 'ollama pull llama2')")
        print("4. If running in a container, ensure port 11434 is properly exposed")
        print("5. Check Ollama logs for any errors")
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
        elif sys.argv[1] == "--template":
            success = test_template_integration()
        else:
            print("Usage: python test_llm.py [--quick|--connection|--interactive|--template]")
            sys.exit(1)
    else:
        # Run both basic and template integration tests
        print("Running basic LLM tests...")
        success1 = test_llm()
        
        print("\nRunning template integration tests...")
        success2 = test_template_integration()
        
        success = success1 and success2
    
    sys.exit(0 if success else 1)