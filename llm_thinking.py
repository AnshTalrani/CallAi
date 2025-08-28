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

    def get_response(self, text):
        print("\nThinking...")
        try:
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