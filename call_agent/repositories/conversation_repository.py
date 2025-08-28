from typing import List, Optional, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from ..models.crm import Conversation, CampaignStage

class ConversationRepository(BaseRepository[Conversation]):
    def get_collection_name(self) -> str:
        return "conversations"
    
    def from_dict(self, data: Dict[str, Any]) -> Conversation:
        # Convert string stage back to enum
        stage_str = data.get('stage', 'introduction')
        stage = CampaignStage(stage_str)
        
        # Convert string dates back to datetime
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        
        return Conversation(
            id=data.get('id'),
            contact_id=data['contact_id'],
            campaign_id=data['campaign_id'],
            call_id=data['call_id'],
            stage=stage,
            transcript=data.get('transcript', []),
            collected_data=data.get('collected_data', {}),
            sentiment_score=data.get('sentiment_score'),
            duration_seconds=data.get('duration_seconds'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def find_by_contact_id(self, contact_id: str) -> List[Conversation]:
        """Find conversations by contact ID"""
        return self.find_by_field('contact_id', contact_id)
    
    def find_by_campaign_id(self, campaign_id: str) -> List[Conversation]:
        """Find conversations by campaign ID"""
        return self.find_by_field('campaign_id', campaign_id)
    
    def find_by_call_id(self, call_id: str) -> Optional[Conversation]:
        """Find conversation by call ID"""
        return self.find_one_by_field('call_id', call_id)
    
    def find_by_stage(self, stage: CampaignStage) -> List[Conversation]:
        """Find conversations by stage"""
        return self.find_by_field('stage', stage.value)
    
    def update_stage(self, conversation_id: str, stage: CampaignStage) -> Optional[Conversation]:
        """Update conversation stage"""
        conversation = self.find_by_id(conversation_id)
        if conversation:
            conversation.stage = stage
            conversation.updated_at = datetime.now()
            return self.update(conversation)
        return None
    
    def add_transcript_entry(self, conversation_id: str, speaker: str, text: str, timestamp: float) -> Optional[Conversation]:
        """Add transcript entry to conversation"""
        conversation = self.find_by_id(conversation_id)
        if conversation:
            conversation.add_transcript_entry(speaker, text, timestamp)
            return self.update(conversation)
        return None
    
    def update_collected_data(self, conversation_id: str, key: str, value: Any) -> Optional[Conversation]:
        """Update collected data in conversation"""
        conversation = self.find_by_id(conversation_id)
        if conversation:
            conversation.update_collected_data(key, value)
            return self.update(conversation)
        return None
    
    def update_sentiment_score(self, conversation_id: str, sentiment_score: float) -> Optional[Conversation]:
        """Update sentiment score for conversation"""
        conversation = self.find_by_id(conversation_id)
        if conversation:
            conversation.sentiment_score = sentiment_score
            conversation.updated_at = datetime.now()
            return self.update(conversation)
        return None
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of conversation"""
        conversation = self.find_by_id(conversation_id)
        if not conversation:
            return None
        
        return {
            'id': conversation.id,
            'contact_id': conversation.contact_id,
            'campaign_id': conversation.campaign_id,
            'stage': conversation.stage.value,
            'duration_seconds': conversation.duration_seconds,
            'sentiment_score': conversation.sentiment_score,
            'collected_data': conversation.collected_data,
            'transcript_length': len(conversation.transcript),
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat()
        }