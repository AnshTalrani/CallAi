# Quick Start Guide - Cloud LM Studio Setup

## 🚀 Get Started in 3 Steps

### 1. Configure Environment
Run the setup script to configure your cloud LM Studio:
```bash
python setup.py
```

This will prompt you for:
- Your Cloud LM Studio API URL
- API key (if required)
- Model name
- Other configuration options

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App

**Option A: Voice Chat (Command Line)**
```bash
python voice_chat_agent.py
```

**Option B: Web Interface**
```bash
python apis/call_agent_api.py
```
Then visit: http://localhost:5000

## 🔧 Manual Configuration

If you prefer to configure manually, edit the `.env` file:

```env
# LLM Configuration
LLM_MODEL_NAME=meta-llama-3.1-8b-instruct
LLM_API_BASE=https://your-cloud-lm-studio-url.com/v1
LLM_API_KEY=your-api-key-here

# Speech Recognition Configuration
WHISPER_MODEL_SIZE=small

# Flask Application Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
```

## 🌐 Cloud LM Studio Requirements

Your Cloud LM Studio instance should:
- Support OpenAI-compatible API format
- Have the `meta-llama-3.1-8b-instruct` model loaded
- Be accessible via HTTPS
- Accept API requests on the `/v1` endpoint

## 🎯 What's Ready Now

✅ **Voice Chat Agent** - Direct speech-to-text-to-speech conversation  
✅ **Web API** - REST API for integration  
✅ **Call Agent System** - Full CRM with campaign management  
✅ **Multi-tenant Support** - User management and isolation  

## 🆘 Troubleshooting

**"Connection refused" errors:**
- Check your Cloud LM Studio URL in `.env`
- Verify the API endpoint is `/v1`
- Ensure your API key is correct

**Audio issues:**
- The app will auto-detect audio devices
- You can set `AUDIO_DEVICE_ID` in `.env` if needed

**Model download issues:**
- First run will download Whisper and TTS models
- Ensure stable internet connection
- Models are cached locally for future use