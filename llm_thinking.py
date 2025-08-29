import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

# Load environment variables from .env file
load_dotenv()
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain.agents import initialize_agent, AgentType

class LLMThinker:
    def __init__(self):
        print("Initializing LLM...")
        
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
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create general tools
        wikipedia = WikipediaAPIWrapper()
        search = DuckDuckGoSearchAPIWrapper()
        
        # Create call agent specific tools
        def extract_contact_info(text):
            """Extract contact information from conversation"""
            # This would integrate with your CRM system
            return {"action": "extract_contact_info", "text": text}
        
        def update_call_status(status):
            """Update the current call status"""
            return {"action": "update_call_status", "status": status}
        
        def schedule_follow_up(date, notes):
            """Schedule a follow-up call"""
            return {"action": "schedule_follow_up", "date": date, "notes": notes}
        
        def record_objection(objection_type, details):
            """Record customer objection for analysis"""
            return {"action": "record_objection", "type": objection_type, "details": details}
        
        tools = [
            Tool(
                name="Wikipedia",
                func=wikipedia.run,
                description="Useful for queries about historical facts, general knowledge, and detailed information. Input should be a search query."
            ),
            Tool(
                name="DuckDuckGo",
                func=search.run,
                description="Useful for queries about current events, news, and real-time information. Input should be a search query."
            ),
            Tool(
                name="ExtractContactInfo",
                func=extract_contact_info,
                description="Extract contact information, preferences, or requirements mentioned in the conversation"
            ),
            Tool(
                name="UpdateCallStatus",
                func=update_call_status,
                description="Update the current call status (in_progress, completed, scheduled, no_answer, etc.)"
            ),
            Tool(
                name="ScheduleFollowUp",
                func=schedule_follow_up,
                description="Schedule a follow-up call or appointment with the contact"
            ),
            Tool(
                name="RecordObjection",
                func=record_objection,
                description="Record customer objections for analysis and training"
            )
        ]
        
        # Initialize the agent with a simpler setup
        self.agent_executor = initialize_agent(
            tools=tools,
            llm=self.chat,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        print("LLM ready!")

    def get_call_agent_instructions(self, campaign_type: str = "sales", stage: str = "introduction", personality_config: dict = None) -> str:
        """Get specialized instructions for call agent behavior"""
        
        base_instructions = """
You are a professional call agent conducting outbound calls. Your role is to:
- Be polite, professional, and respectful
- Speak clearly and at a moderate pace
- Listen actively and respond appropriately
- Stay focused on the campaign objectives
- Handle objections gracefully
- Collect required information systematically
- Never be pushy or aggressive
- Respect if someone wants to end the call
- Keep responses concise (2-3 sentences max)
- Use natural conversation flow
"""
        
        # Add personality configuration if provided
        if personality_config:
            personality_prompt = f"""
PERSONALITY CONFIGURATION:
Name: {personality_config.get('name', 'Alex')}
Tone: {personality_config.get('tone', 'professional_friendly')}
Speaking Pace: {personality_config.get('speaking_pace', 'moderate')}
Empathy Level: {personality_config.get('empathy_level', 8)}/10
Assertiveness Level: {personality_config.get('assertiveness_level', 5)}/10
Humor Level: {personality_config.get('humor_level', 3)}/10
Technical Depth: {personality_config.get('technical_depth', 4)}/10

BEHAVIORAL GUIDELINES:
- Use your name '{personality_config.get('name', 'Alex')}' when introducing yourself
- Maintain a {personality_config.get('tone', 'professional_friendly')} tone throughout
- Speak at a {personality_config.get('speaking_pace', 'moderate')} pace
- Show appropriate empathy based on your empathy level
- Be appropriately assertive based on your assertiveness level
- Use humor sparingly and appropriately based on your humor level
- Adjust technical detail based on your technical depth setting
"""
            base_instructions += personality_prompt
        
        campaign_specific = {
            "sales": """
SALES CAMPAIGN SPECIFIC:
- Focus on understanding customer needs
- Present relevant solutions
- Handle objections with empathy
- Ask qualifying questions
- Look for buying signals
- Be consultative, not pushy
""",
            "support": """
SUPPORT CAMPAIGN SPECIFIC:
- Show empathy for customer issues
- Focus on problem resolution
- Provide clear next steps
- Ensure customer satisfaction
- Document issues accurately
""",
            "survey": """
SURVEY CAMPAIGN SPECIFIC:
- Be neutral and objective
- Ask questions clearly
- Respect time constraints
- Thank participants
- Don't try to sell anything
""",
            "appointment": """
APPOINTMENT CAMPAIGN SPECIFIC:
- Be flexible with scheduling
- Confirm details clearly
- Send confirmation information
- Handle rescheduling requests
"""
        }
        
        stage_specific = {
            "introduction": """
INTRODUCTION STAGE:
- Introduce yourself and company clearly
- State the purpose of the call
- Ask if it's a good time to talk
- Be brief and respectful of their time
""",
            "needs_assessment": """
NEEDS ASSESSMENT STAGE:
- Ask open-ended questions
- Listen for pain points
- Understand their current situation
- Identify decision-making process
""",
            "solution_presentation": """
SOLUTION PRESENTATION STAGE:
- Present relevant benefits
- Address specific needs mentioned
- Use examples and stories
- Ask for feedback
""",
            "objection_handling": """
OBJECTION HANDLING STAGE:
- Acknowledge their concerns
- Provide relevant information
- Ask clarifying questions
- Don't argue or be defensive
""",
            "closing": """
CLOSING STAGE:
- Summarize key points
- Ask for next steps
- Confirm action items
- Thank them for their time
"""
        }
        
        return base_instructions + campaign_specific.get(campaign_type, "") + stage_specific.get(stage, "")

    def get_response(self, text, campaign_type: str = None, stage: str = None, context: dict = None, personality_config: dict = None):
        print("\nThinking...")
        try:
            # If this is a call agent context, use specialized instructions
            if campaign_type and stage:
                instructions = self.get_call_agent_instructions(campaign_type, stage, personality_config)
                enhanced_prompt = f"{instructions}\n\nUser input: {text}\n\nContext: {context or {}}\n\nResponse:"
                response = self.chat.invoke(enhanced_prompt)
                cleaned = ' '.join(response.content.replace('\n', ' ').split())
            else:
                # Use original agent for general conversation
                response = self.agent_executor.invoke({"input": text})
                cleaned = ' '.join(response['output'].replace('\n', ' ').split())
            
            print(f"Assistant: {cleaned}")
            return cleaned
        except Exception as e:
            error_msg = "I apologize, but I encountered an error. Could you rephrase your question?"
            print(f"Assistant: {error_msg}")
            return error_msg

if __name__ == "__main__":
    # Example usage
    thinker = LLMThinker()
    while True:
        user_input = input("\nEnter your message (or 'quit' to exit): ")
        if user_input.lower() in ['quit', 'exit', 'goodbye', 'bye']:
            break
        response = thinker.get_response(user_input) 