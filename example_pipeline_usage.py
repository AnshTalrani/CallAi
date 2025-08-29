#!/usr/bin/env python3
"""
Example usage of the new three-module conversation pipeline
"""

from call_agent.conversation_pipeline import ConversationPipeline
from call_agent.campaign_templates import CampaignTemplateManager

def main():
    print("🚀 Example: Three-Module Conversation Pipeline")
    print("=" * 50)
    
    # Initialize the pipeline
    pipeline = ConversationPipeline()
    
    # Get a sample campaign template
    campaign_template = CampaignTemplateManager.get_sales_campaign_template()
    
    # Setup the pipeline with the campaign
    campaign_config = {
        'name': campaign_template.name,
        'purpose': campaign_template.purpose.value,
        'stages': [stage.value for stage in campaign_template.stages],
        'script_template': campaign_template.script_template,
        'nlp_extraction_rules': [
            {
                'field_name': 'pain_point',
                'extraction_type': 'keyword',
                'keywords': ['problem', 'challenge', 'issue', 'struggle', 'difficulty', 'frustration'],
                'required': True,
                'description': "Customer's main business challenge"
            },
            {
                'field_name': 'budget_range',
                'extraction_type': 'pattern',
                'patterns': [r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD)"],
                'required': False,
                'description': "Customer's budget range"
            },
            {
                'field_name': 'intent',
                'extraction_type': 'intent',
                'required': False,
                'description': "User's intent or interest level"
            }
        ]
    }
    
    pipeline.setup_campaign("example_campaign", campaign_config)
    
    # Example conversation flow
    conversation_examples = [
        {
            'user_input': "Hi, I'm having trouble with my current software system. It's really slow and costing us money.",
            'stage': 'introduction',
            'expected_extractions': ['pain_point', 'intent']
        },
        {
            'user_input': "We're looking at around $50,000 for a new solution. What can you offer?",
            'stage': 'needs_assessment',
            'expected_extractions': ['budget_range', 'intent']
        },
        {
            'user_input': "That sounds expensive. I'm not sure we can afford that right now.",
            'stage': 'objection_handling',
            'expected_extractions': ['intent']
        }
    ]
    
    # Process each example
    for i, example in enumerate(conversation_examples, 1):
        print(f"\n📞 Conversation Turn {i}")
        print(f"User: {example['user_input']}")
        
        # Campaign context
        campaign_context = {
            'campaign_name': 'Advanced Sales Campaign',
            'campaign_type': 'sales',
            'contact_name': 'John Doe',
            'contact_company': 'TechCorp Inc.',
            'current_script': f"Script for {example['stage']} stage"
        }
        
        # Conversation state
        conversation_state = {
            'current_stage': example['stage'],
            'collected_data': {},
            'call_context': {},
            'timestamp': 1234567890
        }
        
        # Process through pipeline
        result = pipeline.process_user_input(
            user_input=example['user_input'],
            campaign_context=campaign_context,
            conversation_state=conversation_state
        )
        
        # Display results
        print(f"🔄 Extracted Data: {len(result.extracted_data)} items")
        for field, data in result.extracted_data.items():
            if hasattr(data, 'value'):
                print(f"   - {field}: {data.value} (confidence: {data.confidence:.2f})")
        
        print(f"🧠 Strategic Instruction:")
        print(f"   - Primary Goal: {result.strategic_instruction.primary_goal}")
        print(f"   - Tone: {result.strategic_instruction.tone_adjustment}")
        print(f"   - Focus Areas: {', '.join(result.strategic_instruction.focus_areas)}")
        
        print(f"🤖 LLM Response: {result.llm_response}")
        print(f"📊 Quality Score: {result.response_quality_score:.2f}")
        print(f"⏱️  Processing Time: {result.processing_time:.2f}s")
        
        print("-" * 50)
    
    # Show pipeline summary
    print("\n📈 Pipeline Summary:")
    summary = pipeline.get_pipeline_summary()
    print(f"Total Conversations: {summary['total_conversations']}")
    print(f"Total Extractions: {summary['total_extractions']}")
    print(f"Average Response Quality: {summary['average_response_quality']:.2f}")
    
    print("\n✅ Pipeline demonstration complete!")

if __name__ == "__main__":
    main()