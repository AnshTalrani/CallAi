from typing import List, Optional, Dict, Any
from datetime import datetime
from .base_repository import BaseRepository
from ..models.crm import Document

class DocumentRepository(BaseRepository[Document]):
    def get_collection_name(self) -> str:
        return "documents"
    
    def from_dict(self, data: Dict[str, Any]) -> Document:
        # Convert string dates back to datetime
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        
        return Document(
            id=data.get('id'),
            user_id=data['user_id'],
            name=data['name'],
            content=data['content'],
            document_type=data['document_type'],
            tags=data.get('tags', []),
            description=data.get('description'),
            is_active=data.get('is_active', True),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def find_by_type(self, document_type: str, user_id: str = None) -> List[Document]:
        """Find documents by type for a specific user"""
        documents = self.find_by_field('document_type', document_type)
        if user_id:
            documents = [doc for doc in documents if doc.user_id == user_id]
        return [doc for doc in documents if doc.is_active]
    
    def find_by_tags(self, tags: List[str], user_id: str = None) -> List[Document]:
        """Find documents by tags"""
        all_documents = self.find_all()
        if user_id:
            all_documents = [doc for doc in all_documents if doc.user_id == user_id]
        
        matching_documents = []
        for doc in all_documents:
            if doc.is_active and any(tag in doc.tags for tag in tags):
                matching_documents.append(doc)
        
        return matching_documents
    
    def search_content(self, query: str, user_id: str = None) -> List[Document]:
        """Search document content"""
        all_documents = self.find_all()
        if user_id:
            all_documents = [doc for doc in all_documents if doc.user_id == user_id]
        
        matching_documents = []
        query_lower = query.lower()
        for doc in all_documents:
            if doc.is_active and (query_lower in doc.content.lower() or 
                                query_lower in doc.name.lower() or
                                query_lower in (doc.description or '').lower()):
                matching_documents.append(doc)
        
        return matching_documents
    
    def find_active_documents(self, user_id: str = None) -> List[Document]:
        """Find all active documents for a specific user"""
        if user_id:
            documents = self.find_by_field('user_id', user_id)
        else:
            documents = self.find_all()
        return [doc for doc in documents if doc.is_active]
    
    def find_by_campaign_context(self, campaign_purpose: str, user_id: str = None) -> List[Document]:
        """Find documents relevant to a campaign purpose"""
        # Map campaign purposes to document types
        purpose_to_types = {
            'sales': ['product_info', 'faq', 'policy'],
            'support': ['faq', 'policy', 'knowledge_base'],
            'survey': ['policy', 'knowledge_base']
        }
        
        relevant_types = purpose_to_types.get(campaign_purpose.lower(), ['policy', 'faq'])
        documents = []
        
        for doc_type in relevant_types:
            type_docs = self.find_by_type(doc_type, user_id)
            documents.extend(type_docs)
        
        return documents




