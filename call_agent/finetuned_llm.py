"""
Fine-tuned LLM Module
Receives strategic instructions and generates appropriate responses
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

# Load environment variables
load_dotenv()

class CampaignType(Enum):
    SALES = "sales"
    SUPPORT = "support"
    SURVEY = "survey"
    APPOINTMENT = "appointment"

class PersonalityType(Enum):
    PROFESSIONAL_FRIENDLY = "professional_friendly"
    EMPATHETIC_UNDERSTANDING = "empathetic_understanding"
    ENTHUSIASTIC_ENGAGING = "enthusiastic_engaging"
    CALM_REASSURING = "calm_reassuring"
    CONSULTATIVE = "consultative"

@dataclass
class LLMContext:
    campaign_type: CampaignType
    personality_type: PersonalityType
    strategic_instruction: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    extracted_data: Dict[str, Any]
    campaign_script: str
    contact_info: Dict[str, Any]

class FineTunedLLM:
    """Fine-tuned LLM for call agent responses"""
    
    def __init__(self):
        # Get configuration from environment variables
        model_name = os.environ.get('LLM_MODEL_NAME', 'meta-llama-3.1-8b-instruct')
        api_base = os.environ.get('LLM_API_BASE', 'http://localhost:1234/v1')
        api_key = os.environ.get('LLM_API_KEY', 'not-needed')
        
        self.chat = ChatOpenAI(
            model_name=model_name,
            openai_api_base=api_base,
            openai_api_key=api_key,
            streaming=True
        )
        
        # Campaign-specific instruction templates
        self.campaign_instructions = {
            CampaignType.SALES: self._get_sales_instructions,
            CampaignType.SUPPORT: self._get_support_instructions,
            CampaignType.SURVEY: self._get_survey_instructions,
            CampaignType.APPOINTMENT: self._get_appointment_instructions
        }
        
        # Personality-specific instruction templates
        self.personality_instructions = {
            PersonalityType.PROFESSIONAL_FRIENDLY: self._get_professional_friendly_instructions,
            PersonalityType.EMPATHETIC_UNDERSTANDING: self._get_empathetic_instructions,
            PersonalityType.ENTHUSIASTIC_ENGAGING: self._get_enthusiastic_instructions,
            PersonalityType.CALM_REASSURING: self._get_calm_instructions,
            PersonalityType.CONSULTATIVE: self._get_consultative_instructions
        }
    
    def generate_response(self, user_input: str, context: LLMContext) -> str:
        """Generate response based on strategic instructions and context"""
        
        # Build comprehensive prompt
        prompt = self._build_prompt(user_input, context)
        
        try:
            # Generate response
            response = self.chat.invoke(prompt)
            cleaned_response = ' '.join(response.content.replace('\n', ' ').split())
            
            return cleaned_response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._get_fallback_response(context)
    
    def _build_prompt(self, user_input: str, context: LLMContext) -> str:
        """Build comprehensive prompt for the LLM"""
        
        # Get campaign-specific instructions
        campaign_instructions = self.campaign_instructions[context.campaign_type](context)
        
        # Get personality-specific instructions
        personality_instructions = self.personality_instructions[context.personality_type](context)
        
        # Build strategic instruction section
        strategic_section = self._build_strategic_section(context.strategic_instruction)
        
        # Build context section
        context_section = self._build_context_section(context)
        
        # Build conversation history section
        history_section = self._build_history_section(context.conversation_history)
        
        # Build extracted data section
        data_section = self._build_data_section(context.extracted_data)
        
        # Combine all sections
        prompt = f"""
{campaign_instructions}

{personality_instructions}

{strategic_section}

{context_section}

{history_section}

{data_section}

CAMPAIGN SCRIPT:
{context.campaign_script}

USER INPUT:
{user_input}

Generate a natural, conversational response that follows the strategic instructions and maintains the specified personality. Keep your response concise (2-3 sentences) and focused on the primary goal.

RESPONSE:
"""
        
        return prompt
    
    def _get_sales_instructions(self, context: LLMContext) -> str:
        """Get sales-specific instructions"""
        return """
SALES CAMPAIGN INSTRUCTIONS:
You are conducting a sales call. Your primary objectives are:
- Understand customer needs and pain points
- Present relevant solutions and benefits
- Handle objections professionally
- Qualify leads and identify buying signals
- Guide the conversation toward closing

Key behaviors:
- Ask qualifying questions
- Listen for pain points and opportunities
- Present benefits that address specific needs
- Handle objections with empathy and facts
- Look for buying signals and respond appropriately
- Be consultative, not pushy
"""
    
    def _get_support_instructions(self, context: LLMContext) -> str:
        """Get support-specific instructions"""
        return """
SUPPORT CAMPAIGN INSTRUCTIONS:
You are conducting a customer support call. Your primary objectives are:
- Understand and empathize with customer issues
- Provide accurate and helpful solutions
- Ensure customer satisfaction
- Document issues and resolutions
- Escalate when necessary

Key behaviors:
- Show empathy for customer frustrations
- Ask clarifying questions to understand the issue
- Provide clear, step-by-step solutions
- Confirm understanding and satisfaction
- Document the interaction accurately
"""
    
    def _get_survey_instructions(self, context: LLMContext) -> str:
        """Get survey-specific instructions"""
        return """
SURVEY CAMPAIGN INSTRUCTIONS:
You are conducting a survey call. Your primary objectives are:
- Collect accurate survey responses
- Maintain neutrality and objectivity
- Respect participant time and preferences
- Thank participants for their time
- Complete all required questions

Key behaviors:
- Ask questions clearly and neutrally
- Don't influence responses
- Respect if someone wants to skip questions
- Thank participants for their time
- Don't try to sell anything
"""
    
    def _get_appointment_instructions(self, context: LLMContext) -> str:
        """Get appointment-specific instructions"""
        return """
APPOINTMENT CAMPAIGN INSTRUCTIONS:
You are scheduling appointments. Your primary objectives are:
- Find suitable appointment times
- Confirm appointment details clearly
- Handle rescheduling requests
- Provide confirmation information
- Ensure participant satisfaction

Key behaviors:
- Be flexible with scheduling options
- Confirm all appointment details clearly
- Provide confirmation information
- Handle rescheduling requests professionally
- Ensure participant has all necessary information
"""
    
    def _get_professional_friendly_instructions(self, context: LLMContext) -> str:
        """Get professional-friendly personality instructions"""
        return """
PERSONALITY: Professional and Friendly
- Maintain a professional tone while being warm and approachable
- Use polite and respectful language
- Show genuine interest in the customer
- Balance professionalism with friendliness
- Be confident but not arrogant
"""
    
    def _get_empathetic_instructions(self, context: LLMContext) -> str:
        """Get empathetic personality instructions"""
        return """
PERSONALITY: Empathetic and Understanding
- Show genuine empathy for customer concerns
- Use understanding and supportive language
- Acknowledge customer feelings and frustrations
- Be patient and compassionate
- Focus on emotional connection and trust
"""
    
    def _get_enthusiastic_instructions(self, context: LLMContext) -> str:
        """Get enthusiastic personality instructions"""
        return """
PERSONALITY: Enthusiastic and Engaging
- Show genuine enthusiasm for the product/service
- Use energetic and positive language
- Be engaging and interactive
- Show excitement about opportunities
- Maintain high energy while being professional
"""
    
    def _get_calm_instructions(self, context: LLMContext) -> str:
        """Get calm personality instructions"""
        return """
PERSONALITY: Calm and Reassuring
- Maintain a calm, steady tone
- Use reassuring and comforting language
- Be patient and unhurried
- Provide reassurance when needed
- Create a sense of stability and trust
"""
    
    def _get_consultative_instructions(self, context: LLMContext) -> str:
        """Get consultative personality instructions"""
        return """
PERSONALITY: Consultative and Expert
- Position yourself as a trusted advisor
- Use expert knowledge to provide value
- Ask insightful questions
- Provide strategic recommendations
- Focus on long-term relationship building
"""
    
    def _build_strategic_section(self, strategic_instruction: Dict[str, Any]) -> str:
        """Build strategic instruction section"""
        return f"""
STRATEGIC INSTRUCTIONS:
Primary Goal: {strategic_instruction.get('primary_goal', 'continue_conversation')}
Secondary Goals: {', '.join(strategic_instruction.get('secondary_goals', []))}
Tone Adjustment: {strategic_instruction.get('tone_adjustment', 'professional_friendly')}
Focus Areas: {', '.join(strategic_instruction.get('focus_areas', []))}
Topics to Avoid: {', '.join(strategic_instruction.get('avoid_topics', []))}
Next Questions: {', '.join(strategic_instruction.get('next_questions', []))}
Urgency Level: {strategic_instruction.get('urgency_level', 5)}/10
Risk Level: {strategic_instruction.get('risk_level', 3)}/10
"""
    
    def _build_context_section(self, context: LLMContext) -> str:
        """Build context section"""
        contact_info = context.contact_info
        return f"""
CONTEXT:
Campaign Type: {context.campaign_type.value}
Contact Name: {contact_info.get('name', 'Unknown')}
Contact Company: {contact_info.get('company', 'Unknown')}
Current Stage: {contact_info.get('current_stage', 'Unknown')}
"""
    
    def _build_history_section(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Build conversation history section"""
        if not conversation_history:
            return "CONVERSATION HISTORY: None"
        
        history_text = "CONVERSATION HISTORY:\n"
        for i, turn in enumerate(conversation_history[-5:], 1):  # Last 5 turns
            history_text += f"Turn {i}: {turn.get('user_input', '')}\n"
        
        return history_text
    
    def _build_data_section(self, extracted_data: Dict[str, Any]) -> str:
        """Build extracted data section"""
        if not extracted_data:
            return "EXTRACTED DATA: None"
        
        data_text = "EXTRACTED DATA:\n"
        for field, data in extracted_data.items():
            if isinstance(data, dict):
                value = data.get('value', 'Unknown')
                confidence = data.get('confidence', 0)
                data_text += f"- {field}: {value} (confidence: {confidence:.2f})\n"
            else:
                data_text += f"- {field}: {data}\n"
        
        return data_text
    
    def _get_fallback_response(self, context: LLMContext) -> str:
        """Get fallback response when LLM fails"""
        fallback_responses = {
            CampaignType.SALES: "I understand. Could you tell me more about your current situation?",
            CampaignType.SUPPORT: "I apologize for the technical issue. Let me help you with that.",
            CampaignType.SURVEY: "Thank you for your time. Let me continue with the next question.",
            CampaignType.APPOINTMENT: "I understand. Let me help you find a better time."
        }
        
        return fallback_responses.get(context.campaign_type, "I understand. How can I help you?")
    
    def get_response_quality_score(self, response: str, context: LLMContext) -> float:
        """Score the quality of a response (0-1)"""
        score = 0.5  # Base score
        
        # Check response length (should be 2-3 sentences)
        sentences = response.split('.')
        if 2 <= len(sentences) <= 4:
            score += 0.2
        
        # Check if response addresses primary goal
        primary_goal = context.strategic_instruction.get('primary_goal', '')
        if primary_goal in response.lower():
            score += 0.2
        
        # Check for appropriate tone
        tone = context.strategic_instruction.get('tone_adjustment', '')
        if tone in response.lower():
            score += 0.1
        
        return min(score, 1.0)