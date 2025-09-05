#!/usr/bin/env python3
"""
Test script for campaign workflow functionality
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from crm.models.crm import Campaign, CampaignStage, Contact, ContactStatus
from crm.models.user import User
from crm.models.campaign_template import CampaignTemplate, StageInstruction
from core.campaign_manager import CampaignManager
from crm.repositories.campaign_repository import CampaignRepository
from crm.repositories.campaign_template_repository import CampaignTemplateRepository
from crm.repositories.contact_repository import ContactRepository
from crm.repositories.user_repository import UserRepository

def create_test_template(user_id: str) -> str:
    """Create a test campaign template"""
    from crm.models.campaign_template import (
        CampaignTemplate, 
        StageInstruction, 
        NLPExtractionRule,
        LLMPersonality,
        PersonalityTrait,
        CommunicationStyle,
        DocumentIntegration
    )
    
    template_repo = CampaignTemplateRepository()
    
    # Create a test template if it doesn't exist
    template_name = "Test Sales Campaign Template"
    template = template_repo.find_by_name(template_name)
    
    if not template:
        # Create stage instructions
        stage_instructions = {
            "introduction": StageInstruction(
                stage_name="introduction",
                primary_objective="Build rapport and introduce the purpose of the call",
                key_questions=[
                    "How are you doing today?",
                    "Is this a good time to talk?"
                ]
            ),
            "needs_assessment": StageInstruction(
                stage_name="needs_assessment",
                primary_objective="Understand customer needs and pain points",
                key_questions=[
                    "What challenges are you currently facing?",
                    "What solutions have you tried before?"
                ]
            )
        }
        
        # Create NLP extraction rules
        nlp_rules = [
            NLPExtractionRule(
                field_name="budget",
                extraction_type="budget_range",
                keywords=["budget", "cost", "price", "investment"],
                required=False
            )
        ]
        
        # Create LLM personality
        personality = LLMPersonality(
            name="Professional Sales",
            personality_traits=[
                PersonalityTrait.PROFESSIONAL,
                PersonalityTrait.ASSERTIVE,
                PersonalityTrait.CONFIDENT
            ],
            communication_style=CommunicationStyle.PROFESSIONAL,
            empathy_level=4,
            assertiveness_level=8,
            technical_depth=5,
            motive="sales"
        )
        
        # Create document integration
        doc_integration = DocumentIntegration(
            required_document_types=["pricing", "product_specs"]
        )
        
        # Create the template
        template = CampaignTemplate(
            name=template_name,
            description="A test sales campaign template",
            stages=[
                "introduction",
                "needs_assessment",
                "solution_presentation",
                "objection_handling",
                "closing"
            ],
            stage_instructions=stage_instructions,
            nlp_extraction_rules=nlp_rules,
            llm_personality=personality,
            document_integration=doc_integration,
            max_call_duration=900,  # 15 minutes
            follow_up_delay_hours=24,
            tags=["sales", "outbound", "test"]
        )
        template = template_repo.create(template)
    
    return template.id

def setup_test_environment():
    """Set up test data and environment"""
    print("Setting up test environment...")
    
    # Create a test user if not exists
    user_repo = UserRepository()
    test_email = "test@example.com"
    test_user = user_repo.find_by_email(test_email)
    if not test_user:
        test_user = user_repo.create_user(
            email=test_email,
            password="testpassword123",
            first_name="Test",
            last_name="User",
            company_name="Test Company"
        )
    
    # Create a test template
    template_id = create_test_template(test_user.id)
    test_user.template_id = template_id
    
    return test_user

def test_campaign_creation():
    """Test creating a new campaign"""
    print("\n=== Testing Campaign Creation ===")
    
    # Setup
    user = setup_test_environment()
    campaign_repo = CampaignRepository()
    campaign_manager = CampaignManager(user=user)
    
    # Test data
    campaign_name = "Test Campaign " + datetime.now().strftime("%Y%m%d%H%M%S")
    campaign_description = "This is a test campaign created by the test script"
    
    # Create campaign
    print(f"Creating campaign: {campaign_name}")
    campaign = campaign_manager.create_campaign(
        name=campaign_name,
        description=campaign_description
    )
    
    # Associate template with campaign
    campaign.template_id = user.template_id
    campaign = campaign_repo.update(campaign)
    
    # Verify template was applied
    assert campaign.template_id == user.template_id, "Template ID was not set correctly"
    
    # Load the template to verify it exists
    template = campaign_manager.template_repo.find_by_id(user.template_id)
    assert template is not None, "Template not found"
    print(f"✅ Campaign template applied: {template.name}")
    
    # Verify
    assert campaign is not None, "Campaign creation failed"
    assert campaign.name == campaign_name, "Campaign name mismatch"
    assert campaign.user_id == user.id, "User ID mismatch"
    
    print(f"✅ Campaign created successfully with ID: {campaign.id}")
    return campaign

def test_add_contacts_to_campaign(campaign):
    """Test adding contacts to a campaign"""
    print("\n=== Testing Adding Contacts to Campaign ===")
    
    contact_repo = ContactRepository()
    
    # Create test contacts
    test_contacts = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "company": "Test Company",
            "status": ContactStatus.NEW
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "+1987654321",
            "company": "Another Company",
            "status": ContactStatus.NEW
        }
    ]
    
    added_contacts = []
    for contact_data in test_contacts:
        contact = Contact(
            user_id=campaign.user_id,
            **contact_data
        )
        contact = contact_repo.create(contact)
        added_contacts.append(contact)
        print(f"Added contact: {contact.first_name} {contact.last_name} ({contact.email})")
    
    # Verify contacts were added by checking each one
    for contact in added_contacts:
        found = contact_repo.find_by_id(contact.id)
        assert found is not None, f"Contact {contact.id} not found in database"
        assert found.user_id == campaign.user_id, "User ID mismatch"
    
    # Get all contacts for the user to verify count
    user_contacts = contact_repo.find_by_field('user_id', campaign.user_id)
    assert len(user_contacts) >= len(added_contacts), "Not all contacts were added"
    
    print(f"✅ Successfully added {len(added_contacts)} contacts to the campaign")
    return added_contacts

def test_campaign_workflow():
    """Test the complete campaign workflow"""
    print("\n=== Starting Campaign Workflow Test ===")
    
    # Test campaign creation
    campaign = test_campaign_creation()
    
    # Test adding contacts
    contacts = test_add_contacts_to_campaign(campaign)
    
    # Get the user with all required fields
    user_repo = UserRepository()
    user = user_repo.find_by_id(campaign.user_id)
    
    # Initialize campaign manager with the full user object
    campaign_manager = CampaignManager(user=user)
    
    # Test getting campaign script for different stages
    print("\n=== Testing Campaign Script Generation ===")
    stages = [
        CampaignStage.INTRODUCTION,
        CampaignStage.NEEDS_ASSESSMENT,
        CampaignStage.SOLUTION_PRESENTATION,
        CampaignStage.OBJECTION_HANDLING,
        CampaignStage.CLOSING
    ]
    
    for stage in stages:
        script = campaign_manager.get_campaign_script(
            campaign_id=campaign.id,
            stage=stage,
            context={
                "contact": {"name": "Test Contact"},
                "company": "Test Company"
            }
        )
        print(f"\nStage: {stage.value}")
        print("-" * 30)
        print(script)
    
    print("\n✅ Campaign workflow test completed successfully!")

if __name__ == "__main__":
    test_campaign_workflow()
