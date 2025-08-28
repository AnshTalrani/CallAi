# Call Agent CRM - Fixed Version

A multi-tenant call agent CRM system with voice recognition, LLM integration, and comprehensive security fixes.

## 🚀 What's Fixed

### Critical Security Fixes
- ✅ **Multi-tenant isolation**: All data is now properly isolated by user
- ✅ **Authentication required**: All endpoints now require proper authentication
- ✅ **Input validation**: Phone numbers, emails, and required fields are validated
- ✅ **User context**: Call agents are now user-specific, not global
- ✅ **Access control**: Users can only access their own data

### Performance & Reliability Fixes
- ✅ **Environment configuration**: LLM and Whisper settings are now configurable
- ✅ **Audio memory leaks**: Fixed audio stream cleanup issues
- ✅ **Conversation persistence**: State is saved immediately to prevent data loss
- ✅ **Rate limiting**: Added protection against API abuse
- ✅ **Error handling**: Improved error messages without information leakage

### Architecture Improvements
- ✅ **Transaction support**: Added basic transaction-like operations
- ✅ **Stage transition logic**: Fixed premature stage transitions
- ✅ **Configurable call context**: Call context is now campaign-specific
- ✅ **Better logging**: Added proper error logging

## 🛠️ Setup Instructions

### 1. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Required: Set a strong secret key
SECRET_KEY=your-very-secure-secret-key-here

# LLM Configuration (adjust for your setup)
LLM_API_BASE=http://localhost:1234/v1
LLM_MODEL_NAME=meta-llama-3.1-8b-instruct

# Audio Configuration
AUDIO_DEVICE_ID=-1  # Use -1 for default device
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start LM Studio

Make sure LM Studio is running on the configured port (default: 1234).

### 4. Run the API Server

```bash
python call_agent_api.py
```

The API will be available at `http://localhost:5000`

## 🔐 Authentication Flow

### 1. Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 2. Use Session Cookie
The server will set a session cookie. Include it in subsequent requests.

## 📋 API Endpoints

### Authentication
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user  
- `GET /auth/profile` - Get user profile

### Contacts
- `GET /contacts` - Get user's contacts
- `POST /contacts` - Create new contact
- `GET /contacts/<id>` - Get specific contact

### Campaigns
- `GET /campaigns` - Get user's campaigns
- `POST /campaigns` - Create new campaign
- `GET /campaigns/<id>` - Get specific campaign

### Calls
- `POST /calls/start` - Start a new call
- `POST /calls/end` - End current call
- `POST /calls/process` - Process user input
- `GET /calls/status` - Get call status

## 🔒 Security Features

### Rate Limiting
- Default: 200 requests per day, 50 per hour
- Call processing: 30 per minute
- Call starting: 10 per minute
- Login attempts: 5 per minute

### Input Validation
- Phone number format validation
- Email format validation
- Required field validation
- User ownership verification

### Session Security
- Secure cookies
- HTTP-only cookies
- Session expiration (1 hour)
- Automatic session cleanup

## 🐛 Bug Fixes Summary

### High Priority
1. **Race condition in call agent initialization** - Fixed with user-specific agents
2. **Missing user validation** - Added authentication to all endpoints
3. **Hardcoded LLM configuration** - Now uses environment variables

### Medium Priority
4. **Inconsistent error handling** - Standardized error responses
5. **Memory leak in audio recording** - Fixed stream cleanup
6. **Missing input validation** - Added comprehensive validation

### Low Priority
7. **Inefficient data loading** - Improved with better caching
8. **Missing transaction support** - Added basic transaction operations
9. **Hardcoded call context** - Made configurable per campaign

## 🧪 Testing

### Create Sample Data
```bash
curl -X POST http://localhost:5000/sample-data \
  -H "Content-Type: application/json" \
  -b "session=your-session-cookie"
```

### Test Call Flow
1. Login and get session cookie
2. Create contacts and campaigns
3. Start a call
4. Process user input
5. End the call

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Required |
| `LLM_API_BASE` | LLM API endpoint | `http://localhost:1234/v1` |
| `LLM_MODEL_NAME` | LLM model name | `meta-llama-3.1-8b-instruct` |
| `WHISPER_MODEL_SIZE` | Whisper model size | `small` |
| `AUDIO_DEVICE_ID` | Audio device ID | `-1` |

## 🚨 Important Notes

1. **Security**: Always use HTTPS in production
2. **Database**: Consider using a real database for production
3. **LLM**: Ensure LM Studio is running before starting the API
4. **Audio**: Test audio devices before running calls
5. **Rate Limits**: Adjust rate limits based on your needs

## 🔧 Troubleshooting

### Common Issues

1. **LLM Connection Failed**
   - Check if LM Studio is running
   - Verify the API base URL in `.env`

2. **Audio Device Issues**
   - Run `python -c "from voice_recognition import VoiceRecognizer; VoiceRecognizer.list_audio_devices()"`
   - Update `AUDIO_DEVICE_ID` in `.env`

3. **Authentication Errors**
   - Check if session cookie is being sent
   - Verify user exists in the system

4. **Rate Limiting**
   - Check rate limit headers in responses
   - Adjust limits in `.env` if needed

## 📈 Performance Considerations

- Whisper model is loaded once per VoiceRecognizer instance
- LLM responses are streamed for better UX
- Audio recording uses efficient buffering
- JSON files are used for simplicity (consider database for production)

## 🔄 Future Improvements

1. **Database Integration**: Replace JSON files with PostgreSQL/MySQL
2. **JWT Tokens**: Replace sessions with JWT for better scalability
3. **Async Processing**: Make audio processing asynchronous
4. **Caching**: Add Redis for better performance
5. **Monitoring**: Add proper logging and monitoring
6. **Testing**: Add comprehensive test suite