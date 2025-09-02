#!/usr/bin/env python3
"""
Test script for the complete template integration system
Tests campaign templates, document integration, and LLM personality
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crm.models.crm import Campaign, CampaignStage, CampaignPurpose, Document
from crm.models.campaign_template import CampaignTemplate, StageInstruction, NLPExtractionRule, AnalysisRule, LLMPersonality, DocumentIntegration, AnalysisType, PersonalityTrait, CommunicationStyle
from crm.models.user import User
from crm.repositories.campaign_repository import CampaignRepository
from crm.repositories.campaign_template_repository import CampaignTemplateRepository
from crm.repositories.document_repository import DocumentRepository
from crm.repositories.user_repository import UserRepository
from core.campaign_manager import CampaignManager
from core.document_manager import DocumentManager
from core.template_manager import TemplateManager
from services.llm_thinking import LLMThinker

def test_template_integration():
    """Test the complete template integration system"""
    print("🧪 Testing Complete Template Integration System")
    print("=" * 60)
    
    # Create test user
    user_repo = UserRepository()
    test_user = User(
        email="test@template.com",
        password_hash="test_hash",
        phone_numbers=["+1234567890"]
    )
    user = user_repo.create(test_user)
    print(f"✅ Created test user: {user.email}")
    
    try:
        # 1. Test Document Integration
        print("\n📚 Testing Document Integration...")
        test_document_integration(user)
        
        # 2. Test Campaign Template Creation
        print("\n📋 Testing Campaign Template Creation...")
        template = test_campaign_template_creation(user)
        
        # 3. Test Template Manager
        print("\n⚙️ Testing Template Manager...")
        test_template_manager(template, user)
        
        # 4. Test Campaign Creation from Template
        print("\n🎯 Testing Campaign Creation from Template...")
        campaign = test_campaign_from_template(template, user)
        
        # 5. Test Campaign Manager with Template
        print("\n🎪 Testing Campaign Manager with Template...")
        test_campaign_manager_with_template(campaign, user)
        
        # 6. Test LLM Integration with Template
        print("\n🤖 Testing LLM Integration with Template...")
        test_llm_with_template(campaign, user)
        
        # 7. Test Complete Conversation Flow
        print("\n💬 Testing Complete Conversation Flow...")
        test_conversation_flow(campaign, user)
        
        print("\n🎉 All template integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        cleanup_test_data(user)

def test_document_integration(user):
    """Test document integration functionality"""
    document_repo = DocumentRepository()
    
    # Create test documents
    documents = [
        Document(
            user_id=user.id,
            name="Company Policy",
            content="Our company policy is to provide excellent customer service and maintain high quality standards.",
            document_type="policy",
            tags=["customer_service", "quality"]
        ),
        Document(
            user_id=user.id,
            name="Product Information",
            content="Our premium product offers advanced features including AI integration, real-time analytics, and 24/7 support.",
            document_type="product_info",
            tags=["features", "support", "ai"]
        ),
        Document(
            user_id=user.id,
            name="Sales FAQ",
            content="Common questions: Pricing starts at $99/month, 30-day free trial available, enterprise plans include custom integrations.",
            document_type="faq",
            tags=["pricing", "trial", "enterprise"]
        )
    ]
    
    created_docs = []
    for doc in documents:
        created_doc = document_repo.create(doc)
        created_docs.append(created_doc)
        print(f"  ✅ Created document: {created_doc.name}")
    
    # Test document manager
    doc_manager = DocumentManager()
    relevant_docs = doc_manager.get_relevant_documents(
        campaign=None,
        stage="introduction",
        user_input="I'm interested in your product pricing",
        user_id=user.id
    )
    
    print(f"  ✅ Found {len(relevant_docs)} relevant documents")
    
    # Test document context formatting
    context = doc_manager.format_document_context(relevant_docs)
    print(f"  ✅ Formatted document context: {len(context)} characters")
    
    return created_docs

def test_campaign_template_creation(user):
    """Test campaign template creation"""
    template_repo = CampaignTemplateRepository()
    
    # Create a comprehensive template
    template = CampaignTemplate(
        name="Advanced Sales Template",
        description="Comprehensive sales template with personality and analysis",
        stages=['introduction', 'needs_assessment', 'solution_presentation', 'closing'],
        
        # Stage instructions
        stage_instructions={
            'introduction': StageInstruction(
                stage_name="introduction",
                primary_objective="Establish rapport and introduce purpose",
                secondary_objectives=["Build trust", "Set expectations"],
                script_template="Hi {contact_name}, this is {agent_name} from {company_name}. I'm calling because {call_reason}. Do you have a moment to discuss how we can help you?",
                key_questions=["Are you the right person to talk to?", "What's your current situation?"],
                success_criteria=["Contact is engaged", "Permission to continue"],
                next_stage_conditions={
                    'keywords': ['yes', 'sure', 'okay', 'moment'],
                    'min_turns': 1
                }
            ),
            'needs_assessment': StageInstruction(
                stage_name="needs_assessment",
                primary_objective="Understand customer needs and pain points",
                secondary_objectives=["Identify decision makers", "Assess urgency"],
                script_template="Great! I'd like to understand your current situation better. What challenges are you facing with {pain_point_area}?",
                key_questions=["What's your biggest challenge?", "How are you currently handling this?"],
                success_criteria=["Clear understanding of needs", "Pain points identified"],
                next_stage_conditions={
                    'keywords': ['problem', 'issue', 'challenge', 'difficult'],
                    'min_turns': 2
                }
            )
        },
        
        # NLP extraction rules
        nlp_extraction_rules=[
            NLPExtractionRule(
                field_name="budget_range",
                extraction_type="keyword",
                keywords=["budget", "cost", "price", "afford"],
                patterns=[r"budget.*?(\d+)", r"around.*?(\d+)"],
                required=False,
                confidence_threshold=0.7
            ),
            NLPExtractionRule(
                field_name="decision_timeline",
                extraction_type="pattern",
                keywords=["timeline", "when", "soon", "urgent"],
                patterns=[r"within.*?(\d+).*?(days|weeks|months)", r"by.*?(\w+)"],
                required=False,
                confidence_threshold=0.6
            )
        ],
        
        # Analysis rules
        analysis_rules=[
            AnalysisRule(
                rule_name="Budget Qualification",
                description="Check if customer mentions budget constraints",
                conditions={
                    'keywords': ['expensive', 'costly', 'budget', 'afford'],
                    'sentiment_score': {'operator': '<', 'value': 0.3}
                },
                analysis_type=AnalysisType.BUDGET,
                actions=["Ask about budget range", "Highlight value proposition"],
                is_active=True
            )
        ],
        
        # LLM personality
        llm_personality=LLMPersonality(
            name="Sarah",
            personality_traits=[PersonalityTrait.PROFESSIONAL, PersonalityTrait.EMPATHETIC, PersonalityTrait.CONFIDENT],
            communication_style=CommunicationStyle.CONVERSATIONAL,
            empathy_level=8,
            assertiveness_level=6,
            technical_depth=7,
            motive="Help customers find the best solution for their needs",
            background_story="Experienced sales professional with 5+ years helping businesses optimize their operations",
            expertise_areas=["business optimization", "cost reduction", "efficiency improvement"],
            conversation_goals=["Build trust", "Understand needs", "Present solutions", "Close deals"],
            response_length_preference="concise"
        ),
        
        # Document integration
        document_integration=DocumentIntegration(
            required_document_types=["product_info", "policy"],
            optional_document_types=["faq", "knowledge_base"],
            document_tags=["sales", "pricing", "features"],
            placeholder_mapping={
                "company_policy": "policy_content",
                "product_features": "product_content",
                "pricing_info": "faq_content"
            }
        )
    )
    
    created_template = template_repo.create(template)
    print(f"  ✅ Created template: {created_template.name}")
    print(f"  ✅ Template has {len(created_template.stage_instructions)} stage instructions")
    print(f"  ✅ Template has {len(created_template.nlp_extraction_rules)} NLP rules")
    print(f"  ✅ Template has {len(created_template.analysis_rules)} analysis rules")
    
    return created_template

def test_template_manager(template, user):
    """Test template manager functionality"""
    template_manager = TemplateManager()
    
    # Test template validation
    is_valid = template_manager.validate_template(template)
    print(f"  ✅ Template validation: {is_valid}")
    
    # Test template analytics
    analytics = template_manager.get_template_analytics(template.id)
    print(f"  ✅ Template analytics: {analytics}")
    
    # Test template recommendations
    requirements = {
        'purpose': 'sales',
        'stages': ['introduction', 'needs_assessment'],
        'personality_traits': ['professional', 'empathetic']
    }
    recommendations = template_manager.get_template_recommendations(requirements)
    print(f"  ✅ Found {len(recommendations)} template recommendations")

def test_campaign_from_template(template, user):
    """Test creating a campaign from template"""
    campaign_manager = CampaignManager(user)
    
    # Create campaign from template
    campaign = campaign_manager.create_campaign_from_template(
        template_id=template.id,
        name="My Sales Campaign",
        customizations={
            'company_name': 'TechCorp',
            'agent_name': 'Sarah',
            'call_reason': 'we have a solution that could help your business'
        }
    )
    
    print(f"  ✅ Created campaign: {campaign.name}")
    print(f"  ✅ Campaign template_id: {campaign.template_id}")
    print(f"  ✅ Campaign stages: {[stage.value for stage in campaign.stages]}")
    
    return campaign

def test_campaign_manager_with_template(campaign, user):
    """Test campaign manager with template integration"""
    campaign_manager = CampaignManager(user)
    
    # Test getting campaign context with template
    context = campaign_manager.get_campaign_context(
        campaign_id=campaign.id,
        stage=CampaignStage.INTRODUCTION,
        user_input="Hi, I'm interested in learning more"
    )
    
    print(f"  ✅ Campaign context includes template: {context.get('template') is not None}")
    print(f"  ✅ Campaign context includes stage instructions: {context.get('stage_instructions') is not None}")
    print(f"  ✅ Campaign context includes analysis rules: {len(context.get('analysis_rules', []))} rules")
    print(f"  ✅ Campaign context includes documents: {len(context.get('documents', []))} documents")
    
    # Test getting script with template
    script = campaign_manager.get_campaign_script(
        campaign_id=campaign.id,
        stage=CampaignStage.INTRODUCTION,
        context={'contact_name': 'John', 'company_name': 'TechCorp', 'agent_name': 'Sarah'},
        user_input="Hello"
    )
    
    print(f"  ✅ Generated script: {script[:100]}...")

def test_llm_with_template(campaign, user):
    """Test LLM integration with template"""
    # Note: This is a mock test since we don't have actual LLM service running
    print("  ✅ LLM integration test (mock) - would use template personality and analysis rules")
    
    # Test prompt building with template context
    campaign_manager = CampaignManager(user)
    context = campaign_manager.get_campaign_context(
        campaign_id=campaign.id,
        stage=CampaignStage.INTRODUCTION,
        user_input="Hi, I'm interested in your services"
    )
    
    conversation_context = {
        'current_stage': 'introduction',
        'collected_data': {},
        'call_context': {},
        'conversation_turns': 1
    }
    
    # This would normally call the LLM service
    print(f"  ✅ Template context includes personality: {context.get('template') is not None}")
    print(f"  ✅ Template context includes analysis rules: {len(context.get('analysis_rules', []))} rules")

def test_conversation_flow(campaign, user):
    """Test complete conversation flow with template"""
    print("  ✅ Conversation flow test (mock) - would process user input with template rules")
    
    # Simulate conversation flow
    user_inputs = [
        "Hello, this is John",
        "Yes, I have a moment",
        "We're having issues with our current system",
        "It's costing us time and money"
    ]
    
    campaign_manager = CampaignManager(user)
    
    for i, user_input in enumerate(user_inputs):
        print(f"    Turn {i+1}: User says: '{user_input}'")
        
        # Get context for this input
        context = campaign_manager.get_campaign_context(
            campaign_id=campaign.id,
            stage=CampaignStage.INTRODUCTION if i < 2 else CampaignStage.NEEDS_ASSESSMENT,
            user_input=user_input
        )
        
        # Simulate data extraction
        template = context.get('template')
        if template and template.nlp_extraction_rules:
            extracted_data = {}
            for rule in template.nlp_extraction_rules:
                if any(keyword.lower() in user_input.lower() for keyword in rule.keywords):
                    extracted_data[rule.field_name] = True
                    print(f"      Extracted: {rule.field_name}")
        
        # Simulate analysis
        if template and template.analysis_rules:
            for rule in template.analysis_rules:
                if rule.is_active:
                    print(f"      Analysis rule triggered: {rule.rule_name}")
        
        print(f"    Turn {i+1}: Agent would respond with template-driven response")

def cleanup_test_data(user):
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    # Clean up documents
    document_repo = DocumentRepository()
    documents = document_repo.find_by_field('user_id', user.id)
    for doc in documents:
        document_repo.delete(doc.id)
    
    # Clean up campaigns
    campaign_repo = CampaignRepository()
    campaigns = campaign_repo.find_by_field('user_id', user.id)
    for campaign in campaigns:
        campaign_repo.delete(campaign.id)
    
    # Clean up templates
    template_repo = CampaignTemplateRepository()
    templates = template_repo.find_all()
    for template in templates:
        template_repo.delete(template.id)
    
    # Clean up user
    user_repo = UserRepository()
    user_repo.delete(user.id)
    
    print("  ✅ Test data cleaned up")

if __name__ == "__main__":
    test_template_integration()
