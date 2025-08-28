# Multi-Tenant CRM System

This is a multi-tenant CRM (Customer Relationship Management) system designed for SaaS applications where each client (user) has their own isolated environment with campaigns, contacts, conversations, and calls.

## 🏗️ Architecture Overview

The system implements a **multi-tenant architecture** where:

- **Users** (clients) are the tenants
- Each user has their own isolated **CRM data**
- Data is filtered by `user_id` at the repository level
- Users cannot access each other's data
- Each user has their own campaigns, contacts, conversations, and calls

## 🎯 Key Features

### Multi-Tenancy
- **Data Isolation**: Each user's data is completely isolated
- **User Management**: Registration, authentication, and profile management
- **Subscription Plans**: Different feature limits based on user plans
- **Usage Tracking**: Monitor usage against plan limits

### CRM Features
- **Campaign Management**: Create and manage sales campaigns
- **Contact Management**: Store and organize customer contacts
- **Call Tracking**: Track phone calls and their outcomes
- **Conversation Management**: Store conversation transcripts and data
- **Script Management**: Dynamic script generation for different campaign stages

### User Plans
- **Free**: 3 campaigns, 100 contacts, 50 calls/month
- **Basic**: 10 campaigns, 1,000 contacts, 500 calls/month
- **Professional**: 50 campaigns, 10,000 contacts, 5,000 calls/month
- **Enterprise**: Unlimited campaigns, contacts, and calls

## 📁 Project Structure

```
call_agent/
├── models/
│   ├── user.py          # User model with multi-tenant support
│   └── crm.py           # CRM models (Contact, Campaign, Call, Conversation)
├── repositories/
│   ├── base_repository.py      # Base repository with JSON storage
│   ├── user_repository.py      # User management repository
│   ├── campaign_repository.py  # Campaign repository with user filtering
│   ├── contact_repository.py   # Contact repository with user filtering
│   ├── conversation_repository.py  # Conversation repository with user filtering
│   └── call_repository.py      # Call repository with user filtering
├── user_manager.py      # User management service
└── campaign_manager.py  # Campaign management service

# API and Demo
multi_tenant_api.py      # Flask API server
demo_multi_tenant.py     # Demo script showing multi-tenancy
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
python demo_multi_tenant.py
```

This will:
- Create two demo users (companies)
- Create campaigns, contacts, calls, and conversations for each
- Demonstrate data isolation between users
- Show usage statistics

### 3. Start the API Server

```bash
python multi_tenant_api.py
```

The API server will start on `http://localhost:5000`

## 📊 Data Models

### User Model
```python
@dataclass
class User:
    id: str
    email: str
    password_hash: str
    first_name: Optional[str]
    last_name: Optional[str]
    company_name: Optional[str]
    status: UserStatus  # ACTIVE, INACTIVE, SUSPENDED, TRIAL
    plan: UserPlan      # FREE, BASIC, PROFESSIONAL, ENTERPRISE
    api_key: Optional[str]
    # ... other fields
```

### CRM Models (All with user_id for multi-tenancy)
```python
@dataclass
class Campaign:
    id: str
    user_id: str  # Multi-tenant: belongs to specific user
    name: str
    description: Optional[str]
    stages: List[CampaignStage]
    # ... other fields

@dataclass
class Contact:
    id: str
    user_id: str  # Multi-tenant: belongs to specific user
    phone_number: str
    first_name: Optional[str]
    last_name: Optional[str]
    # ... other fields

@dataclass
class Call:
    id: str
    user_id: str  # Multi-tenant: belongs to specific user
    contact_id: str
    campaign_id: str
    status: CallStatus
    # ... other fields

@dataclass
class Conversation:
    id: str
    user_id: str  # Multi-tenant: belongs to specific user
    contact_id: str
    campaign_id: str
    call_id: str
    stage: CampaignStage
    # ... other fields
```

## 🔐 Authentication & Authorization

### User Registration
```python
from call_agent.user_manager import UserManager

user_manager = UserManager()
user = user_manager.register_user(
    email="user@company.com",
    password="secure_password",
    first_name="John",
    last_name="Doe",
    company_name="My Company"
)
```

### User Authentication
```python
user = user_manager.authenticate_user("user@company.com", "secure_password")
if user:
    print(f"Welcome {user.full_name}!")
```

### API Key Authentication
```python
user = user_manager.authenticate_by_api_key("your-api-key-here")
```

## 📈 Usage Examples

### Creating a Campaign for a User
```python
from call_agent.campaign_manager import CampaignManager
from call_agent.models.crm import CampaignStage

# Initialize with user context
campaign_manager = CampaignManager(user)

# Create campaign (automatically associated with user)
campaign = campaign_manager.create_campaign(
    name="Sales Campaign 2024",
    description="Q1 sales campaign for enterprise clients",
    stages=[
        CampaignStage.INTRODUCTION,
        CampaignStage.NEEDS_ASSESSMENT,
        CampaignStage.SOLUTION_PRESENTATION,
        CampaignStage.CLOSING
    ]
)
```

### Adding Contacts for a User
```python
from call_agent.repositories.contact_repository import ContactRepository
from call_agent.models.crm import Contact

contact_repo = ContactRepository()

contact = Contact(
    user_id=user.id,  # Associate with specific user
    phone_number="+1234567890",
    first_name="Alice",
    last_name="Johnson",
    email="alice@company.com",
    company="Tech Corp",
    tags=["enterprise", "decision-maker"]
)

created_contact = contact_repo.create(contact)
```

### Getting User's Data (Filtered by user_id)
```python
# Get all campaigns for user
campaigns = user_manager.get_user_campaigns(user.id)

# Get all contacts for user
contacts = user_manager.get_user_contacts(user.id)

# Get all calls for user
calls = user_manager.get_user_calls(user.id)

# Get dashboard data
dashboard = user_manager.get_user_dashboard_data(user.id)
```

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/profile` - Get user profile

### CRM Operations
- `GET /api/dashboard` - Get user dashboard
- `GET /api/campaigns` - Get user campaigns
- `POST /api/campaigns` - Create new campaign
- `GET /api/contacts` - Get user contacts
- `POST /api/contacts` - Create new contact
- `GET /api/conversations` - Get user conversations
- `GET /api/calls` - Get user calls
- `GET /api/usage` - Get usage statistics

### Example API Usage

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@company.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "My Company"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@company.com",
    "password": "password123"
  }'

# Get dashboard (requires session cookie from login)
curl -X GET http://localhost:5000/api/dashboard
```

## 🔒 Data Isolation

The system ensures complete data isolation through:

1. **User ID Filtering**: All queries filter by `user_id`
2. **Repository Level Security**: Data access controlled at repository level
3. **Manager Context**: Campaign and other managers require user context
4. **API Authentication**: All API endpoints require authentication

### Example of Data Isolation
```python
# User A can only see their own data
user_a_contacts = contact_repo.find_by_field('user_id', user_a.id)

# User B can only see their own data  
user_b_contacts = contact_repo.find_by_field('user_id', user_b.id)

# No cross-contamination between users
assert len(set(c.id for c in user_a_contacts) & set(c.id for c in user_b_contacts)) == 0
```

## 📊 Usage Tracking

The system tracks usage against plan limits:

```python
usage_stats = user_manager.get_user_usage_stats(user.id)
print(f"Plan: {usage_stats['plan']}")
print(f"Campaigns: {usage_stats['usage']['campaigns']}/{usage_stats['limits']['campaigns']}")
print(f"Contacts: {usage_stats['usage']['contacts']}/{usage_stats['limits']['contacts']}")
print(f"Calls: {usage_stats['usage']['calls']}")
```

## 🛠️ Development

### Adding New Features

1. **New Models**: Always include `user_id` field for multi-tenancy
2. **New Repositories**: Extend `BaseRepository` and implement user filtering
3. **New Managers**: Accept user context in constructor
4. **API Endpoints**: Use `@require_auth` decorator

### Database Considerations

Currently uses JSON files for storage. For production:

1. **Use PostgreSQL** with proper indexing on `user_id`
2. **Implement row-level security** (RLS)
3. **Add database migrations** for schema changes
4. **Use connection pooling** for better performance

### Security Best Practices

1. **Use JWT tokens** instead of sessions for API authentication
2. **Implement rate limiting** per user
3. **Add audit logging** for all data access
4. **Use HTTPS** in production
5. **Implement proper password hashing** (bcrypt, Argon2)

## 🚀 Production Deployment

### Environment Variables
```bash
export FLASK_SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/crm_db"
export REDIS_URL="redis://localhost:6379"
```

### Docker Deployment
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "multi_tenant_api.py"]
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For questions or support, please open an issue on GitHub.