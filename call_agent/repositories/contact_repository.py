from typing import List, Optional, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from ..models.crm import Contact, ContactStatus

class ContactRepository(BaseRepository[Contact]):
    def get_collection_name(self) -> str:
        return "contacts"
    
    def from_dict(self, data: Dict[str, Any]) -> Contact:
        # Convert string status back to enum
        status_str = data.get('status', 'new')
        status = ContactStatus(status_str)
        
        # Convert string dates back to datetime
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        
        return Contact(
            id=data.get('id'),
            user_id=data.get('user_id'),  # Multi-tenant support
            phone_number=data['phone_number'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            company=data.get('company'),
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            tags=data.get('tags', []),
            custom_fields=data.get('custom_fields', {})
        )
    
    def find_by_phone_number(self, phone_number: str, user_id: str = None) -> Optional[Contact]:
        """Find contact by phone number for a specific user"""
        if user_id:
            contacts = self.find_by_field('user_id', user_id)
            for contact in contacts:
                if contact.phone_number == phone_number:
                    return contact
            return None
        else:
            return self.find_one_by_field('phone_number', phone_number)
    
    def find_by_status(self, status: ContactStatus, user_id: str = None) -> List[Contact]:
        """Find contacts by status for a specific user"""
        if user_id:
            contacts = self.find_by_field('user_id', user_id)
            return [contact for contact in contacts if contact.status == status]
        else:
            return self.find_by_field('status', status.value)
    
    def find_by_tag(self, tag: str, user_id: str = None) -> List[Contact]:
        """Find contacts by tag for a specific user"""
        if user_id:
            contacts = self.find_by_field('user_id', user_id)
        else:
            contacts = self.find_all()
        return [contact for contact in contacts if tag in contact.tags]
    
    def update_status(self, contact_id: str, status: ContactStatus) -> Optional[Contact]:
        """Update contact status"""
        contact = self.find_by_id(contact_id)
        if contact:
            contact.status = status
            contact.updated_at = datetime.now()
            return self.update(contact)
        return None
    
    def add_tag(self, contact_id: str, tag: str) -> Optional[Contact]:
        """Add tag to contact"""
        contact = self.find_by_id(contact_id)
        if contact and tag not in contact.tags:
            contact.tags.append(tag)
            contact.updated_at = datetime.now()
            return self.update(contact)
        return contact
    
    def remove_tag(self, contact_id: str, tag: str) -> Optional[Contact]:
        """Remove tag from contact"""
        contact = self.find_by_id(contact_id)
        if contact and tag in contact.tags:
            contact.tags.remove(tag)
            contact.updated_at = datetime.now()
            return self.update(contact)
        return contact
    
    def update_custom_field(self, contact_id: str, field: str, value: Any) -> Optional[Contact]:
        """Update custom field for contact"""
        contact = self.find_by_id(contact_id)
        if contact:
            contact.custom_fields[field] = value
            contact.updated_at = datetime.now()
            return self.update(contact)
        return None