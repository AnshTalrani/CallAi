"""
Advanced Campaign Templates with NLP Extraction and Stage-based Behavior
"""

from typing import List, Dict, Any
from .models.crm import (
    CampaignTemplate, CampaignPurpose, CampaignStage, 
    NLPExtractionRule, StageBehavior, PreferredTiming, CustomerPersonality
)

class CampaignTemplateManager:
    """Manages pre-built campaign templates with advanced NLP and behavior configuration"""
    
    @staticmethod
    def get_sales_campaign_template() -> CampaignTemplate:
        """Sales campaign template with lead qualification and objection handling"""
        return CampaignTemplate(
            name="Advanced Sales Campaign",
            purpose=CampaignPurpose.SALES,
            description="Comprehensive sales campaign with lead qualification, needs assessment, and objection handling",
            stages=[
                CampaignStage.INTRODUCTION,
                CampaignStage.NEEDS_ASSESSMENT,
                CampaignStage.SOLUTION_PRESENTATION,
                CampaignStage.OBJECTION_HANDLING,
                CampaignStage.CLOSING
            ],
            
            # NLP Extraction Rules
            nlp_extraction_rules=[
                NLPExtractionRule(
                    field_name="pain_point",
                    extraction_type="keyword",
                    keywords=["problem", "challenge", "issue", "struggle", "difficulty", "frustration"],
                    required=True,
                    description="Customer's main business challenge"
                ),
                NLPExtractionRule(
                    field_name="budget_range",
                    extraction_type="pattern",
                    patterns=[r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD)"],
                    required=False,
                    description="Customer's budget range"
                ),
                NLPExtractionRule(
                    field_name="decision_maker",
                    extraction_type="entity",
                    keywords=["CEO", "CTO", "CFO", "Manager", "Director", "Owner"],
                    required=False,
                    description="Decision maker role"
                ),
                NLPExtractionRule(
                    field_name="timeline",
                    extraction_type="keyword",
                    keywords=["ASAP", "urgent", "next month", "quarter", "year", "immediate"],
                    required=False,
                    description="Implementation timeline"
                ),
                NLPExtractionRule(
                    field_name="company_size",
                    extraction_type="pattern",
                    patterns=[r"(\d+)\s*(?:employees?|staff|people)"],
                    required=False,
                    description="Company size in employees"
                ),
                NLPExtractionRule(
                    field_name="industry",
                    extraction_type="entity",
                    keywords=["technology", "healthcare", "finance", "retail", "manufacturing", "education"],
                    required=False,
                    description="Customer's industry"
                )
            ],
            
            # Stage-based LLM Behavior
            stage_behaviors=[
                StageBehavior(
                    stage=CampaignStage.INTRODUCTION,
                    personality_traits=["professional", "friendly"],
                    response_style="conversational",
                    empathy_level=7,
                    assertiveness_level=4,
                    humor_level=3,
                    technical_depth=3,
                    call_to_action="Ask if they have time to discuss"
                ),
                StageBehavior(
                    stage=CampaignStage.NEEDS_ASSESSMENT,
                    personality_traits=["professional", "curious"],
                    response_style="conversational",
                    empathy_level=8,
                    assertiveness_level=3,
                    humor_level=2,
                    technical_depth=4,
                    call_to_action="Understand their challenges"
                ),
                StageBehavior(
                    stage=CampaignStage.SOLUTION_PRESENTATION,
                    personality_traits=["professional", "confident"],
                    response_style="professional",
                    empathy_level=6,
                    assertiveness_level=6,
                    humor_level=2,
                    technical_depth=7,
                    call_to_action="Present relevant solution"
                ),
                StageBehavior(
                    stage=CampaignStage.OBJECTION_HANDLING,
                    personality_traits=["professional", "empathetic"],
                    response_style="conversational",
                    empathy_level=9,
                    assertiveness_level=5,
                    humor_level=2,
                    technical_depth=6,
                    call_to_action="Address concerns professionally"
                ),
                StageBehavior(
                    stage=CampaignStage.CLOSING,
                    personality_traits=["professional", "assertive"],
                    response_style="professional",
                    empathy_level=5,
                    assertiveness_level=8,
                    humor_level=1,
                    technical_depth=4,
                    call_to_action="Schedule next steps"
                )
            ],
            
            # Script Templates
            script_templates={
                'introduction': {
                    'script': "Hello! This is {agent_name} calling from {company_name}. I hope you're having a great day. I'm reaching out because we have a solution that I think would be perfect for your business. Do you have a moment to hear about it?",
                    'transition_rules': {
                        'keywords': ['yes', 'sure', 'okay', 'tell me', 'interested'],
                        'min_turns': 2,
                        'sentiment_threshold': 0.2
                    }
                },
                'needs_assessment': {
                    'script': "Great! To make sure I'm offering you the right solution, could you tell me a bit about your current business challenges? What's the biggest pain point you're facing right now?",
                    'transition_rules': {
                        'keywords': ['problem', 'challenge', 'issue', 'need', 'struggle'],
                        'min_turns': 3,
                        'sentiment_threshold': 0.1
                    }
                },
                'solution_presentation': {
                    'script': "Based on what you've told me, I think our {product_name} would be perfect for you. It specifically addresses {pain_point} and has helped companies like yours increase their {benefit} by {percentage}. Would you like to hear more about how it works?",
                    'transition_rules': {
                        'keywords': ['yes', 'sure', 'how', 'tell me', 'interested'],
                        'min_turns': 2,
                        'sentiment_threshold': 0.3
                    }
                },
                'objection_handling': {
                    'script': "I understand your concern about {objection}. Many of our customers had the same worry initially. However, {counter_argument}. Plus, we offer a {guarantee}. What do you think about that?",
                    'transition_rules': {
                        'keywords': ['okay', 'good', 'interesting', 'makes sense'],
                        'min_turns': 2,
                        'sentiment_threshold': 0.3
                    }
                },
                'closing': {
                    'script': "Perfect! I'd love to schedule a quick demo for you. When would be a good time? I have availability {available_times}. Also, what's the best email to send you the details?",
                    'transition_rules': {
                        'keywords': ['yes', 'sure', 'okay', 'good time'],
                        'min_turns': 2,
                        'sentiment_threshold': 0.4
                    }
                }
            },
            
            # Campaign Settings
            preferred_timing=[PreferredTiming.BUSINESS_HOURS, PreferredTiming.MORNING, PreferredTiming.AFTERNOON],
            customer_personality_targets=[CustomerPersonality.DRIVER, CustomerPersonality.ANALYTICAL, CustomerPersonality.OPTIMISTIC],
            max_call_duration=1200,  # 20 minutes
            follow_up_delay_hours=48,
            
            # Custom Tags
            custom_tags={
                'sales_methodology': 'SPIN Selling',
                'target_decision_makers': ['CEO', 'CTO', 'VP Sales'],
                'success_metrics': ['qualified_leads', 'demo_bookings', 'sales_conversions'],
                'objection_handling_style': 'empathic_consultative'
            }
        )
    
    @staticmethod
    def get_customer_support_template() -> CampaignTemplate:
        """Customer support campaign template with issue resolution focus"""
        return CampaignTemplate(
            name="Customer Support Campaign",
            purpose=CampaignPurpose.CUSTOMER_SUPPORT,
            description="Proactive customer support with issue resolution and satisfaction tracking",
            stages=[
                CampaignStage.INTRODUCTION,
                CampaignStage.NEEDS_ASSESSMENT,
                CampaignStage.SOLUTION_PRESENTATION,
                CampaignStage.CLOSING
            ],
            
            # NLP Extraction Rules
            nlp_extraction_rules=[
                NLPExtractionRule(
                    field_name="issue_type",
                    extraction_type="keyword",
                    keywords=["bug", "error", "problem", "issue", "broken", "not working"],
                    required=True,
                    description="Type of technical issue"
                ),
                NLPExtractionRule(
                    field_name="product_feature",
                    extraction_type="entity",
                    keywords=["login", "dashboard", "reporting", "billing", "API", "mobile app"],
                    required=False,
                    description="Affected product feature"
                ),
                NLPExtractionRule(
                    field_name="severity_level",
                    extraction_type="keyword",
                    keywords=["critical", "high", "medium", "low", "urgent", "blocking"],
                    required=False,
                    description="Issue severity level"
                ),
                NLPExtractionRule(
                    field_name="resolution_satisfaction",
                    extraction_type="rating",
                    keywords=["1", "2", "3", "4", "5", "satisfied", "happy", "unhappy"],
                    required=True,
                    description="Customer satisfaction with resolution"
                )
            ],
            
            # Stage-based LLM Behavior
            stage_behaviors=[
                StageBehavior(
                    stage=CampaignStage.INTRODUCTION,
                    personality_traits=["professional", "empathetic"],
                    response_style="conversational",
                    empathy_level=9,
                    assertiveness_level=3,
                    humor_level=2,
                    technical_depth=4,
                    call_to_action="Show concern and readiness to help"
                ),
                StageBehavior(
                    stage=CampaignStage.NEEDS_ASSESSMENT,
                    personality_traits=["professional", "curious"],
                    response_style="conversational",
                    empathy_level=8,
                    assertiveness_level=3,
                    humor_level=1,
                    technical_depth=6,
                    call_to_action="Understand the issue completely"
                ),
                StageBehavior(
                    stage=CampaignStage.SOLUTION_PRESENTATION,
                    personality_traits=["professional", "helpful"],
                    response_style="professional",
                    empathy_level=7,
                    assertiveness_level=5,
                    humor_level=1,
                    technical_depth=8,
                    call_to_action="Provide clear solution steps"
                ),
                StageBehavior(
                    stage=CampaignStage.CLOSING,
                    personality_traits=["professional", "caring"],
                    response_style="conversational",
                    empathy_level=8,
                    assertiveness_level=3,
                    humor_level=2,
                    technical_depth=3,
                    call_to_action="Ensure satisfaction and offer additional help"
                )
            ],
            
            # Script Templates
            script_templates={
                'introduction': {
                    'script': "Hello! This is {agent_name} from {company_name} support. I'm calling to follow up on your recent {issue_type} ticket. How are you doing today?",
                    'transition_rules': {
                        'keywords': ['fine', 'good', 'okay', 'better'],
                        'min_turns': 1,
                        'sentiment_threshold': 0.0
                    }
                },
                'needs_assessment': {
                    'script': "I see you reported an issue with {product_feature}. Can you walk me through what happened and what you were trying to do when the problem occurred?",
                    'transition_rules': {
                        'keywords': ['problem', 'issue', 'error', 'happened'],
                        'min_turns': 2,
                        'sentiment_threshold': 0.0
                    }
                },
                'solution_presentation': {
                    'script': "I understand the issue now. This is actually a known problem that we've identified and fixed. The solution involves {solution_steps}. Would you like me to walk you through the fix?",
                    'transition_rules': {
                        'keywords': ['yes', 'sure', 'please', 'walk me through'],
                        'min_turns': 1,
                        'sentiment_threshold': 0.2
                    }
                },
                'closing': {
                    'script': "Great! I've documented this resolution in your ticket. Is there anything else I can help you with today? Also, would you like me to send you a follow-up email with the solution steps?",
                    'transition_rules': {
                        'keywords': ['no', 'thanks', 'goodbye', 'that\'s all'],
                        'min_turns': 1,
                        'sentiment_threshold': 0.0
                    }
                }
            },
            
            # Campaign Settings
            preferred_timing=[PreferredTiming.BUSINESS_HOURS, PreferredTiming.MORNING, PreferredTiming.AFTERNOON],
            customer_personality_targets=[CustomerPersonality.AMIABLE, CustomerPersonality.ANALYTICAL, CustomerPersonality.SKEPTICAL],
            max_call_duration=900,  # 15 minutes
            follow_up_delay_hours=24,
            
            # Custom Tags
            custom_tags={
                'support_tier': 'Tier 2',
                'escalation_path': 'Senior Support Engineer',
                'sla_target': '4 hours',
                'knowledge_base_articles': True,
                'customer_education': True
            }
        )
    
    @staticmethod
    def get_survey_campaign_template() -> CampaignTemplate:
        """Survey campaign template with feedback collection and analysis"""
        return CampaignTemplate(
            name="Customer Satisfaction Survey",
            purpose=CampaignPurpose.SURVEY,
            description="Comprehensive customer feedback collection with satisfaction metrics",
            stages=[
                CampaignStage.INTRODUCTION,
                CampaignStage.NEEDS_ASSESSMENT,
                CampaignStage.SOLUTION_PRESENTATION,
                CampaignStage.CLOSING
            ],
            
            # NLP Extraction Rules
            nlp_extraction_rules=[
                NLPExtractionRule(
                    field_name="satisfaction_rating",
                    extraction_type="rating",
                    keywords=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                    required=True,
                    description="Overall satisfaction rating (1-10)"
                ),
                NLPExtractionRule(
                    field_name="improvement_areas",
                    extraction_type="keyword",
                    keywords=["better", "improve", "enhance", "fix", "change", "add"],
                    required=False,
                    description="Areas for improvement"
                ),
                NLPExtractionRule(
                    field_name="product_usage",
                    extraction_type="keyword",
                    keywords=["daily", "weekly", "monthly", "rarely", "never", "often"],
                    required=False,
                    description="How often they use the product"
                ),
                NLPExtractionRule(
                    field_name="recommendation_likelihood",
                    extraction_type="rating",
                    keywords=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                    required=False,
                    description="Likelihood to recommend (1-10)"
                ),
                NLPExtractionRule(
                    field_name="feature_requests",
                    extraction_type="keyword",
                    keywords=["wish", "want", "need", "would like", "should have"],
                    required=False,
                    description="Requested new features"
                )
            ],
            
            # Stage-based LLM Behavior
            stage_behaviors=[
                StageBehavior(
                    stage=CampaignStage.INTRODUCTION,
                    personality_traits=["professional", "friendly"],
                    response_style="conversational",
                    empathy_level=6,
                    assertiveness_level=3,
                    humor_level=4,
                    technical_depth=2,
                    call_to_action="Get consent for survey participation"
                ),
                StageBehavior(
                    stage=CampaignStage.NEEDS_ASSESSMENT,
                    personality_traits=["professional", "curious"],
                    response_style="conversational",
                    empathy_level=7,
                    assertiveness_level=3,
                    humor_level=3,
                    technical_depth=3,
                    call_to_action="Collect satisfaction ratings"
                ),
                StageBehavior(
                    stage=CampaignStage.SOLUTION_PRESENTATION,
                    personality_traits=["professional", "curious"],
                    response_style="conversational",
                    empathy_level=7,
                    assertiveness_level=3,
                    humor_level=2,
                    technical_depth=3,
                    call_to_action="Understand improvement areas"
                ),
                StageBehavior(
                    stage=CampaignStage.CLOSING,
                    personality_traits=["professional", "appreciative"],
                    response_style="conversational",
                    empathy_level=8,
                    assertiveness_level=2,
                    humor_level=3,
                    technical_depth=2,
                    call_to_action="Thank and close survey"
                )
            ],
            
            # Script Templates
            script_templates={
                'introduction': {
                    'script': "Hello! This is {agent_name} calling from {company_name}. We're conducting a brief customer satisfaction survey and would really value your feedback. Do you have 2-3 minutes to help us improve our service?",
                    'transition_rules': {
                        'keywords': ['yes', 'sure', 'okay', 'have time'],
                        'min_turns': 1,
                        'sentiment_threshold': 0.0
                    }
                },
                'needs_assessment': {
                    'script': "Thank you! First, how would you rate your overall satisfaction with our {product_name} on a scale of 1 to 10, where 10 is extremely satisfied?",
                    'transition_rules': {
                        'keywords': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                        'min_turns': 1,
                        'sentiment_threshold': 0.0
                    }
                },
                'solution_presentation': {
                    'script': "Thank you for that rating. What's the main reason for your rating? What could we do better to improve your experience?",
                    'transition_rules': {
                        'keywords': ['because', 'reason', 'better', 'improve'],
                        'min_turns': 2,
                        'sentiment_threshold': 0.0
                    }
                },
                'closing': {
                    'script': "Thank you so much for your valuable feedback! We really appreciate you taking the time to help us improve. Is there anything else you'd like to share with us?",
                    'transition_rules': {
                        'keywords': ['no', 'thanks', 'goodbye', 'that\'s all'],
                        'min_turns': 1,
                        'sentiment_threshold': 0.0
                    }
                }
            },
            
            # Campaign Settings
            preferred_timing=[PreferredTiming.BUSINESS_HOURS, PreferredTiming.EVENING, PreferredTiming.WEEKEND],
            customer_personality_targets=[CustomerPersonality.AMIABLE, CustomerPersonality.EXPRESSIVE, CustomerPersonality.ANALYTICAL],
            max_call_duration=600,  # 10 minutes
            follow_up_delay_hours=0,  # No follow-up needed for surveys
            
            # Custom Tags
            custom_tags={
                'survey_type': 'Customer Satisfaction',
                'target_response_rate': '80%',
                'data_analysis': 'Sentiment Analysis + Trend Analysis',
                'actionable_insights': True,
                'customer_segmentation': True
            }
        )
    
    @staticmethod
    def get_lead_generation_template() -> CampaignTemplate:
        """Lead generation campaign template with qualification focus"""
        return CampaignTemplate(
            name="Lead Generation Campaign",
            purpose=CampaignPurpose.LEAD_GENERATION,
            description="Proactive lead generation with qualification and nurturing",
            stages=[
                CampaignStage.INTRODUCTION,
                CampaignStage.NEEDS_ASSESSMENT,
                CampaignStage.CLOSING
            ],
            
            # NLP Extraction Rules
            nlp_extraction_rules=[
                NLPExtractionRule(
                    field_name="company_size",
                    extraction_type="pattern",
                    patterns=[r"(\d+)\s*(?:employees?|staff|people)"],
                    required=False,
                    description="Company size in employees"
                ),
                NLPExtractionRule(
                    field_name="industry",
                    extraction_type="entity",
                    keywords=["technology", "healthcare", "finance", "retail", "manufacturing"],
                    required=False,
                    description="Customer's industry"
                ),
                NLPExtractionRule(
                    field_name="pain_point",
                    extraction_type="keyword",
                    keywords=["problem", "challenge", "issue", "struggle", "difficulty"],
                    required=False,
                    description="Business challenges"
                ),
                NLPExtractionRule(
                    field_name="budget_authority",
                    extraction_type="keyword",
                    keywords=["yes", "no", "maybe", "depends", "need to check"],
                    required=False,
                    description="Budget decision authority"
                )
            ],
            
            # Stage-based LLM Behavior
            stage_behaviors=[
                StageBehavior(
                    stage=CampaignStage.INTRODUCTION,
                    personality_traits=["professional", "friendly"],
                    response_style="conversational",
                    empathy_level=6,
                    assertiveness_level=4,
                    humor_level=3,
                    technical_depth=3,
                    call_to_action="Get permission to continue"
                ),
                StageBehavior(
                    stage=CampaignStage.NEEDS_ASSESSMENT,
                    personality_traits=["professional", "curious"],
                    response_style="conversational",
                    empathy_level=7,
                    assertiveness_level=3,
                    humor_level=2,
                    technical_depth=4,
                    call_to_action="Qualify the lead"
                ),
                StageBehavior(
                    stage=CampaignStage.CLOSING,
                    personality_traits=["professional", "helpful"],
                    response_style="conversational",
                    empathy_level=6,
                    assertiveness_level=4,
                    humor_level=2,
                    technical_depth=3,
                    call_to_action="Schedule follow-up"
                )
            ],
            
            # Script Templates
            script_templates={
                'introduction': {
                    'script': "Hello! This is {agent_name} from {company_name}. I'm calling because we help companies like yours with {value_proposition}. Do you have a moment to discuss how we might be able to help?",
                    'transition_rules': {
                        'keywords': ['yes', 'sure', 'okay', 'tell me more'],
                        'min_turns': 1,
                        'sentiment_threshold': 0.0
                    }
                },
                'needs_assessment': {
                    'script': "Great! To understand how we can best help you, could you tell me a bit about your company? What industry are you in and how many employees do you have?",
                    'transition_rules': {
                        'keywords': ['industry', 'employees', 'company', 'business'],
                        'min_turns': 2,
                        'sentiment_threshold': 0.0
                    }
                },
                'closing': {
                    'script': "Thank you for the information! Based on what you've shared, I think we could definitely help. Would you be interested in a brief follow-up call next week to discuss this further?",
                    'transition_rules': {
                        'keywords': ['yes', 'interested', 'follow-up', 'next week'],
                        'min_turns': 1,
                        'sentiment_threshold': 0.2
                    }
                }
            },
            
            # Campaign Settings
            preferred_timing=[PreferredTiming.BUSINESS_HOURS, PreferredTiming.MORNING, PreferredTiming.AFTERNOON],
            customer_personality_targets=[CustomerPersonality.OPTIMISTIC, CustomerPersonality.EXPRESSIVE, CustomerPersonality.DRIVER],
            max_call_duration=600,  # 10 minutes
            follow_up_delay_hours=168,  # 1 week
            
            # Custom Tags
            custom_tags={
                'lead_quality': 'B2B',
                'nurturing_sequence': 'Email + Phone',
                'qualification_criteria': ['Budget', 'Authority', 'Need', 'Timeline'],
                'conversion_target': '15%'
            }
        )
    
    @staticmethod
    def get_all_templates() -> Dict[str, CampaignTemplate]:
        """Get all available campaign templates"""
        return {
            'sales': CampaignTemplateManager.get_sales_campaign_template(),
            'customer_support': CampaignTemplateManager.get_customer_support_template(),
            'survey': CampaignTemplateManager.get_survey_campaign_template(),
            'lead_generation': CampaignTemplateManager.get_lead_generation_template()
        }
    
    @staticmethod
    def get_template_by_purpose(purpose: CampaignPurpose) -> CampaignTemplate:
        """Get campaign template by purpose"""
        templates = CampaignTemplateManager.get_all_templates()
        purpose_map = {
            CampaignPurpose.SALES: 'sales',
            CampaignPurpose.CUSTOMER_SUPPORT: 'customer_support',
            CampaignPurpose.SURVEY: 'survey',
            CampaignPurpose.LEAD_GENERATION: 'lead_generation'
        }
        
        template_key = purpose_map.get(purpose, 'sales')
        return templates[template_key]
    
    @staticmethod
    def customize_template(base_template: CampaignTemplate, customizations: Dict[str, Any]) -> CampaignTemplate:
        """Customize a base template with specific settings"""
        # Create a copy of the base template
        import copy
        customized = copy.deepcopy(base_template)
        
        # Apply customizations
        for key, value in customizations.items():
            if hasattr(customized, key):
                setattr(customized, key, value)
        
        return customized

