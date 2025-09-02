from typing import List, Optional, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from ..models.campaign_template import CampaignTemplate

class CampaignTemplateRepository(BaseRepository[CampaignTemplate]):
    def get_collection_name(self) -> str:
        return "campaign_templates"
    
    def from_dict(self, data: Dict[str, Any]) -> CampaignTemplate:
        return CampaignTemplate.from_dict(data)
    
    def find_by_name(self, name: str) -> Optional[CampaignTemplate]:
        """Find template by name"""
        templates = self.find_all()
        for template in templates:
            if template.name.lower() == name.lower():
                return template
        return None
    
    def find_by_tags(self, tags: List[str]) -> List[CampaignTemplate]:
        """Find templates by tags"""
        templates = self.find_all()
        matching_templates = []
        
        for template in templates:
            if template.is_active and any(tag in template.tags for tag in tags):
                matching_templates.append(template)
        
        return matching_templates
    
    def find_active_templates(self) -> List[CampaignTemplate]:
        """Find all active templates"""
        templates = self.find_all()
        return [template for template in templates if template.is_active]
    
    def find_by_motive(self, motive: str) -> List[CampaignTemplate]:
        """Find templates by LLM motive"""
        templates = self.find_all()
        matching_templates = []
        
        for template in templates:
            if (template.is_active and 
                template.llm_personality.motive.lower() == motive.lower()):
                matching_templates.append(template)
        
        return matching_templates
    
    def find_by_personality_traits(self, traits: List[str]) -> List[CampaignTemplate]:
        """Find templates by personality traits"""
        templates = self.find_all()
        matching_templates = []
        
        for template in templates:
            if not template.is_active:
                continue
            
            template_traits = [trait.value for trait in template.llm_personality.personality_traits]
            if any(trait in template_traits for trait in traits):
                matching_templates.append(template)
        
        return matching_templates
    
    def search_templates(self, query: str) -> List[CampaignTemplate]:
        """Search templates by name, description, or tags"""
        templates = self.find_all()
        matching_templates = []
        query_lower = query.lower()
        
        for template in templates:
            if not template.is_active:
                continue
            
            # Search in name
            if query_lower in template.name.lower():
                matching_templates.append(template)
                continue
            
            # Search in description
            if query_lower in template.description.lower():
                matching_templates.append(template)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in template.tags):
                matching_templates.append(template)
                continue
            
            # Search in personality traits
            traits = [trait.value.lower() for trait in template.llm_personality.personality_traits]
            if query_lower in traits:
                matching_templates.append(template)
                continue
        
        return matching_templates
    
    def get_prebuilt_templates(self) -> List[CampaignTemplate]:
        """Get system pre-built templates"""
        # This would typically return templates that come with the system
        # For now, we'll return templates with specific tags
        return self.find_by_tags(['prebuilt', 'system'])
    
    def find_templates_by_stage_count(self, stage_count: int) -> List[CampaignTemplate]:
        """Find templates with specific number of stages"""
        templates = self.find_all()
        matching_templates = []
        
        for template in templates:
            if template.is_active and len(template.stages) == stage_count:
                matching_templates.append(template)
        
        return matching_templates
    
    def find_templates_by_duration(self, max_duration: int) -> List[CampaignTemplate]:
        """Find templates with specific max call duration"""
        templates = self.find_all()
        matching_templates = []
        
        for template in templates:
            if template.is_active and template.max_call_duration <= max_duration:
                matching_templates.append(template)
        
        return matching_templates
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get statistics about templates"""
        templates = self.find_all()
        active_templates = [t for t in templates if t.is_active]
        
        # Count by motive
        motives = {}
        for template in active_templates:
            motive = template.llm_personality.motive
            motives[motive] = motives.get(motive, 0) + 1
        
        # Count by personality traits
        traits = {}
        for template in active_templates:
            for trait in template.llm_personality.personality_traits:
                trait_name = trait.value
                traits[trait_name] = traits.get(trait_name, 0) + 1
        
        # Count by stage count
        stage_counts = {}
        for template in active_templates:
            stage_count = len(template.stages)
            stage_counts[stage_count] = stage_counts.get(stage_count, 0) + 1
        
        return {
            'total_templates': len(templates),
            'active_templates': len(active_templates),
            'motives': motives,
            'personality_traits': traits,
            'stage_counts': stage_counts
        }




