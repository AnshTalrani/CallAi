# Local Voice Chat MVP with Tool-use and Memory

A voice-based chat application that allows users to interact with an AI assistant using speech. The application leverages OpenAI's [Whisper small](https://huggingface.co/openai/whisper-small) for accurate speech recognition and [Kokoro-TTS](https://huggingface.co/hexgrad/Kokoro-82M) for natural-sounding voice synthesis. It uses [Ollama](https://ollama.ai/) for local LLM inference, supporting various models like Llama 2, Mistral, and Phi-3.

**Requirements**:
- Python 3.12 (required for PyTorch compatibility)
- Ollama installed and running locally
- At least 8GB RAM (16GB recommended for larger models)

## Features

- 🎙️ Real-time speech-to-text with Whisper
- 🤖 Local LLM inference with Ollama
- 🗣️ Natural-sounding text-to-speech with Kokoro-TTS
- 🛠️ Tool use and memory capabilities
- 🏠 100% local - no data leaves your machine

## Quick Start

1. **Install Ollama**
   - Linux/macOS:
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ```
   - Windows (PowerShell):
     ```powershell
     winget install ollama.ollama
     ```

2. **Download a Model**
   ```bash
   ollama pull llama2  # or mistral, phi3, etc.
   ```

3. **Install System Dependencies**
   - macOS:
     ```bash
     brew install portaudio
     ```
   - Ubuntu/Debian:
     ```bash
     sudo apt-get install portaudio19-dev python3-pyaudio
     ```

4. **Set Up Python Environment**
   ```bash
   python3.12 -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run the Application**
   ```bash
   python voice_chat_agent.py
   ```

   Or start the web interface:
   ```bash
   python apis/call_agent_api.py
   ```
   Then visit http://localhost:5000 in your browser
