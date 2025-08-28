#!/usr/bin/env python3
"""
Call Agent API - REST API for the call agent system
"""

from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sys
import os
import threading
import time
import re
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure project root is on Python path (so `call_agent` package is importable)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from call_agent.call_agent import CallAgent
from call_agent.campaign_manager import CampaignManager
from call_agent.models.crm import Contact, ContactStatus, CallStatus
from call_agent.repositories.contact_repository import ContactRepository
from call_agent.repositories.conversation_repository import ConversationRepository
from call_agent.user_manager import UserManager

TEMPLATES_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'templates'))
STATIC_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'static'))
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for localhost testing
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize user manager
user_manager = UserManager()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = user_manager.get_user_by_id(user_id)
        if not user:
            session.pop('user_id', None)
            return jsonify({'error': 'Invalid session'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if user_id:
        return user_manager.get_user_by_id(user_id)
    return None

# ---------------- UI ROUTES ----------------
@app.route('/', methods=['GET'])
def index_page():
    """Serve the web UI"""
    try:
        return render_template('index.html')
    except Exception:
        # If template not found yet, provide a minimal fallback
        return "UI not found. Please ensure templates/index.html exists.", 200

def validate_phone_number(phone_number: str) -> bool:
    """Validate phone number format"""
    # Basic phone number validation
    phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
    return bool(phone_pattern.match(phone_number))

def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))

def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, str]:
    """Validate required fields in request data"""
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    return True, ""

# Global call agent instances per user
call_agents = {}
call_agent_lock = threading.Lock()

def get_call_agent(user_id: str = None):
    """Get or create call agent instance for specific user"""
    global call_agents
    with call_agent_lock:
        if user_id not in call_agents:
            # Get user context
            user = None
            if user_id:
                from call_agent.user_manager import UserManager
                user_manager = UserManager()
                user = user_manager.get_user_by_id(user_id)
            
            call_agents[user_id] = CallAgent(user=user, device_id=1)
        return call_agents[user_id]

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Call Agent API is running'})

@app.route('/auth/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    """Register new user"""
    try:
        data = request.json
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user already exists
        existing_user = user_manager.get_user_by_email(data['email'])
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        user = user_manager.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            company_name=data.get('company_name')
        )
        
        if user:
            session['user_id'] = user.id
            return jsonify({
                'message': 'Registration successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'company_name': user.company_name
                }
            })
        else:
            return jsonify({'error': 'Registration failed'}), 500
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Login user"""
    try:
        data = request.json
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = user_manager.authenticate_user(data['email'], data['password'])
        if user:
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'company_name': user.company_name
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@app.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/auth/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile"""
    try:
        user = get_current_user()
        return jsonify({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'company_name': user.company_name
        })
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve profile'}), 500

@app.route('/contacts', methods=['GET'])
@require_auth
def get_contacts():
    """Get all contacts for current user"""
    try:
        user = get_current_user()
        contact_repo = ContactRepository()
        contacts = contact_repo.find_by_field('user_id', user.id)
        return jsonify([contact.to_dict() for contact in contacts])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve contacts'}), 500

@app.route('/contacts', methods=['POST'])
@require_auth
def create_contact():
    """Create a new contact"""
    try:
        user = get_current_user()
        data = request.json
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['phone_number'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate phone number
        if not validate_phone_number(data['phone_number']):
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Validate email if provided
        if data.get('email') and not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        contact = Contact(
            user_id=user.id,
            phone_number=data['phone_number'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            company=data.get('company'),
            status=ContactStatus.NEW
        )
        
        contact_repo = ContactRepository()
        created_contact = contact_repo.create(contact)
        return jsonify(created_contact.to_dict()), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create contact'}), 500

@app.route('/contacts/<contact_id>', methods=['GET'])
@require_auth
def get_contact(contact_id):
    """Get a specific contact"""
    try:
        user = get_current_user()
        contact_repo = ContactRepository()
        contact = contact_repo.find_by_id(contact_id)
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        # Verify contact belongs to current user
        if contact.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(contact.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve contact'}), 500

@app.route('/campaigns', methods=['GET'])
@require_auth
def get_campaigns():
    """Get all campaigns for current user"""
    try:
        user = get_current_user()
        campaign_manager = CampaignManager(user=user)
        campaigns = campaign_manager.campaign_repo.find_by_field('user_id', user.id)
        return jsonify([campaign.to_dict() for campaign in campaigns])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve campaigns'}), 500

@app.route('/campaigns', methods=['POST'])
@require_auth
def create_campaign():
    """Create a new campaign"""
    try:
        user = get_current_user()
        data = request.json
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['name'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        campaign_type = data.get('type', 'sales')
        
        campaign_manager = CampaignManager(user=user)
        campaign = campaign_manager.create_sample_campaign(campaign_type)
        
        return jsonify(campaign.to_dict()), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create campaign'}), 500

@app.route('/campaigns/<campaign_id>', methods=['GET'])
@require_auth
def get_campaign(campaign_id):
    """Get a specific campaign"""
    try:
        user = get_current_user()
        campaign_manager = CampaignManager(user=user)
        campaign = campaign_manager.campaign_repo.find_by_id(campaign_id)
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Verify campaign belongs to current user
        if campaign.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(campaign.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve campaign'}), 500

@app.route('/calls/start', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def start_call():
    """Start a new call"""
    try:
        user = get_current_user()
        data = request.json
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['contact_id', 'campaign_id', 'phone_number'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate phone number
        if not validate_phone_number(data['phone_number']):
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        contact_id = data['contact_id']
        campaign_id = data['campaign_id']
        phone_number = data['phone_number']
        
        agent = get_call_agent(user.id)
        success = agent.start_call(contact_id, campaign_id, phone_number)
        
        if success:
            return jsonify({
                'message': 'Call started successfully',
                'call_id': agent.current_call.id if agent.current_call else None
            })
        else:
            return jsonify({'error': 'Failed to start call'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to start call'}), 500

@app.route('/calls/end', methods=['POST'])
@require_auth
def end_call():
    """End the current call"""
    try:
        user = get_current_user()
        data = request.json
        status = data.get('status', 'completed')
        notes = data.get('notes')
        
        agent = get_call_agent(user.id)
        call_status = CallStatus(status)
        success = agent.end_call(call_status, notes)
        
        if success:
            return jsonify({'message': 'Call ended successfully'})
        else:
            return jsonify({'error': 'No active call to end'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to end call'}), 500

@app.route('/calls/process', methods=['POST'])
@require_auth
@limiter.limit("30 per minute")
def process_input():
    """Process user input during a call"""
    try:
        user = get_current_user()
        data = request.json
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['text'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        user_text = data['text']
        
        agent = get_call_agent(user.id)
        response = agent.process_user_input(user_text)
        
        return jsonify({
            'response': response,
            'conversation_id': agent.current_conversation.id if agent.current_conversation else None
        })
    except Exception as e:
        return jsonify({'error': 'Failed to process input'}), 500

@app.route('/calls/status', methods=['GET'])
@require_auth
def get_call_status():
    """Get current call status"""
    try:
        user = get_current_user()
        agent = get_call_agent(user.id)
        if agent.current_call:
            summary = agent.get_call_summary()
            return jsonify(summary)
        else:
            return jsonify({'status': 'no_active_call'})
    except Exception as e:
        return jsonify({'error': 'Failed to get call status'}), 500

@app.route('/conversations/<conversation_id>', methods=['GET'])
@require_auth
def get_conversation(conversation_id):
    """Get conversation details"""
    try:
        user = get_current_user()
        conversation_repo = ConversationRepository()
        conversation = conversation_repo.find_by_id(conversation_id)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Verify conversation belongs to current user
        if conversation.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(conversation.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve conversation'}), 500

@app.route('/conversations/<conversation_id>/summary', methods=['GET'])
@require_auth
def get_conversation_summary(conversation_id):
    """Get conversation summary"""
    try:
        user = get_current_user()
        conversation_repo = ConversationRepository()
        conversation = conversation_repo.find_by_id(conversation_id)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Verify conversation belongs to current user
        if conversation.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        summary = conversation_repo.get_conversation_summary(conversation_id)
        if summary:
            return jsonify(summary)
        else:
            return jsonify({'error': 'Failed to generate summary'}), 500
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve conversation summary'}), 500

@app.route('/campaigns/<campaign_id>/script', methods=['GET'])
@require_auth
def get_campaign_script(campaign_id):
    """Get script for a campaign stage"""
    try:
        user = get_current_user()
        data = request.args
        stage = data.get('stage', 'introduction')
        
        campaign_manager = CampaignManager(user=user)
        script = campaign_manager.get_campaign_script(campaign_id, stage)
        
        return jsonify({'script': script})
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve campaign script'}), 500

@app.route('/campaigns/<campaign_id>/behavior', methods=['GET'])
@require_auth
def get_campaign_behavior(campaign_id):
    """Get campaign behavior configuration"""
    try:
        user = get_current_user()
        campaign_manager = CampaignManager(user=user)
        behavior = campaign_manager.get_campaign_behavior_config(campaign_id)
        return jsonify(behavior)
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve campaign behavior'}), 500

@app.route('/sample-data', methods=['POST'])
@require_auth
def create_sample_data():
    """Create sample data for testing"""
    try:
        user = get_current_user()
        
        # Create sample contacts
        contact_repo = ContactRepository()
        campaign_manager = CampaignManager(user=user)
        
        contacts = []
        
        contact1 = Contact(
            user_id=user.id,
            phone_number="+1234567890",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            company="Tech Solutions Inc",
            status=ContactStatus.NEW
        )
        contacts.append(contact_repo.create(contact1))
        
        contact2 = Contact(
            user_id=user.id,
            phone_number="+1987654321",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@business.com",
            company="Business Corp",
            status=ContactStatus.NEW
        )
        contacts.append(contact_repo.create(contact2))
        
        # Create sample campaigns
        sales_campaign = campaign_manager.create_sample_campaign("sales")
        support_campaign = campaign_manager.create_sample_campaign("support")
        survey_campaign = campaign_manager.create_sample_campaign("survey")
        
        return jsonify({
            'message': 'Sample data created successfully',
            'contacts': [c.to_dict() for c in contacts],
            'campaigns': [sales_campaign.to_dict(), support_campaign.to_dict(), survey_campaign.to_dict()]
        })
    except Exception as e:
        return jsonify({'error': 'Failed to create sample data'}), 500

if __name__ == '__main__':
    print("Starting Call Agent API Server...")
    print("API will be available at http://localhost:5000")
    print("Make sure LM Studio is running on port 1234")
    
    app.run(host='0.0.0.0', port=5000, debug=True)