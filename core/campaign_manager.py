from typing import Dict, Any, List, Optional
from crm.models.crm import Campaign, CampaignStage, Contact, Conversation
from crm.models.user import User
from crm.repositories.campaign_repository import CampaignRepository
from crm.repositories.contact_repository import ContactRepository
from crm.repositories.conversation_repository import ConversationRepository
from crm.repositories.call_repository import CallRepository
from crm.repositories.campaign_template_repository import CampaignTemplateRepository
from core.document_manager import DocumentManager
from core.template_manager import TemplateManager

class CampaignManager:
    """Manages campaign behavior and script generation"""
    
    def __init__(self, user: User = None):
        self.user = user
        self.campaign_repo = CampaignRepository()
        self.contact_repo = ContactRepository()
        self.conversation_repo = ConversationRepository()
        self.call_repo = CallRepository()
        self.document_manager = DocumentManager()
        self.template_repo = CampaignTemplateRepository()
        self.template_manager = TemplateManager()
    
    def create_campaign(self, name: str, description: str = None, stages: List[CampaignStage] = None) -> Campaign:
        """Create a new campaign for the current user"""
        if not self.user:
            raise ValueError("User must be provided to create a campaign")
        
        if stages is None:
            stages = [
                CampaignStage.INTRODUCTION,
                CampaignStage.NEEDS_ASSESSMENT,
                CampaignStage.SOLUTION_PRESENTATION,
                CampaignStage.OBJECTION_HANDLING,
                CampaignStage.CLOSING
            ]
        
        campaign = Campaign(
            user_id=self.user.id,
            name=name,
            description=description,
            stages=stages
        )
        
        return self.campaign_repo.create(campaign)
    
    def get_campaign_script(self, campaign_id: str, stage: CampaignStage, context: Dict[str, Any] = None, user_input: str = None) -> str:
        """Get script for a specific campaign stage with template and document integration"""
        campaign = self.campaign_repo.find_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Verify campaign belongs to current user
        if self.user and campaign.user_id != self.user.id:
            raise ValueError(f"Campaign {campaign_id} does not belong to current user")
        
        # Get template if available (check if campaign has template_id)
        template = None
        if hasattr(campaign, 'template_id') and campaign.template_id:
            template = self.template_repo.find_by_id(campaign.template_id)
        
        # If template exists, use template-based script
        if template and stage.value in template.stage_instructions:
            instruction = template.stage_instructions[stage.value]
            script = instruction.script_template
        else:
            # Fallback to campaign script template
            script_template = campaign.script_template.get(stage.value, {})
            script = script_template.get('script', f"Default script for {stage.value}")
        
        # Get relevant documents for this campaign and stage
        relevant_documents = self.document_manager.get_relevant_documents(
            campaign=campaign,
            stage=stage.value,
            user_input=user_input,
            user_id=self.user.id if self.user else campaign.user_id
        )
        
        # Extract document placeholders
        document_placeholders = self.document_manager.get_document_placeholders(relevant_documents)
        
        # Merge context with document placeholders
        full_context = context or {}
        full_context.update(document_placeholders)
        
        # Replace placeholders with context data
        if full_context:
            for key, value in full_context.items():
                placeholder = f"{{{key}}}"
                script = script.replace(placeholder, str(value))
        
        return script
    
    def get_campaign_context(self, campaign_id: str, stage: CampaignStage = None, user_input: str = None) -> Dict[str, Any]:
        """Get comprehensive context including template, documents, and analysis for a campaign"""
        campaign = self.campaign_repo.find_by_id(campaign_id)
        if not campaign:
            return {}
        
        # Get template if available
        template = None
        if hasattr(campaign, 'template_id') and campaign.template_id:
            template = self.template_repo.find_by_id(campaign.template_id)
        
        # Get relevant documents
        relevant_documents = self.document_manager.get_relevant_documents(
            campaign=campaign,
            stage=stage.value if stage else None,
            user_input=user_input,
            user_id=self.user.id if self.user else campaign.user_id
        )
        
        # Format document context
        document_context = self.document_manager.format_document_context(relevant_documents)
        
        # Extract document placeholders
        document_placeholders = self.document_manager.get_document_placeholders(relevant_documents)
        
        # Get stage instructions if template exists
        stage_instructions = None
        if template and stage and stage.value in template.stage_instructions:
            stage_instructions = template.stage_instructions[stage.value]
        
        # Get analysis rules if template exists
        analysis_rules = []
        if template:
            analysis_rules = template.analysis_rules
        
        return {
            'campaign': campaign,
            'template': template,
            'stage_instructions': stage_instructions,
            'analysis_rules': analysis_rules,
            'documents': relevant_documents,
            'document_context': document_context,
            'document_placeholders': document_placeholders
        }
    
    def get_next_stage(self, campaign_id: str, current_stage: CampaignStage) -> Optional[CampaignStage]:
        """Get the next stage in the campaign"""
        campaign = self.campaign_repo.find_by_id(campaign_id)
        if not campaign:
            return None
        
        try:
            current_index = campaign.stages.index(current_stage)
            if current_index + 1 < len(campaign.stages):
                return campaign.stages[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def should_transition_stage(self, conversation_id: str, user_input: str, sentiment_score: float = None) -> bool:
        """Determine if conversation should transition to next stage"""
        conversation = self.conversation_repo.find_by_id(conversation_id)
        if not conversation:
            return False
        
        # Get campaign stage rules
        campaign = self.campaign_repo.find_by_id(conversation.campaign_id)
        if not campaign:
            return False
        
        stage_rules = campaign.script_template.get(conversation.stage.value, {}).get('transition_rules', {})
        
        # All conditions must be met for transition (AND logic)
        conditions_met = True
        
        # Check minimum turns requirement
        if 'min_turns' in stage_rules:
            min_turns = stage_rules['min_turns']
            if len(conversation.transcript) < min_turns:
                conditions_met = False
        
        # Check keyword requirement
        if 'keywords' in stage_rules and conditions_met:
            keywords = stage_rules['keywords']
            if not any(keyword.lower() in user_input.lower() for keyword in keywords):
                conditions_met = False
        
        # Check sentiment threshold requirement
        if 'sentiment_threshold' in stage_rules and sentiment_score is not None and conditions_met:
            threshold = stage_rules['sentiment_threshold']
            if sentiment_score < threshold:
                conditions_met = False
        
        # Check for explicit transition signals
        if 'transition_signals' in stage_rules and conditions_met:
            signals = stage_rules['transition_signals']
            if any(signal.lower() in user_input.lower() for signal in signals):
                return True
        
        return conditions_met
    
    def extract_data_from_input(self, campaign_id: str, user_input: str) -> Dict[str, Any]:
        """Extract relevant data from user input based on campaign configuration"""
        campaign = self.campaign_repo.find_by_id(campaign_id)
        if not campaign:
            return {}
        
        extracted_data = {}
        
        # Extract data based on configured fields
        for field in campaign.data_collection_fields:
            # Simple keyword-based extraction (can be enhanced with NLP)
            if field.lower() in ['name', 'first_name']:
                # Look for patterns like "my name is X" or "I'm X"
                import re
                patterns = [
                    r"my name is (\w+)",
                    r"i'm (\w+)",
                    r"i am (\w+)",
                    r"call me (\w+)"
                ]
                for pattern in patterns:
                    match = re.search(pattern, user_input.lower())
                    if match:
                        extracted_data[field] = match.group(1).title()
                        break
            
            elif field.lower() in ['email']:
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                match = re.search(email_pattern, user_input)
                if match:
                    extracted_data[field] = match.group(0)
            
            elif field.lower() in ['phone', 'phone_number']:
                import re
                phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
                match = re.search(phone_pattern, user_input)
                if match:
                    extracted_data[field] = match.group(0)
            
            elif field.lower() in ['company', 'business']:
                # Look for company mentions
                import re
                patterns = [
                    r"i work at (\w+)",
                    r"i'm from (\w+)",
                    r"(\w+) company",
                    r"(\w+) corp",
                    r"(\w+) inc"
                ]
                for pattern in patterns:
                    match = re.search(pattern, user_input.lower())
                    if match:
                        extracted_data[field] = match.group(1).title()
                        break
        
        return extracted_data
    
    def get_campaign_behavior_config(self, campaign_id: str) -> Dict[str, Any]:
        """Get behavior configuration for a campaign"""
        campaign = self.campaign_repo.find_by_id(campaign_id)
        if not campaign:
            return {}
        
        return {
            'name': campaign.name,
            'stages': [stage.value for stage in campaign.stages],
            'script_template': campaign.script_template,
            'data_collection_fields': campaign.data_collection_fields,
            'voice_settings': campaign.script_template.get('voice_settings', {}),
            'personality': campaign.script_template.get('personality', {}),
            'fallback_responses': campaign.script_template.get('fallback_responses', [])
        }
    
    def create_sample_campaign(self, campaign_type: str = "sales") -> Campaign:
        """DEPRECATED: Create a sample campaign based on type. Use create_campaign_from_template instead."""
        import warnings
        warnings.warn(
            "create_sample_campaign is deprecated. Use create_campaign_from_template with a template instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        if not self.user:
            raise ValueError("User must be provided to create a campaign")
        
        # Try to find a suitable template first
        template_recommendations = self.get_template_recommendations({
            'purpose': campaign_type,
            'stages': ['introduction', 'needs_assessment', 'solution_presentation', 'closing']
        })
        
        if template_recommendations:
            # Use the first recommended template
            template = template_recommendations[0]
            return self.create_campaign_from_template(
                template_id=template.id,
                name=f"{campaign_type.title()} Campaign",
                customizations={'campaign_type': campaign_type}
            )
        
        # Fallback to old method if no templates available
        if campaign_type == "sales":
            return self._create_sales_campaign()
        elif campaign_type == "support":
            return self._create_support_campaign()
        elif campaign_type == "survey":
            return self._create_survey_campaign()
        else:
            raise ValueError(f"Unknown campaign type: {campaign_type}")
    
    def _create_legacy_campaign(self, campaign_type: str = "sales") -> Campaign:
        """Legacy method to create campaigns without templates"""
        if campaign_type == "sales":
            return self._create_sales_campaign()
        elif campaign_type == "support":
            return self._create_support_campaign()
        elif campaign_type == "survey":
            return self._create_survey_campaign()
        else:
            raise ValueError(f"Unknown campaign type: {campaign_type}")
    
    def _create_sales_campaign(self) -> Campaign:
        """Create a sample sales campaign"""
        script_template = {
            'introduction': {
                'script': "Hello! This is {agent_name} calling from {company_name}. I hope you're having a great day. I'm reaching out because we have a special offer that I think would be perfect for your business. Do you have a moment to hear about it?",
                'transition_rules': {
                    'keywords': ['yes', 'sure', 'okay', 'tell me'],
                    'min_turns': 2
                }
            },
            'needs_assessment': {
                'script': "Great! To make sure I'm offering you the right solution, could you tell me a bit about your current business challenges? What's the biggest pain point you're facing right now?",
                'transition_rules': {
                    'keywords': ['problem', 'challenge', 'issue', 'need'],
                    'min_turns': 3
                }
            },
            'solution_presentation': {
                'script': "Based on what you've told me, I think our {product_name} would be perfect for you. It specifically addresses {pain_point} and has helped companies like yours increase their {benefit} by {percentage}. Would you like to hear more about how it works?",
                'transition_rules': {
                    'keywords': ['yes', 'sure', 'how', 'tell me'],
                    'min_turns': 2
                }
            },
            'objection_handling': {
                'script': "I understand your concern about {objection}. Many of our customers had the same worry initially. However, {counter_argument}. Plus, we offer a {guarantee}. What do you think about that?",
                'transition_rules': {
                    'keywords': ['okay', 'good', 'interesting'],
                    'sentiment_threshold': 0.3
                }
            },
            'closing': {
                'script': "Perfect! I'd love to schedule a quick demo for you. When would be a good time? I have availability {available_times}. Also, what's the best email to send you the details?",
                'transition_rules': {
                    'keywords': ['schedule', 'demo', 'email'],
                    'min_turns': 2
                }
            }
        }
        
        campaign = Campaign(
            user_id=self.user.id,
            name="Sales Outreach Campaign",
            description="A comprehensive sales campaign for product outreach",
            stages=[
                CampaignStage.INTRODUCTION,
                CampaignStage.NEEDS_ASSESSMENT,
                CampaignStage.SOLUTION_PRESENTATION,
                CampaignStage.OBJECTION_HANDLING,
                CampaignStage.CLOSING
            ],
            script_template=script_template,
            data_collection_fields=['name', 'email', 'company', 'pain_point', 'budget', 'decision_maker']
        )
        
        return self.campaign_repo.create(campaign)
    
    def create_campaign_from_template(self, template_id: str, name: str = None, customizations: Dict[str, Any] = None) -> Campaign:
        """Create a campaign from a template with optional customizations"""
        if not self.user:
            raise ValueError("User must be provided to create a campaign")
        
        # Create campaign from template
        campaign = self.template_manager.create_campaign_from_template(
            template_id=template_id,
            customizations=customizations
        )
        
        # Set user_id for the campaign
        campaign.user_id = self.user.id
        
        # Set custom name if provided
        if name:
            campaign.name = name
        
        return self.campaign_repo.create(campaign)
    
    def get_template_recommendations(self, requirements: Dict[str, Any]) -> List[Any]:
        """Get template recommendations based on requirements"""
        return self.template_manager.get_template_recommendations(requirements)
    
    def _create_support_campaign(self) -> Campaign:
        """Create a sample support campaign"""
        script_template = {
            'introduction': {
                'script': "Hello! This is {agent_name} from {company_name} support. I'm calling to follow up on your recent {issue_type} ticket. How are you doing today?",
                'transition_rules': {
                    'keywords': ['fine', 'good', 'okay'],
                    'min_turns': 1
                }
            },
            'needs_assessment': {
                'script': "I see you reported an issue with {product_feature}. Can you walk me through what happened and what you were trying to do when the problem occurred?",
                'transition_rules': {
                    'keywords': ['problem', 'issue', 'error'],
                    'min_turns': 2
                }
            },
            'solution_presentation': {
                'script': "I understand the issue now. This is actually a known problem that we've identified and fixed. The solution involves {solution_steps}. Would you like me to walk you through the fix?",
                'transition_rules': {
                    'keywords': ['yes', 'sure', 'please'],
                    'min_turns': 1
                }
            },
            'closing': {
                'script': "Great! I've documented this resolution in your ticket. Is there anything else I can help you with today? Also, would you like me to send you a follow-up email with the solution steps?",
                'transition_rules': {
                    'keywords': ['no', 'thanks', 'goodbye'],
                    'min_turns': 1
                }
            }
        }
        
        campaign = Campaign(
            user_id=self.user.id,
            name="Customer Support Follow-up",
            description="Support campaign for following up on customer issues",
            stages=[
                CampaignStage.INTRODUCTION,
                CampaignStage.NEEDS_ASSESSMENT,
                CampaignStage.SOLUTION_PRESENTATION,
                CampaignStage.CLOSING
            ],
            script_template=script_template,
            data_collection_fields=['issue_type', 'product_feature', 'resolution_satisfaction', 'additional_help_needed']
        )
        
        return self.campaign_repo.create(campaign)
    
    def _create_survey_campaign(self) -> Campaign:
        """Create a sample survey campaign"""
        script_template = {
            'introduction': {
                'script': "Hello! This is {agent_name} calling from {company_name}. We're conducting a brief customer satisfaction survey and would really value your feedback. Do you have 2-3 minutes to help us improve our service?",
                'transition_rules': {
                    'keywords': ['yes', 'sure', 'okay'],
                    'min_turns': 1
                }
            },
            'needs_assessment': {
                'script': "Thank you! First, how would you rate your overall satisfaction with our {product_name} on a scale of 1 to 10, where 10 is extremely satisfied?",
                'transition_rules': {
                    'keywords': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                    'min_turns': 1
                }
            },
            'solution_presentation': {
                'script': "Thank you for that rating. What's the main reason for your rating? What could we do better to improve your experience?",
                'transition_rules': {
                    'keywords': ['because', 'reason', 'better'],
                    'min_turns': 2
                }
            },
            'closing': {
                'script': "Thank you so much for your valuable feedback! We really appreciate you taking the time to help us improve. Is there anything else you'd like to share with us?",
                'transition_rules': {
                    'keywords': ['no', 'thanks', 'goodbye'],
                    'min_turns': 1
                }
            }
        }
        
        campaign = Campaign(
            user_id=self.user.id,
            name="Customer Satisfaction Survey",
            description="Survey campaign for gathering customer feedback",
            stages=[
                CampaignStage.INTRODUCTION,
                CampaignStage.NEEDS_ASSESSMENT,
                CampaignStage.SOLUTION_PRESENTATION,
                CampaignStage.CLOSING
            ],
            script_template=script_template,
            data_collection_fields=['satisfaction_rating', 'feedback_reason', 'improvement_suggestions', 'willing_to_recommend']
        )
        
        return self.campaign_repo.create(campaign)