from typing import Optional, List, Dict, Any
from crm.models.user import User, UserStatus, UserPlan
from crm.repositories.user_repository import UserRepository
from crm.repositories.campaign_repository import CampaignRepository
from crm.repositories.contact_repository import ContactRepository
from crm.repositories.conversation_repository import ConversationRepository
from crm.repositories.call_repository import CallRepository

class UserManager:
    """Manages user operations and multi-tenant data access"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.campaign_repo = CampaignRepository()
        self.contact_repo = ContactRepository()
        self.conversation_repo = ConversationRepository()
        self.call_repo = CallRepository()
    
    def register_user(self, email: str, password: str, first_name: str = None, 
                     last_name: str = None, company_name: str = None) -> User:
        """Register a new user"""
        return self.user_repo.create_user(email, password, first_name, last_name, company_name)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        return self.user_repo.authenticate_user(email, password)
    
    def authenticate_by_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate user by API key"""
        return self.user_repo.find_by_api_key(api_key)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.user_repo.find_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.user_repo.find_by_email(email)
    
    def update_user_profile(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user profile information"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'company_name', 'phone_number', 'phone_numbers', 'settings']
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = self._get_current_datetime()
        return self.user_repo.update(user)
    
    def update_user_plan(self, user_id: str, plan: UserPlan) -> Optional[User]:
        """Update user's subscription plan"""
        return self.user_repo.update_user_plan(user_id, plan)
    
    def update_user_status(self, user_id: str, status: UserStatus) -> Optional[User]:
        """Update user's account status"""
        return self.user_repo.update_user_status(user_id, status)
    
    def change_password(self, user_id: str, new_password: str) -> Optional[User]:
        """Change user's password"""
        return self.user_repo.change_password(user_id, new_password)
    
    def update_user(self, user: User) -> Optional[User]:
        """Update user record (pass-through for compatibility)."""
        return self.user_repo.update(user)

    def regenerate_api_key(self, user_id: str) -> Optional[User]:
        """Regenerate user's API key"""
        return self.user_repo.regenerate_api_key(user_id)
    
    def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard data for a user"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {}
        
        # Get user's data counts
        campaigns = self.campaign_repo.find_by_field('user_id', user_id)
        contacts = self.contact_repo.find_by_field('user_id', user_id)
        conversations = self.conversation_repo.find_by_field('user_id', user_id)
        calls = self.call_repo.find_by_field('user_id', user_id)
        
        # Count by status
        active_campaigns = len([c for c in campaigns if c.is_active])
        new_contacts = len([c for c in contacts if c.status.value == 'new'])
        completed_calls = len([c for c in calls if c.status.value == 'completed'])
        
        return {
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'company_name': user.company_name,
                'plan': user.plan.value,
                'status': user.status.value
            },
            'stats': {
                'total_campaigns': len(campaigns),
                'active_campaigns': active_campaigns,
                'total_contacts': len(contacts),
                'new_contacts': new_contacts,
                'total_conversations': len(conversations),
                'total_calls': len(calls),
                'completed_calls': completed_calls
            }
        }
    
    def get_user_campaigns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all campaigns for a user"""
        campaigns = self.campaign_repo.find_by_field('user_id', user_id)
        return [campaign.to_dict() for campaign in campaigns]
    
    def get_user_contacts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all contacts for a user"""
        contacts = self.contact_repo.find_by_field('user_id', user_id)
        return [contact.to_dict() for contact in contacts]
    
    def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        conversations = self.conversation_repo.find_by_field('user_id', user_id)
        return [conversation.to_dict() for conversation in conversations]
    
    def get_user_calls(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all calls for a user"""
        calls = self.call_repo.find_by_field('user_id', user_id)
        return [call.to_dict() for call in calls]
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a user (for GDPR compliance)"""
        try:
            # Delete all user's data
            campaigns = self.campaign_repo.find_by_field('user_id', user_id)
            contacts = self.contact_repo.find_by_field('user_id', user_id)
            conversations = self.conversation_repo.find_by_field('user_id', user_id)
            calls = self.call_repo.find_by_field('user_id', user_id)
            
            for campaign in campaigns:
                self.campaign_repo.delete(campaign.id)
            
            for contact in contacts:
                self.contact_repo.delete(contact.id)
            
            for conversation in conversations:
                self.conversation_repo.delete(conversation.id)
            
            for call in calls:
                self.call_repo.delete(call.id)
            
            # Finally delete the user
            return self.user_repo.delete(user_id)
        except Exception:
            return False
    
    def get_user_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {}
        
        # Get plan limits
        plan_limits = {
            UserPlan.FREE: {'campaigns': 3, 'contacts': 100, 'calls_per_month': 50},
            UserPlan.BASIC: {'campaigns': 10, 'contacts': 1000, 'calls_per_month': 500},
            UserPlan.PROFESSIONAL: {'campaigns': 50, 'contacts': 10000, 'calls_per_month': 5000},
            UserPlan.ENTERPRISE: {'campaigns': -1, 'contacts': -1, 'calls_per_month': -1}  # Unlimited
        }
        
        limits = plan_limits.get(user.plan, {})
        
        # Get current usage
        campaigns = self.campaign_repo.find_by_field('user_id', user_id)
        contacts = self.contact_repo.find_by_field('user_id', user_id)
        calls = self.call_repo.find_by_field('user_id', user_id)
        
        return {
            'plan': user.plan.value,
            'limits': limits,
            'usage': {
                'campaigns': len(campaigns),
                'contacts': len(contacts),
                'calls': len(calls)
            }
        }
    
    def _get_current_datetime(self):
        """Get current datetime"""
        from datetime import datetime
        return datetime.now()