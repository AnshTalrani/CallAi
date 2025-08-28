from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

class ContactStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    CONVERTED = "converted"
    LOST = "lost"

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

@dataclass
class Contact:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    phone_number: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    status: ContactStatus = ContactStatus.NEW
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'company': self.company,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags,
            'custom_fields': self.custom_fields
        }

@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str
    campaign_id: str
    call_id: str
    stage: CampaignStage = CampaignStage.INTRODUCTION
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    collected_data: Dict[str, Any] = field(default_factory=dict)
    sentiment_score: Optional[float] = None
    duration_seconds: Optional[int] = None
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'campaign_id': self.campaign_id,
            'call_id': self.call_id,
            'stage': self.stage.value,
            'transcript': self.transcript,
            'collected_data': self.collected_data,
            'sentiment_score': self.sentiment_score,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class Call:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str
    campaign_id: str
    phone_number: str
    status: CallStatus = CallStatus.SCHEDULED
    scheduled_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    recording_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class Campaign:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    stages: List[CampaignStage] = field(default_factory=list)
    script_template: Dict[str, Any] = field(default_factory=dict)
    data_collection_fields: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stages': [stage.value for stage in self.stages],
            'script_template': self.script_template,
            'data_collection_fields': self.data_collection_fields,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }