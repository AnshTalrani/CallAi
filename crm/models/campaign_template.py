from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

class AnalysisType(Enum):
    """Types of analysis that can be performed"""
    SENTIMENT = "sentiment"
    INTENT = "intent"
    URGENCY = "urgency"
    BUDGET = "budget"
    AUTHORITY = "authority"
    INTEREST_LEVEL = "interest_level"
    OBJECTION_TYPE = "objection_type"
    DECISION_MAKER = "decision_maker"

class PersonalityTrait(Enum):
    """LLM personality traits"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ASSERTIVE = "assertive"
    EMPATHETIC = "empathetic"
    TECHNICAL = "technical"
    CASUAL = "casual"
    FORMAL = "formal"
    ENTHUSIASTIC = "enthusiastic"
    PATIENT = "patient"
    CONFIDENT = "confident"

class CommunicationStyle(Enum):
    """LLM communication styles"""
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    TECHNICAL = "technical"
    SALES_ORIENTED = "sales_oriented"
    SUPPORT_ORIENTED = "support_oriented"

@dataclass
class StageInstruction:
    """Detailed instructions for each campaign stage"""
    stage_name: str
    primary_objective: str
    secondary_objectives: List[str] = field(default_factory=list)
    key_questions: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    failure_indicators: List[str] = field(default_factory=list)
    next_stage_conditions: Dict[str, Any] = field(default_factory=dict)
    fallback_actions: List[str] = field(default_factory=list)
    required_data: List[str] = field(default_factory=list)
    optional_data: List[str] = field(default_factory=list)
    script_template: str = ""
    transition_keywords: List[str] = field(default_factory=list)
    min_turns: int = 2
    max_turns: int = 10
    sentiment_threshold: float = 0.3

@dataclass
class NLPExtractionRule:
    """Advanced NLP extraction rules"""
    field_name: str
    extraction_type: str  # "keyword", "sentiment", "entity", "pattern", "rating", "intent"
    keywords: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)  # Regex patterns
    required: bool = False
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    confidence_threshold: float = 0.7
    fallback_value: Optional[str] = None
    extraction_priority: int = 1

@dataclass
class AnalysisRule:
    """Rules for analyzing extracted data and conversation flow"""
    rule_name: str
    analysis_type: AnalysisType
    conditions: Dict[str, Any]  # Conditions that trigger the analysis
    actions: List[str]  # Actions to take when conditions are met
    priority: int = 1
    description: str = ""
    is_active: bool = True
    trigger_threshold: float = 0.5

@dataclass
class LLMPersonality:
    """Comprehensive LLM personality configuration"""
    name: str
    personality_traits: List[PersonalityTrait] = field(default_factory=list)
    communication_style: CommunicationStyle = CommunicationStyle.CONVERSATIONAL
    empathy_level: int = 5  # 1-10 scale
    assertiveness_level: int = 5  # 1-10 scale
    technical_depth: int = 5  # 1-10 scale
    humor_level: int = 3  # 1-10 scale
    formality_level: int = 5  # 1-10 scale
    motive: str = "sales"  # "sales", "support", "survey", "consultation"
    background_story: str = ""
    expertise_areas: List[str] = field(default_factory=list)
    conversation_goals: List[str] = field(default_factory=list)
    response_length_preference: str = "medium"  # "short", "medium", "long"
    tone_adjustment_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentIntegration:
    """Document integration configuration for campaigns"""
    required_document_types: List[str] = field(default_factory=list)
    optional_document_types: List[str] = field(default_factory=list)
    document_tags: List[str] = field(default_factory=list)
    context_extraction_rules: Dict[str, Any] = field(default_factory=dict)
    placeholder_mapping: Dict[str, str] = field(default_factory=dict)
    knowledge_base_priority: int = 1

@dataclass
class CampaignTemplate:
    """Comprehensive campaign template with all advanced features"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Campaign Structure
    stages: List[str] = field(default_factory=list)
    stage_instructions: Dict[str, StageInstruction] = field(default_factory=dict)
    
    # NLP Configuration
    nlp_extraction_rules: List[NLPExtractionRule] = field(default_factory=list)
    analysis_rules: List[AnalysisRule] = field(default_factory=list)
    
    # LLM Configuration
    llm_personality: LLMPersonality = field(default_factory=lambda: LLMPersonality(name="Default"))
    
    # Document Integration
    document_integration: DocumentIntegration = field(default_factory=DocumentIntegration)
    
    # Campaign Settings
    max_call_duration: int = 900  # 15 minutes in seconds
    follow_up_delay_hours: int = 24
    retry_attempts: int = 3
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_assurance_rules: Dict[str, Any] = field(default_factory=dict)
    
    # Custom Configuration
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for storage"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'stages': self.stages,
            'stage_instructions': {
                stage: {
                    'stage_name': instr.stage_name,
                    'primary_objective': instr.primary_objective,
                    'secondary_objectives': instr.secondary_objectives,
                    'key_questions': instr.key_questions,
                    'success_criteria': instr.success_criteria,
                    'failure_indicators': instr.failure_indicators,
                    'next_stage_conditions': instr.next_stage_conditions,
                    'fallback_actions': instr.fallback_actions,
                    'required_data': instr.required_data,
                    'optional_data': instr.optional_data,
                    'script_template': instr.script_template,
                    'transition_keywords': instr.transition_keywords,
                    'min_turns': instr.min_turns,
                    'max_turns': instr.max_turns,
                    'sentiment_threshold': instr.sentiment_threshold
                } for stage, instr in self.stage_instructions.items()
            },
            'nlp_extraction_rules': [
                {
                    'field_name': rule.field_name,
                    'extraction_type': rule.extraction_type,
                    'keywords': rule.keywords,
                    'patterns': rule.patterns,
                    'required': rule.required,
                    'validation_rules': rule.validation_rules,
                    'description': rule.description,
                    'confidence_threshold': rule.confidence_threshold,
                    'fallback_value': rule.fallback_value,
                    'extraction_priority': rule.extraction_priority
                } for rule in self.nlp_extraction_rules
            ],
            'analysis_rules': [
                {
                    'rule_name': rule.rule_name,
                    'analysis_type': rule.analysis_type.value,
                    'conditions': rule.conditions,
                    'actions': rule.actions,
                    'priority': rule.priority,
                    'description': rule.description,
                    'is_active': rule.is_active,
                    'trigger_threshold': rule.trigger_threshold
                } for rule in self.analysis_rules
            ],
            'llm_personality': {
                'name': self.llm_personality.name,
                'personality_traits': [trait.value for trait in self.llm_personality.personality_traits],
                'communication_style': self.llm_personality.communication_style.value,
                'empathy_level': self.llm_personality.empathy_level,
                'assertiveness_level': self.llm_personality.assertiveness_level,
                'technical_depth': self.llm_personality.technical_depth,
                'humor_level': self.llm_personality.humor_level,
                'formality_level': self.llm_personality.formality_level,
                'motive': self.llm_personality.motive,
                'background_story': self.llm_personality.background_story,
                'expertise_areas': self.llm_personality.expertise_areas,
                'conversation_goals': self.llm_personality.conversation_goals,
                'response_length_preference': self.llm_personality.response_length_preference,
                'tone_adjustment_rules': self.llm_personality.tone_adjustment_rules
            },
            'document_integration': {
                'required_document_types': self.document_integration.required_document_types,
                'optional_document_types': self.document_integration.optional_document_types,
                'document_tags': self.document_integration.document_tags,
                'context_extraction_rules': self.document_integration.context_extraction_rules,
                'placeholder_mapping': self.document_integration.placeholder_mapping,
                'knowledge_base_priority': self.document_integration.knowledge_base_priority
            },
            'max_call_duration': self.max_call_duration,
            'follow_up_delay_hours': self.follow_up_delay_hours,
            'retry_attempts': self.retry_attempts,
            'success_metrics': self.success_metrics,
            'quality_assurance_rules': self.quality_assurance_rules,
            'custom_settings': self.custom_settings,
            'tags': self.tags,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CampaignTemplate':
        """Create template from dictionary"""
        # Convert stage instructions
        stage_instructions = {}
        for stage, instr_data in data.get('stage_instructions', {}).items():
            stage_instructions[stage] = StageInstruction(
                stage_name=instr_data['stage_name'],
                primary_objective=instr_data['primary_objective'],
                secondary_objectives=instr_data.get('secondary_objectives', []),
                key_questions=instr_data.get('key_questions', []),
                success_criteria=instr_data.get('success_criteria', []),
                failure_indicators=instr_data.get('failure_indicators', []),
                next_stage_conditions=instr_data.get('next_stage_conditions', {}),
                fallback_actions=instr_data.get('fallback_actions', []),
                required_data=instr_data.get('required_data', []),
                optional_data=instr_data.get('optional_data', []),
                script_template=instr_data.get('script_template', ''),
                transition_keywords=instr_data.get('transition_keywords', []),
                min_turns=instr_data.get('min_turns', 2),
                max_turns=instr_data.get('max_turns', 10),
                sentiment_threshold=instr_data.get('sentiment_threshold', 0.3)
            )
        
        # Convert NLP extraction rules
        nlp_rules = []
        for rule_data in data.get('nlp_extraction_rules', []):
            nlp_rules.append(NLPExtractionRule(
                field_name=rule_data['field_name'],
                extraction_type=rule_data['extraction_type'],
                keywords=rule_data.get('keywords', []),
                patterns=rule_data.get('patterns', []),
                required=rule_data.get('required', False),
                validation_rules=rule_data.get('validation_rules', {}),
                description=rule_data.get('description', ''),
                confidence_threshold=rule_data.get('confidence_threshold', 0.7),
                fallback_value=rule_data.get('fallback_value'),
                extraction_priority=rule_data.get('extraction_priority', 1)
            ))
        
        # Convert analysis rules
        analysis_rules = []
        for rule_data in data.get('analysis_rules', []):
            analysis_rules.append(AnalysisRule(
                rule_name=rule_data['rule_name'],
                analysis_type=AnalysisType(rule_data['analysis_type']),
                conditions=rule_data['conditions'],
                actions=rule_data['actions'],
                priority=rule_data.get('priority', 1),
                description=rule_data.get('description', ''),
                is_active=rule_data.get('is_active', True),
                trigger_threshold=rule_data.get('trigger_threshold', 0.5)
            ))
        
        # Convert LLM personality
        personality_data = data.get('llm_personality', {})
        llm_personality = LLMPersonality(
            name=personality_data.get('name', 'Default'),
            personality_traits=[PersonalityTrait(trait) for trait in personality_data.get('personality_traits', [])],
            communication_style=CommunicationStyle(personality_data.get('communication_style', 'conversational')),
            empathy_level=personality_data.get('empathy_level', 5),
            assertiveness_level=personality_data.get('assertiveness_level', 5),
            technical_depth=personality_data.get('technical_depth', 5),
            humor_level=personality_data.get('humor_level', 3),
            formality_level=personality_data.get('formality_level', 5),
            motive=personality_data.get('motive', 'sales'),
            background_story=personality_data.get('background_story', ''),
            expertise_areas=personality_data.get('expertise_areas', []),
            conversation_goals=personality_data.get('conversation_goals', []),
            response_length_preference=personality_data.get('response_length_preference', 'medium'),
            tone_adjustment_rules=personality_data.get('tone_adjustment_rules', {})
        )
        
        # Convert document integration
        doc_data = data.get('document_integration', {})
        document_integration = DocumentIntegration(
            required_document_types=doc_data.get('required_document_types', []),
            optional_document_types=doc_data.get('optional_document_types', []),
            document_tags=doc_data.get('document_tags', []),
            context_extraction_rules=doc_data.get('context_extraction_rules', {}),
            placeholder_mapping=doc_data.get('placeholder_mapping', {}),
            knowledge_base_priority=doc_data.get('knowledge_base_priority', 1)
        )
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            description=data.get('description', ''),
            version=data.get('version', '1.0'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
            stages=data.get('stages', []),
            stage_instructions=stage_instructions,
            nlp_extraction_rules=nlp_rules,
            analysis_rules=analysis_rules,
            llm_personality=llm_personality,
            document_integration=document_integration,
            max_call_duration=data.get('max_call_duration', 900),
            follow_up_delay_hours=data.get('follow_up_delay_hours', 24),
            retry_attempts=data.get('retry_attempts', 3),
            success_metrics=data.get('success_metrics', {}),
            quality_assurance_rules=data.get('quality_assurance_rules', {}),
            custom_settings=data.get('custom_settings', {}),
            tags=data.get('tags', []),
            is_active=data.get('is_active', True)
        )




