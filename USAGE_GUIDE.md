# Call Agent System Usage Guide

## Overview

The Call Agent System is a comprehensive voice calling solution with CRM integration, campaign management, and multi-tenant support. It allows you to conduct automated voice calls with intelligent conversation management and data collection.

## Key Features

- **CRM Module**: Contact management, call tracking, conversation history
- **Campaign Manager**: Template-based campaigns with stages and scripts
- **Multi-tenant Support**: User isolation and data security
- **Voice Integration**: Speech-to-text, text-to-speech, and call recording
- **Data Collection**: Automatic extraction of information from conversations

## Quick Start

### 1. Basic Setup

```python
from call_agent.user_manager import UserManager
from call_agent.campaign_manager import CampaignManager
from call_agent.call_agent import CallAgent
from call_agent.models.crm import Contact, ContactStatus
from call_agent.repositories.contact_repository import ContactRepository

# Initialize user management
user_manager = UserManager()

# Register a new user
user = user_manager.register_user(
    email="your@email.com",
    password="secure_password",
    first_name="Your",
    last_name="Name",
    company_name="Your Company"
)
```

### 2. Create Campaigns

```python
# Initialize campaign manager with user context
campaign_manager = CampaignManager(user=user)

# Create a custom campaign
campaign = campaign_manager.create_campaign(
    name="Sales Outreach",
    description="Outbound sales calls for new product",
    stages=[
        CampaignStage.INTRODUCTION,
        CampaignStage.NEEDS_ASSESSMENT,
        CampaignStage.SOLUTION_PRESENTATION,
        CampaignStage.CLOSING
    ]
)

# Or use pre-built templates
sales_campaign = campaign_manager.create_sample_campaign("sales")
support_campaign = campaign_manager.create_sample_campaign("support")
survey_campaign = campaign_manager.create_sample_campaign("survey")
```

### 3. Manage Contacts

```python
# Initialize contact repository
contact_repo = ContactRepository()

# Create contacts
contact = Contact(
    user_id=user.id,  # Important: Always include user_id
    phone_number="+1234567890",
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    company="Tech Corp",
    status=ContactStatus.NEW
)

created_contact = contact_repo.create(contact)
```

### 4. Conduct Calls

```python
# Initialize call agent with user context
call_agent = CallAgent(user=user, device_id=1)

# Conduct a call
call_agent.conduct_call(
    contact_id=created_contact.id,
    campaign_id=campaign.id,
    phone_number=created_contact.phone_number
)
```

## Campaign Management

### Campaign Stages

The system supports these predefined stages:
- `INTRODUCTION`: Initial greeting and context setting
- `NEEDS_ASSESSMENT`: Understanding customer needs
- `SOLUTION_PRESENTATION`: Presenting your solution
- `OBJECTION_HANDLING`: Addressing concerns
- `CLOSING`: Finalizing the conversation
- `FOLLOW_UP`: Post-call follow-up

### Script Templates

Campaigns use script templates with placeholders:

```python
script_template = {
    'introduction': {
        'script': "Hello! This is {agent_name} calling from {company_name}. I hope you're having a great day. I'm reaching out because we have a special offer that I think would be perfect for your business. Do you have a moment to hear about it?",
        'transition_rules': {
            'keywords': ['yes', 'sure', 'okay', 'tell me'],
            'min_turns': 2
        }
    }
}
```

### Data Collection

Configure what information to extract from conversations:

```python
campaign = Campaign(
    user_id=user.id,
    name="Lead Generation",
    data_collection_fields=[
        'name', 'email', 'company', 'pain_point', 
        'budget', 'decision_maker', 'timeline'
    ]
)
```

## Multi-Tenant Usage

### User Authentication

```python
# Authenticate user
user = user_manager.authenticate_user("user@example.com", "password")

# Or use API key
user = user_manager.authenticate_by_api_key("your_api_key")
```

### Data Isolation

All data is automatically filtered by user_id:

```python
# Get user's campaigns only
campaigns = campaign_manager.campaign_repo.find_by_field('user_id', user.id)

# Get user's contacts only
contacts = contact_repo.find_by_field('user_id', user.id)
```

### User Dashboard

```python
# Get comprehensive user data
dashboard_data = user_manager.get_user_dashboard_data(user.id)

print(f"Total campaigns: {dashboard_data['stats']['total_campaigns']}")
print(f"Active campaigns: {dashboard_data['stats']['active_campaigns']}")
print(f"Total contacts: {dashboard_data['stats']['total_contacts']}")
print(f"Completed calls: {dashboard_data['stats']['completed_calls']}")
```

## Advanced Features

### Custom Campaign Behavior

```python
# Get campaign behavior configuration
behavior_config = campaign_manager.get_campaign_behavior_config(campaign.id)

# Configure voice settings
behavior_config['voice_settings'] = {
    'voice': 'en_us_001',
    'speed': 1.0,
    'pitch': 0.0
}

# Configure personality
behavior_config['personality'] = {
    'tone': 'professional',
    'style': 'conversational',
    'empathy_level': 'high'
}
```

### Conversation Analysis

```python
# Get conversation summary
conversation_repo = ConversationRepository()
summary = conversation_repo.get_conversation_summary(conversation_id)

print(f"Stage: {summary['stage']}")
print(f"Duration: {summary['duration_seconds']} seconds")
print(f"Sentiment: {summary['sentiment_score']}")
print(f"Collected data: {summary['collected_data']}")
```

### Call Recording

```python
# Start recording
call_agent.start_recording("call_recording.wav")

# Conduct call...
# Recording happens automatically

# Stop recording
call_agent.stop_recording()
```

## API Usage

### REST API Endpoints

```bash
# Health check
GET /health

# User management
POST /auth/register
POST /auth/login
GET /auth/profile

# Campaigns
GET /campaigns
POST /campaigns
GET /campaigns/{id}

# Contacts
GET /contacts
POST /contacts
GET /contacts/{id}

# Calls
POST /calls/start
POST /calls/end
GET /calls/{id}
```

### Example API Call

```python
import requests

# Authenticate
response = requests.post('http://localhost:5000/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['token']

# Start a call
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:5000/calls/start', json={
    'contact_id': 'contact_id',
    'campaign_id': 'campaign_id',
    'phone_number': '+1234567890'
}, headers=headers)
```

## Error Handling

### Common Issues

1. **Missing user_id**: Always include user_id when creating entities
2. **Permission errors**: Ensure user owns the resources they're accessing
3. **Audio device issues**: Check device_id and audio permissions
4. **Campaign not found**: Verify campaign exists and belongs to user

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check call agent status
print(f"Current call: {call_agent.current_call}")
print(f"Current conversation: {call_agent.current_conversation}")
print(f"Current stage: {call_agent.current_conversation.stage if call_agent.current_conversation else None}")
```

## Best Practices

1. **Always use user context**: Initialize all components with user
2. **Validate ownership**: Check resource ownership before operations
3. **Handle errors gracefully**: Implement proper error handling
4. **Monitor usage**: Track API usage and call statistics
5. **Secure data**: Use proper authentication and authorization
6. **Test campaigns**: Test campaigns before production use
7. **Backup data**: Regularly backup conversation and call data

## Troubleshooting

### Call Agent Issues

- **No audio detected**: Check microphone permissions and device_id
- **Script not working**: Verify campaign template and stage configuration
- **Data not collected**: Check data_collection_fields configuration

### Multi-tenant Issues

- **Data leakage**: Ensure user_id is always included
- **Permission denied**: Verify user owns the resource
- **Authentication failed**: Check credentials and API key

### Performance Issues

- **Slow response**: Check LLM configuration and network
- **Memory usage**: Monitor conversation transcript size
- **Storage**: Clean up old recordings and data

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Test with sample data first
4. Review the multi-tenant demo in `demo_multi_tenant.py`