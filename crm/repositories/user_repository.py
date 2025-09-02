from typing import Optional, List
from .base_repository import BaseRepository
from ..models.user import User, UserStatus, UserPlan
import uuid
import hashlib
import secrets

class UserRepository(BaseRepository[User]):
    """Repository for user management"""
    
    def get_collection_name(self) -> str:
        return "users"
    
    def from_dict(self, data: dict) -> User:
        """Convert dictionary to User instance"""
        from ..models.user import UserStatus, UserPlan
        
        # Convert string enums back to enum instances
        status = UserStatus(data.get('status', 'active'))
        plan = UserPlan(data.get('plan', 'free'))
        
        # Support both phone_number (legacy) and phone_numbers (new)
        phone_number = data.get('phone_number')
        phone_numbers = data.get('phone_numbers', [])
        if phone_number and not phone_numbers:
            phone_numbers = [phone_number]
        
        return User(
            id=data.get('id'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            company_name=data.get('company_name'),
            phone_number=phone_number,
            phone_numbers=phone_numbers,
            status=status,
            plan=plan,
            settings=data.get('settings', {}),
            api_key=data.get('api_key'),
            created_at=self._parse_datetime(data.get('created_at')),
            updated_at=self._parse_datetime(data.get('updated_at')),
            last_login_at=self._parse_datetime(data.get('last_login_at'))
        )
    
    def create_user(self, email: str, password: str, first_name: str = None, 
                   last_name: str = None, company_name: str = None) -> User:
        """Create a new user with hashed password"""
        # Check if user already exists
        existing_user = self.find_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Generate API key
        api_key = self._generate_api_key()
        
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            api_key=api_key
        )
        
        return self.create(user)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.find_by_email(email)
        if not user:
            return None
        
        if not user.is_active():
            return None
        
        if self._verify_password(password, user.password_hash):
            user.update_last_login()
            self.update(user)
            return user
        
        return None
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        return self.find_one_by_field('email', email)
    
    def find_by_api_key(self, api_key: str) -> Optional[User]:
        """Find user by API key"""
        return self.find_one_by_field('api_key', api_key)
    
    def update_user_plan(self, user_id: str, plan: UserPlan) -> Optional[User]:
        """Update user's subscription plan"""
        user = self.find_by_id(user_id)
        if not user:
            return None
        
        user.plan = plan
        user.updated_at = self._get_current_datetime()
        return self.update(user)
    
    def update_user_status(self, user_id: str, status: UserStatus) -> Optional[User]:
        """Update user's account status"""
        user = self.find_by_id(user_id)
        if not user:
            return None
        
        user.status = status
        user.updated_at = self._get_current_datetime()
        return self.update(user)
    
    def regenerate_api_key(self, user_id: str) -> Optional[User]:
        """Regenerate user's API key"""
        user = self.find_by_id(user_id)
        if not user:
            return None
        
        user.api_key = self._generate_api_key()
        user.updated_at = self._get_current_datetime()
        return self.update(user)
    
    def change_password(self, user_id: str, new_password: str) -> Optional[User]:
        """Change user's password"""
        user = self.find_by_id(user_id)
        if not user:
            return None
        
        user.password_hash = self._hash_password(new_password)
        user.updated_at = self._get_current_datetime()
        return self.update(user)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)
    
    def _parse_datetime(self, datetime_str: str):
        """Parse datetime string to datetime object"""
        from datetime import datetime
        if datetime_str:
            return datetime.fromisoformat(datetime_str)
        return None
    
    def _get_current_datetime(self):
        """Get current datetime"""
        from datetime import datetime
        return datetime.now()