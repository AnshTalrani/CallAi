"""
NLP Extraction Module
Extracts structured information from user input based on campaign templates
"""

import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ExtractionType(Enum):
    KEYWORD = "keyword"
    PATTERN = "pattern"
    ENTITY = "entity"
    SENTIMENT = "sentiment"
    INTENT = "intent"

@dataclass
class ExtractionRule:
    field_name: str
    extraction_type: ExtractionType
    keywords: List[str] = None
    patterns: List[str] = None
    required: bool = False
    description: str = ""
    confidence_threshold: float = 0.7

@dataclass
class ExtractedData:
    field_name: str
    value: Any
    confidence: float
    source_text: str
    extraction_type: ExtractionType

class NLPExtractor:
    """Extracts structured information from user input based on campaign templates"""
    
    def __init__(self):
        self.extraction_rules: Dict[str, List[ExtractionRule]] = {}
        self.extracted_data: Dict[str, ExtractedData] = {}
        
    def add_campaign_rules(self, campaign_id: str, rules: List[ExtractionRule]):
        """Add extraction rules for a specific campaign"""
        self.extraction_rules[campaign_id] = rules
        
    def extract_from_text(self, text: str, campaign_id: str) -> Dict[str, ExtractedData]:
        """Extract information from text based on campaign rules"""
        if campaign_id not in self.extraction_rules:
            return {}
            
        rules = self.extraction_rules[campaign_id]
        extracted = {}
        
        for rule in rules:
            result = self._apply_extraction_rule(text, rule)
            if result:
                extracted[rule.field_name] = result
                
        return extracted
    
    def _apply_extraction_rule(self, text: str, rule: ExtractionRule) -> Optional[ExtractedData]:
        """Apply a single extraction rule to text"""
        text_lower = text.lower()
        
        if rule.extraction_type == ExtractionType.KEYWORD:
            return self._extract_keywords(text, text_lower, rule)
        elif rule.extraction_type == ExtractionType.PATTERN:
            return self._extract_patterns(text, rule)
        elif rule.extraction_type == ExtractionType.ENTITY:
            return self._extract_entities(text, text_lower, rule)
        elif rule.extraction_type == ExtractionType.SENTIMENT:
            return self._extract_sentiment(text, rule)
        elif rule.extraction_type == ExtractionType.INTENT:
            return self._extract_intent(text, text_lower, rule)
            
        return None
    
    def _extract_keywords(self, text: str, text_lower: str, rule: ExtractionRule) -> Optional[ExtractedData]:
        """Extract information based on keyword matching"""
        if not rule.keywords:
            return None
            
        found_keywords = []
        for keyword in rule.keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
                
        if found_keywords:
            confidence = len(found_keywords) / len(rule.keywords)
            if confidence >= rule.confidence_threshold:
                return ExtractedData(
                    field_name=rule.field_name,
                    value=found_keywords,
                    confidence=confidence,
                    source_text=text,
                    extraction_type=rule.extraction_type
                )
        return None
    
    def _extract_patterns(self, text: str, rule: ExtractionRule) -> Optional[ExtractedData]:
        """Extract information based on regex patterns"""
        if not rule.patterns:
            return None
            
        matches = []
        for pattern in rule.patterns:
            pattern_matches = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(pattern_matches)
            
        if matches:
            # Use the first match for now
            value = matches[0] if isinstance(matches[0], str) else matches[0][0]
            confidence = 0.9  # High confidence for pattern matches
            return ExtractedData(
                field_name=rule.field_name,
                value=value,
                confidence=confidence,
                source_text=text,
                extraction_type=rule.extraction_type
            )
        return None
    
    def _extract_entities(self, text: str, text_lower: str, rule: ExtractionRule) -> Optional[ExtractedData]:
        """Extract named entities based on keywords"""
        if not rule.keywords:
            return None
            
        found_entities = []
        for keyword in rule.keywords:
            if keyword.lower() in text_lower:
                found_entities.append(keyword)
                
        if found_entities:
            confidence = len(found_entities) / len(rule.keywords)
            if confidence >= rule.confidence_threshold:
                return ExtractedData(
                    field_name=rule.field_name,
                    value=found_entities[0],  # Use first match
                    confidence=confidence,
                    source_text=text,
                    extraction_type=rule.extraction_type
                )
        return None
    
    def _extract_sentiment(self, text: str, rule: ExtractionRule) -> Optional[ExtractedData]:
        """Extract sentiment from text"""
        # Simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy', 'satisfied']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'unhappy', 'dissatisfied', 'problem']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = positive_count / (positive_count + negative_count + 1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = negative_count / (positive_count + negative_count + 1)
        else:
            sentiment = "neutral"
            confidence = 0.5
            
        return ExtractedData(
            field_name=rule.field_name,
            value=sentiment,
            confidence=confidence,
            source_text=text,
            extraction_type=rule.extraction_type
        )
    
    def _extract_intent(self, text: str, text_lower: str, rule: ExtractionRule) -> Optional[ExtractedData]:
        """Extract user intent from text"""
        intent_keywords = {
            'interested': ['interested', 'tell me more', 'sounds good', 'yes'],
            'not_interested': ['not interested', 'no thanks', 'not now', 'busy'],
            'objection': ['expensive', 'cost', 'price', 'budget', 'think about it'],
            'question': ['how', 'what', 'when', 'where', 'why', 'question'],
            'request_info': ['send', 'email', 'brochure', 'information', 'details']
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                confidence = 0.8
                return ExtractedData(
                    field_name=rule.field_name,
                    value=intent,
                    confidence=confidence,
                    source_text=text,
                    extraction_type=rule.extraction_type
                )
                
        return ExtractedData(
            field_name=rule.field_name,
            value="general",
            confidence=0.5,
            source_text=text,
            extraction_type=rule.extraction_type
        )
    
    def get_extraction_summary(self, campaign_id: str) -> Dict[str, Any]:
        """Get summary of all extracted data for a campaign"""
        if campaign_id not in self.extraction_rules:
            return {}
            
        summary = {}
        for field_name, extracted_data in self.extracted_data.items():
            if extracted_data.confidence >= 0.7:  # Only include high-confidence extractions
                summary[field_name] = {
                    'value': extracted_data.value,
                    'confidence': extracted_data.confidence,
                    'type': extracted_data.extraction_type.value
                }
        return summary