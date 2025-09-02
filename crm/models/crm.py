from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

class ContactStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    QUALIFIED = "qualified"
    NOT_INTERESTED = "not_interested"
    FOLLOW_UP = "follow_up"

class CallStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"

class CampaignStage(Enum):
    INTRODUCTION = "introduction"
    NEEDS_ASSESSMENT = "needs_assessment"
    SOLUTION_PRESENTATION = "solution_presentation"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"

class CampaignPurpose(Enum):
    SALES = "sales"
    CUSTOMER_SUPPORT = "customer_support"
    SURVEY = "survey"
    LEAD_GENERATION = "lead_generation"
    APPOINTMENT_BOOKING = "appointment_booking"
    FEEDBACK_COLLECTION = "feedback_collection"

class CustomerPersonality(Enum):
    ANALYTICAL = "analytical"      # Data-driven, logical
    DRIVER = "driver"              # Fast-paced, results-oriented
    EXPRESSIVE = "expressive"      # Enthusiastic, relationship-focused
    AMIABLE = "amiable"            # Patient, supportive
    SKEPTICAL = "skeptical"        # Cautious, questioning
    OPTIMISTIC = "optimistic"      # Positive, opportunity-focused

class PreferredTiming(Enum):
    MORNING = "morning"            # 9 AM - 12 PM
    AFTERNOON = "afternoon"        # 12 PM - 5 PM
    EVENING = "evening"            # 5 PM - 8 PM
    WEEKEND = "weekend"            # Saturday/Sunday
    BUSINESS_HOURS = "business_hours"  # 9 AM - 6 PM
    FLEXIBLE = "flexible"          # Any time

@dataclass
class NLPExtractionRule:
    """Defines what data to extract from conversations"""
    field_name: str
    extraction_type: str  # "keyword", "sentiment", "entity", "pattern", "rating"
    keywords: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)  # Regex patterns
    required: bool = False
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

@dataclass
class StageBehavior:
    """Defines LLM behavior for each campaign stage"""
    stage: CampaignStage
    personality_traits: List[str] = field(default_factory=list)  # "professional", "friendly", "assertive"
    response_style: str = "conversational"  # "conversational", "professional", "casual", "formal"
    empathy_level: int = 5  # 1-10 scale
    assertiveness_level: int = 5  # 1-10 scale
    humor_level: int = 3  # 1-10 scale
    technical_depth: int = 5  # 1-10 scale
    call_to_action: Optional[str] = None

@dataclass
class CampaignTemplate:
    """Advanced campaign template with NLP and behavior configuration"""
    name: str
    purpose: CampaignPurpose
    description: str
    stages: List[CampaignStage]
    
    # NLP Configuration
    nlp_extraction_rules: List[NLPExtractionRule] = field(default_factory=list)
    sentiment_analysis: bool = True
    entity_recognition: bool = True
    intent_classification: bool = True
    
    # Stage-based LLM Behavior
    stage_behaviors: List[StageBehavior] = field(default_factory=list)
    
    # Script Templates
    script_templates: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Campaign Settings
    preferred_timing: List[PreferredTiming] = field(default_factory=list)
    customer_personality_targets: List[CustomerPersonality] = field(default_factory=list)
    max_call_duration: int = 900  # 15 minutes in seconds
    follow_up_delay_hours: int = 24
    
    # Custom Tags
    custom_tags: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'purpose': self.purpose.value,
            'description': self.description,
            'stages': [stage.value for stage in self.stages],
            'nlp_extraction_rules': [
                {
                    'field_name': rule.field_name,
                    'extraction_type': rule.extraction_type,
                    'keywords': rule.keywords,
                    'patterns': rule.patterns,
                    'required': rule.required,
                    'validation_rules': rule.validation_rules,
                    'description': rule.description
                } for rule in self.nlp_extraction_rules
            ],
            'sentiment_analysis': self.sentiment_analysis,
            'entity_recognition': self.entity_recognition,
            'intent_classification': self.intent_classification,
            'stage_behaviors': [
                {
                    'stage': behavior.stage.value,
                    'personality_traits': behavior.personality_traits,
                    'response_style': behavior.response_style,
                    'empathy_level': behavior.empathy_level,
                    'assertiveness_level': behavior.assertiveness_level,
                    'humor_level': behavior.humor_level,
                    'technical_depth': behavior.technical_depth,
                    'call_to_action': behavior.call_to_action
                } for behavior in self.stage_behaviors
            ],
            'script_templates': self.script_templates,
            'preferred_timing': [timing.value for timing in self.preferred_timing],
            'customer_personality_targets': [personality.value for personality in self.customer_personality_targets],
            'max_call_duration': self.max_call_duration,
            'follow_up_delay_hours': self.follow_up_delay_hours,
            'custom_tags': self.custom_tags
        }

@dataclass
class Contact:
    user_id: str  # Multi-tenant: belongs to a specific user
    phone_number: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    status: ContactStatus = ContactStatus.NEW
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    preferred_timing: List[PreferredTiming] = field(default_factory=list)
    personality_assessment: Optional[CustomerPersonality] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'company': self.company,
            'status': self.status.value,
            'tags': self.tags,
            'custom_fields': self.custom_fields,
            'preferred_timing': [timing.value for timing in self.preferred_timing],
            'personality_assessment': self.personality_assessment.value if self.personality_assessment else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class Conversation:
    user_id: str  # Multi-tenant: belongs to a specific user
    contact_id: str
    campaign_id: str
    call_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stage: CampaignStage = CampaignStage.INTRODUCTION
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    collected_data: Dict[str, Any] = field(default_factory=dict)
    sentiment_score: Optional[float] = None
    duration_seconds: Optional[int] = None
    nlp_insights: Dict[str, Any] = field(default_factory=dict)  # NLP analysis results
    stage_transitions: List[Dict[str, Any]] = field(default_factory=list)  # Track stage changes
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_transcript_entry(self, speaker: str, text: str, timestamp: float):
        self.transcript.append({
            'speaker': speaker,
            'text': text,
            'timestamp': timestamp
        })
        self.updated_at = datetime.now()
    
    def update_collected_data(self, key: str, value: Any):
        self.collected_data[key] = value
        self.updated_at = datetime.now()
    
    def add_nlp_insight(self, key: str, value: Any):
        self.nlp_insights[key] = value
        self.updated_at = datetime.now()
    
    def add_stage_transition(self, from_stage: CampaignStage, to_stage: CampaignStage, reason: str, timestamp: float):
        self.stage_transitions.append({
            'from_stage': from_stage.value,
            'to_stage': to_stage.value,
            'reason': reason,
            'timestamp': timestamp
        })
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'campaign_id': self.campaign_id,
            'call_id': self.call_id,
            'stage': self.stage.value,
            'transcript': self.transcript,
            'collected_data': self.collected_data,
            'sentiment_score': self.sentiment_score,
            'duration_seconds': self.duration_seconds,
            'nlp_insights': self.nlp_insights,
            'stage_transitions': self.stage_transitions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class Call:
    user_id: str  # Multi-tenant: belongs to a specific user
    contact_id: str
    campaign_id: str
    phone_number: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: CallStatus = CallStatus.SCHEDULED
    scheduled_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    notes: Optional[str] = None
    call_quality_score: Optional[float] = None  # 1-10 scale
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'campaign_id': self.campaign_id,
            'phone_number': self.phone_number,
            'status': self.status.value,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'recording_url': self.recording_url,
            'notes': self.notes,
            'call_quality_score': self.call_quality_score,
            'follow_up_required': self.follow_up_required,
            'follow_up_notes': self.follow_up_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class Campaign:
    user_id: str  # Multi-tenant: belongs to a specific user
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: Optional[str] = None
    purpose: CampaignPurpose = CampaignPurpose.SALES
    template_id: Optional[str] = None  # Reference to campaign template
    stages: List[CampaignStage] = field(default_factory=list)
    script_template: Dict[str, Any] = field(default_factory=dict)
    data_collection_fields: List[str] = field(default_factory=list)
    nlp_extraction_rules: List[NLPExtractionRule] = field(default_factory=list)
    stage_behaviors: List[StageBehavior] = field(default_factory=list)
    preferred_timing: List[PreferredTiming] = field(default_factory=list)
    customer_personality_targets: List[CustomerPersonality] = field(default_factory=list)
    max_call_duration: int = 900  # 15 minutes
    follow_up_delay_hours: int = 24
    custom_tags: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'purpose': self.purpose.value,
            'template_id': self.template_id,
            'stages': [stage.value for stage in self.stages],
            'script_template': self.script_template,
            'data_collection_fields': self.data_collection_fields,
            'nlp_extraction_rules': [
                {
                    'field_name': rule.field_name,
                    'extraction_type': rule.extraction_type,
                    'keywords': rule.keywords,
                    'patterns': rule.patterns,
                    'required': rule.required,
                    'validation_rules': rule.validation_rules,
                    'description': rule.description
                } for rule in self.nlp_extraction_rules
            ],
            'stage_behaviors': [
                {
                    'stage': behavior.stage.value,
                    'personality_traits': behavior.personality_traits,
                    'response_style': behavior.response_style,
                    'empathy_level': behavior.empathy_level,
                    'assertiveness_level': behavior.assertiveness_level,
                    'humor_level': behavior.humor_level,
                    'technical_depth': behavior.technical_depth,
                    'call_to_action': behavior.call_to_action
                } for behavior in self.stage_behaviors
            ],
            'preferred_timing': [timing.value for timing in self.preferred_timing],
            'customer_personality_targets': [personality.value for personality in self.customer_personality_targets],
            'max_call_duration': self.max_call_duration,
            'follow_up_delay_hours': self.follow_up_delay_hours,
            'custom_tags': self.custom_tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

@dataclass
class Document:
    """Company documents, policies, product info, and knowledge base"""
    user_id: str  # Multi-tenant: belongs to a specific user
    name: str
    content: str
    document_type: str  # "policy", "product_info", "faq", "script", "knowledge_base"
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'content': self.content,
            'document_type': self.document_type,
            'tags': self.tags,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }