# Campaign Template Structure Documentation

## Overview

The Campaign Template system provides a comprehensive, template-driven approach to creating and managing voice call campaigns. Every aspect of a campaign is defined through templates, including stages, instructions, NLP extraction rules, analysis rules, LLM personality, and document integration.

## Template Structure

### Core Template Components

```python
@dataclass
class CampaignTemplate:
    # Basic Information
    id: str
    name: str
    description: str
    version: str
    
    # Campaign Structure
    stages: List[str]
    stage_instructions: Dict[str, StageInstruction]
    
    # NLP Configuration
    nlp_extraction_rules: List[NLPExtractionRule]
    analysis_rules: List[AnalysisRule]
    
    # LLM Configuration
    llm_personality: LLMPersonality
    
    # Document Integration
    document_integration: DocumentIntegration
    
    # Campaign Settings
    max_call_duration: int
    follow_up_delay_hours: int
    retry_attempts: int
    success_metrics: Dict[str, Any]
    quality_assurance_rules: Dict[str, Any]
    
    # Custom Configuration
    custom_settings: Dict[str, Any]
    tags: List[str]
    is_active: bool
```

## 1. Campaign Stages

### Stage Definition
Each campaign consists of multiple stages that define the conversation flow:

```python
stages = [
    "introduction",
    "needs_assessment", 
    "solution_presentation",
    "objection_handling",
    "closing"
]
```

### Stage Instructions
Each stage has detailed instructions that guide the LLM behavior:

```python
@dataclass
class StageInstruction:
    stage_name: str
    primary_objective: str
    secondary_objectives: List[str]
    key_questions: List[str]
    success_criteria: List[str]
    failure_indicators: List[str]
    next_stage_conditions: Dict[str, Any]
    fallback_actions: List[str]
    required_data: List[str]
    optional_data: List[str]
    script_template: str
    transition_keywords: List[str]
    min_turns: int
    max_turns: int
    sentiment_threshold: float
```

#### Example Stage Instruction:
```json
{
  "stage_name": "Introduction",
  "primary_objective": "Establish rapport and introduce the purpose of the call",
  "secondary_objectives": [
    "Confirm contact information",
    "Assess initial interest level",
    "Set expectations for the conversation"
  ],
  "key_questions": [
    "Do you have a moment to discuss business solutions?",
    "What's the best time to reach you?",
    "Are you the decision maker for this type of solution?"
  ],
  "success_criteria": [
    "Contact confirms they have time to talk",
    "Contact shows interest in learning more",
    "Contact provides basic information"
  ],
  "failure_indicators": [
    "Contact immediately says they're not interested",
    "Contact is too busy to talk",
    "Contact is not the decision maker"
  ],
  "next_stage_conditions": {
    "min_turns": 2,
    "sentiment_threshold": 0.2,
    "keywords": ["yes", "sure", "okay", "tell me", "interested"]
  },
  "fallback_actions": [
    "Schedule a follow-up call",
    "Send information via email",
    "Ask for referral to decision maker"
  ],
  "required_data": ["contact_name", "company_name", "initial_interest"],
  "optional_data": ["best_time_to_call", "decision_maker_info"],
  "script_template": "Hello! This is {agent_name} calling from {company_name}...",
  "transition_keywords": ["yes", "sure", "okay", "tell me", "interested"],
  "min_turns": 2,
  "max_turns": 5,
  "sentiment_threshold": 0.2
}
```

## 2. NLP Extraction Rules

### Rule Structure
NLP extraction rules define what data to extract from conversations:

```python
@dataclass
class NLPExtractionRule:
    field_name: str
    extraction_type: str  # "keyword", "sentiment", "entity", "pattern", "rating", "intent"
    keywords: List[str]
    patterns: List[str]  # Regex patterns
    required: bool
    validation_rules: Dict[str, Any]
    description: str
    confidence_threshold: float
    fallback_value: Optional[str]
    extraction_priority: int
```

### Extraction Types

#### 1. Entity Extraction
Extract specific entities like names, companies, etc.
```json
{
  "field_name": "contact_name",
  "extraction_type": "entity",
  "keywords": ["my name is", "i'm", "i am", "call me"],
  "patterns": ["my name is (\\w+)", "i'm (\\w+)", "i am (\\w+)"],
  "required": true,
  "confidence_threshold": 0.8,
  "fallback_value": "there"
}
```

#### 2. Keyword Extraction
Extract information based on keywords:
```json
{
  "field_name": "pain_points",
  "extraction_type": "keyword",
  "keywords": ["problem", "challenge", "issue", "struggle", "difficulty", "pain"],
  "required": true,
  "confidence_threshold": 0.6
}
```

#### 3. Pattern Extraction
Extract data using regex patterns:
```json
{
  "field_name": "budget_range",
  "extraction_type": "pattern",
  "keywords": ["budget", "cost", "price", "investment"],
  "patterns": ["\\$\\d+", "\\d+\\s*dollars", "budget.*\\$\\d+"],
  "required": false,
  "validation_rules": {"min_amount": 100, "max_amount": 100000}
}
```

#### 4. Sentiment Extraction
Extract sentiment-based information:
```json
{
  "field_name": "objections",
  "extraction_type": "sentiment",
  "keywords": ["concern", "worry", "doubt", "hesitation", "but", "however"],
  "required": false,
  "validation_rules": {"sentiment_threshold": -0.3}
}
```

## 3. Analysis Rules

### Rule Structure
Analysis rules define how to analyze extracted data and trigger actions:

```python
@dataclass
class AnalysisRule:
    rule_name: str
    analysis_type: AnalysisType
    conditions: Dict[str, Any]
    actions: List[str]
    priority: int
    description: str
    is_active: bool
    trigger_threshold: float
```

### Analysis Types

#### 1. Interest Level Detection
```json
{
  "rule_name": "High Interest Detection",
  "analysis_type": "interest_level",
  "conditions": {
    "sentiment_score": ">0.5",
    "keywords": ["interested", "tell me more", "how does it work"],
    "min_turns": 3
  },
  "actions": [
    "Move to solution presentation",
    "Provide detailed information",
    "Schedule demo"
  ],
  "priority": 1,
  "trigger_threshold": 0.7
}
```

#### 2. Budget Concern Detection
```json
{
  "rule_name": "Budget Concern Detection",
  "analysis_type": "budget",
  "conditions": {
    "keywords": ["expensive", "cost", "price", "budget"],
    "sentiment_score": "<0.2"
  },
  "actions": [
    "Address pricing concerns",
    "Offer payment plans",
    "Highlight ROI"
  ],
  "priority": 2,
  "trigger_threshold": 0.6
}
```

#### 3. Authority Level Assessment
```json
{
  "rule_name": "Authority Level Assessment",
  "analysis_type": "authority",
  "conditions": {
    "keywords": ["decision", "approval", "boss", "manager"],
    "response_pattern": "deferral"
  },
  "actions": [
    "Ask for decision maker contact",
    "Provide information for decision maker",
    "Schedule follow-up with decision maker"
  ],
  "priority": 1,
  "trigger_threshold": 0.5
}
```

## 4. LLM Personality

### Personality Structure
Define the LLM's personality and communication style:

```python
@dataclass
class LLMPersonality:
    name: str
    personality_traits: List[PersonalityTrait]
    communication_style: CommunicationStyle
    empathy_level: int  # 1-10 scale
    assertiveness_level: int  # 1-10 scale
    technical_depth: int  # 1-10 scale
    humor_level: int  # 1-10 scale
    formality_level: int  # 1-10 scale
    motive: str  # "sales", "support", "survey", "consultation"
    background_story: str
    expertise_areas: List[str]
    conversation_goals: List[str]
    response_length_preference: str  # "short", "medium", "long"
    tone_adjustment_rules: Dict[str, Any]
```

### Personality Traits
Available personality traits:
- `PROFESSIONAL` - Formal and business-like
- `FRIENDLY` - Warm and approachable
- `ASSERTIVE` - Confident and direct
- `EMPATHETIC` - Understanding and caring
- `TECHNICAL` - Detailed and precise
- `CASUAL` - Relaxed and informal
- `FORMAL` - Structured and proper
- `ENTHUSIASTIC` - Energetic and positive
- `PATIENT` - Calm and understanding
- `CONFIDENT` - Self-assured and bold

### Communication Styles
- `CONVERSATIONAL` - Natural and flowing
- `PROFESSIONAL` - Business-appropriate
- `CASUAL` - Relaxed and informal
- `FORMAL` - Structured and proper
- `TECHNICAL` - Detailed and precise
- `SALES_ORIENTED` - Persuasive and goal-focused
- `SUPPORT_ORIENTED` - Helpful and solution-focused

### Example Personality Configuration:
```json
{
  "name": "Sarah - Sales Professional",
  "personality_traits": ["professional", "friendly", "confident", "empathetic"],
  "communication_style": "sales_oriented",
  "empathy_level": 8,
  "assertiveness_level": 7,
  "technical_depth": 6,
  "humor_level": 4,
  "formality_level": 6,
  "motive": "sales",
  "background_story": "Sarah is a seasoned sales professional with 5 years of experience...",
  "expertise_areas": ["business solutions", "sales process", "customer needs analysis"],
  "conversation_goals": [
    "Build rapport quickly",
    "Understand customer challenges",
    "Present relevant solutions",
    "Address concerns effectively",
    "Secure next steps"
  ],
  "response_length_preference": "medium",
  "tone_adjustment_rules": {
    "formal_customers": {"formality_level": 8, "technical_depth": 7},
    "casual_customers": {"formality_level": 4, "humor_level": 6},
    "technical_customers": {"technical_depth": 8, "formality_level": 7},
    "busy_customers": {"response_length_preference": "short", "assertiveness_level": 8}
  }
}
```

## 5. Document Integration

### Integration Structure
Define how documents are integrated into campaigns:

```python
@dataclass
class DocumentIntegration:
    required_document_types: List[str]
    optional_document_types: List[str]
    document_tags: List[str]
    context_extraction_rules: Dict[str, Any]
    placeholder_mapping: Dict[str, str]
    knowledge_base_priority: int
```

### Example Configuration:
```json
{
  "required_document_types": ["product_info", "policy"],
  "optional_document_types": ["faq", "knowledge_base"],
  "document_tags": ["sales", "product", "company"],
  "context_extraction_rules": {
    "product_info": "extract_features_and_benefits",
    "policy": "extract_company_policies",
    "faq": "extract_common_questions"
  },
  "placeholder_mapping": {
    "product_name": "product_info.product_name",
    "company_name": "policy.company_name",
    "features": "product_info.product_features",
    "benefits": "product_info.product_benefits",
    "pricing": "product_info.pricing_info"
  },
  "knowledge_base_priority": 1
}
```

## 6. Campaign Settings

### Quality Assurance Rules
```json
{
  "quality_assurance_rules": {
    "min_conversation_turns": 10,
    "required_data_fields": ["contact_name", "pain_points"],
    "sentiment_threshold": 0.2,
    "objection_handling_required": true
  }
}
```

### Success Metrics
```json
{
  "success_metrics": {
    "conversion_rate": 0.15,
    "average_call_duration": 600,
    "objection_resolution_rate": 0.8,
    "demo_scheduling_rate": 0.6
  }
}
```

### Custom Settings
```json
{
  "custom_settings": {
    "follow_up_strategy": "email_and_call",
    "demo_duration": 30,
    "pricing_tier": "professional"
  }
}
```

## Template Usage

### 1. Creating Campaigns from Templates
```python
template_manager = TemplateManager()

# Create campaign from template
campaign = template_manager.create_campaign_from_template(
    template_id="template-sales-001",
    customizations={
        "name": "My Custom Sales Campaign",
        "max_call_duration": 1200
    }
)
```

### 2. Template Recommendations
```python
requirements = {
    'motive': 'sales',
    'personality_traits': ['professional', 'friendly'],
    'stage_count': 5,
    'max_duration': 900
}

recommendations = template_manager.get_template_recommendations(requirements)
```

### 3. Template Validation
```python
validation = template_manager.validate_template(template)
if validation['is_valid']:
    print("Template is valid")
else:
    print(f"Errors: {validation['errors']}")
```

### 4. Template Analytics
```python
analytics = template_manager.get_template_analytics(template_id)
print(f"Template has {analytics['template_info']['stages_count']} stages")
print(f"NLP rules: {analytics['template_info']['nlp_rules_count']}")
```

## Template-Driven Workflow

1. **Template Selection**: Choose or create a template based on requirements
2. **Customization**: Modify template parameters as needed
3. **Validation**: Validate template structure and completeness
4. **Campaign Creation**: Generate campaign from template
5. **Document Integration**: Link relevant documents and knowledge base
6. **Deployment**: Deploy campaign with full context and instructions

## Benefits of Template-Driven Approach

1. **Consistency**: All campaigns follow structured, proven patterns
2. **Efficiency**: Quick campaign creation from pre-built templates
3. **Quality**: Built-in validation and quality assurance rules
4. **Flexibility**: Easy customization while maintaining structure
5. **Scalability**: Templates can be reused and shared across teams
6. **Intelligence**: Advanced NLP and analysis rules for better outcomes
7. **Integration**: Seamless document and knowledge base integration

This template structure provides a comprehensive foundation for creating intelligent, document-aware, and personality-driven voice call campaigns.




