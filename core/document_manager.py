from typing import List, Dict, Any, Optional
from crm.models.crm import Document, Campaign, CampaignPurpose
from crm.repositories.document_repository import DocumentRepository

class DocumentManager:
    """Manages document integration and knowledge base for campaigns"""
    
    def __init__(self):
        self.document_repo = DocumentRepository()
    
    def get_relevant_documents(self, campaign: Campaign, stage: str = None, 
                             user_input: str = None, user_id: str = None) -> List[Document]:
        """Get relevant documents for current campaign context"""
        documents = []
        
        # Get documents based on campaign purpose
        campaign_purpose = campaign.purpose.value if campaign and hasattr(campaign, 'purpose') else 'general'
        purpose_docs = self.document_repo.find_by_campaign_context(
            campaign_purpose, 
            user_id or (campaign.user_id if campaign else None)
        )
        documents.extend(purpose_docs)
        
        # Get documents based on current stage
        if stage:
            stage_docs = self.document_repo.find_by_tags([stage], user_id or (campaign.user_id if campaign else None))
            documents.extend(stage_docs)
        
        # Get documents based on user input (if provided)
        if user_input:
            # Extract key terms from user input
            key_terms = self._extract_key_terms(user_input)
            for term in key_terms:
                term_docs = self.document_repo.search_content(term, user_id or (campaign.user_id if campaign else None))
                documents.extend(term_docs)
        
        # Remove duplicates and return
        unique_docs = {}
        for doc in documents:
            if doc.id not in unique_docs:
                unique_docs[doc.id] = doc
        
        return list(unique_docs.values())
    
    def extract_knowledge_snippets(self, documents: List[Document], query: str = None) -> List[str]:
        """Extract relevant knowledge snippets from documents"""
        snippets = []
        
        for doc in documents:
            if query:
                # If query provided, look for relevant sections
                relevant_sections = self._find_relevant_sections(doc.content, query)
                snippets.extend(relevant_sections)
            else:
                # Otherwise, use document summary or key points
                summary = self._extract_summary(doc.content)
                snippets.append(f"{doc.name}: {summary}")
        
        return snippets
    
    def format_document_context(self, documents: List[Document], max_length: int = 2000) -> str:
        """Format documents for LLM context"""
        if not documents:
            return ""
        
        context_parts = []
        current_length = 0
        
        for doc in documents:
            # Create a concise summary of the document
            doc_summary = f"Document: {doc.name}\nType: {doc.document_type}\n"
            
            # Add key content (truncated if needed)
            content_preview = doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
            doc_summary += f"Content: {content_preview}\n"
            
            # Add tags if available
            if doc.tags:
                doc_summary += f"Tags: {', '.join(doc.tags)}\n"
            
            doc_summary += "\n"
            
            # Check if adding this would exceed max length
            if current_length + len(doc_summary) > max_length:
                break
            
            context_parts.append(doc_summary)
            current_length += len(doc_summary)
        
        return "\n".join(context_parts)
    
    def get_document_placeholders(self, documents: List[Document]) -> Dict[str, str]:
        """Extract placeholders from documents for script templates"""
        placeholders = {}
        
        for doc in documents:
            if doc.document_type == "product_info":
                # Extract product-related placeholders
                placeholders.update(self._extract_product_placeholders(doc))
            elif doc.document_type == "policy":
                # Extract policy-related placeholders
                placeholders.update(self._extract_policy_placeholders(doc))
            elif doc.document_type == "faq":
                # Extract FAQ-related placeholders
                placeholders.update(self._extract_faq_placeholders(doc))
        
        return placeholders
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from user input"""
        # Simple keyword extraction - can be enhanced with NLP
        words = text.lower().split()
        # Filter out common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        key_terms = [word for word in words if len(word) > 3 and word not in stop_words]
        return key_terms[:5]  # Limit to top 5 terms
    
    def _find_relevant_sections(self, content: str, query: str) -> List[str]:
        """Find relevant sections in document content"""
        # Simple implementation - can be enhanced with better NLP
        lines = content.split('\n')
        relevant_lines = []
        
        query_terms = query.lower().split()
        
        for line in lines:
            line_lower = line.lower()
            if any(term in line_lower for term in query_terms):
                relevant_lines.append(line.strip())
        
        return relevant_lines[:3]  # Limit to 3 most relevant lines
    
    def _extract_summary(self, content: str) -> str:
        """Extract a summary from document content"""
        # Simple implementation - take first few sentences
        sentences = content.split('.')
        summary = '. '.join(sentences[:2]) + '.'
        return summary if len(summary) < 200 else summary[:200] + "..."
    
    def _extract_product_placeholders(self, doc: Document) -> Dict[str, str]:
        """Extract product-related placeholders from product info document"""
        placeholders = {}
        
        # Look for common product-related patterns
        content_lower = doc.content.lower()
        
        # Extract product name
        if 'product name:' in content_lower:
            start = content_lower.find('product name:') + 13
            end = content_lower.find('\n', start)
            if end == -1:
                end = len(content_lower)
            placeholders['product_name'] = doc.content[start:end].strip()
        
        # Extract features
        if 'features:' in content_lower:
            start = content_lower.find('features:') + 9
            end = content_lower.find('\n\n', start)
            if end == -1:
                end = len(content_lower)
            placeholders['product_features'] = doc.content[start:end].strip()
        
        # Extract benefits
        if 'benefits:' in content_lower:
            start = content_lower.find('benefits:') + 9
            end = content_lower.find('\n\n', start)
            if end == -1:
                end = len(content_lower)
            placeholders['product_benefits'] = doc.content[start:end].strip()
        
        return placeholders
    
    def _extract_policy_placeholders(self, doc: Document) -> Dict[str, str]:
        """Extract policy-related placeholders from policy document"""
        placeholders = {}
        
        content_lower = doc.content.lower()
        
        # Extract company name
        if 'company name:' in content_lower:
            start = content_lower.find('company name:') + 13
            end = content_lower.find('\n', start)
            if end == -1:
                end = len(content_lower)
            placeholders['company_name'] = doc.content[start:end].strip()
        
        # Extract policies
        if 'policy:' in content_lower:
            start = content_lower.find('policy:') + 7
            end = content_lower.find('\n\n', start)
            if end == -1:
                end = len(content_lower)
            placeholders['company_policy'] = doc.content[start:end].strip()
        
        return placeholders
    
    def _extract_faq_placeholders(self, doc: Document) -> Dict[str, str]:
        """Extract FAQ-related placeholders from FAQ document"""
        placeholders = {}
        
        # Extract common questions and answers
        lines = doc.content.split('\n')
        faqs = []
        
        for i, line in enumerate(lines):
            if line.strip().endswith('?') and i + 1 < len(lines):
                question = line.strip()
                answer = lines[i + 1].strip()
                faqs.append(f"Q: {question}\nA: {answer}")
        
        if faqs:
            placeholders['faq_section'] = '\n\n'.join(faqs[:3])  # Limit to 3 FAQs
        
        return placeholders
