from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
from datetime import datetime
import os
import sys

# Ensure project root is on Python path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from call_agent.user_manager import UserManager
from call_agent.campaign_manager import CampaignManager
from call_agent.models.user import UserStatus, UserPlan
from call_agent.models.crm import CampaignStage, ContactStatus, CallStatus
from call_agent.repositories.contact_repository import ContactRepository
from call_agent.repositories.call_repository import CallRepository
from call_agent.repositories.conversation_repository import ConversationRepository

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
CORS(app)

# Initialize managers
user_manager = UserManager()

# Simple session-based authentication (use JWT in production)
def get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if user_id:
        return user_manager.get_user_by_id(user_id)
    return None

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    try:
        user = user_manager.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            company_name=data.get('company_name')
        )
        
        # Auto-login after registration
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'company_name': user.company_name,
                'plan': user.plan.value
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    user = user_manager.authenticate_user(data['email'], data['password'])
    if user:
        session['user_id'] = user.id
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'company_name': user.company_name,
                'plan': user.plan.value
            }
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/api/auth/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile"""
    user = get_current_user()
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'company_name': user.company_name,
        'phone_number': user.phone_number,
        'plan': user.plan.value,
        'status': user.status.value,
        'created_at': user.created_at.isoformat()
    })

@app.route('/api/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """Get user dashboard data"""
    user = get_current_user()
    dashboard_data = user_manager.get_user_dashboard_data(user.id)
    return jsonify(dashboard_data)

@app.route('/api/campaigns', methods=['GET'])
@require_auth
def get_campaigns():
    """Get all campaigns for current user"""
    user = get_current_user()
    campaigns = user_manager.get_user_campaigns(user.id)
    return jsonify(campaigns)

@app.route('/api/campaigns', methods=['POST'])
@require_auth
def create_campaign():
    """Create a new campaign for current user"""
    user = get_current_user()
    data = request.get_json()
    
    campaign_manager = CampaignManager(user)
    
    try:
        stages = []
        if 'stages' in data:
            stages = [CampaignStage(stage) for stage in data['stages']]
        
        campaign = campaign_manager.create_campaign(
            name=data['name'],
            description=data.get('description'),
            stages=stages
        )
        
        return jsonify(campaign.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/contacts', methods=['GET'])
@require_auth
def get_contacts():
    """Get all contacts for current user"""
    user = get_current_user()
    contacts = user_manager.get_user_contacts(user.id)
    return jsonify(contacts)

@app.route('/api/contacts', methods=['POST'])
@require_auth
def create_contact():
    """Create a new contact for current user"""
    user = get_current_user()
    data = request.get_json()
    
    contact_repo = ContactRepository()
    
    try:
        contact = Contact(
            user_id=user.id,
            phone_number=data['phone_number'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            company=data.get('company'),
            tags=data.get('tags', []),
            custom_fields=data.get('custom_fields', {})
        )
        
        created_contact = contact_repo.create(contact)
        return jsonify(created_contact.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/conversations', methods=['GET'])
@require_auth
def get_conversations():
    """Get all conversations for current user"""
    user = get_current_user()
    conversations = user_manager.get_user_conversations(user.id)
    return jsonify(conversations)

@app.route('/api/calls', methods=['GET'])
@require_auth
def get_calls():
    """Get all calls for current user"""
    user = get_current_user()
    calls = user_manager.get_user_calls(user.id)
    return jsonify(calls)

@app.route('/api/usage', methods=['GET'])
@require_auth
def get_usage():
    """Get usage statistics for current user"""
    user = get_current_user()
    usage_stats = user_manager.get_user_usage_stats(user.id)
    return jsonify(usage_stats)

@app.route('/api/campaigns/<campaign_id>/script', methods=['GET'])
@require_auth
def get_campaign_script(campaign_id):
    """Get script for a specific campaign stage"""
    user = get_current_user()
    data = request.get_json() or {}
    
    campaign_manager = CampaignManager(user)
    
    try:
        stage = CampaignStage(data.get('stage', 'introduction'))
        context = data.get('context', {})
        
        script = campaign_manager.get_campaign_script(campaign_id, stage, context)
        return jsonify({'script': script})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Import Contact model for the create_contact endpoint
from call_agent.models.crm import Contact

if __name__ == '__main__':
    print("Starting Multi-Tenant CRM API Server...")
    print("Available endpoints:")
    print("  POST /api/auth/register - Register new user")
    print("  POST /api/auth/login - Login user")
    print("  POST /api/auth/logout - Logout user")
    print("  GET  /api/auth/profile - Get user profile")
    print("  GET  /api/dashboard - Get dashboard data")
    print("  GET  /api/campaigns - Get user campaigns")
    print("  POST /api/campaigns - Create new campaign")
    print("  GET  /api/contacts - Get user contacts")
    print("  POST /api/contacts - Create new contact")
    print("  GET  /api/conversations - Get user conversations")
    print("  GET  /api/calls - Get user calls")
    print("  GET  /api/usage - Get usage statistics")
    print("  GET  /api/campaigns/<id>/script - Get campaign script")
    print("\nExample usage:")
    print("1. Register: curl -X POST http://localhost:5000/api/auth/register -H 'Content-Type: application/json' -d '{\"email\":\"user@example.com\",\"password\":\"password123\",\"first_name\":\"John\",\"last_name\":\"Doe\"}'")
    print("2. Login: curl -X POST http://localhost:5000/api/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"user@example.com\",\"password\":\"password123\"}'")
    print("3. Get Dashboard: curl -X GET http://localhost:5000/api/dashboard")
    
    app.run(debug=True, host='0.0.0.0', port=5000)