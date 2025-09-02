# Quick Start Guide - Ollama Setup

## 🚀 Get Started in 3 Steps

### 1. Install Ollama
First, install Ollama on your system:

**Linux/macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows (PowerShell):**
```powershell
winget install ollama.ollama
```

### 2. Download a Model
Download a model (e.g., llama2, mistral, phi3):
```bash
ollama pull llama2
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App

**Option A: Voice Chat (Command Line)**
```bash
python voice_chat_agent.py
```

**Option B: Web Interface**
```bash
python apis/call_agent_api.py
```
Then visit: http://localhost:5000

## 🔧 Configuration

You can customize the behavior by editing the `.env` file:

```env
# LLM Configuration
LLM_MODEL_NAME=llama2  # or any other model you've pulled with Ollama
OLLAMA_BASE_URL=http://localhost:11434  # Change if running Ollama on a different host/port

# Speech Recognition Configuration
WHISPER_MODEL_SIZE=small  # tiny, base, small, medium, large

# Application Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
```

## 🌐 Running Ollama in Production

For production use:
1. Run Ollama as a service:
   ```bash
   sudo systemctl enable ollama
   sudo systemctl start ollama
   ```

2. For remote access, configure the OLLAMA_HOST environment variable:
   ```bash
   # In /etc/systemd/system/ollama.service.d/environment.conf
   [Service]
   Environment="OLLAMA_HOST=0.0.0.0"
   ```

3. Restart the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart ollama
   ```

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