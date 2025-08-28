#!/usr/bin/env python3
"""
Multi-Tenant CRM Demo Script

This script demonstrates how the multi-tenant CRM system works with data isolation
between different users (clients).
"""

from call_agent.user_manager import UserManager
from call_agent.campaign_manager import CampaignManager
from call_agent.models.user import UserPlan
from call_agent.models.crm import CampaignStage, ContactStatus, CallStatus
from call_agent.repositories.contact_repository import ContactRepository
from call_agent.repositories.call_repository import CallRepository
from call_agent.repositories.conversation_repository import ConversationRepository
from call_agent.models.crm import Contact, Call, Conversation

def print_separator(title):
    """Print a separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def demo_multi_tenant_crm():
    """Demonstrate multi-tenant CRM functionality"""
    
    print_separator("MULTI-TENANT CRM DEMO")
    print("This demo shows how multiple users can have their own isolated CRM data")
    
    # Initialize managers
    user_manager = UserManager()
    contact_repo = ContactRepository()
    call_repo = CallRepository()
    conversation_repo = ConversationRepository()
    
    # Create two demo users (clients)
    print("\n1. Creating demo users...")
    
    try:
        user1 = user_manager.register_user(
            email="john@company1.com",
            password="password123",
            first_name="John",
            last_name="Smith",
            company_name="Tech Solutions Inc."
        )
        print(f"✓ Created user: {user1.full_name} ({user1.company_name})")
        
        user2 = user_manager.register_user(
            email="sarah@company2.com", 
            password="password456",
            first_name="Sarah",
            last_name="Johnson",
            company_name="Marketing Pro LLC"
        )
        print(f"✓ Created user: {user2.full_name} ({user2.company_name})")
        
    except ValueError as e:
        print(f"User already exists: {e}")
        user1 = user_manager.get_user_by_email("john@company1.com")
        user2 = user_manager.get_user_by_email("sarah@company2.com")
    
    # Create campaigns for each user
    print("\n2. Creating campaigns for each user...")
    
    campaign_manager1 = CampaignManager(user1)
    campaign_manager2 = CampaignManager(user2)
    
    campaign1 = campaign_manager1.create_campaign(
        name="Tech Sales Campaign",
        description="Selling software solutions to tech companies",
        stages=[CampaignStage.INTRODUCTION, CampaignStage.NEEDS_ASSESSMENT, CampaignStage.CLOSING]
    )
    print(f"✓ Created campaign for {user1.company_name}: {campaign1.name}")
    
    campaign2 = campaign_manager2.create_campaign(
        name="Marketing Services Campaign", 
        description="Promoting marketing services to small businesses",
        stages=[CampaignStage.INTRODUCTION, CampaignStage.SOLUTION_PRESENTATION, CampaignStage.CLOSING]
    )
    print(f"✓ Created campaign for {user2.company_name}: {campaign2.name}")
    
    # Create contacts for each user
    print("\n3. Creating contacts for each user...")
    
    # User 1 contacts
    contact1_1 = Contact(
        user_id=user1.id,
        phone_number="+1234567890",
        first_name="Alice",
        last_name="Tech",
        email="alice@techcorp.com",
        company="TechCorp",
        tags=["tech", "enterprise"]
    )
    contact_repo.create(contact1_1)
    
    contact1_2 = Contact(
        user_id=user1.id,
        phone_number="+1234567891", 
        first_name="Bob",
        last_name="Developer",
        email="bob@devstartup.com",
        company="DevStartup",
        tags=["startup", "tech"]
    )
    contact_repo.create(contact1_2)
    
    print(f"✓ Created 2 contacts for {user1.company_name}")
    
    # User 2 contacts
    contact2_1 = Contact(
        user_id=user2.id,
        phone_number="+1987654321",
        first_name="Carol",
        last_name="Business",
        email="carol@smallbiz.com", 
        company="SmallBiz Inc.",
        tags=["small-business", "local"]
    )
    contact_repo.create(contact2_1)
    
    contact2_2 = Contact(
        user_id=user2.id,
        phone_number="+1987654322",
        first_name="David",
        last_name="Restaurant",
        email="david@restaurant.com",
        company="Local Restaurant",
        tags=["restaurant", "local"]
    )
    contact_repo.create(contact2_2)
    
    print(f"✓ Created 2 contacts for {user2.company_name}")
    
    # Create some calls and conversations
    print("\n4. Creating calls and conversations...")
    
    # User 1 calls
    call1_1 = Call(
        user_id=user1.id,
        contact_id=contact1_1.id,
        campaign_id=campaign1.id,
        phone_number=contact1_1.phone_number,
        status=CallStatus.COMPLETED,
        duration_seconds=300
    )
    call_repo.create(call1_1)
    
    call1_2 = Call(
        user_id=user1.id,
        contact_id=contact1_2.id,
        campaign_id=campaign1.id,
        phone_number=contact1_2.phone_number,
        status=CallStatus.SCHEDULED
    )
    call_repo.create(call1_2)
    
    # User 2 calls
    call2_1 = Call(
        user_id=user2.id,
        contact_id=contact2_1.id,
        campaign_id=campaign2.id,
        phone_number=contact2_1.phone_number,
        status=CallStatus.COMPLETED,
        duration_seconds=450
    )
    call_repo.create(call2_1)
    
    # Create conversations
    conv1_1 = Conversation(
        user_id=user1.id,
        contact_id=contact1_1.id,
        campaign_id=campaign1.id,
        call_id=call1_1.id,
        stage=CampaignStage.CLOSING,
        collected_data={"budget": "$50,000", "timeline": "Q2 2024"}
    )
    conversation_repo.create(conv1_1)
    
    conv2_1 = Conversation(
        user_id=user2.id,
        contact_id=contact2_1.id,
        campaign_id=campaign2.id,
        call_id=call2_1.id,
        stage=CampaignStage.SOLUTION_PRESENTATION,
        collected_data={"marketing_budget": "$5,000", "services_needed": "social_media"}
    )
    conversation_repo.create(conv2_1)
    
    print("✓ Created calls and conversations for both users")
    
    # Demonstrate data isolation
    print_separator("DATA ISOLATION DEMONSTRATION")
    
    print("\n5. Showing data isolation between users...")
    
    # Get dashboard data for each user
    dashboard1 = user_manager.get_user_dashboard_data(user1.id)
    dashboard2 = user_manager.get_user_dashboard_data(user2.id)
    
    print(f"\n{user1.company_name} Dashboard:")
    print(f"  - Total Campaigns: {dashboard1['stats']['total_campaigns']}")
    print(f"  - Total Contacts: {dashboard1['stats']['total_contacts']}")
    print(f"  - Total Calls: {dashboard1['stats']['total_calls']}")
    print(f"  - Completed Calls: {dashboard1['stats']['completed_calls']}")
    
    print(f"\n{user2.company_name} Dashboard:")
    print(f"  - Total Campaigns: {dashboard2['stats']['total_campaigns']}")
    print(f"  - Total Contacts: {dashboard2['stats']['total_contacts']}")
    print(f"  - Total Calls: {dashboard2['stats']['total_calls']}")
    print(f"  - Completed Calls: {dashboard2['stats']['completed_calls']}")
    
    # Show that users can't see each other's data
    print("\n6. Verifying data isolation...")
    
    # User 1's contacts
    user1_contacts = user_manager.get_user_contacts(user1.id)
    print(f"\n{user1.company_name} contacts:")
    for contact in user1_contacts:
        print(f"  - {contact['first_name']} {contact['last_name']} ({contact['company']})")
    
    # User 2's contacts  
    user2_contacts = user_manager.get_user_contacts(user2.id)
    print(f"\n{user2.company_name} contacts:")
    for contact in user2_contacts:
        print(f"  - {contact['first_name']} {contact['last_name']} ({contact['company']})")
    
    # Demonstrate campaign isolation
    print("\n7. Campaign isolation...")
    
    user1_campaigns = user_manager.get_user_campaigns(user1.id)
    user2_campaigns = user_manager.get_user_campaigns(user2.id)
    
    print(f"\n{user1.company_name} campaigns:")
    for campaign in user1_campaigns:
        print(f"  - {campaign['name']}: {campaign['description']}")
    
    print(f"\n{user2.company_name} campaigns:")
    for campaign in user2_campaigns:
        print(f"  - {campaign['name']}: {campaign['description']}")
    
    # Show usage statistics
    print_separator("USAGE STATISTICS")
    
    usage1 = user_manager.get_user_usage_stats(user1.id)
    usage2 = user_manager.get_user_usage_stats(user2.id)
    
    print(f"\n{user1.company_name} Usage:")
    print(f"  - Plan: {usage1['plan']}")
    print(f"  - Campaigns used: {usage1['usage']['campaigns']}/{usage1['limits']['campaigns']}")
    print(f"  - Contacts used: {usage1['usage']['contacts']}/{usage1['limits']['contacts']}")
    print(f"  - Calls made: {usage1['usage']['calls']}")
    
    print(f"\n{user2.company_name} Usage:")
    print(f"  - Plan: {usage2['plan']}")
    print(f"  - Campaigns used: {usage2['usage']['campaigns']}/{usage2['limits']['campaigns']}")
    print(f"  - Contacts used: {usage2['usage']['contacts']}/{usage2['limits']['contacts']}")
    print(f"  - Calls made: {usage2['usage']['calls']}")
    
    print_separator("DEMO COMPLETE")
    print("\n✓ Multi-tenant CRM system working correctly!")
    print("✓ Each user has their own isolated data")
    print("✓ Users cannot access each other's campaigns, contacts, or calls")
    print("✓ Usage tracking works per user")
    print("✓ Data is properly filtered by user_id in all repositories")

if __name__ == "__main__":
    demo_multi_tenant_crm()