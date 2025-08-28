#!/usr/bin/env python3
"""
Comprehensive test script for all AI models (STT, TTS, LLM)
Tests each component individually and provides a summary
"""

import sys
import time
import subprocess
from typing import Dict, List, Tuple

def run_test_script(script_name: str, args: List[str] = None) -> Tuple[bool, str]:
    """Run a test script and return success status and output"""
    try:
        cmd = [sys.executable, script_name]
        if args:
            cmd.extend(args)
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        return success, output
        
    except subprocess.TimeoutExpired:
        return False, f"Test timed out after 5 minutes"
    except Exception as e:
        return False, f"Error running test: {e}"

def test_stt() -> Tuple[bool, str]:
    """Test STT functionality"""
    print("\n" + "="*60)
    print("TESTING SPEECH-TO-TEXT (STT)")
    print("="*60)
    
    # First try quick test
    success, output = run_test_script("test_stt.py", ["--quick"])
    
    if success:
        print("✅ STT Quick Test PASSED")
        return True, output
    else:
        print("❌ STT Quick Test FAILED")
        print("Output:", output)
        return False, output

def test_tts() -> Tuple[bool, str]:
    """Test TTS functionality"""
    print("\n" + "="*60)
    print("TESTING TEXT-TO-SPEECH (TTS)")
    print("="*60)
    
    # First try initialization test
    success, output = run_test_script("test_tts.py", ["--init-only"])
    
    if success:
        print("✅ TTS Initialization Test PASSED")
        return True, output
    else:
        print("❌ TTS Initialization Test FAILED")
        print("Output:", output)
        return False, output

def test_llm() -> Tuple[bool, str]:
    """Test LLM functionality"""
    print("\n" + "="*60)
    print("TESTING LARGE LANGUAGE MODEL (LLM)")
    print("="*60)
    
    # First try connection test
    success, output = run_test_script("test_llm.py", ["--connection"])
    
    if success:
        print("✅ LLM Connection Test PASSED")
        return True, output
    else:
        print("❌ LLM Connection Test FAILED")
        print("Output:", output)
        return False, output

def test_all_models() -> Dict[str, Tuple[bool, str]]:
    """Test all models and return results"""
    results = {}
    
    print("🤖 COMPREHENSIVE AI MODEL TEST SUITE")
    print("="*60)
    print("This will test all three AI components:")
    print("1. Speech-to-Text (STT) - Whisper model")
    print("2. Text-to-Speech (TTS) - Kokoro model") 
    print("3. Large Language Model (LLM) - LM Studio")
    print("="*60)
    
    # Test STT
    results['stt'] = test_stt()
    
    # Test TTS
    results['tts'] = test_tts()
    
    # Test LLM
    results['llm'] = test_llm()
    
    return results

def print_summary(results: Dict[str, Tuple[bool, str]]):
    """Print a summary of all test results"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for model, (success, output) in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{model.upper():<15} {status}")
        if success:
            passed += 1
    
    print("-" * 60)
    print(f"Overall: {passed}/{total} models working")
    
    if passed == total:
        print("🎉 ALL MODELS ARE WORKING CORRECTLY!")
    elif passed > 0:
        print("⚠️  Some models have issues. Check individual test outputs above.")
    else:
        print("❌ No models are working. Please check your setup.")
    
    print("="*60)

def interactive_test_menu():
    """Interactive menu for testing individual components"""
    while True:
        print("\n" + "="*50)
        print("AI MODEL TEST MENU")
        print("="*50)
        print("1. Test Speech-to-Text (STT)")
        print("2. Test Text-to-Speech (TTS)")
        print("3. Test Large Language Model (LLM)")
        print("4. Test All Models")
        print("5. Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            success, output = test_stt()
            if not success:
                print(f"\nSTT Test failed. Output:\n{output}")
        elif choice == "2":
            success, output = test_tts()
            if not success:
                print(f"\nTTS Test failed. Output:\n{output}")
        elif choice == "3":
            success, output = test_llm()
            if not success:
                print(f"\nLLM Test failed. Output:\n{output}")
        elif choice == "4":
            results = test_all_models()
            print_summary(results)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_test_menu()
        elif sys.argv[1] == "--stt":
            success, output = test_stt()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--tts":
            success, output = test_tts()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--llm":
            success, output = test_llm()
            sys.exit(0 if success else 1)
        else:
            print("Usage: python test_all_models.py [--interactive|--stt|--tts|--llm]")
            sys.exit(1)
    else:
        # Run all tests
        results = test_all_models()
        print_summary(results)
        
        # Exit with appropriate code
        all_passed = all(success for success, _ in results.values())
        sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()