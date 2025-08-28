#!/usr/bin/env python3
"""
Call Agent Example - Demonstrates how to use the call agent system
"""

import sys
import os
from voice_recognition import select_audio_device

# Ensure project root is on path so `call_agent` can be imported after move
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from call_agent.call_agent import CallAgent
from call_agent.campaign_manager import CampaignManager
from call_agent.models.crm import Contact, ContactStatus
from call_agent.repositories.contact_repository import ContactRepository

def create_sample_data():
    """Create sample contacts and campaigns for demonstration"""
    print("Creating sample data...")
    
    # Create a sample user for demonstration
    from call_agent.user_manager import UserManager
    from call_agent.models.user import User, UserStatus, UserPlan
    
    user_manager = UserManager()
    
    # Create a demo user
    demo_user = user_manager.register_user(
        email="demo@example.com",
        password="demo123",
        first_name="Demo",
        last_name="User",
        company_name="Demo Company"
    )
    
    # Initialize repositories with user context
    contact_repo = ContactRepository()
    campaign_manager = CampaignManager(user=demo_user)
    
    # Create sample contacts
    contacts = []
    
    contact1 = Contact(
        user_id=demo_user.id,
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        company="Tech Solutions Inc",
        status=ContactStatus.NEW
    )
    contacts.append(contact_repo.create(contact1))
    
    contact2 = Contact(
        user_id=demo_user.id,
        phone_number="+1987654321",
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@business.com",
        company="Business Corp",
        status=ContactStatus.NEW
    )
    contacts.append(contact_repo.create(contact2))
    
    # Create sample campaigns
    sales_campaign = campaign_manager.create_sample_campaign("sales")
    support_campaign = campaign_manager.create_sample_campaign("support")
    survey_campaign = campaign_manager.create_sample_campaign("survey")
    
    print(f"Created {len(contacts)} contacts and 3 campaigns")
    return contacts, [sales_campaign, support_campaign, survey_campaign]

def main():
    """Main function to demonstrate call agent functionality"""
    print("=== Call Agent System Demo ===\n")
    
    # Create sample data
    contacts, campaigns = create_sample_data()
    
    # Select audio device
    device_id = select_audio_device()
    
    # Initialize call agent with user context
    agent = CallAgent(user=demo_user, device_id=device_id)
    
    try:
        while True:
            print("\n" + "="*50)
            print("Call Agent Demo Menu:")
            print("1. List contacts")
            print("2. List campaigns")
            print("3. Start a call")
            print("4. View call history")
            print("5. Exit")
            print("="*50)
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\n--- Contacts ---")
                for i, contact in enumerate(contacts, 1):
                    print(f"{i}. {contact.first_name} {contact.last_name}")
                    print(f"   Phone: {contact.phone_number}")
                    print(f"   Company: {contact.company}")
                    print(f"   Status: {contact.status.value}")
                    print()
            
            elif choice == "2":
                print("\n--- Campaigns ---")
                for i, campaign in enumerate(campaigns, 1):
                    print(f"{i}. {campaign.name}")
                    print(f"   Description: {campaign.description}")
                    print(f"   Stages: {[stage.value for stage in campaign.stages]}")
                    print(f"   Active: {campaign.is_active}")
                    print()
            
            elif choice == "3":
                print("\n--- Start a Call ---")
                
                # Select contact
                print("Select a contact:")
                for i, contact in enumerate(contacts, 1):
                    print(f"{i}. {contact.first_name} {contact.last_name} ({contact.phone_number})")
                
                try:
                    contact_choice = int(input("Enter contact number: ")) - 1
                    if 0 <= contact_choice < len(contacts):
                        selected_contact = contacts[contact_choice]
                    else:
                        print("Invalid contact selection")
                        continue
                except ValueError:
                    print("Invalid input")
                    continue
                
                # Select campaign
                print("\nSelect a campaign:")
                for i, campaign in enumerate(campaigns, 1):
                    print(f"{i}. {campaign.name}")
                
                try:
                    campaign_choice = int(input("Enter campaign number: ")) - 1
                    if 0 <= campaign_choice < len(campaigns):
                        selected_campaign = campaigns[campaign_choice]
                    else:
                        print("Invalid campaign selection")
                        continue
                except ValueError:
                    print("Invalid input")
                    continue
                
                print(f"\nStarting call with {selected_contact.first_name} using {selected_campaign.name} campaign...")
                print("Press Ctrl+C to end the call early")
                
                # Conduct the call
                agent.conduct_call(
                    contact_id=selected_contact.id,
                    campaign_id=selected_campaign.id,
                    phone_number=selected_contact.phone_number
                )
                
                # Show call summary
                summary = agent.get_call_summary()
                if summary:
                    print("\n--- Call Summary ---")
                    print(f"Contact: {summary['contact']['name']}")
                    print(f"Campaign: {summary['campaign']}")
                    print(f"Duration: {summary['duration']} seconds")
                    print(f"Final Stage: {summary['stage']}")
                    print(f"Collected Data: {summary['collected_data']}")
                    print(f"Transcript Entries: {summary['transcript_length']}")
            
            elif choice == "4":
                print("\n--- Call History ---")
                # This would typically show call history from the database
                print("Call history feature would show past calls here")
                print("(Implementation depends on your specific needs)")
            
            elif choice == "5":
                print("\nExiting...")
                break
            
            else:
                print("Invalid choice. Please enter 1-5.")
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        agent.cleanup()
        print("Call agent cleaned up")

if __name__ == "__main__":
    main()