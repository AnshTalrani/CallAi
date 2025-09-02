#!/usr/bin/env python3
"""
Test script for campaign template functionality
"""

import sys
import os

# Add project root to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from crm.models.campaign_template import CampaignTemplate, StageInstruction, NLPExtractionRule, AnalysisRule, LLMPersonality, DocumentIntegration, PersonalityTrait, CommunicationStyle, AnalysisType
from crm.repositories.campaign_template_repository import CampaignTemplateRepository
from core.template_manager import TemplateManager

def test_campaign_template():
    """Test the campaign template functionality"""
    print("Testing Campaign Template System...")
    print("=" * 60)
    
    # Initialize repositories and managers
    template_repo = CampaignTemplateRepository()
    template_manager = TemplateManager()
    
    print("1. Testing template loading...")
    templates = template_repo.find_active_templates()
    print(f"   Found {len(templates)} active templates")
    
    if templates:
        template = templates[0]
        print(f"   Testing with template: {template.name}")
        print(f"   Version: {template.version}")
        print(f"   Stages: {len(template.stages)}")
        print()
        
        # Test 2: Template structure validation
        print("2. Testing template validation...")
        validation = template_manager.validate_template(template)
        print(f"   Is valid: {validation['is_valid']}")
        if validation['errors']:
            print(f"   Errors: {validation['errors']}")
        if validation['warnings']:
            print(f"   Warnings: {validation['warnings']}")
        if validation['suggestions']:
            print(f"   Suggestions: {validation['suggestions']}")
        print()
        
        # Test 3: Template analytics
        print("3. Testing template analytics...")
        analytics = template_manager.get_template_analytics(template.id)
        print(f"   Template info: {analytics['template_info']['name']}")
        print(f"   Stages count: {analytics['template_info']['stages_count']}")
        print(f"   NLP rules count: {analytics['template_info']['nlp_rules_count']}")
        print(f"   Analysis rules count: {analytics['template_info']['analysis_rules_count']}")
        print(f"   Personality traits: {analytics['template_info']['personality_traits']}")
        print(f"   Communication style: {analytics['template_info']['communication_style']}")
        print(f"   Motive: {analytics['template_info']['motive']}")
        print()
        
        # Test 4: Stage instructions
        print("4. Testing stage instructions...")
        for stage, instruction in template.stage_instructions.items():
            print(f"   Stage: {stage}")
            print(f"     Primary objective: {instruction.primary_objective}")
            print(f"     Key questions: {len(instruction.key_questions)}")
            print(f"     Success criteria: {len(instruction.success_criteria)}")
            print(f"     Required data: {len(instruction.required_data)}")
            print(f"     Min turns: {instruction.min_turns}")
            print(f"     Max turns: {instruction.max_turns}")
            print(f"     Sentiment threshold: {instruction.sentiment_threshold}")
            print()
        
        # Test 5: NLP extraction rules
        print("5. Testing NLP extraction rules...")
        for rule in template.nlp_extraction_rules:
            print(f"   Field: {rule.field_name}")
            print(f"     Type: {rule.extraction_type}")
            print(f"     Required: {rule.required}")
            print(f"     Keywords: {len(rule.keywords)}")
            print(f"     Patterns: {len(rule.patterns)}")
            print(f"     Confidence threshold: {rule.confidence_threshold}")
            print()
        
        # Test 6: Analysis rules
        print("6. Testing analysis rules...")
        for rule in template.analysis_rules:
            print(f"   Rule: {rule.rule_name}")
            print(f"     Type: {rule.analysis_type.value}")
            print(f"     Priority: {rule.priority}")
            print(f"     Actions: {len(rule.actions)}")
            print(f"     Trigger threshold: {rule.trigger_threshold}")
            print()
        
        # Test 7: LLM personality
        print("7. Testing LLM personality...")
        personality = template.llm_personality
        print(f"   Name: {personality.name}")
        print(f"   Traits: {[trait.value for trait in personality.personality_traits]}")
        print(f"   Communication style: {personality.communication_style.value}")
        print(f"   Empathy level: {personality.empathy_level}/10")
        print(f"   Assertiveness level: {personality.assertiveness_level}/10")
        print(f"   Technical depth: {personality.technical_depth}/10")
        print(f"   Motive: {personality.motive}")
        print(f"   Expertise areas: {len(personality.expertise_areas)}")
        print(f"   Conversation goals: {len(personality.conversation_goals)}")
        print()
        
        # Test 8: Document integration
        print("8. Testing document integration...")
        doc_integration = template.document_integration
        print(f"   Required document types: {doc_integration.required_document_types}")
        print(f"   Optional document types: {doc_integration.optional_document_types}")
        print(f"   Document tags: {doc_integration.document_tags}")
        print(f"   Placeholder mappings: {len(doc_integration.placeholder_mapping)}")
        print()
        
        # Test 9: Template conversion to campaign
        print("9. Testing template to campaign conversion...")
        try:
            campaign = template_manager._convert_template_to_campaign(template)
            print(f"   Campaign name: {campaign.name}")
            print(f"   Campaign stages: {len(campaign.stages)}")
            print(f"   Script template keys: {list(campaign.script_template.keys())}")
            print(f"   Data collection fields: {len(campaign.data_collection_fields)}")
            print(f"   Max call duration: {campaign.max_call_duration}")
            print()
        except Exception as e:
            print(f"   Error converting template: {e}")
            print()
        
        # Test 10: Template recommendations
        print("10. Testing template recommendations...")
        requirements = {
            'motive': 'sales',
            'personality_traits': ['professional', 'friendly'],
            'stage_count': 5,
            'max_duration': 900
        }
        recommendations = template_manager.get_template_recommendations(requirements)
        print(f"   Found {len(recommendations)} matching templates")
        for i, rec_template in enumerate(recommendations[:3], 1):
            score = _calculate_template_score(rec_template, requirements)
            print(f"   {i}. {rec_template.name} (Score: {score:.2f})")
        print()
        
    else:
        print("   No templates found for testing")
        print()
    
    # Test 11: Template statistics
    print("11. Testing template statistics...")
    stats = template_repo.get_template_statistics()
    print(f"   Total templates: {stats['total_templates']}")
    print(f"   Active templates: {stats['active_templates']}")
    print(f"   Motives: {stats['motives']}")
    print(f"   Personality traits: {stats['personality_traits']}")
    print(f"   Stage counts: {stats['stage_counts']}")
    print()
    
    print("Campaign Template Test Complete!")
    print("=" * 60)

def _calculate_template_score(template, requirements):
    """Helper method to calculate template score"""
    score = 0.0
    total_checks = 0
    
    # Check motive match
    if 'motive' in requirements:
        total_checks += 1
        if template.llm_personality.motive.lower() == requirements['motive'].lower():
            score += 1.0
    
    # Check personality traits
    if 'personality_traits' in requirements:
        total_checks += 1
        required_traits = set(requirements['personality_traits'])
        template_traits = set(trait.value for trait in template.llm_personality.personality_traits)
        if required_traits.intersection(template_traits):
            score += 0.8
    
    # Check stage count
    if 'stage_count' in requirements:
        total_checks += 1
        if len(template.stages) == requirements['stage_count']:
            score += 1.0
        elif abs(len(template.stages) - requirements['stage_count']) <= 1:
            score += 0.5
    
    # Check duration
    if 'max_duration' in requirements:
        total_checks += 1
        if template.max_call_duration <= requirements['max_duration']:
            score += 1.0
    
    return score / total_checks if total_checks > 0 else 0.0

if __name__ == "__main__":
    test_campaign_template()
