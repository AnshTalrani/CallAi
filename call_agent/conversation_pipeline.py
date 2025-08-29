"""
Conversation Pipeline
Orchestrates the three-module system: NLP Extractor → Mid-Conversation Brain → Fine-tuned LLM
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import json

from .nlp_extractor import NLPExtractor, ExtractionRule, ExtractionType
from .mid_conversation_brain import MidConversationBrain, StrategicInstruction
from .finetuned_llm import FineTunedLLM, LLMContext, CampaignType, PersonalityType

@dataclass
class PipelineResult:
    user_input: str
    extracted_data: Dict[str, Any]
    strategic_instruction: StrategicInstruction
    llm_response: str
    response_quality_score: float
    processing_time: float
    pipeline_metadata: Dict[str, Any]

class ConversationPipeline:
    """Main pipeline orchestrating the three-module system"""
    
    def __init__(self):
        self.nlp_extractor = NLPExtractor()
        self.mid_conversation_brain = MidConversationBrain()
        self.finetuned_llm = FineTunedLLM()
        
        # Pipeline state
        self.conversation_history: List[Dict[str, Any]] = []
        self.extracted_data_history: List[Dict[str, Any]] = []
        self.pipeline_metadata: Dict[str, Any] = {}
        
    def setup_campaign(self, campaign_id: str, campaign_config: Dict[str, Any]):
        """Setup the pipeline for a specific campaign"""
        
        # Extract NLP rules from campaign config
        nlp_rules = self._extract_nlp_rules_from_campaign(campaign_config)
        self.nlp_extractor.add_campaign_rules(campaign_id, nlp_rules)
        
        # Store campaign configuration
        self.pipeline_metadata['campaign_id'] = campaign_id
        self.pipeline_metadata['campaign_config'] = campaign_config
        
        print(f"Pipeline setup complete for campaign: {campaign_id}")
    
    def process_user_input(self, 
                          user_input: str,
                          campaign_context: Dict[str, Any],
                          conversation_state: Dict[str, Any]) -> PipelineResult:
        """Process user input through the three-module pipeline"""
        
        start_time = time.time()
        
        try:
            # Step 1: NLP Extraction
            print("🔄 Step 1: NLP Extraction")
            campaign_id = self.pipeline_metadata.get('campaign_id', 'default')
            extracted_data = self.nlp_extractor.extract_from_text(user_input, campaign_id)
            
            # Store extracted data
            self.extracted_data_history.append(extracted_data)
            
            print(f"   Extracted: {len(extracted_data)} data points")
            
            # Step 2: Mid-Conversation Brain Analysis
            print("🧠 Step 2: Mid-Conversation Brain Analysis")
            strategic_instruction = self.mid_conversation_brain.analyze_conversation(
                user_input=user_input,
                extracted_data=extracted_data,
                campaign_context=campaign_context,
                conversation_state=conversation_state
            )
            
            print(f"   Primary Goal: {strategic_instruction.primary_goal}")
            print(f"   Tone: {strategic_instruction.tone_adjustment}")
            
            # Step 3: Fine-tuned LLM Response Generation
            print("🤖 Step 3: Fine-tuned LLM Response Generation")
            
            # Build LLM context
            llm_context = self._build_llm_context(
                user_input=user_input,
                extracted_data=extracted_data,
                strategic_instruction=strategic_instruction,
                campaign_context=campaign_context,
                conversation_state=conversation_state
            )
            
            # Generate response
            llm_response = self.finetuned_llm.generate_response(user_input, llm_context)
            
            # Score response quality
            response_quality_score = self.finetuned_llm.get_response_quality_score(llm_response, llm_context)
            
            # Update conversation history
            self.conversation_history.append({
                'user_input': user_input,
                'timestamp': time.time(),
                'stage': conversation_state.get('current_stage'),
                'extracted_data': extracted_data,
                'strategic_instruction': strategic_instruction.__dict__,
                'llm_response': llm_response,
                'response_quality_score': response_quality_score
            })
            
            processing_time = time.time() - start_time
            
            print(f"   Response Quality Score: {response_quality_score:.2f}")
            print(f"   Processing Time: {processing_time:.2f}s")
            
            return PipelineResult(
                user_input=user_input,
                extracted_data=extracted_data,
                strategic_instruction=strategic_instruction,
                llm_response=llm_response,
                response_quality_score=response_quality_score,
                processing_time=processing_time,
                pipeline_metadata={
                    'campaign_id': campaign_id,
                    'conversation_turn': len(self.conversation_history),
                    'total_extractions': len(self.extracted_data_history)
                }
            )
            
        except Exception as e:
            print(f"❌ Pipeline Error: {e}")
            # Return fallback result
            return self._create_fallback_result(user_input, start_time)
    
    def _extract_nlp_rules_from_campaign(self, campaign_config: Dict[str, Any]) -> List[ExtractionRule]:
        """Extract NLP extraction rules from campaign configuration"""
        rules = []
        
        # Extract rules from campaign template
        nlp_rules_config = campaign_config.get('nlp_extraction_rules', [])
        
        for rule_config in nlp_rules_config:
            rule = ExtractionRule(
                field_name=rule_config.get('field_name'),
                extraction_type=ExtractionType(rule_config.get('extraction_type', 'keyword')),
                keywords=rule_config.get('keywords', []),
                patterns=rule_config.get('patterns', []),
                required=rule_config.get('required', False),
                description=rule_config.get('description', ''),
                confidence_threshold=rule_config.get('confidence_threshold', 0.7)
            )
            rules.append(rule)
        
        # Add default rules if none provided
        if not rules:
            rules = self._get_default_extraction_rules()
        
        return rules
    
    def _get_default_extraction_rules(self) -> List[ExtractionRule]:
        """Get default extraction rules"""
        return [
            ExtractionRule(
                field_name="intent",
                extraction_type=ExtractionType.INTENT,
                required=False,
                description="User's intent or interest level"
            ),
            ExtractionRule(
                field_name="sentiment",
                extraction_type=ExtractionType.SENTIMENT,
                required=False,
                description="User's sentiment"
            ),
            ExtractionRule(
                field_name="pain_point",
                extraction_type=ExtractionType.KEYWORD,
                keywords=["problem", "challenge", "issue", "struggle", "difficulty", "frustration"],
                required=False,
                description="Customer's main challenge"
            ),
            ExtractionRule(
                field_name="budget_range",
                extraction_type=ExtractionType.PATTERN,
                patterns=[r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD)"],
                required=False,
                description="Customer's budget range"
            )
        ]
    
    def _build_llm_context(self,
                          user_input: str,
                          extracted_data: Dict[str, Any],
                          strategic_instruction: StrategicInstruction,
                          campaign_context: Dict[str, Any],
                          conversation_state: Dict[str, Any]) -> LLMContext:
        """Build context for the fine-tuned LLM"""
        
        # Determine campaign type
        campaign_type_str = campaign_context.get('campaign_type', 'sales').lower()
        campaign_type = CampaignType(campaign_type_str)
        
        # Determine personality type
        personality_str = strategic_instruction.tone_adjustment.lower().replace('_', '_')
        try:
            personality_type = PersonalityType(personality_str)
        except ValueError:
            personality_type = PersonalityType.PROFESSIONAL_FRIENDLY
        
        # Build contact info
        contact_info = {
            'name': campaign_context.get('contact_name', 'Unknown'),
            'company': campaign_context.get('contact_company', 'Unknown'),
            'current_stage': conversation_state.get('current_stage', 'Unknown')
        }
        
        # Get campaign script
        campaign_script = campaign_context.get('current_script', 'No script available')
        
        return LLMContext(
            campaign_type=campaign_type,
            personality_type=personality_type,
            strategic_instruction=strategic_instruction.__dict__,
            conversation_history=self.conversation_history[-5:],  # Last 5 turns
            extracted_data=extracted_data,
            campaign_script=campaign_script,
            contact_info=contact_info
        )
    
    def _create_fallback_result(self, user_input: str, start_time: float) -> PipelineResult:
        """Create fallback result when pipeline fails"""
        fallback_response = "I apologize, but I'm having trouble processing that right now. Could you please repeat?"
        
        return PipelineResult(
            user_input=user_input,
            extracted_data={},
            strategic_instruction=StrategicInstruction(
                primary_goal="continue_conversation",
                secondary_goals=[],
                tone_adjustment="professional_friendly",
                focus_areas=[],
                avoid_topics=[],
                next_questions=[],
                urgency_level=5,
                risk_level=3
            ),
            llm_response=fallback_response,
            response_quality_score=0.3,
            processing_time=time.time() - start_time,
            pipeline_metadata={'error': 'pipeline_failure'}
        )
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline performance"""
        return {
            'total_conversations': len(self.conversation_history),
            'total_extractions': len(self.extracted_data_history),
            'average_response_quality': sum(
                conv.get('response_quality_score', 0) for conv in self.conversation_history
            ) / max(len(self.conversation_history), 1),
            'campaign_id': self.pipeline_metadata.get('campaign_id'),
            'recent_performance': [
                {
                    'turn': conv.get('conversation_turn', i),
                    'quality_score': conv.get('response_quality_score', 0),
                    'extractions': len(conv.get('extracted_data', {}))
                }
                for i, conv in enumerate(self.conversation_history[-5:], 1)
            ]
        }
    
    def reset_pipeline(self):
        """Reset pipeline state"""
        self.conversation_history.clear()
        self.extracted_data_history.clear()
        self.pipeline_metadata.clear()
        print("Pipeline state reset")
    
    def export_conversation_data(self, filepath: str):
        """Export conversation data for analysis"""
        data = {
            'conversation_history': self.conversation_history,
            'extracted_data_history': self.extracted_data_history,
            'pipeline_metadata': self.pipeline_metadata,
            'summary': self.get_pipeline_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Conversation data exported to: {filepath}")