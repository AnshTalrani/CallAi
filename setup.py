#!/usr/bin/env python3
"""
Setup script for Voice Chat Agent with Cloud LM Studio
"""

import os
import sys
from pathlib import Path

def get_user_input(prompt, default=""):
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def create_env_file():
    """Create .env file with user configuration"""
    print("🔧 Setting up Voice Chat Agent with Cloud LM Studio")
    print("=" * 50)
    
    # Get cloud LM Studio configuration
    print("\n🌐 Cloud LM Studio Configuration:")
    api_base = get_user_input(
        "Enter your Cloud LM Studio API base URL", 
        "https://your-cloud-lm-studio-url.com/v1"
    )
    
    api_key = get_user_input(
        "Enter your Cloud LM Studio API key (if required)", 
        "not-needed"
    )
    
    model_name = get_user_input(
        "Enter the model name", 
        "meta-llama-3.1-8b-instruct"
    )
    
    # Get other configuration
    print("\n🔊 Audio Configuration:")
    whisper_model = get_user_input(
        "Whisper model size (tiny, base, small, medium, large)", 
        "small"
    )
    
    # Get Flask configuration
    print("\n🌐 Web Server Configuration:")
    secret_key = get_user_input(
        "Flask secret key", 
        "your-secret-key-change-this-in-production"
    )
    
    # Create .env content
    env_content = f"""# LLM Configuration
LLM_MODEL_NAME={model_name}
LLM_API_BASE={api_base}
LLM_API_KEY={api_key}

# Speech Recognition Configuration
WHISPER_MODEL_SIZE={whisper_model}

# Flask Application Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development
FLASK_DEBUG=1

# Audio Configuration (optional - will auto-detect if not set)
# AUDIO_DEVICE_ID=1

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
"""
    
    # Write .env file
    env_path = Path(".env")
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print(f"\n✅ Created {env_path}")
    print("\n📋 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run voice chat: python voice_chat_agent.py")
    print("3. Or run web API: python apis/call_agent_api.py")
    
    return True

def main():
    """Main setup function"""
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()