#!/usr/bin/env python3
"""
Simple TTS test that checks basic audio dependencies without kokoro
"""

import sys
import time

def test_tts_dependencies():
    """Test if basic TTS dependencies are available"""
    print("=" * 50)
    print("Simple TTS Dependencies Test")
    print("=" * 50)
    
    try:
        # Test basic audio dependencies
        print("Testing basic audio dependencies...")
        
        # Test numpy
        try:
            import numpy as np
            print("✓ NumPy available")
        except ImportError as e:
            print(f"❌ NumPy not available: {e}")
            return False
        
        # Test sounddevice
        try:
            import sounddevice as sd
            print("✓ SoundDevice available")
            
            # Test if we can get device info
            devices = sd.query_devices()
            print(f"✓ Audio devices detected: {len(devices)} devices")
            
        except ImportError as e:
            print(f"❌ SoundDevice not available: {e}")
            return False
        except Exception as e:
            print(f"⚠️  SoundDevice available but has issues: {e}")
        
        # Test torch (for potential TTS models)
        try:
            import torch
            print("✓ PyTorch available")
            print(f"✓ PyTorch version: {torch.__version__}")
            
            # Check CUDA availability
            if torch.cuda.is_available():
                print("✓ CUDA available for GPU acceleration")
            else:
                print("⚠️  CUDA not available, will use CPU")
                
        except ImportError as e:
            print(f"❌ PyTorch not available: {e}")
            return False
        
        # Test transformers (for potential TTS models)
        try:
            import transformers
            print("✓ Transformers available")
            print(f"✓ Transformers version: {transformers.__version__}")
        except ImportError as e:
            print(f"⚠️  Transformers not available: {e}")
        
        print("\n✅ Basic TTS dependencies test PASSED!")
        print("Note: This test only checks dependencies, not actual TTS functionality.")
        print("For full TTS testing, you would need a TTS model like kokoro or similar.")
        
        return True
        
    except Exception as e:
        print(f"❌ TTS dependencies test FAILED: {e}")
        return False

def test_audio_playback():
    """Test basic audio playback capability"""
    print("\n" + "=" * 30)
    print("AUDIO PLAYBACK TEST")
    print("=" * 30)
    
    try:
        import numpy as np
        import sounddevice as sd
        
        # Generate a simple test tone
        print("Generating test tone...")
        sample_rate = 44100
        duration = 1.0  # 1 second
        frequency = 440.0  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t) * 0.3
        
        print("Playing test tone...")
        sd.play(tone, sample_rate)
        sd.wait()
        
        print("✓ Audio playback test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Audio playback test failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--playback":
        success = test_audio_playback()
    else:
        success = test_tts_dependencies()
    
    sys.exit(0 if success else 1)