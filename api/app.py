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

from core.call_agent import CallAgent
from core.campaign_manager import CampaignManager
from crm.models.crm import Contact, ContactStatus, CallStatus, Document
from crm.repositories.contact_repository import ContactRepository
from crm.repositories.conversation_repository import ConversationRepository
from crm.repositories.document_repository import DocumentRepository
from crm.repositories.campaign_template_repository import CampaignTemplateRepository
from core.user_manager import UserManager
from core.template_manager import TemplateManager

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
@require_auth
def index_page():
    """Serve the web UI - requires authentication"""
    try:
        user = get_current_user()
        # Check if user has phone number configured (required for Asterisk)
        if not user.phone_number:
            return render_template('phone_setup.html', user=user)
        return render_template('dashboard.html', user=user)
    except Exception as e:
        return jsonify({'error': 'Authentication required'}), 401

@app.route('/login', methods=['GET'])
def login_page():
    """Serve the login page for unauthenticated users"""
    try:
        return render_template('login.html')
    except Exception:
        return "Login page not found. Please ensure templates/login.html exists.", 200

@app.route('/phone-setup', methods=['GET'])
@require_auth
def phone_setup_page():
    """Phone number setup page for authenticated users"""
    try:
        user = get_current_user()
        return render_template('phone_setup.html', user=user)
    except Exception as e:
        return jsonify({'error': 'Authentication required'}), 401

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
                from core.user_manager import UserManager
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
            'company_name': user.company_name,
            'phone_number': user.phone_number
        })
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve profile'}), 500

@app.route('/auth/profile/phone', methods=['POST'])
@require_auth
def update_phone_number():
    """Update user's phone number for Asterisk integration"""
    try:
        user = get_current_user()
        data = request.json
        
        if not data or 'phone_number' not in data:
            return jsonify({'error': 'Phone number is required'}), 400
        
        # Validate phone number format
        if not validate_phone_number(data['phone_number']):
            return jsonify({'error': 'Invalid phone number format. Use format: +1234567890'}), 400
        
        # Update user's phone number
        user.phone_number = data['phone_number']
        user_manager.update_user(user)
        
        return jsonify({
            'message': 'Phone number updated successfully',
            'phone_number': user.phone_number
        })
    except Exception as e:
        return jsonify({'error': 'Failed to update phone number'}), 500

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
        
        # Try to create from template first
        try:
            campaign = campaign_manager.create_sample_campaign(campaign_type)
        except Exception as template_error:
            # Fallback to old method if template creation fails
            print(f"Template creation failed, falling back to legacy method: {template_error}")
            campaign = campaign_manager._create_legacy_campaign(campaign_type)
        
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

@app.route('/calls/direct', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def direct_call():
    """Start an ad-hoc call without CRM context"""
    try:
        user = get_current_user()
        data = request.json
        is_valid, error_msg = validate_required_fields(data, ['phone_number'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        if not validate_phone_number(data['phone_number']):
            return jsonify({'error': 'Invalid phone number format'}), 400
        from_number = data.get('from_number')
        agent = get_call_agent(user.id)
        success = agent.start_direct_call(data['phone_number'], from_number)
        if success:
            return jsonify({'message': 'Call started successfully'})
        else:
            return jsonify({'error': 'Failed to start call'}), 400
    except Exception:
        return jsonify({'error': 'Failed to start call'}), 500


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
        from_number = data.get('from_number')  # New: allow user to specify their number
        if from_number and from_number not in (user.phone_numbers or []):
            return jsonify({'error': 'Invalid from_number'}), 400
        
        agent = get_call_agent(user.id)
        success = agent.start_call(contact_id, campaign_id, phone_number, from_number=from_number)
        
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

@app.route('/calls/hold', methods=['POST'])
@require_auth
def hold_call():
    user = get_current_user()
    data = request.json
    channel_id = data.get('channel_id')
    if not channel_id:
        return jsonify({'error': 'Missing channel_id'}), 400
    agent = get_call_agent(user.id)
    agent.asterisk_integration.hold_call(channel_id)
    return jsonify({'message': 'Call put on hold'})

@app.route('/calls/unhold', methods=['POST'])
@require_auth
def unhold_call():
    user = get_current_user()
    data = request.json
    channel_id = data.get('channel_id')
    if not channel_id:
        return jsonify({'error': 'Missing channel_id'}), 400
    agent = get_call_agent(user.id)
    agent.asterisk_integration.unhold_call(channel_id)
    return jsonify({'message': 'Call removed from hold'})

@app.route('/calls/transfer', methods=['POST'])
@require_auth
def transfer_call():
    user = get_current_user()
    data = request.json
    channel_id = data.get('channel_id')
    new_extension = data.get('new_extension')
    if not channel_id or not new_extension:
        return jsonify({'error': 'Missing channel_id or new_extension'}), 400
    agent = get_call_agent(user.id)
    agent.asterisk_integration.transfer_call(channel_id, new_extension)
    return jsonify({'message': 'Call transferred'})

@app.route('/calls/dtmf', methods=['POST'])
@require_auth
def send_dtmf():
    user = get_current_user()
    data = request.json
    channel_id = data.get('channel_id')
    dtmf = data.get('dtmf')
    if not channel_id or not dtmf:
        return jsonify({'error': 'Missing channel_id or dtmf'}), 400
    agent = get_call_agent(user.id)
    agent.asterisk_integration.send_dtmf(channel_id, dtmf)
    return jsonify({'message': 'DTMF sent'})

@app.route('/calls/outcome', methods=['POST'])
@require_auth
def call_outcome():
    user = get_current_user()
    data = request.json
    call_id = data.get('call_id')
    outcome = data.get('outcome')
    notes = data.get('notes')
    if not call_id or not outcome:
        return jsonify({'error': 'Missing call_id or outcome'}), 400
    agent = get_call_agent(user.id)
    agent.asterisk_integration.track_call_outcome(call_id, outcome, notes)
    return jsonify({'message': 'Call outcome tracked'})

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
        
        # Create sample campaigns using templates
        try:
            sales_campaign = campaign_manager.create_sample_campaign("sales")
            support_campaign = campaign_manager.create_sample_campaign("support")
            survey_campaign = campaign_manager.create_sample_campaign("survey")
            print("Created template-based sample campaigns")
        except Exception as e:
            print(f"Template creation failed, using legacy fallback: {e}")
            sales_campaign = campaign_manager._create_legacy_campaign("sales")
            support_campaign = campaign_manager._create_legacy_campaign("support")
            survey_campaign = campaign_manager._create_legacy_campaign("survey")
            print("Created legacy sample campaigns")
        
        return jsonify({
            'message': 'Sample data created successfully',
            'contacts': [c.to_dict() for c in contacts],
            'campaigns': [sales_campaign.to_dict(), support_campaign.to_dict(), survey_campaign.to_dict()]
        })
    except Exception as e:
        return jsonify({'error': 'Failed to create sample data'}), 500

@app.route('/auth/phone_numbers', methods=['GET'])
@require_auth
def get_phone_numbers():
    """Get current user's phone numbers"""
    user = get_current_user()
    return jsonify({'phone_numbers': user.phone_numbers or []})

@app.route('/auth/phone_numbers', methods=['POST'])
@require_auth
def add_phone_number():
    """Add a phone number to the current user"""
    user = get_current_user()
    data = request.json
    phone_number = data.get('phone_number')
    if not phone_number or not validate_phone_number(phone_number):
        return jsonify({'error': 'Invalid phone number'}), 400
    if phone_number not in user.phone_numbers:
        user.phone_numbers.append(phone_number)
        user_manager.update_user_profile(user.id, phone_numbers=user.phone_numbers)
    return jsonify({'phone_numbers': user.phone_numbers})

@app.route('/auth/phone_numbers', methods=['DELETE'])
@require_auth
def remove_phone_number():
    """Remove a phone number from the current user"""
    user = get_current_user()
    data = request.json
    phone_number = data.get('phone_number')
    if not phone_number or phone_number not in user.phone_numbers:
        return jsonify({'error': 'Phone number not found'}), 400
    user.phone_numbers.remove(phone_number)
    user_manager.update_user_profile(user.id, phone_numbers=user.phone_numbers)
    return jsonify({'phone_numbers': user.phone_numbers})

# ---------------- DOCUMENT MANAGEMENT ROUTES ----------------

@app.route('/documents', methods=['GET'])
@require_auth
def get_documents():
    """Get all documents for the current user"""
    try:
        user = get_current_user()
        document_repo = DocumentRepository()
        documents = document_repo.find_active_documents(user.id)
        return jsonify([doc.to_dict() for doc in documents])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve documents'}), 500

@app.route('/documents', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def create_document():
    """Create a new document"""
    try:
        user = get_current_user()
        data = request.json
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['name', 'content', 'document_type'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        document = Document(
            user_id=user.id,
            name=data['name'],
            content=data['content'],
            document_type=data['document_type'],
            tags=data.get('tags', []),
            description=data.get('description')
        )
        
        document_repo = DocumentRepository()
        created_document = document_repo.create(document)
        
        return jsonify(created_document.to_dict()), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create document'}), 500

@app.route('/documents/<document_id>', methods=['GET'])
@require_auth
def get_document(document_id):
    """Get a specific document"""
    try:
        user = get_current_user()
        document_repo = DocumentRepository()
        document = document_repo.find_by_id(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        if document.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(document.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve document'}), 500

@app.route('/documents/<document_id>', methods=['PUT'])
@require_auth
@limiter.limit("10 per minute")
def update_document(document_id):
    """Update a document"""
    try:
        user = get_current_user()
        data = request.json
        
        document_repo = DocumentRepository()
        document = document_repo.find_by_id(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        if document.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update fields
        if 'name' in data:
            document.name = data['name']
        if 'content' in data:
            document.content = data['content']
        if 'document_type' in data:
            document.document_type = data['document_type']
        if 'tags' in data:
            document.tags = data['tags']
        if 'description' in data:
            document.description = data['description']
        if 'is_active' in data:
            document.is_active = data['is_active']
        
        updated_document = document_repo.update(document)
        return jsonify(updated_document.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to update document'}), 500

@app.route('/documents/<document_id>', methods=['DELETE'])
@require_auth
def delete_document(document_id):
    """Delete a document"""
    try:
        user = get_current_user()
        document_repo = DocumentRepository()
        document = document_repo.find_by_id(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        if document.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        document_repo.delete(document_id)
        return jsonify({'message': 'Document deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Failed to delete document'}), 500

@app.route('/documents/search', methods=['POST'])
@require_auth
def search_documents():
    """Search documents by content"""
    try:
        user = get_current_user()
        data = request.json
        
        if not data.get('query'):
            return jsonify({'error': 'Search query required'}), 400
        
        document_repo = DocumentRepository()
        documents = document_repo.search_content(data['query'], user.id)
        
        return jsonify([doc.to_dict() for doc in documents])
    except Exception as e:
        return jsonify({'error': 'Failed to search documents'}), 500

@app.route('/documents/type/<document_type>', methods=['GET'])
@require_auth
def get_documents_by_type(document_type):
    """Get documents by type"""
    try:
        user = get_current_user()
        document_repo = DocumentRepository()
        documents = document_repo.find_by_type(document_type, user.id)
        
        return jsonify([doc.to_dict() for doc in documents])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve documents'}), 500

# ---------------- CAMPAIGN TEMPLATE ROUTES ----------------

@app.route('/campaign-templates', methods=['GET'])
@require_auth
def get_campaign_templates():
    """Get all campaign templates"""
    try:
        user = get_current_user()
        template_repo = CampaignTemplateRepository()
        templates = template_repo.find_active_templates()
        return jsonify([template.to_dict() for template in templates])
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve templates'}), 500

@app.route('/campaign-templates', methods=['POST'])
@require_auth
@limiter.limit("5 per minute")
def create_campaign_template():
    """Create a new campaign template"""
    try:
        user = get_current_user()
        data = request.json
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['name', 'description', 'stages'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        template_manager = TemplateManager()
        template = template_manager.create_custom_template(
            name=data['name'],
            description=data['description'],
            stages=data['stages'],
            customizations=data.get('customizations', {})
        )
        
        template_repo = CampaignTemplateRepository()
        created_template = template_repo.create(template)
        
        return jsonify(created_template.to_dict()), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create template'}), 500

@app.route('/campaign-templates/<template_id>', methods=['GET'])
@require_auth
def get_campaign_template(template_id):
    """Get a specific campaign template"""
    try:
        user = get_current_user()
        template_repo = CampaignTemplateRepository()
        template = template_repo.find_by_id(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify(template.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve template'}), 500

@app.route('/campaign-templates/<template_id>', methods=['PUT'])
@require_auth
@limiter.limit("5 per minute")
def update_campaign_template(template_id):
    """Update a campaign template"""
    try:
        user = get_current_user()
        data = request.json
        
        template_repo = CampaignTemplateRepository()
        template = template_repo.find_by_id(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # Update template fields
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'stages' in data:
            template.stages = data['stages']
        if 'customizations' in data:
            template_manager = TemplateManager()
            template = template_manager.customize_template(template, data['customizations'])
        
        updated_template = template_repo.update(template)
        return jsonify(updated_template.to_dict())
    except Exception as e:
        return jsonify({'error': 'Failed to update template'}), 500

@app.route('/campaign-templates/<template_id>', methods=['DELETE'])
@require_auth
def delete_campaign_template(template_id):
    """Delete a campaign template"""
    try:
        user = get_current_user()
        template_repo = CampaignTemplateRepository()
        template = template_repo.find_by_id(template_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        template_repo.delete(template_id)
        return jsonify({'message': 'Template deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Failed to delete template'}), 500

@app.route('/campaign-templates/recommendations', methods=['POST'])
@require_auth
def get_template_recommendations():
    """Get template recommendations based on requirements"""
    try:
        user = get_current_user()
        data = request.json
        
        if not data.get('requirements'):
            return jsonify({'error': 'Requirements required'}), 400
        
        template_manager = TemplateManager()
        recommendations = template_manager.get_template_recommendations(data['requirements'])
        
        return jsonify([template.to_dict() for template in recommendations])
    except Exception as e:
        return jsonify({'error': 'Failed to get recommendations'}), 500

@app.route('/campaign-templates/analytics', methods=['GET'])
@require_auth
def get_template_analytics():
    """Get template analytics and statistics"""
    try:
        user = get_current_user()
        template_repo = CampaignTemplateRepository()
        analytics = template_repo.get_template_statistics()
        
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': 'Failed to get analytics'}), 500

@app.route('/campaigns/from-template', methods=['POST'])
@require_auth
@limiter.limit("10 per minute")
def create_campaign_from_template():
    """Create a campaign from a template"""
    try:
        user = get_current_user()
        data = request.json
        
        # Validate required fields
        is_valid, error_msg = validate_required_fields(data, ['template_id'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        campaign_manager = CampaignManager(user)
        campaign = campaign_manager.create_campaign_from_template(
            template_id=data['template_id'],
            name=data.get('name'),
            customizations=data.get('customizations', {})
        )
        
        return jsonify(campaign.to_dict()), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create campaign from template'}), 500

if __name__ == '__main__':
    print("Starting Call Agent API Server...")
    print("API will be available at http://localhost:5000")
    print("Ensure Ollama is running on port 11434")
    app.run(host='0.0.0.0', port=5000, debug=False)