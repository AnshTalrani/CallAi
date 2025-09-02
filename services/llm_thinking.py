import os
import json
import requests
import ollama
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_community.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOllama
from typing import Dict, Any, List, Optional

class LLMThinker:
    def __init__(self):
        print("Initializing LLM...")
        
        # Get configuration from environment variables
        self.model_name = os.environ.get('LLM_MODEL_NAME', 'phi3')
        self.base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # Initialize Ollama client
        self.client = ollama.Client(host=self.base_url)
        
        # Verify model is available
        try:
            list_response = self.client.list()
            available_models = []
            if hasattr(list_response, 'models'):
                # Newer ollama versions (>=0.5.x)
                available_models = [m.model for m in list_response.models]
            elif isinstance(list_response, dict):
                # Back-compat with dict response shape
                available_models = [m.get('name', '') for m in list_response.get('models', [])]
            else:
                # Fallback: try to iterate directly
                try:
                    available_models = [m.model for m in list_response]
                except Exception:
                    pass

            if not any(name.startswith(self.model_name) for name in available_models):
                print(f"Model '{self.model_name}' not found on Ollama – attempting to pull…")
                self.client.pull(self.model_name)
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
            raise
        
        # Initialize ChatOllama for LangChain
        self.chat = ChatOllama(base_url=self.base_url, model=self.model_name)
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Template context storage
        self.current_campaign_context = None
        self.current_document_context = None
        self.current_template_personality = None
        
        # Create tools
        wikipedia = WikipediaAPIWrapper()
        search = DuckDuckGoSearchAPIWrapper()
        
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
                name="CampaignContext",
                func=self._get_campaign_context,
                description="Get current campaign context, stage information, and available documents. Use when you need to understand the current conversation context."
            ),
            Tool(
                name="DocumentSearch",
                func=self._search_campaign_documents,
                description="Search for relevant documents and information within the current campaign context. Input should be a search query."
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

    def get_response(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Get a response from the LLM with the given text input and optional context"""
        print("\nThinking...")
        try:
            # Prepare the prompt with any context
            prompt = self._prepare_prompt(text, context)
            
            # Generate response using Ollama
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False
            )
            
            response_text = response.get('response', '').strip()
            print(f"\nAssistant: {response_text}")
            return response_text
                
        except Exception as e:
            error_msg = f"Error in get_response: {str(e)}"
            print(error_msg)
            return "I apologize, but I encountered an error. Could you rephrase your question?"
    
    def _prepare_prompt(self, text, context=None):
        """Prepare the prompt with any additional context"""
        prompt = text
        
        # Add context if available
        if context:
            prompt = f"Context: {context}\n\nQuestion: {text}"
            
        return prompt
    
    def get_response_with_context(self, user_input: str, campaign_context: Dict[str, Any] = None, 
                                 conversation_context: Dict[str, Any] = None) -> str:
        """Get LLM response with comprehensive context including documents and template analysis"""
        print("\nThinking with context...")
        
        try:
            # Process analysis rules if template exists
            analysis_actions = []
            if campaign_context and campaign_context.get('analysis_rules'):
                analysis_actions = self._process_analysis_rules(
                    campaign_context['analysis_rules'], 
                    user_input, 
                    conversation_context
                )
            
            # Prepare the full context
            context = {
                'user_input': user_input,
                'campaign': campaign_context or {},
                'conversation': conversation_context or {},
                'analysis_actions': [str(action) for action in analysis_actions]  # Convert actions to strings
            }
            
            # Format the prompt with context
            context_str = json.dumps(context, indent=2, default=str)
            prompt = f"Context: {context_str}\n\nUser: {user_input}\n\nAssistant:"
            
            # Get response with context
            response = self.get_response(prompt, context)
            
            # Process any actions in the response
            if analysis_actions:
                response = self._process_response_actions(response, analysis_actions)
                
            return response
            
        except Exception as e:
            error_msg = f"Error in get_response_with_context: {str(e)}"
            print(error_msg)
            return "I apologize, but I encountered an error while processing your request."
    
    def _process_analysis_rules(self, analysis_rules: List[Any], user_input: str, 
                               conversation_context: Dict[str, Any]) -> List[str]:
        """Process analysis rules and return applicable actions"""
        actions = []
        
        for rule in analysis_rules:
            if not rule.is_active:
                continue
            
            # Simple rule evaluation (can be enhanced with more sophisticated NLP)
            conditions_met = self._evaluate_rule_conditions(rule, user_input, conversation_context)
            
            if conditions_met:
                actions.extend(rule.actions)
        
        return actions
    
    def _evaluate_rule_conditions(self, rule: Any, user_input: str, 
                                 conversation_context: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        conditions = rule.conditions
        user_input_lower = user_input.lower()
        
        # Check keywords
        if 'keywords' in conditions:
            keywords = conditions['keywords']
            if not any(keyword.lower() in user_input_lower for keyword in keywords):
                return False
        
        # Check sentiment (simplified - would need actual sentiment analysis)
        if 'sentiment_score' in conditions:
            sentiment_condition = conditions['sentiment_score']
            # This is a placeholder - would need actual sentiment analysis
            # For now, we'll assume neutral sentiment
            pass
        
        # Check min_turns
        if 'min_turns' in conditions:
            min_turns = conditions['min_turns']
            # This would need to be tracked in conversation context
            # For now, we'll assume conditions are met
            pass
        
        return True
    
    def build_comprehensive_prompt(self, user_input: str, campaign_context: Dict[str, Any] = None,
                                  conversation_context: Dict[str, Any] = None) -> str:
        """Build comprehensive prompt with all context including documents and template personality"""
        
        prompt_parts = []
        
        # Campaign context
        if campaign_context:
            campaign = campaign_context.get('campaign')
            if campaign:
                prompt_parts.append(f"Campaign: {campaign.name}")
                prompt_parts.append(f"Campaign Purpose: {campaign.purpose.value}")
                if campaign.description:
                    prompt_parts.append(f"Campaign Description: {campaign.description}")
            
            # Template personality context
            template = campaign_context.get('template')
            if template:
                personality = template.llm_personality
                prompt_parts.append(f"\nAgent Personality:")
                prompt_parts.append(f"Name: {personality.name}")
                prompt_parts.append(f"Traits: {', '.join([trait.value for trait in personality.personality_traits])}")
                prompt_parts.append(f"Communication Style: {personality.communication_style.value}")
                prompt_parts.append(f"Empathy Level: {personality.empathy_level}/10")
                prompt_parts.append(f"Assertiveness Level: {personality.assertiveness_level}/10")
                prompt_parts.append(f"Technical Depth: {personality.technical_depth}/10")
                prompt_parts.append(f"Motive: {personality.motive}")
                if personality.background_story:
                    prompt_parts.append(f"Background: {personality.background_story}")
                if personality.expertise_areas:
                    prompt_parts.append(f"Expertise: {', '.join(personality.expertise_areas)}")
                if personality.conversation_goals:
                    prompt_parts.append(f"Goals: {', '.join(personality.conversation_goals)}")
            
            # Stage instructions context
            stage_instructions = campaign_context.get('stage_instructions')
            if stage_instructions:
                prompt_parts.append(f"\nCurrent Stage Instructions:")
                prompt_parts.append(f"Primary Objective: {stage_instructions.primary_objective}")
                if stage_instructions.secondary_objectives:
                    prompt_parts.append(f"Secondary Objectives: {', '.join(stage_instructions.secondary_objectives)}")
                if stage_instructions.key_questions:
                    prompt_parts.append(f"Key Questions: {', '.join(stage_instructions.key_questions)}")
                if stage_instructions.success_criteria:
                    prompt_parts.append(f"Success Criteria: {', '.join(stage_instructions.success_criteria)}")
            
            # Document context
            document_context = campaign_context.get('document_context')
            if document_context:
                prompt_parts.append(f"\nRelevant Knowledge Base:\n{document_context}")
            
            # Document placeholders
            document_placeholders = campaign_context.get('document_placeholders', {})
            if document_placeholders:
                placeholder_info = "\n".join([f"{key}: {value}" for key, value in document_placeholders.items()])
                prompt_parts.append(f"\nAvailable Information:\n{placeholder_info}")
        
        # Conversation context
        if conversation_context:
            current_stage = conversation_context.get('current_stage')
            if current_stage:
                prompt_parts.append(f"\nCurrent Stage: {current_stage}")
            
            collected_data = conversation_context.get('collected_data', {})
            if collected_data:
                data_info = "\n".join([f"{key}: {value}" for key, value in collected_data.items()])
                prompt_parts.append(f"\nCollected Information:\n{data_info}")
        
        # User input
        prompt_parts.append(f"\nUser Input: {user_input}")
        
        # Template-based instructions
        if campaign_context and campaign_context.get('template'):
            template = campaign_context['template']
            personality = template.llm_personality
            
            prompt_parts.append(f"""
Instructions:
- You are {personality.name} with the following personality: {', '.join([trait.value for trait in personality.personality_traits])}
- Communication style: {personality.communication_style.value}
- Motive: {personality.motive}
- Response length: {personality.response_length_preference}
- Respond naturally as if you're having a real conversation
- Use the available knowledge base and information to provide accurate responses
- If you don't have specific information, be honest about it
- Adapt your response based on the current stage and collected information
- Follow the stage instructions and objectives provided
""")
        else:
            # Fallback instructions
            prompt_parts.append("""
Instructions:
- Respond naturally as if you're having a real conversation
- Use the available knowledge base and information to provide accurate responses
- Keep your response conversational and under 2-3 sentences
- If you don't have specific information, be honest about it
- Adapt your response based on the current stage and collected information
""")
        
        return "\n".join(prompt_parts)
    
    def _get_campaign_context(self, query: str = "") -> str:
        """Tool function to get current campaign context"""
        # This would need to be set by the CallAgent when calling the LLM
        if hasattr(self, 'current_campaign_context'):
            return f"Current campaign context: {self.current_campaign_context}"
        else:
            return "No campaign context available. This tool should be called from within a campaign."
    
    def _search_campaign_documents(self, query: str) -> str:
        """Tool function to search campaign documents"""
        # This would need to be set by the CallAgent when calling the LLM
        if hasattr(self, 'current_document_context'):
            if query.lower() in self.current_document_context.lower():
                return f"Found relevant information: {self.current_document_context}"
            else:
                return f"No specific information found for '{query}' in current documents."
        else:
            return "No document context available. This tool should be called from within a campaign."

if __name__ == "__main__":
    # Example usage
    thinker = LLMThinker()
    while True:
        user_input = input("\nEnter your message (or 'quit' to exit): ")
        if user_input.lower() in ['quit', 'exit', 'goodbye', 'bye']:
            break
        response = thinker.get_response(user_input) 