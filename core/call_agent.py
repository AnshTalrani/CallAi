import time
import threading
from typing import Optional, Dict, Any, List
from datetime import datetime
import sounddevice as sd
import numpy as np
import wave
import os

from services.voice_recognition import VoiceRecognizer
from services.text_to_speech import TTSGenerator
from langchain_pipeline import CallLangChainPipeline
import os

# Dynamically select telephony backend based on env var TELEPHONY_BACKEND.
_TELEPHONY_BACKEND = os.getenv("TELEPHONY_BACKEND", "freepbx").lower()
from telephony.freepbx_integration import FreePBXIntegration as TelephonyBackend

from crm.models.crm import Contact, Call, CallStatus, CampaignStage, ContactStatus
from crm.repositories.contact_repository import ContactRepository
from crm.repositories.conversation_repository import ConversationRepository
from core.campaign_manager import CampaignManager

class CallAgent:
    """Main call agent that handles voice calls with CRM integration"""
    
    def __init__(self, user=None, device_id: int = 1, sample_rate: int = 16000):
        print("\nInitializing Call Agent...")
        
        # Store user context for multi-tenant support
        self.user = user
        
        # Initialize voice components
        self.recognizer = VoiceRecognizer(device_id)
        # Legacy components kept for recording & playback; generation now via LangChain pipeline
        self.tts = TTSGenerator(default_voice='af_heart')
        self.pipeline = CallLangChainPipeline()
        
        # Initialize repositories
        self.contact_repo = ContactRepository()
        self.conversation_repo = ConversationRepository()
        
        # Initialize campaign manager with user context
        self.campaign_manager = CampaignManager(user=user)
        
        # Initialize telephony backend
        # Telephony backend (FreePBX AMI)
        pbx_host = os.environ.get('FREEPBX_HOST', '127.0.0.1')
        pbx_port = int(os.environ.get('FREEPBX_AMI_PORT', 5038))
        pbx_user = os.environ.get('FREEPBX_AMI_USER', 'admin')
        pbx_pass = os.environ.get('FREEPBX_AMI_PASS', 'amp111')
        self.telephony = TelephonyBackend(pbx_host, pbx_port, pbx_user, pbx_pass)
        # Backwards-compat alias (existing code uses self.asterisk_integration)
        self.asterisk_integration = self.telephony
        
        # Call state
        self.current_call: Optional[Call] = None
        self.current_conversation: Optional[Any] = None
        self.current_contact: Optional[Contact] = None
        self.current_campaign: Optional[Any] = None
        
        # Audio settings
        self.sample_rate = sample_rate
        self.is_recording = False
        self.recording_thread = None
        
        # Call context
        self.call_context: Dict[str, Any] = {}
        
        print("Call Agent initialization complete!")
    
    def cleanup(self):
        """Clean up all resources"""
        if hasattr(self, 'recognizer'):
            self.recognizer.cleanup()
        if hasattr(self, 'tts'):
            self.tts.cleanup()
        if self.is_recording:
            self.stop_recording()
    
    def start_direct_call(self, phone_number: str, from_number: str | None = None) -> bool:
        """Originate a one-off call without requiring CRM context."""
        channel = self.asterisk_integration.originate_call(
            from_number=from_number or "anonymous",
            to_number=phone_number,
            context="public",
            extension=phone_number,
        )
        return bool(channel)

    def start_call(self, contact_id: str, campaign_id: str, phone_number: str, from_number: str = None) -> bool:
        """Start a new call using Asterisk"""
        try:
            # Get contact and campaign with user validation
            contact = self.contact_repo.find_by_id(contact_id)
            if not contact:
                print(f"Contact {contact_id} not found")
                return False
            
            # Verify contact belongs to current user
            if self.user and contact.user_id != self.user.id:
                print(f"Contact {contact_id} does not belong to current user")
                return False
            
            campaign = self.campaign_manager.campaign_repo.find_by_id(campaign_id)
            if not campaign:
                print(f"Campaign {campaign_id} not found")
                return False
            
            # Verify campaign belongs to current user
            if self.user and campaign.user_id != self.user.id:
                print(f"Campaign {campaign_id} does not belong to current user")
                return False
            
            # Create call record with user context
            call = Call(
                user_id=self.user.id if self.user else contact.user_id,
                contact_id=contact_id,
                campaign_id=campaign_id,
                phone_number=phone_number,
                status=CallStatus.IN_PROGRESS,
                start_time=datetime.now()
            )
            
            # Create conversation record with user context
            conversation = self.conversation_repo.create(
                self.conversation_repo.from_dict({
                    'user_id': self.user.id if self.user else contact.user_id,
                    'contact_id': contact_id,
                    'campaign_id': campaign_id,
                    'call_id': call.id,
                    'stage': CampaignStage.INTRODUCTION.value
                })
            )
            
            # Set current state
            self.current_call = call
            self.current_conversation = conversation
            self.current_contact = contact
            self.current_campaign = campaign
            
            # Initialize call context from campaign or use defaults
            campaign_context = campaign.script_template.get('call_context', {})
            self.call_context = {
                'agent_name': campaign_context.get('agent_name', 'Sarah'),
                'company_name': campaign_context.get('company_name', 'TechCorp'),
                'contact_name': f"{contact.first_name or 'there'}",
                'product_name': campaign_context.get('product_name', 'Business Solution Pro'),
                'available_times': campaign_context.get('available_times', 'tomorrow at 2 PM or Friday at 10 AM')
            }
            
            print(f"Call started with {contact.first_name or 'contact'} at {phone_number}")
            print(f"Campaign: {campaign.name}")
            
            # Use user's selected phone number as caller ID (from_number)
            if not from_number:
                from_number = self.user.phone_numbers[0] if self.user and self.user.phone_numbers else self.user.phone_number
            # Originate call via Asterisk
            channel = self.asterisk_integration.originate_call(
                from_number=from_number,
                to_number=phone_number,
                context='default',
                extension=phone_number
            )
            if not channel:
                print(f"Asterisk failed to originate call from {from_number} to {phone_number}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error starting call: {e}")
            return False
    
    def end_call(self, status: CallStatus = CallStatus.COMPLETED, notes: str = None) -> bool:
        """End the current call"""
        if not self.current_call:
            print("No active call to end")
            return False
        
        try:
            # Update call status
            self.current_call.status = status
            self.current_call.end_time = datetime.now()
            self.current_call.notes = notes
            
            if self.current_call.start_time and self.current_call.end_time:
                duration = self.current_call.end_time - self.current_call.start_time
                self.current_call.duration_seconds = int(duration.total_seconds())
            
            # Update conversation duration
            if self.current_conversation:
                self.current_conversation.duration_seconds = self.current_call.duration_seconds
                self.conversation_repo.update(self.current_conversation)
            
            # Update contact status based on call outcome
            if self.current_contact:
                if status == CallStatus.COMPLETED:
                    self.current_contact.status = ContactStatus.CONTACTED
                elif status == CallStatus.NO_ANSWER:
                    self.current_contact.status = ContactStatus.NEW
                
                self.contact_repo.update(self.current_contact)
            
            print(f"Call ended with status: {status.value}")
            print(f"Duration: {self.current_call.duration_seconds} seconds")
            
            # Clear current state
            self.current_call = None
            self.current_conversation = None
            self.current_contact = None
            self.current_campaign = None
            self.call_context = {}
            
            return True
            
        except Exception as e:
            print(f"Error ending call: {e}")
            return False
    
    def get_current_script(self) -> str:
        """Get the current script based on campaign stage with document integration"""
        if not self.current_campaign or not self.current_conversation:
            return "Hello! How can I help you today?"
        
        stage = self.current_conversation.stage
        return self.campaign_manager.get_campaign_script(
            self.current_campaign.id,
            stage,
            self.call_context
        )
    
    def process_user_input(self, user_text: str) -> str:
        """Process user input and generate response with template-driven flow"""
        if not self.current_conversation:
            return "I'm sorry, but I'm not currently in a call. Please start a call first."
        
        if not user_text or not user_text.strip():
            return "I didn't catch that. Could you please repeat?"
        
        try:
            # Add user input to transcript and persist immediately
            timestamp = time.time()
            self.conversation_repo.add_transcript_entry(
                self.current_conversation.id,
                'user',
                user_text,
                timestamp
            )
            
            # Persist conversation state immediately
            self.conversation_repo.update(self.current_conversation)
            
            # Extract data from user input using template rules if available
            extracted_data = self._extract_data_with_template_rules(user_text)
            
            # Update collected data and persist
            for key, value in extracted_data.items():
                self.conversation_repo.update_collected_data(
                    self.current_conversation.id,
                    key,
                    value
                )
            
            # Persist conversation state again after data updates
            self.conversation_repo.update(self.current_conversation)
            
            # Check if we should transition to next stage using template rules
            should_transition = self._should_transition_with_template_rules(user_text)
            
            if should_transition:
                next_stage = self.campaign_manager.get_next_stage(
                    self.current_campaign.id,
                    self.current_conversation.stage
                )
                if next_stage:
                    self.conversation_repo.update_stage(
                        self.current_conversation.id,
                        next_stage
                    )
                    self.current_conversation.stage = next_stage
            
            # Get comprehensive campaign context including template, documents, and analysis
            campaign_context = self.campaign_manager.get_campaign_context(
                self.current_campaign.id,
                self.current_conversation.stage,
                user_text
            )
            
            # Prepare conversation context
            conversation_context = {
                'current_stage': self.current_conversation.stage.value,
                'collected_data': self.current_conversation.collected_data,
                'call_context': self.call_context,
                'conversation_turns': len(self.current_conversation.transcript)
            }
            
            # Generate response using LLM with template-driven context
            response = self.thinker.get_response_with_context(
                user_text,
                campaign_context,
                conversation_context
            )
            
            # Add agent response to transcript
            self.conversation_repo.add_transcript_entry(
                self.current_conversation.id,
                'agent',
                response,
                time.time()
            )
            
            return response
            
        except Exception as e:
            print(f"Error processing user input: {e}")
            # Log the error for debugging but don't expose it to user
            import logging
            logging.error(f"Error in process_user_input: {e}")
            return "I'm sorry, I'm having trouble processing that. Could you please repeat?"
    
    def _extract_data_with_template_rules(self, user_text: str) -> Dict[str, Any]:
        """Extract data using template NLP rules if available"""
        # Get template from campaign context
        campaign_context = self.campaign_manager.get_campaign_context(
            self.current_campaign.id,
            self.current_conversation.stage
        )
        
        template = campaign_context.get('template')
        if template and template.nlp_extraction_rules:
            # Use template NLP rules
            extracted_data = {}
            for rule in template.nlp_extraction_rules:
                if rule.extraction_type == 'keyword':
                    # Simple keyword extraction
                    if any(keyword.lower() in user_text.lower() for keyword in rule.keywords):
                        extracted_data[rule.field_name] = True
                elif rule.extraction_type == 'entity':
                    # Simple entity extraction (can be enhanced)
                    for pattern in rule.patterns:
                        import re
                        match = re.search(pattern, user_text, re.IGNORECASE)
                        if match:
                            extracted_data[rule.field_name] = match.group(1)
                            break
                elif rule.extraction_type == 'pattern':
                    # Pattern-based extraction
                    for pattern in rule.patterns:
                        import re
                        match = re.search(pattern, user_text, re.IGNORECASE)
                        if match:
                            extracted_data[rule.field_name] = match.group(0)
                            break
            
            return extracted_data
        else:
            # Fallback to original extraction method
            return self.campaign_manager.extract_data_from_input(
                self.current_campaign.id,
                user_text
            )
    
    def _should_transition_with_template_rules(self, user_text: str) -> bool:
        """Check if should transition using template rules"""
        # Get template from campaign context
        campaign_context = self.campaign_manager.get_campaign_context(
            self.current_campaign.id,
            self.current_conversation.stage
        )
        
        template = campaign_context.get('template')
        stage_instructions = campaign_context.get('stage_instructions')
        
        if template and stage_instructions:
            # Use template transition rules
            conditions = stage_instructions.next_stage_conditions
            
            # Check min_turns
            if 'min_turns' in conditions:
                min_turns = conditions['min_turns']
                if len(self.current_conversation.transcript) < min_turns:
                    return False
            
            # Check keywords
            if 'keywords' in conditions:
                keywords = conditions['keywords']
                if not any(keyword.lower() in user_text.lower() for keyword in keywords):
                    return False
            
            # Check sentiment threshold (simplified)
            if 'sentiment_threshold' in conditions:
                # This would need actual sentiment analysis
                # For now, assume conditions are met
                pass
            
            return True
        else:
            # Fallback to original transition logic
            return self.campaign_manager.should_transition_stage(
                self.current_conversation.id,
                user_text
            )
    
    def start_recording(self, output_file: str = "call_recording.wav"):
        """Start recording the call"""
        if self.is_recording:
            print("Already recording")
            return
        
        self.is_recording = True
        self.recording_file = output_file
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()
        print("Call recording started")
    
    def stop_recording(self):
        """Stop recording the call"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()
        print("Call recording stopped")
    
    def _record_audio(self):
        """Internal method to record audio"""
        stream = None
        wf = None
        try:
            stream = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype=np.int16)
            stream.start()
            
            wf = wave.open(self.recording_file, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            
            while self.is_recording:
                audio_data, _ = stream.read(1024)
                wf.writeframes(audio_data.tobytes())
                
        except Exception as e:
            print(f"Error recording audio: {e}")
        finally:
            # Ensure proper cleanup
            if wf:
                wf.close()
            if stream:
                stream.stop()
                stream.close()
    
    def run_campaign(self, campaign_id: str):
        """Dial through all leads in a campaign sequentially"""
        while True:
            lead = self.contact_repo.get_next_lead(campaign_id)
            if not lead:
                print("No more leads – campaign completed")
                break
            ok = self.conduct_call(lead.id, campaign_id, lead.phone_number)
            if not ok:
                print("Call failed – skipping to next lead")
                continue

    def conduct_call(self, contact_id: str, campaign_id: str, phone_number: str):
        """Conduct a complete call from start to finish"""
        if not self.start_call(contact_id, campaign_id, phone_number):
            return
        
        try:
            # Start recording
            self.start_recording()
            
            # Get initial script
            initial_script = self.get_current_script()
            print(f"\nAgent: {initial_script}")
            
            # Speak initial script
            self.tts.generate_speech(initial_script)
            
            # Add agent's initial message to transcript
            self.conversation_repo.add_transcript_entry(
                self.current_conversation.id,
                'agent',
                initial_script,
                time.time()
            )
            
            print("\nCall in progress. Press Ctrl+C to end call.")
            
            # Main call loop
            while self.current_call and self.current_call.status == CallStatus.IN_PROGRESS:
                try:
                    # Record and transcribe user input
                    audio_data = self.recognizer.record_audio()
                    
                    if audio_data is not None and len(audio_data) > 0:
                        user_text = self.recognizer.transcribe_audio(audio_data)
                        print(f"\nUser: {user_text}")
                        
                        # Check for call end keywords
                        if user_text.lower() in ['goodbye', 'bye', 'end call', 'hang up']:
                            response = "Thank you for your time. Have a great day!"
                            self.tts.generate_speech(response)
                            break
                        
                        if not user_text.strip():
                            continue
                        
                        # Run unified LangChain pipeline step
                        step_out = self.pipeline.run_step(
                            audio_data,
                            self.current_campaign.id,
                            {
                                "call_context": self.call_context,
                                "conversation_turns": len(self.current_conversation.transcript),
                            },
                        )
                        response = step_out["response"]
                        print(f"\nAgent: {response}")
                        # Play the TTS audio returned from the pipeline to avoid double synthesis
                        tts_audio = step_out.get("tts_audio")
                        if tts_audio:
                            try:
                                sd.play(np.frombuffer(tts_audio, dtype=np.float32), samplerate=24000, blocking=True)
                                sd.wait()
                            except Exception:
                                # Fallback to local generation if playback fails
                                self.tts.generate_speech(response)
                        else:
                            self.tts.generate_speech(response)
                        # Break if pipeline signals end of call
                        if step_out.get("call_finished"):
                            break
                        
                    else:
                        print("\nNo audio detected, continuing...")
                
                except KeyboardInterrupt:
                    print("\nCall interrupted by user")
                    break
                except Exception as e:
                    print(f"\nError in call loop: {e}")
                    continue
            
            # End call
            self.end_call(CallStatus.COMPLETED)
            self.stop_recording()
            return True
            
        except Exception as e:
            print(f"Error conducting call: {e}")
            self.end_call(CallStatus.FAILED, str(e))
            self.stop_recording()
    
    def get_call_summary(self) -> Dict[str, Any]:
        """Get summary of the last call"""
        if not self.current_conversation:
            return {}
        
        return {
            'call_id': self.current_call.id if self.current_call else None,
            'contact': {
                'name': f"{self.current_contact.first_name or ''} {self.current_contact.last_name or ''}".strip(),
                'phone': self.current_contact.phone_number if self.current_contact else None
            },
            'campaign': self.current_campaign.name if self.current_campaign else None,
            'stage': self.current_conversation.stage.value,
            'duration': self.current_conversation.duration_seconds,
            'collected_data': self.current_conversation.collected_data,
            'transcript_length': len(self.current_conversation.transcript)
        }