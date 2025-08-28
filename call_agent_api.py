#!/usr/bin/env python3
"""
Call Agent API - REST API for the call agent system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import threading
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from call_agent.call_agent import CallAgent
from call_agent.campaign_manager import CampaignManager
from call_agent.models.crm import Contact, ContactStatus, CallStatus
from call_agent.repositories.contact_repository import ContactRepository
from call_agent.repositories.conversation_repository import ConversationRepository

app = Flask(__name__)
CORS(app)

# Global call agent instance
call_agent = None
call_agent_lock = threading.Lock()

def get_call_agent():
    """Get or create call agent instance"""
    global call_agent
    with call_agent_lock:
        if call_agent is None:
            call_agent = CallAgent(device_id=1)
        return call_agent

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Call Agent API is running'})

@app.route('/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts"""
    try:
        contact_repo = ContactRepository()
        contacts = contact_repo.find_all()
        return jsonify([contact.to_dict() for contact in contacts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/contacts', methods=['POST'])
def create_contact():
    """Create a new contact"""
    try:
        data = request.json
        contact = Contact(
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
        return jsonify({'error': str(e)}), 500

@app.route('/contacts/<contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a specific contact"""
    try:
        contact_repo = ContactRepository()
        contact = contact_repo.find_by_id(contact_id)
        if contact:
            return jsonify(contact.to_dict())
        else:
            return jsonify({'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns', methods=['GET'])
def get_campaigns():
    """Get all campaigns"""
    try:
        campaign_manager = CampaignManager()
        campaigns = campaign_manager.campaign_repo.find_all()
        return jsonify([campaign.to_dict() for campaign in campaigns])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    try:
        data = request.json
        campaign_type = data.get('type', 'sales')
        
        campaign_manager = CampaignManager()
        campaign = campaign_manager.create_sample_campaign(campaign_type)
        
        return jsonify(campaign.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get a specific campaign"""
    try:
        campaign_manager = CampaignManager()
        campaign = campaign_manager.campaign_repo.find_by_id(campaign_id)
        if campaign:
            return jsonify(campaign.to_dict())
        else:
            return jsonify({'error': 'Campaign not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calls/start', methods=['POST'])
def start_call():
    """Start a new call"""
    try:
        data = request.json
        contact_id = data['contact_id']
        campaign_id = data['campaign_id']
        phone_number = data['phone_number']
        
        agent = get_call_agent()
        success = agent.start_call(contact_id, campaign_id, phone_number)
        
        if success:
            return jsonify({
                'message': 'Call started successfully',
                'call_id': agent.current_call.id if agent.current_call else None
            })
        else:
            return jsonify({'error': 'Failed to start call'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calls/end', methods=['POST'])
def end_call():
    """End the current call"""
    try:
        data = request.json
        status = data.get('status', 'completed')
        notes = data.get('notes')
        
        agent = get_call_agent()
        call_status = CallStatus(status)
        success = agent.end_call(call_status, notes)
        
        if success:
            return jsonify({'message': 'Call ended successfully'})
        else:
            return jsonify({'error': 'No active call to end'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calls/process', methods=['POST'])
def process_input():
    """Process user input during a call"""
    try:
        data = request.json
        user_text = data['text']
        
        agent = get_call_agent()
        response = agent.process_user_input(user_text)
        
        return jsonify({
            'response': response,
            'conversation_id': agent.current_conversation.id if agent.current_conversation else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calls/status', methods=['GET'])
def get_call_status():
    """Get current call status"""
    try:
        agent = get_call_agent()
        if agent.current_call:
            summary = agent.get_call_summary()
            return jsonify(summary)
        else:
            return jsonify({'status': 'no_active_call'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get conversation details"""
    try:
        conversation_repo = ConversationRepository()
        conversation = conversation_repo.find_by_id(conversation_id)
        if conversation:
            return jsonify(conversation.to_dict())
        else:
            return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/conversations/<conversation_id>/summary', methods=['GET'])
def get_conversation_summary(conversation_id):
    """Get conversation summary"""
    try:
        conversation_repo = ConversationRepository()
        summary = conversation_repo.get_conversation_summary(conversation_id)
        if summary:
            return jsonify(summary)
        else:
            return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns/<campaign_id>/script', methods=['GET'])
def get_campaign_script(campaign_id):
    """Get script for a campaign stage"""
    try:
        data = request.args
        stage = data.get('stage', 'introduction')
        
        campaign_manager = CampaignManager()
        script = campaign_manager.get_campaign_script(campaign_id, stage)
        
        return jsonify({'script': script})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/campaigns/<campaign_id>/behavior', methods=['GET'])
def get_campaign_behavior(campaign_id):
    """Get campaign behavior configuration"""
    try:
        campaign_manager = CampaignManager()
        behavior = campaign_manager.get_campaign_behavior_config(campaign_id)
        return jsonify(behavior)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sample-data', methods=['POST'])
def create_sample_data():
    """Create sample data for testing"""
    try:
        # Create sample contacts
        contact_repo = ContactRepository()
        campaign_manager = CampaignManager()
        
        contacts = []
        
        contact1 = Contact(
            phone_number="+1234567890",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            company="Tech Solutions Inc",
            status=ContactStatus.NEW
        )
        contacts.append(contact_repo.create(contact1))
        
        contact2 = Contact(
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Call Agent API Server...")
    print("API will be available at http://localhost:5000")
    print("Make sure LM Studio is running on port 1234")
    
    app.run(host='0.0.0.0', port=5000, debug=True)