# AI Model Test Scripts

This directory contains simple test scripts to verify that your STT (Speech-to-Text), TTS (Text-to-Speech), and LLM (Large Language Model) components are working correctly.

## Quick Start

### Test All Models at Once
```bash
python test_all_models.py
```

### Interactive Testing Menu
```bash
python test_all_models.py --interactive
```

## Individual Test Scripts

### 1. Speech-to-Text (STT) Test
Tests the Whisper model for speech recognition.

**Quick test (no audio recording):**
```bash
python test_stt.py --quick
```

**Full test (with audio recording):**
```bash
python test_stt.py
```

### 2. Text-to-Speech (TTS) Test
Tests the Kokoro TTS model for speech synthesis.

**Initialization test (no audio playback):**
```bash
python test_tts.py --init-only
```

**Quick test (with audio playback):**
```bash
python test_tts.py --quick
```

**Full test (interactive with audio):**
```bash
python test_tts.py
```

### 3. Large Language Model (LLM) Test
Tests the LLM setup with Ollama.

**Connection test (basic connectivity):**
```bash
python test_llm.py --connection
```

**Quick test (simple response):**
```bash
python test_llm.py --quick
```

**Interactive test (chat mode):**
```bash
python test_llm.py --interactive
```

**Full test (multiple prompts):**
```bash
python test_llm.py
```

## Prerequisites

Before running the tests, make sure you have:

1. **All dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Audio hardware configured:**
   - Microphone for STT tests
   - Speakers/headphones for TTS tests

3. **Ollama running (for LLM tests):**
   - LM Studio should be running on `http://localhost:11434`
   - Model `meta-llama-3.1-8b-instruct` should be loaded

## Test Results

### Success Indicators
- ✅ **STT**: Whisper model loads and can transcribe audio
- ✅ **TTS**: Kokoro model loads and can generate speech
- ✅ **LLM**: LangChain connects to Ollama and generates responses

### Common Issues

#### STT Issues
- **No audio devices found**: Check microphone connection
- **Model loading fails**: Check internet connection for Whisper download
- **CUDA errors**: Install appropriate PyTorch version for your GPU

#### TTS Issues
- **Kokoro model fails**: Check internet connection for model download
- **Audio playback issues**: Check audio device configuration
- **Memory errors**: Ensure sufficient RAM for model loading

#### LLM Issues
- **Connection refused**: Make sure Ollama is running
- **Model not found**: Load the correct model in LM Studio
- **API errors**: Check the API endpoint configuration

## Troubleshooting

### Check Dependencies
```bash
python -c "import torch, transformers, kokoro, langchain; print('All dependencies OK')"
```

### Check Audio Devices
```bash
python -c "from voice_recognition import VoiceRecognizer; VoiceRecognizer.list_audio_devices()"
```

### Check LM Studio Connection
```bash
curl http://192.168.1.6:1234/v1/models
```

## Test Script Features

- **Non-interactive tests**: Use `--quick` or `--init-only` flags
- **Timeout protection**: Tests timeout after 5 minutes
- **Detailed error reporting**: Shows specific failure reasons
- **Cleanup handling**: Properly closes resources
- **Exit codes**: Scripts exit with 0 for success, 1 for failure

## Example Usage

```bash
# Quick check of all models
python test_all_models.py

# Test only STT with audio recording
python test_stt.py

# Test only TTS without audio playback
python test_tts.py --init-only

# Test only LLM connection
python test_llm.py --connection

# Interactive menu for all tests
python test_all_models.py --interactive
```

## Integration with CI/CD

The test scripts are designed to work in automated environments:

```bash
# Run all tests and exit with appropriate code
python test_all_models.py
echo $?  # 0 if all passed, 1 if any failed
```

This makes them suitable for continuous integration pipelines.