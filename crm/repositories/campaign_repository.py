from typing import List, Optional, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from ..models.crm import Campaign, CampaignStage, CampaignPurpose

class CampaignRepository(BaseRepository[Campaign]):
    def get_collection_name(self) -> str:
        return "campaigns"
    
    def from_dict(self, data: Dict[str, Any]) -> Campaign:
        # Convert string stages back to enums
        stages = [CampaignStage(stage) for stage in data.get('stages', [])]
        
        # Convert string dates back to datetime
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        
        return Campaign(
            id=data.get('id'),
            user_id=data.get('user_id'),  # Multi-tenant support
            name=data['name'],
            description=data.get('description'),
            purpose=CampaignPurpose(data.get('purpose', 'sales')) if data.get('purpose') else None,
            template_id=data.get('template_id'),  # Include template_id
            stages=stages,
            script_template=data.get('script_template', {}),
            data_collection_fields=data.get('data_collection_fields', []),
            nlp_extraction_rules=data.get('nlp_extraction_rules', []),
            stage_behaviors=data.get('stage_behaviors', []),
            preferred_timing=data.get('preferred_timing', []),
            customer_personality_targets=data.get('customer_personality_targets', []),
            max_call_duration=data.get('max_call_duration', 900),
            follow_up_delay_hours=data.get('follow_up_delay_hours', 24),
            custom_tags=data.get('custom_tags', {}),
            created_at=created_at,
            updated_at=updated_at,
            is_active=data.get('is_active', True)
        )
    
    def find_active_campaigns(self, user_id: str = None) -> List[Campaign]:
        """Find all active campaigns for a specific user"""
        if user_id:
            campaigns = self.find_by_field('user_id', user_id)
        else:
            campaigns = self.find_all()
        return [campaign for campaign in campaigns if campaign.is_active]
    
    def find_by_name(self, name: str, user_id: str = None) -> Optional[Campaign]:
        """Find campaign by name for a specific user"""
        if user_id:
            campaigns = self.find_by_field('user_id', user_id)
            for campaign in campaigns:
                if campaign.name == name:
                    return campaign
            return None
        else:
            return self.find_one_by_field('name', name)
    
    def activate_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Activate a campaign"""
        campaign = self.find_by_id(campaign_id)
        if campaign:
            campaign.is_active = True
            campaign.updated_at = datetime.now()
            return self.update(campaign)
        return None
    
    def deactivate_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Deactivate a campaign"""
        campaign = self.find_by_id(campaign_id)
        if campaign:
            campaign.is_active = False
            campaign.updated_at = datetime.now()
            return self.update(campaign)
        return None
    
    def update_script_template(self, campaign_id: str, script_template: Dict[str, Any]) -> Optional[Campaign]:
        """Update campaign script template"""
        campaign = self.find_by_id(campaign_id)
        if campaign:
            campaign.script_template = script_template
            campaign.updated_at = datetime.now()
            return self.update(campaign)
        return None
    
    def add_data_collection_field(self, campaign_id: str, field: str) -> Optional[Campaign]:
        """Add data collection field to campaign"""
        campaign = self.find_by_id(campaign_id)
        if campaign and field not in campaign.data_collection_fields:
            campaign.data_collection_fields.append(field)
            campaign.updated_at = datetime.now()
            return self.update(campaign)
        return campaign
    
    def remove_data_collection_field(self, campaign_id: str, field: str) -> Optional[Campaign]:
        """Remove data collection field from campaign"""
        campaign = self.find_by_id(campaign_id)
        if campaign and field in campaign.data_collection_fields:
            campaign.data_collection_fields.remove(field)
            campaign.updated_at = datetime.now()
            return self.update(campaign)
        return campaign
    
    def get_campaign_summary(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of campaign"""
        campaign = self.find_by_id(campaign_id)
        if not campaign:
            return None
        
        return {
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'stages': [stage.value for stage in campaign.stages],
            'data_collection_fields': campaign.data_collection_fields,
            'is_active': campaign.is_active,
            'created_at': campaign.created_at.isoformat(),
            'updated_at': campaign.updated_at.isoformat()
        }