from typing import List, Optional, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from ..models.crm import Call, CallStatus

class CallRepository(BaseRepository[Call]):
    def get_collection_name(self) -> str:
        return "calls"
    
    def from_dict(self, data: Dict[str, Any]) -> Call:
        # Convert string status back to enum
        status_str = data.get('status', 'scheduled')
        status = CallStatus(status_str)
        
        # Convert string dates back to datetime
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        scheduled_time = datetime.fromisoformat(data['scheduled_time']) if data.get('scheduled_time') else None
        start_time = datetime.fromisoformat(data['start_time']) if data.get('start_time') else None
        end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else None
        
        return Call(
            id=data.get('id'),
            user_id=data.get('user_id'),  # Multi-tenant support
            contact_id=data['contact_id'],
            campaign_id=data['campaign_id'],
            phone_number=data['phone_number'],
            status=status,
            scheduled_time=scheduled_time,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=data.get('duration_seconds'),
            recording_url=data.get('recording_url'),
            notes=data.get('notes'),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def find_by_contact_id(self, contact_id: str, user_id: str = None) -> List[Call]:
        """Find calls by contact ID for a specific user"""
        if user_id:
            calls = self.find_by_field('user_id', user_id)
            return [call for call in calls if call.contact_id == contact_id]
        else:
            return self.find_by_field('contact_id', contact_id)
    
    def find_by_campaign_id(self, campaign_id: str, user_id: str = None) -> List[Call]:
        """Find calls by campaign ID for a specific user"""
        if user_id:
            calls = self.find_by_field('user_id', user_id)
            return [call for call in calls if call.campaign_id == campaign_id]
        else:
            return self.find_by_field('campaign_id', campaign_id)
    
    def find_by_status(self, status: CallStatus, user_id: str = None) -> List[Call]:
        """Find calls by status for a specific user"""
        if user_id:
            calls = self.find_by_field('user_id', user_id)
            return [call for call in calls if call.status == status]
        else:
            return self.find_by_field('status', status.value)
    
    def find_scheduled_calls(self, user_id: str = None) -> List[Call]:
        """Find all scheduled calls for a specific user"""
        return self.find_by_status(CallStatus.SCHEDULED, user_id)
    
    def find_completed_calls(self, user_id: str = None) -> List[Call]:
        """Find all completed calls for a specific user"""
        return self.find_by_status(CallStatus.COMPLETED, user_id)
    
    def find_failed_calls(self, user_id: str = None) -> List[Call]:
        """Find all failed calls for a specific user"""
        return self.find_by_status(CallStatus.FAILED, user_id)
    
    def update_status(self, call_id: str, status: CallStatus) -> Optional[Call]:
        """Update call status"""
        call = self.find_by_id(call_id)
        if call:
            call.status = status
            call.updated_at = datetime.now()
            return self.update(call)
        return None
    
    def start_call(self, call_id: str) -> Optional[Call]:
        """Mark call as started"""
        call = self.find_by_id(call_id)
        if call:
            call.status = CallStatus.IN_PROGRESS
            call.start_time = datetime.now()
            call.updated_at = datetime.now()
            return self.update(call)
        return None
    
    def end_call(self, call_id: str, duration_seconds: int = None, recording_url: str = None) -> Optional[Call]:
        """Mark call as ended"""
        call = self.find_by_id(call_id)
        if call:
            call.status = CallStatus.COMPLETED
            call.end_time = datetime.now()
            if duration_seconds:
                call.duration_seconds = duration_seconds
            if recording_url:
                call.recording_url = recording_url
            call.updated_at = datetime.now()
            return self.update(call)
        return None
    
    def fail_call(self, call_id: str, reason: str = None) -> Optional[Call]:
        """Mark call as failed"""
        call = self.find_by_id(call_id)
        if call:
            call.status = CallStatus.FAILED
            call.end_time = datetime.now()
            if reason:
                call.notes = reason
            call.updated_at = datetime.now()
            return self.update(call)
        return None
    
    def add_notes(self, call_id: str, notes: str) -> Optional[Call]:
        """Add notes to call"""
        call = self.find_by_id(call_id)
        if call:
            if call.notes:
                call.notes += f"\n{notes}"
            else:
                call.notes = notes
            call.updated_at = datetime.now()
            return self.update(call)
        return None
    
    def get_call_summary(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of call"""
        call = self.find_by_id(call_id)
        if not call:
            return None
        
        return {
            'id': call.id,
            'contact_id': call.contact_id,
            'campaign_id': call.campaign_id,
            'phone_number': call.phone_number,
            'status': call.status.value,
            'duration_seconds': call.duration_seconds,
            'recording_url': call.recording_url,
            'notes': call.notes,
            'scheduled_time': call.scheduled_time.isoformat() if call.scheduled_time else None,
            'start_time': call.start_time.isoformat() if call.start_time else None,
            'end_time': call.end_time.isoformat() if call.end_time else None,
            'created_at': call.created_at.isoformat(),
            'updated_at': call.updated_at.isoformat()
        }