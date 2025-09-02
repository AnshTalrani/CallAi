from typing import List, Dict, Any, Optional
from crm.models.campaign_template import (
    CampaignTemplate, StageInstruction, NLPExtractionRule, 
    AnalysisRule, LLMPersonality, DocumentIntegration,
    PersonalityTrait, CommunicationStyle, AnalysisType
)
from crm.repositories.campaign_template_repository import CampaignTemplateRepository
from crm.models.crm import Campaign, CampaignStage, CampaignPurpose
import uuid

class TemplateManager:
    """Manages campaign templates and template-based campaign creation"""
    
    def __init__(self):
        self.template_repo = CampaignTemplateRepository()
    
    def create_campaign_from_template(self, template_id: str, customizations: Dict[str, Any] = None) -> Campaign:
        """Create a campaign from a template with optional customizations"""
        template = self.template_repo.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Apply customizations if provided
        if customizations:
            template = self._apply_customizations(template, customizations)
        
        # Convert template to campaign
        campaign = self._convert_template_to_campaign(template)
        
        return campaign
    
    def create_custom_template(self, name: str, description: str, 
                             stages: List[str], customizations: Dict[str, Any] = None) -> CampaignTemplate:
        """Create a custom template with specified parameters"""
        template = CampaignTemplate(
            name=name,
            description=description,
            stages=stages
        )
        
        # Apply customizations
        if customizations:
            template = self._apply_customizations(template, customizations)
        
        # Save template
        return self.template_repo.create(template)
    
    def get_template_recommendations(self, requirements: Dict[str, Any]) -> List[CampaignTemplate]:
        """Get template recommendations based on requirements"""
        templates = self.template_repo.find_active_templates()
        recommendations = []
        
        for template in templates:
            score = self._calculate_template_score(template, requirements)
            if score > 0.5:  # Minimum score threshold
                recommendations.append((template, score))
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [template for template, score in recommendations]
    
    def customize_template(self, template_id: str, customizations: Dict[str, Any]) -> CampaignTemplate:
        """Customize an existing template"""
        template = self.template_repo.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        customized_template = self._apply_customizations(template, customizations)
        customized_template.id = str(uuid.uuid4())  # New ID for customized version
        customized_template.name = f"{customized_template.name} (Customized)"
        
        return self.template_repo.create(customized_template)
    
    def validate_template(self, template: CampaignTemplate) -> Dict[str, Any]:
        """Validate a template and return validation results"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check required fields
        if not template.name:
            validation_results['errors'].append("Template name is required")
            validation_results['is_valid'] = False
        
        if not template.stages:
            validation_results['errors'].append("At least one stage is required")
            validation_results['is_valid'] = False
        
        # Check stage instructions
        for stage in template.stages:
            if stage not in template.stage_instructions:
                validation_results['warnings'].append(f"No instructions found for stage: {stage}")
        
        # Check NLP extraction rules
        for rule in template.nlp_extraction_rules:
            if not rule.field_name:
                validation_results['errors'].append("NLP extraction rule missing field name")
                validation_results['is_valid'] = False
            
            if not rule.extraction_type:
                validation_results['errors'].append(f"NLP extraction rule '{rule.field_name}' missing extraction type")
                validation_results['is_valid'] = False
        
        # Check LLM personality
        if not template.llm_personality.name:
            validation_results['warnings'].append("LLM personality name not specified")
        
        # Check document integration
        if not template.document_integration.required_document_types:
            validation_results['suggestions'].append("Consider adding required document types for better context")
        
        return validation_results
    
    def get_template_analytics(self, template_id: str) -> Dict[str, Any]:
        """Get analytics for a specific template"""
        template = self.template_repo.find_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        analytics = {
            'template_info': {
                'name': template.name,
                'version': template.version,
                'stages_count': len(template.stages),
                'nlp_rules_count': len(template.nlp_extraction_rules),
                'analysis_rules_count': len(template.analysis_rules),
                'personality_traits': [trait.value for trait in template.llm_personality.personality_traits],
                'communication_style': template.llm_personality.communication_style.value,
                'motive': template.llm_personality.motive
            },
            'stage_analysis': {},
            'nlp_analysis': {},
            'personality_analysis': {}
        }
        
        # Analyze stages
        for stage, instruction in template.stage_instructions.items():
            analytics['stage_analysis'][stage] = {
                'objectives_count': len(instruction.secondary_objectives) + 1,
                'questions_count': len(instruction.key_questions),
                'success_criteria_count': len(instruction.success_criteria),
                'required_data_count': len(instruction.required_data),
                'min_turns': instruction.min_turns,
                'max_turns': instruction.max_turns,
                'sentiment_threshold': instruction.sentiment_threshold
            }
        
        # Analyze NLP rules
        extraction_types = {}
        for rule in template.nlp_extraction_rules:
            extraction_types[rule.extraction_type] = extraction_types.get(rule.extraction_type, 0) + 1
        
        analytics['nlp_analysis'] = {
            'total_rules': len(template.nlp_extraction_rules),
            'extraction_types': extraction_types,
            'required_fields': len([r for r in template.nlp_extraction_rules if r.required]),
            'average_confidence_threshold': sum(r.confidence_threshold for r in template.nlp_extraction_rules) / len(template.nlp_extraction_rules) if template.nlp_extraction_rules else 0
        }
        
        # Analyze personality
        analytics['personality_analysis'] = {
            'traits_count': len(template.llm_personality.personality_traits),
            'empathy_level': template.llm_personality.empathy_level,
            'assertiveness_level': template.llm_personality.assertiveness_level,
            'technical_depth': template.llm_personality.technical_depth,
            'humor_level': template.llm_personality.humor_level,
            'formality_level': template.llm_personality.formality_level,
            'expertise_areas_count': len(template.llm_personality.expertise_areas),
            'conversation_goals_count': len(template.llm_personality.conversation_goals)
        }
        
        return analytics
    
    def _apply_customizations(self, template: CampaignTemplate, customizations: Dict[str, Any]) -> CampaignTemplate:
        """Apply customizations to a template"""
        # Create a copy of the template
        customized = CampaignTemplate.from_dict(template.to_dict())
        
        # Apply customizations
        if 'name' in customizations:
            customized.name = customizations['name']
        
        if 'description' in customizations:
            customized.description = customizations['description']
        
        if 'stages' in customizations:
            customized.stages = customizations['stages']
        
        if 'stage_instructions' in customizations:
            for stage, instruction_data in customizations['stage_instructions'].items():
                if stage in customized.stage_instructions:
                    # Update existing instruction
                    instruction = customized.stage_instructions[stage]
                    for key, value in instruction_data.items():
                        if hasattr(instruction, key):
                            setattr(instruction, key, value)
                else:
                    # Create new instruction
                    customized.stage_instructions[stage] = StageInstruction(**instruction_data)
        
        if 'nlp_extraction_rules' in customizations:
            customized.nlp_extraction_rules = [
                NLPExtractionRule(**rule_data) for rule_data in customizations['nlp_extraction_rules']
            ]
        
        if 'analysis_rules' in customizations:
            customized.analysis_rules = [
                AnalysisRule(**rule_data) for rule_data in customizations['analysis_rules']
            ]
        
        if 'llm_personality' in customizations:
            personality_data = customizations['llm_personality']
            personality = customized.llm_personality
            
            if 'name' in personality_data:
                personality.name = personality_data['name']
            
            if 'personality_traits' in personality_data:
                personality.personality_traits = [
                    PersonalityTrait(trait) for trait in personality_data['personality_traits']
                ]
            
            if 'communication_style' in personality_data:
                personality.communication_style = CommunicationStyle(personality_data['communication_style'])
            
            # Apply other personality attributes
            for attr in ['empathy_level', 'assertiveness_level', 'technical_depth', 
                        'humor_level', 'formality_level', 'motive', 'background_story',
                        'expertise_areas', 'conversation_goals', 'response_length_preference']:
                if attr in personality_data:
                    setattr(personality, attr, personality_data[attr])
        
        if 'document_integration' in customizations:
            doc_data = customizations['document_integration']
            doc_integration = customized.document_integration
            
            for attr in ['required_document_types', 'optional_document_types', 'document_tags',
                        'context_extraction_rules', 'placeholder_mapping', 'knowledge_base_priority']:
                if attr in doc_data:
                    setattr(doc_integration, attr, doc_data[attr])
        
        if 'max_call_duration' in customizations:
            customized.max_call_duration = customizations['max_call_duration']
        
        if 'follow_up_delay_hours' in customizations:
            customized.follow_up_delay_hours = customizations['follow_up_delay_hours']
        
        if 'tags' in customizations:
            customized.tags = customizations['tags']
        
        return customized
    
    def _convert_template_to_campaign(self, template: CampaignTemplate, user_id: str = None) -> Campaign:
        """Convert a template to a campaign"""
        # Convert stages
        stages = [CampaignStage(stage) for stage in template.stages]
        
        # Convert script template
        script_template = {}
        for stage, instruction in template.stage_instructions.items():
            script_template[stage] = {
                'script': instruction.script_template,
                'transition_rules': {
                    'keywords': instruction.transition_keywords,
                    'min_turns': instruction.min_turns,
                    'sentiment_threshold': instruction.sentiment_threshold
                }
            }
        
        # Convert data collection fields
        data_collection_fields = []
        for rule in template.nlp_extraction_rules:
            if rule.required:
                data_collection_fields.append(rule.field_name)
        
        # Create campaign
        campaign = Campaign(
            user_id=user_id or "template-generated",
            name=template.name,
            description=template.description,
            stages=stages,
            script_template=script_template,
            data_collection_fields=data_collection_fields,
            template_id=template.id,  # Set the template_id reference
            max_call_duration=template.max_call_duration,
            follow_up_delay_hours=template.follow_up_delay_hours,
            custom_tags=template.custom_settings
        )
        
        return campaign
    
    def _calculate_template_score(self, template: CampaignTemplate, requirements: Dict[str, Any]) -> float:
        """Calculate how well a template matches requirements"""
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
        
        # Check tags
        if 'tags' in requirements:
            total_checks += 1
            required_tags = set(requirements['tags'])
            template_tags = set(template.tags)
            if required_tags.intersection(template_tags):
                score += 0.6
        
        return score / total_checks if total_checks > 0 else 0.0
