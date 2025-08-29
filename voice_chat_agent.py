import os
from dotenv import load_dotenv
from voice_recognition import VoiceRecognizer, select_audio_device
from text_to_speech import TTSGenerator
from call_agent.conversation_pipeline import ConversationPipeline

# Load environment variables from .env file
load_dotenv()

class VoiceAgent:
    def __init__(self, device_id=1):
        print("\nInitializing Voice Chat Agent...")
        self.recognizer = VoiceRecognizer(device_id)
        self.tts = TTSGenerator(default_voice='af_heart')
        self.pipeline = ConversationPipeline()
        
        # Minimal default campaign setup so this standalone works
        default_campaign_config = {
            'name': 'Ad-hoc Voice Chat',
            'purpose': 'sales',
            'stages': ['introduction', 'needs_assessment', 'solution_presentation', 'objection_handling', 'closing'],
            'script_template': {
                'introduction': {'script': 'Greet and ask how you can help.'},
                'needs_assessment': {'script': 'Ask about challenges and goals.'},
                'solution_presentation': {'script': 'Present tailored benefits.'},
                'objection_handling': {'script': 'Acknowledge and address concerns.'},
                'closing': {'script': 'Summarize and propose next steps.'}
            },
            'nlp_extraction_rules': []
        }
        self.pipeline.setup_campaign("adhoc_voice_chat", default_campaign_config)
        
        print("Voice Chat Agent initialization complete!")

    def cleanup(self):
        """Clean up all resources."""
        if hasattr(self, 'recognizer'):
            self.recognizer.cleanup()
        if hasattr(self, 'tts'):
            self.tts.cleanup()

    def chat_loop(self):
        print("\nVoice Chat Agent ready! Press Ctrl+C to exit")
        print("Make sure LM Studio is running and the API is active!")
        print("Speak clearly into your microphone. You should see █ when voice is detected.")
        
        try:
            current_stage = 'introduction'
            while True:
                try:
                    # Record and transcribe audio
                    audio_data = self.recognizer.record_audio()
                    
                    if audio_data is not None and len(audio_data) > 0:
                        # Convert speech to text
                        text = self.recognizer.transcribe_audio(audio_data)
                        print(f"\nYou said: {text}")
                        
                        if text.lower() in ['quit', 'exit', 'goodbye', 'bye']:
                            print("\nGoodbye!")
                            break
                        
                        if not text.strip():
                            print("\nNo speech detected, trying again...")
                            continue
                        
                        # Build minimal contexts
                        campaign_context = {
                            'campaign_name': 'Ad-hoc Voice Chat',
                            'campaign_type': 'sales',
                            'contact_name': 'Caller',
                            'contact_company': 'Unknown',
                            'current_script': f"Script for {current_stage} stage"
                        }
                        conversation_state = {
                            'current_stage': current_stage,
                            'collected_data': {},
                            'call_context': {},
                            'timestamp': 0
                        }
                        
                        # Process via pipeline
                        result = self.pipeline.process_user_input(
                            user_input=text,
                            campaign_context=campaign_context,
                            conversation_state=conversation_state
                        )
                        
                        # Optionally advance stage if strategy suggests
                        if result.strategic_instruction.primary_goal == 'transition_stage':
                            stage_order = ['introduction', 'needs_assessment', 'solution_presentation', 'objection_handling', 'closing']
                            try:
                                idx = stage_order.index(current_stage)
                                if idx + 1 < len(stage_order):
                                    current_stage = stage_order[idx + 1]
                            except ValueError:
                                pass
                        
                        # Convert response to speech
                        print("\nSpeaking...")
                        self.tts.generate_speech(result.llm_response)
                    else:
                        print("\nNo audio recorded, trying again...")
                    
                except Exception as e:
                    print(f"\nError in conversation loop: {e}")
                    print("Restarting recording...")
                
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"\nError: {e}")
            print("Make sure LM Studio is running and the API is active!")
        finally:
            self.cleanup()

def main():
    device_id = select_audio_device()
    
    agent = VoiceAgent(
        device_id=device_id       # Selected device
    )
    agent.chat_loop()

if __name__ == "__main__":
    main() 