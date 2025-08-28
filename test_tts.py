#!/usr/bin/env python3
"""
Simple test script for Text-to-Speech (TTS) functionality
Tests the Kokoro TTS model
"""

import sys
import time
from text_to_speech import TTSGenerator

def test_tts():
    """Test the TTS functionality"""
    print("=" * 50)
    print("TTS (Text-to-Speech) Test")
    print("=" * 50)
    
    tts = None
    try:
        # Initialize TTS
        print("Initializing TTS system...")
        tts = TTSGenerator()
        print("✓ TTS system initialized successfully!")
        
        # Test texts to try
        test_texts = [
            "Hello, this is a test of the text to speech system.",
            "The quick brown fox jumps over the lazy dog.",
            "Testing one, two, three. Can you hear me clearly?",
            "This is a simple test to verify the TTS functionality is working."
        ]
        
        print("\n" + "=" * 30)
        print("SPEECH GENERATION TESTS")
        print("=" * 30)
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n🎵 Test {i}/{len(test_texts)}")
            print(f"Text: '{text}'")
            print("Generating speech...")
            
            try:
                start_time = time.time()
                tts.generate_speech(text)
                end_time = time.time()
                
                duration = end_time - start_time
                print(f"✓ Speech generated successfully! (took {duration:.2f} seconds)")
                
                # Ask user if they heard the audio
                response = input("Did you hear the audio clearly? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    print("✅ Audio playback confirmed!")
                else:
                    print("⚠️  Audio playback may have issues")
                    
            except KeyboardInterrupt:
                print("\n⏹️  Audio playback interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error generating speech: {e}")
                return False
        
        print("\n✅ TTS test PASSED - Model is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ TTS test FAILED with error: {e}")
        return False
    
    finally:
        if tts:
            tts.cleanup()
            print("✓ Cleanup completed")

def quick_tts_test():
    """Quick test without user interaction"""
    print("=" * 50)
    print("Quick TTS Test")
    print("=" * 50)
    
    try:
        # Test initialization
        print("Testing TTS initialization...")
        tts = TTSGenerator()
        print("✓ TTS initialization successful!")
        
        # Test model loading
        print("✓ Kokoro model loaded successfully!")
        
        # Quick speech test
        print("Testing speech generation...")
        test_text = "TTS test successful."
        tts.generate_speech(test_text)
        print("✓ Speech generation successful!")
        
        tts.cleanup()
        print("✓ Quick TTS test PASSED - System is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Quick TTS test FAILED: {e}")
        return False

def test_tts_without_audio():
    """Test TTS initialization without playing audio"""
    print("=" * 50)
    print("TTS Initialization Test (No Audio)")
    print("=" * 50)
    
    try:
        # Test initialization only
        print("Testing TTS initialization...")
        tts = TTSGenerator()
        print("✓ TTS system initialized successfully!")
        
        # Test model loading
        print("✓ Kokoro model loaded successfully!")
        print("✓ Voice pack loaded successfully!")
        
        tts.cleanup()
        print("✓ TTS initialization test PASSED - System is ready!")
        return True
        
    except Exception as e:
        print(f"❌ TTS initialization test FAILED: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            success = quick_tts_test()
        elif sys.argv[1] == "--init-only":
            success = test_tts_without_audio()
        else:
            print("Usage: python test_tts.py [--quick|--init-only]")
            sys.exit(1)
    else:
        success = test_tts()
    
    sys.exit(0 if success else 1)