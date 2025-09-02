#!/usr/bin/env python3
"""
Test script for document integration
"""

import sys
import os

# Add project root to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from crm.models.crm import Document, Campaign, CampaignStage, CampaignPurpose
from crm.repositories.document_repository import DocumentRepository
from crm.repositories.campaign_repository import CampaignRepository
from core.document_manager import DocumentManager
from core.campaign_manager import CampaignManager
from core.user_manager import UserManager

def test_document_integration():
    """Test the document integration functionality"""
    print("Testing Document Integration...")
    print("=" * 50)
    
    # Initialize repositories and managers
    document_repo = DocumentRepository()
    campaign_repo = CampaignRepository()
    document_manager = DocumentManager()
    
    # Get or create a test user
    user_manager = UserManager()
    user = user_manager.get_user_by_id("66baef9c-7477-4a83-a8e9-233c49ac8f4d")
    if not user:
        print("Test user not found. Please run the system first to create sample data.")
        return
    
    campaign_manager = CampaignManager(user=user)
    
    print(f"Testing with user: {user.first_name} {user.last_name}")
    print()
    
    # Test 1: Get all documents
    print("1. Testing document retrieval...")
    documents = document_repo.find_active_documents(user.id)
    print(f"   Found {len(documents)} documents")
    for doc in documents:
        print(f"   - {doc.name} ({doc.document_type})")
    print()
    
    # Test 2: Get documents by type
    print("2. Testing document retrieval by type...")
    product_docs = document_repo.find_by_type("product_info", user.id)
    print(f"   Found {len(product_docs)} product info documents")
    for doc in product_docs:
        print(f"   - {doc.name}")
    print()
    
    # Test 3: Search documents
    print("3. Testing document search...")
    search_results = document_repo.search_content("pricing", user.id)
    print(f"   Found {len(search_results)} documents containing 'pricing'")
    for doc in search_results:
        print(f"   - {doc.name}")
    print()
    
    # Test 4: Get campaign context
    print("4. Testing campaign context with documents...")
    campaigns = campaign_repo.find_active_campaigns(user.id)
    if campaigns:
        campaign = campaigns[0]
        print(f"   Testing with campaign: {campaign.name}")
        
        # Get campaign context
        context = campaign_manager.get_campaign_context(
            campaign.id,
            CampaignStage.INTRODUCTION
        )
        
        print(f"   Found {len(context.get('documents', []))} relevant documents")
        print(f"   Document context length: {len(context.get('document_context', ''))} characters")
        print(f"   Document placeholders: {list(context.get('document_placeholders', {}).keys())}")
        print()
        
        # Test 5: Get script with document integration
        print("5. Testing script generation with document integration...")
        script = campaign_manager.get_campaign_script(
            campaign.id,
            CampaignStage.INTRODUCTION,
            user_input="I'm interested in your product"
        )
        print(f"   Generated script: {script[:100]}...")
        print()
        
        # Test 6: Test document placeholders
        print("6. Testing document placeholders...")
        placeholders = document_manager.get_document_placeholders(context.get('documents', []))
        print(f"   Extracted placeholders: {list(placeholders.keys())}")
        for key, value in placeholders.items():
            print(f"   - {key}: {value[:50]}...")
        print()
        
    else:
        print("   No campaigns found for testing")
        print()
    
    # Test 7: Test document relevance by campaign purpose
    print("7. Testing document relevance by campaign purpose...")
    sales_docs = document_repo.find_by_campaign_context("sales", user.id)
    print(f"   Found {len(sales_docs)} documents relevant for sales campaigns")
    for doc in sales_docs:
        print(f"   - {doc.name} ({doc.document_type})")
    print()
    
    print("Document Integration Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_document_integration()




