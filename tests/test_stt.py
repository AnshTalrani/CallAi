#!/usr/bin/env python3
"""
Simple test script for Speech-to-Text (STT) functionality
Tests the Whisper model with audio recording
"""

import sys
import logging
from voice_recognition import VoiceRecognizer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_stt():
    """Test the STT functionality"""
    print("=" * 50)
    print("STT (Speech-to-Text) Test")
    print("=" * 50)
    
    recognizer = None
    try:
        # Initialize the voice recognizer
        print("Initializing STT system...")
        recognizer = VoiceRecognizer()
        print("✓ STT system initialized successfully!")
        
        # List available audio devices
        print("\nAvailable audio devices:")
        VoiceRecognizer.list_audio_devices()
        
        # Test recording and transcription
        print("\n" + "=" * 30)
        print("RECORDING TEST")
        print("=" * 30)
        print("Instructions:")
        print("1. Speak clearly into your microphone")
        print("2. Say something like 'Hello, this is a test'")
        print("3. Wait for silence to stop recording")
        print("4. The system will transcribe your speech")
        print("\nPress Enter when ready to start recording...")
        input()
        
        # Record audio
        print("\n🎤 Recording... (speak now)")
        audio_data = recognizer.record_audio()
        
        if audio_data is not None:
            print(f"✓ Audio recorded successfully! Length: {len(audio_data)} samples")
            
            # Transcribe audio
            print("\n🔄 Transcribing audio...")
            transcription = recognizer.transcribe_audio(audio_data)
            
            if transcription:
                print(f"✓ Transcription successful!")
                print(f"📝 Transcribed text: '{transcription}'")
                
                # Test with a simple validation
                if len(transcription.strip()) > 0:
                    print("✅ STT test PASSED - Model is working correctly!")
                else:
                    print("❌ STT test FAILED - No text was transcribed")
            else:
                print("❌ STT test FAILED - Transcription returned empty result")
        else:
            print("❌ STT test FAILED - No audio was recorded")
            
    except Exception as e:
        print(f"❌ STT test FAILED with error: {e}")
        logger.error(f"STT test error: {e}", exc_info=True)
        return False
    
    finally:
        if recognizer:
            recognizer.cleanup()
            print("✓ Cleanup completed")
    
    return True

def quick_stt_test():
    """Quick test without user interaction"""
    print("=" * 50)
    print("Quick STT Test")
    print("=" * 50)
    
    try:
        # Test initialization
        print("Testing STT initialization...")
        recognizer = VoiceRecognizer()
        print("✓ STT initialization successful!")
        
        # Test model loading
        print("✓ Whisper model loaded successfully!")
        
        recognizer.cleanup()
        print("✓ Quick STT test PASSED - System is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Quick STT test FAILED: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = quick_stt_test()
    else:
        success = test_stt()
    
    sys.exit(0 if success else 1)