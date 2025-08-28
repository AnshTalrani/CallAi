from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"

class UserPlan(Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

@dataclass
class User:
    email: str
    password_hash: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    status: UserStatus = UserStatus.ACTIVE
    plan: UserPlan = UserPlan.FREE
    settings: Dict[str, Any] = field(default_factory=dict)
    api_key: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'email': self.email,
            'password_hash': self.password_hash,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'phone_number': self.phone_number,
            'status': self.status.value,
            'plan': self.plan.value,
            'settings': self.settings,
            'api_key': self.api_key,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    @property
    def full_name(self) -> str:
        """Get the full name of the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login_at = datetime.now()
        self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """Check if the user account is active"""
        return self.status == UserStatus.ACTIVE
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access a specific feature based on their plan"""
        plan_features = {
            UserPlan.FREE: ['basic_crm', 'limited_campaigns', 'basic_analytics'],
            UserPlan.BASIC: ['basic_crm', 'unlimited_campaigns', 'basic_analytics', 'email_support'],
            UserPlan.PROFESSIONAL: ['advanced_crm', 'unlimited_campaigns', 'advanced_analytics', 'priority_support', 'api_access'],
            UserPlan.ENTERPRISE: ['enterprise_crm', 'unlimited_campaigns', 'enterprise_analytics', 'dedicated_support', 'api_access', 'custom_integrations']
        }
        
        return feature in plan_features.get(self.plan, [])