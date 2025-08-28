# Call Agent System

A comprehensive call agent system that integrates LLM, STT, and TTS capabilities with CRM functionality and campaign management. This system allows you to conduct automated voice calls with intelligent conversation management, data collection, and campaign-driven behavior.

## Features

### 🎯 Core Call Agent Features
- **Voice Recognition**: Real-time speech-to-text using Whisper
- **Natural Language Processing**: LLM-powered conversation intelligence
- **Text-to-Speech**: Natural voice synthesis using Kokoro TTS
- **Call Recording**: Automatic call recording and storage

### 📊 CRM Integration
- **Contact Management**: Store and manage contact information
- **Call History**: Track all call interactions and outcomes
- **Conversation Tracking**: Full transcript and data collection
- **Status Management**: Contact status tracking (new, contacted, interested, etc.)

### 🎪 Campaign Management
- **Campaign Templates**: Pre-defined campaign types (sales, support, survey)
- **Stage-based Conversations**: Multi-stage conversation flows
- **Script Management**: Dynamic script generation with context
- **Data Collection**: Automated extraction of relevant information
- **Behavior Configuration**: Customizable agent personality and responses

### 🔧 Technical Features
- **Repository Pattern**: Clean data access layer
- **REST API**: Full API for integration with other systems
- **JSON Storage**: Simple file-based data storage
- **Modular Architecture**: Easy to extend and customize

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements_call_agent.txt

# Make sure LM Studio is running on port 1234
# (Required for LLM functionality)
```

### 2. Basic Usage

#### Command Line Demo
```bash
python call_agent_example.py
```

#### API Server
```bash
python call_agent_api.py
```

### 3. Create Sample Data

The system will automatically create sample contacts and campaigns when you first run it.

## Architecture

### Directory Structure
```
call_agent/
├── __init__.py
├── call_agent.py          # Main call agent class
├── campaign_manager.py    # Campaign behavior management
├── models/
│   ├── __init__.py
│   └── crm.py            # Data models (Contact, Call, Campaign, etc.)
└── repositories/
    ├── __init__.py
    ├── base_repository.py # Base repository class
    ├── contact_repository.py
    ├── conversation_repository.py
    └── campaign_repository.py
```

### Key Components

#### 1. CallAgent (`call_agent.py`)
The main class that orchestrates the entire call process:
- Manages call lifecycle (start, conduct, end)
- Integrates STT, LLM, and TTS
- Handles conversation state and transitions
- Records calls and manages transcripts

#### 2. CampaignManager (`campaign_manager.py`)
Manages campaign behavior and script generation:
- Creates and manages campaign templates
- Generates dynamic scripts based on context
- Handles stage transitions
- Extracts data from conversations

#### 3. Data Models (`models/crm.py`)
Defines the data structures:
- `Contact`: Contact information and status
- `Call`: Call metadata and status
- `Conversation`: Full conversation with transcript
- `Campaign`: Campaign configuration and scripts

#### 4. Repositories (`repositories/`)
Data access layer:
- `BaseRepository`: Common database operations
- `ContactRepository`: Contact CRUD operations
- `ConversationRepository`: Conversation management
- `CampaignRepository`: Campaign management

## Usage Examples

### 1. Basic Call Agent Usage

```python
from call_agent.call_agent import CallAgent
from call_agent.campaign_manager import CampaignManager

# Initialize
agent = CallAgent(device_id=1)
campaign_manager = CampaignManager()

# Create a campaign
campaign = campaign_manager.create_sample_campaign("sales")

# Create a contact
contact = Contact(
    phone_number="+1234567890",
    first_name="John",
    last_name="Doe",
    company="Tech Corp"
)

# Conduct a call
agent.conduct_call(
    contact_id=contact.id,
    campaign_id=campaign.id,
    phone_number=contact.phone_number
)
```

### 2. API Usage

#### Start a call
```bash
curl -X POST http://localhost:5000/calls/start \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "contact-uuid",
    "campaign_id": "campaign-uuid",
    "phone_number": "+1234567890"
  }'
```

#### Process user input
```bash
curl -X POST http://localhost:5000/calls/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, I am interested in your product"}'
```

#### Get call status
```bash
curl http://localhost:5000/calls/status
```

### 3. Campaign Configuration

Campaigns define the behavior and flow of conversations:

```python
# Sales campaign stages
stages = [
    CampaignStage.INTRODUCTION,
    CampaignStage.NEEDS_ASSESSMENT,
    CampaignStage.SOLUTION_PRESENTATION,
    CampaignStage.OBJECTION_HANDLING,
    CampaignStage.CLOSING
]

# Script template with placeholders
script_template = {
    'introduction': {
        'script': "Hello! This is {agent_name} calling from {company_name}...",
        'transition_rules': {
            'keywords': ['yes', 'sure', 'okay'],
            'min_turns': 2
        }
    }
}
```

## Campaign Types

### 1. Sales Campaign
- **Purpose**: Product outreach and lead generation
- **Stages**: Introduction → Needs Assessment → Solution Presentation → Objection Handling → Closing
- **Data Collection**: Name, email, company, pain points, budget, decision maker

### 2. Support Campaign
- **Purpose**: Customer support and issue resolution
- **Stages**: Introduction → Needs Assessment → Solution Presentation → Closing
- **Data Collection**: Issue type, product feature, resolution satisfaction

### 3. Survey Campaign
- **Purpose**: Customer feedback and satisfaction surveys
- **Stages**: Introduction → Needs Assessment → Solution Presentation → Closing
- **Data Collection**: Satisfaction rating, feedback reason, improvement suggestions

## Data Storage

The system uses JSON files for data storage in the `data/` directory:
- `contacts.json`: Contact information
- `conversations.json`: Conversation transcripts and data
- `campaigns.json`: Campaign configurations

## API Endpoints

### Health Check
- `GET /health` - System health status

### Contacts
- `GET /contacts` - List all contacts
- `POST /contacts` - Create new contact
- `GET /contacts/<id>` - Get specific contact

### Campaigns
- `GET /campaigns` - List all campaigns
- `POST /campaigns` - Create new campaign
- `GET /campaigns/<id>` - Get specific campaign
- `GET /campaigns/<id>/script` - Get campaign script
- `GET /campaigns/<id>/behavior` - Get campaign behavior config

### Calls
- `POST /calls/start` - Start a new call
- `POST /calls/end` - End current call
- `POST /calls/process` - Process user input
- `GET /calls/status` - Get call status

### Conversations
- `GET /conversations/<id>` - Get conversation details
- `GET /conversations/<id>/summary` - Get conversation summary

### Utilities
- `POST /sample-data` - Create sample data for testing

## Configuration

### Environment Variables
```bash
# Optional: Set data directory
DATA_DIR=./data

# Optional: Set audio device
AUDIO_DEVICE_ID=1
```

### Campaign Customization

You can customize campaigns by modifying the script templates:

```python
# Custom script with dynamic content
script_template = {
    'introduction': {
        'script': "Hello {contact_name}! This is {agent_name} from {company_name}...",
        'transition_rules': {
            'keywords': ['yes', 'sure'],
            'sentiment_threshold': 0.3,
            'min_turns': 2
        }
    }
}
```

## Extending the System

### Adding New Campaign Types

1. Create a new method in `CampaignManager`:
```python
def create_custom_campaign(self, name: str) -> Campaign:
    script_template = {
        # Your custom script template
    }
    
    campaign = Campaign(
        name=name,
        stages=[CampaignStage.INTRODUCTION, CampaignStage.CLOSING],
        script_template=script_template,
        data_collection_fields=['custom_field1', 'custom_field2']
    )
    
    return self.campaign_repo.create(campaign)
```

### Adding New Data Models

1. Create a new model in `models/crm.py`
2. Create a corresponding repository in `repositories/`
3. Add API endpoints in `call_agent_api.py`

### Custom Data Extraction

Extend the `extract_data_from_input` method in `CampaignManager` to add custom data extraction logic.

## Troubleshooting

### Common Issues

1. **LM Studio not running**: Make sure LM Studio is running on port 1234
2. **Audio device issues**: Check your audio device configuration
3. **Import errors**: Ensure all dependencies are installed
4. **Data directory**: The system will create the `data/` directory automatically

### Debug Mode

Run the API server in debug mode for detailed error messages:
```bash
python call_agent_api.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Create an issue on GitHub