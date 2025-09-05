# CallAi Refactor Plan

## Overview
This document outlines the complete refactoring plan for the CallAi system, moving from a scattered, monolithic architecture to a clean, modular, template-driven system.

## Current Problems
- **Pipeline Fragmentation**: 3 separate pipelines (API → call_agent, langchain_pipeline, conversational_pipeline)
- **Duplicated Logic**: STT/TTS implemented in 3+ places, campaign logic split between managers
- **Tight Coupling**: CallAgent directly imports telephony backends, mixed concerns
- **Missing Abstractions**: No pipeline interface, hard-coded telephony, scattered context building

## New Architecture

### Core Philosophy
- **Template-Driven**: All behavior controlled by campaign templates
- **Modular**: Single responsibility per component
- **Streaming**: Immediate response with filler + barge-in support
- **Testable**: Each service can be tested independently

### File Structure

```
new/
├── orchestrators/                    # 🔄 NEW - Build from scratch
│   ├── call_orchestrator.py          # Call lifecycle + telephony
│   ├── conversation_orchestrator.py  # Main conversation flow
│   └── session_manager.py            # Session state management
├── pipeline/                         # 🔄 NEW - Build from scratch
│   ├── decision_engine.py           # Decision tree execution
│   ├── context_builder.py           # Context assembly 
│   ├── extractor_service.py         # Streaming Extractor LLM
│   ├── response_generator.py        # Response Generator 
│   ├── tool_orchestrator.py         # Tool execution
│   └── llm_client.py                # Base LLM interface (rebuild from llm_thinking.py)
├── audio/                           # 🔄 REFACTOR - From services/
│   ├── stt_service.py               # ASR (refactor from voice_recognition.py)
│   ├── tts_service.py               # TTS (refactor from text_to_speech.py)
│   └── streaming_manager.py         # 🔄 NEW - Handle streaming + barge-in
├── telephony/                       # 🔄 REFACTOR - From telephony/
│   ├── telephony_interface.py       # 🔄 NEW - Abstract interface
│   └── freepbx_adapter.py           # FreePBX implementation (refactor from freepbx_integration.py)
├── repositories/                    # ✅ KEEP - Move from crm/repositories/
│   ├── campaign-specific/            # Per user
│   │   ├── campaign_template_repo.py # (from campaign_repository.py)
│   │   ├── conversation_repo.py      # (from conversation_repository.py)
│   │   ├── documents_repo.py        # (from document_repository.py)
│   │   ├── call_repo.py             # (from call_repository.py)
│   │   └── contact_repo.py          # (from contact_repository.py)
│   └── system/                      # Global
│       ├── users_repo.py            # (from user_repository.py)
│       ├── template_prebuilt_repo.py # (from campaign_template_repository.py)
│       └── base_repository.py      # (from base_repository.py)
├── templates/                       # 🔄 NEW - Build from scratch
│   ├── campaign_template.py         # Template structure (rebuild from crm/models/campaign_template.py)
│   └── template_builder.py          # UI-driven template creation (rebuild from template_manager.py)
├── api/                             # ✅ KEEP - Minor updates
│   ├── app.py                       # Flask API (keep with minor updates)
│   └── data/                        # JSON persistence files (keep as-is)
├── templates/                       # ✅ KEEP - UI templates
│   ├── dashboard.html               # (keep as-is)
│   ├── index.html                   # (keep as-is)
│   ├── login.html                   # (keep as-is)
│   └── phone_setup.html             # (keep as-is)
└── static/                          # ✅ KEEP - Static assets
    ├── app.js                       # (keep as-is)
    └── styles.css                   # (keep as-is)
```

### Migration Tags
- 🔄 **NEW** - Build from scratch
- 🔄 **REFACTOR** - Refactor existing file
- ✅ **KEEP** - Keep with minor updates

## Migration Plan

### Phase 1: Foundation (Keep as-is)
1. **Repositories** - Move to new structure, keep logic
   - `crm/repositories/base_repository.py` → `repositories/system/base_repository.py`
   - `crm/repositories/campaign_repository.py` → `repositories/campaign-specific/campaign_template_repo.py`
   - `crm/repositories/contact_repository.py` → `repositories/campaign-specific/contact_repo.py`
   - `crm/repositories/conversation_repository.py` → `repositories/campaign-specific/conversation_repo.py`
   - `crm/repositories/user_repository.py` → `repositories/system/users_repo.py`
   - `crm/repositories/call_repository.py` → `repositories/campaign-specific/call_repo.py`
   - `crm/repositories/document_repository.py` → `repositories/campaign-specific/documents_repo.py`
   - `crm/repositories/campaign_template_repository.py` → `repositories/system/template_prebuilt_repo.py`

2. **API & UI** - Keep in place, minor updates
   - `api/app.py` - Keep with minor updates
   - `templates/` - Keep HTML templates as-is
   - `static/` - Keep JS/CSS as-is
   - `api/data/` - Keep JSON persistence files

### Phase 2: Core Services (Refactor)
1. **STT Service** - `services/voice_recognition.py` → `audio/stt_service.py`
2. **TTS Service** - `services/text_to_speech.py` → `audio/tts_service.py`  
3. **Telephony** - `telephony/freepbx_integration.py` → `telephony/freepbx_adapter.py`

### Phase 3: New Components (Build from scratch)
1. **Orchestrators** - Build new session management and call orchestration
   - `orchestrators/session_manager.py`
   - `orchestrators/call_orchestrator.py`
   - `orchestrators/conversation_orchestrator.py`

2. **Pipeline** - Build new modular pipeline components
   - `pipeline/decision_engine.py`
   - `pipeline/context_builder.py` (rebuild from `core/document_manager.py`)
   - `pipeline/extractor_service.py`
   - `pipeline/response_generator.py` (rebuild from `services/llm_thinking.py`)
   - `pipeline/tool_orchestrator.py`
   - `pipeline/llm_client.py` (rebuild from `services/llm_thinking.py`)

3. **Templates** - Build new template system
   - `templates/campaign_template.py` (rebuild from `crm/models/campaign_template.py`)
   - `templates/template_builder.py` (rebuild from `core/template_manager.py`)

4. **Audio Streaming** - Build new streaming manager
   - `audio/streaming_manager.py`

5. **Telephony Interface** - Build abstract interface
   - `telephony/telephony_interface.py`

### Phase 4: Integration
1. **Wire components** together
2. **Test end-to-end** flow
3. **Migrate data** if needed

### Files to Remove
- `telephony/asterisk_integration.py`
- `telephony/freeswitch_integration.py`
- `core/campaign_templates.py`
- `langchain_pipeline.py` (replace with new pipeline)
- `services/conversational_pipeline.py` (replace with orchestrators)
- `core/call_agent.py` (replace with orchestrators)

## Component Details

### 1. Session Manager (`orchestrators/session_manager.py`)

**Purpose**: Maintains per-call state and manages conversation flow

**Responsibilities**:
- Maintains per-call state: conversation history, user metadata, campaign context, extracted signals
- Tracks active tool calls and LLM streams
- Manages barge-in events (user interrupts ongoing TTS/stream)

**Data Structure**:
```python
{
  "session_id": "abc123",
  "conversation_history": [
    {"role": "user", "text": "..."},
    {"role": "assistant", "text": "..."}
  ],
  "extracted_signals": {
    "intent": "interested_but_delay",
    "entities": {...},
    "filler": "Sure, let me check that for you..."
  },
  "campaign_stage": "warm_lead",
  "active_tools": [],
  "tts_state": {
    "current_stream": null,
    "barge_in_requested": false
  }
}
```

### 2. Streaming Extractor LLM (`pipeline/extractor_service.py`)

**Purpose**: Parse user input into structured signals (intent, entities, stage)

**Responsibilities**:
- Extract intent, entities, and stage from user input
- Generate optional filler if tool call may be required
- Use small-medium LLM (MiniLM, LLaMA-3 7–8B) quantized for speed
- Support streaming mode for immediate filler tokens

**Input**:
- Last N conversation turns (context window)
- User utterance
- Optional campaign rules / persona hints

**Output**:
```python
{
  "intent": "interested_but_delay",
  "entities": {"project": "AI Platform", "timeframe": "next week"},
  "filler": "Sure, let me check that for you..."
}
```

**LangChain Integration**:
```python
from langchain.schema import BaseOutputParser
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class ExtractedSignalsParser(BaseOutputParser):
    def parse(self, text: str) -> ExtractedSignals:
        return ExtractedSignals.from_json(text)

class ExtractorService:
    def __init__(self):
        self.chain = LLMChain(
            llm=self.extractor_llm,
            prompt=PromptTemplate(
                template="Extract intent, entities, and stage from: {input}",
                input_variables=["input"]
            ),
            output_parser=ExtractedSignalsParser()
        )
    
    async def extract_signals(self, utterance: str, template: CampaignTemplate):
        return await self.chain.arun(input=utterance)
```

**Why LangChain Helps**: Structured output parsing, prompt templating, and chain composition are exactly what LangChain excels at.

### 3. Decision Engine (`pipeline/decision_engine.py`)

**Purpose**: Algorithmic decision making based on campaign template decision trees

**Responsibilities**:
- Read extracted signals + campaign template
- Determine next actions:
  - Which tools to call (web search, CRM, DB)
  - Discount logic or offers
  - Update stage / internal state
  - Whether filler is needed
- Handle stage transitions (replaces stage_engine)

**LangChain Integration**:
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class DecisionEngine:
    def __init__(self):
        self.decision_prompt = PromptTemplate(
            template="""
            Based on the extracted signals and campaign rules, decide:
            - Which tools to call: {tool_options}
            - Next stage: {stage_options}
            - Use filler: {filler_needed}
            
            Signals: {signals}
            Template Rules: {template_rules}
            """,
            input_variables=["signals", "template_rules", "tool_options", "stage_options", "filler_needed"]
        )
        
        self.chain = LLMChain(
            llm=self.decision_llm,
            prompt=self.decision_prompt
        )
    
    async def make_decision(self, signals: ExtractedSignals, template: CampaignTemplate):
        return await self.chain.arun(
            signals=signals,
            template_rules=template.conversation_rules,
            tool_options=template.tool_configs,
            stage_options=template.stage_transitions,
            filler_needed=template.filler_rules
        )
```

**Why LangChain Helps**: Complex decision logic with structured prompts benefits from LangChain's prompt management.

### 4. Tool Orchestrator (`pipeline/tool_orchestrator.py`)

**Purpose**: Execute tools asynchronously with barge-in support

**Responsibilities**:
- Run tool calls asynchronously (web search, RAG, CRM)
- Stream filler immediately if flagged
- Handle partial streaming / barge-in: user can interrupt while tool is running
- Use documents provided by campaign template

**LangChain Integration**:
```python
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

class ToolOrchestrator:
    def __init__(self):
        self.tools = [
            Tool(name="web_search", func=self.web_search),
            Tool(name="crm_lookup", func=self.crm_lookup),
            Tool(name="document_search", func=self.document_search)
        ]
        
        self.agent = create_react_agent(
            llm=self.tool_llm,
            tools=self.tools,
            prompt=self.create_tool_prompt()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    async def execute_tools(self, tool_decisions: List[ToolDecision], template: CampaignTemplate):
        return await self.agent_executor.arun(
            input=f"Execute tools: {tool_decisions}",
            context=template.business_context
        )
```

**Why LangChain Helps**: Tool abstraction, agent execution, and ReAct pattern are perfect for this use case.

### 5. Response Generator (`pipeline/response_generator.py`)

**Purpose**: Generate natural, context-aware responses with streaming

**Responsibilities**:
- Take conversation context + extracted signals + tool results
- Produce natural, context-aware response, streamed token-by-token
- Support interruptions (barge-in): stop current stream if user speaks
- Use streaming LLM API to push tokens to TTS immediately

**Input to LLM**:
```
SYSTEM: You are a polite assistant. (sales/customer support/survey, depends on campaign template)
CONTEXT: <conversation_history>
SIGNALS: <extracted_signals>
TOOL_RESULTS: <search snippet or CRM data>
System instructions (decision engine result): Generate final response to user, follow campaign tone, confirm next step.
```

**LangChain Integration**:
```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate

class ResponseGenerator:
    def __init__(self):
        self.memory = ConversationBufferWindowMemory(k=5)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are {personality}"),
            ("human", "{user_input}"),
            ("assistant", "{context}")
        ])
        
        self.chain = ConversationChain(
            llm=self.response_llm,
            memory=self.memory,
            prompt=self.prompt
        )
    
    async def generate_response(self, context: Context, template: CampaignTemplate):
        return await self.chain.arun(
            personality=template.personality,
            user_input=context.user_input,
            context=context.tool_results
        )
```

**Why LangChain Helps**: Conversation memory management, prompt templating, and streaming responses are core LangChain features.

### 6. Context Builder (`pipeline/context_builder.py`)

**Purpose**: Context assembly from documents and conversation history

**LangChain Integration**:
```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ContextBuilder:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
        self.vectorstore = None
    
    async def build_context(self, documents: List[Document], conversation_history: List[Message]):
        # Build vector store from documents
        texts = self.text_splitter.split_texts([doc.content for doc in documents])
        self.vectorstore = FAISS.from_texts(texts, self.embeddings)
        
        # Create retrieval chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.context_llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )
        
        return await qa_chain.arun(query=conversation_history[-1].content)
```

**Why LangChain Helps**: Document retrieval, vector stores, and context building are core LangChain features.

### 7. Components NOT Using LangChain

**Session Manager (`orchestrators/session_manager.py`)**: ❌ **Pure state management** - LangChain doesn't add value here

**STT Service (`audio/stt_service.py`)**: ❌ **Pure audio processing** - Keep current Whisper implementation

**TTS Service (`audio/tts_service.py`)**: ❌ **Pure audio synthesis** - Keep current Kokoro implementation

**Repositories**: ❌ **Pure data persistence** - Keep current repository pattern

**API Layer**: ❌ **Pure web API** - Keep current Flask implementation

## Campaign Template System

### Template Structure
```python
class CampaignTemplate:
    # Structure (same for all templates)
    stages: List[Stage]           # introduction, needs, solution, closing
    stage_transitions: Dict       # when to move between stages
    data_collection: List[str]    # what to extract from user
    conversation_rules: Dict     # how to handle different scenarios
    
    # Content (different per use case)
    scripts: Dict[str, str]      # what to say in each stage
    personality: Dict            # agent personality
    business_context: Dict       # company/product info
    custom_fields: Dict          # user-specific data
```

### Template Creation Process
1. **Pre-built Templates**: Sales, customer support, survey, etc.
2. **User Selection**: Users choose template and customize content
3. **UI-Driven**: Campaign creation UI builds campaign template
4. **Document Upload**: Per campaign type (policy docs for support, product docs for sales)

### Template Integration
- **Conversation Orchestrator** reads templates to understand structure
- **Decision Engine** uses template decision trees
- **Response Generator** uses template scripts and personality
- **Tool Orchestrator** uses template documents

## Template-Module Connections

### Template → Conversation Orchestrator
```python
# Conversation Orchestrator loads template at call start
class ConversationOrchestrator:
    def __init__(self, template_repo):
        self.template_repo = template_repo
    
    async def start_conversation(self, campaign_id: str):
        template = await self.template_repo.get_by_campaign_id(campaign_id)
        # Template drives entire conversation flow
        return await self.process_with_template(template)
```

### Template → Session Manager
```python
# Session Manager stores template context
class SessionManager:
    async def create_session(self, call_id: str, template: CampaignTemplate):
        session_state = {
            "campaign_template": template,
            "current_stage": template.stages[0],
            "stage_rules": template.stage_transitions,
            "data_fields": template.data_collection,
            "personality": template.personality
        }
        return session_state
```

### Template → Extractor Service
```python
# Extractor uses template rules for signal extraction
class ExtractorService:
    async def extract_signals(self, utterance: str, template: CampaignTemplate):
        # Template defines what entities to extract
        entities = self.extract_entities(utterance, template.data_collection)
        # Template defines intent classification rules
        intent = self.classify_intent(utterance, template.conversation_rules)
        return ExtractedSignals(intent, entities, template.personality)
```

### Template → Decision Engine
```python
# Decision Engine uses template decision trees
class DecisionEngine:
    async def make_decision(self, signals: ExtractedSignals, template: CampaignTemplate):
        # Template defines decision tree logic
        decision_tree = template.conversation_rules["decision_tree"]
        # Template defines stage transition rules
        stage_rules = template.stage_transitions[signals.current_stage]
        return Decision(tool_calls, next_stage, use_filler)
```

### Template → Tool Orchestrator
```python
# Tool Orchestrator uses template documents
class ToolOrchestrator:
    async def execute_tools(self, tool_decisions: List[ToolDecision], template: CampaignTemplate):
        # Template provides documents for RAG
        documents = template.business_context["documents"]
        # Template defines tool configurations
        tool_configs = template.conversation_rules["tools"]
        return await self.run_tools(tool_decisions, documents, tool_configs)
```

### Template → Response Generator
```python
# Response Generator uses template scripts and personality
class ResponseGenerator:
    async def generate_response(self, context: Context, template: CampaignTemplate):
        # Template provides stage-specific scripts
        script = template.scripts[context.current_stage]
        # Template defines personality and tone
        personality = template.personality
        # Template provides business context
        business_context = template.business_context
        return await self.generate_with_template(script, personality, business_context)
```

### Template → Audio Services
```python
# TTS uses template voice settings
class TTSService:
    async def generate_speech(self, text: str, template: CampaignTemplate):
        # Template defines voice characteristics
        voice_settings = template.personality["voice_settings"]
        # Template defines speaking style
        speaking_style = template.personality["speaking_style"]
        return await self.synthesize_with_style(text, voice_settings, speaking_style)
```

### Template → Repositories
```python
# Campaign Template Repository
class CampaignTemplateRepository:
    async def get_by_campaign_id(self, campaign_id: str) -> CampaignTemplate:
        # Load template associated with campaign
        return await self.find_template_for_campaign(campaign_id)
    
    async def get_prebuilt_templates(self) -> List[CampaignTemplate]:
        # Return available pre-built templates
        return await self.find_prebuilt_templates()

# Document Repository uses template document requirements
class DocumentRepository:
    async def get_template_documents(self, template: CampaignTemplate) -> List[Document]:
        # Template defines required document types
        required_types = template.business_context["required_documents"]
        return await self.find_by_types(required_types)
```

## Template Flow Diagram

```
Campaign Template (Created via UI)
         ↓
    Loaded by Conversation Orchestrator
         ↓
    ┌─────────────────────────────────────┐
    │  Template drives all components:   │
    │                                     │
    │  Session Manager ← Template State   │
    │  Extractor ← Template Rules         │
    │  Decision Engine ← Template Trees   │
    │  Tool Orchestrator ← Template Docs │
    │  Response Generator ← Template Scripts │
    │  TTS ← Template Voice Settings      │
    │  Repositories ← Template Data       │
    └─────────────────────────────────────┘
```

## Template Structure Alignment

### Why Template Structure Must Match Conversation Orchestrator

**YES** - The Campaign Template structure should exactly match the Conversation Orchestrator flow because:

1. **Single Source of Truth**: Template defines the exact flow that Conversation Orchestrator executes
2. **Predictable Behavior**: Same structure = same execution path
3. **Easy Validation**: Can validate template against orchestrator requirements
4. **Maintainable**: Changes to orchestrator flow automatically reflect in template structure
5. **Testable**: Can test template → orchestrator mapping directly

### Template Structure Mirroring Orchestrator Flow

```python
class CampaignTemplate:
    # Matches ConversationOrchestrator.process_user_input()
    session_config: SessionConfig          # → SessionManager
    extraction_rules: ExtractionRules      # → ExtractorService  
    decision_tree: DecisionTree           # → DecisionEngine
    tool_configs: ToolConfigs             # → ToolOrchestrator
    response_templates: ResponseTemplates # → ResponseGenerator
    audio_settings: AudioSettings         # → TTSService
    
    # Each section maps directly to orchestrator method
    def to_orchestrator_config(self) -> OrchestratorConfig:
        return OrchestratorConfig(
            session_manager_config=self.session_config,
            extractor_config=self.extraction_rules,
            decision_engine_config=self.decision_tree,
            tool_orchestrator_config=self.tool_configs,
            response_generator_config=self.response_templates,
            audio_config=self.audio_settings
        )
```

### Template Validation Against Orchestrator

```python
class TemplateValidator:
    def validate_template(self, template: CampaignTemplate) -> ValidationResult:
        """Validate template structure matches orchestrator requirements"""
        
        # Check session config matches SessionManager interface
        session_valid = self.validate_session_config(template.session_config)
        
        # Check extraction rules match ExtractorService interface
        extraction_valid = self.validate_extraction_rules(template.extraction_rules)
        
        # Check decision tree matches DecisionEngine interface
        decision_valid = self.validate_decision_tree(template.decision_tree)
        
        # Check tool configs match ToolOrchestrator interface
        tool_valid = self.validate_tool_configs(template.tool_configs)
        
        # Check response templates match ResponseGenerator interface
        response_valid = self.validate_response_templates(template.response_templates)
        
        return ValidationResult(
            is_valid=all([session_valid, extraction_valid, decision_valid, tool_valid, response_valid]),
            errors=self.collect_errors()
        )
```

## UI Integration

### Current UI Status
- **Solid foundation** - just needs campaign creation/display improvements
- **Campaign creation** → **Campaign Template** → **Campaign execution**

### Required UI Improvements
1. **Campaign Creation**:
   - Template selection and customization
   - Document upload per campaign type
   - Rich form for template configuration

2. **Campaign Display**:
   - All columns: stages, user extraction columns, call timings
   - Conversation summaries and detailed analytics
   - Campaign template visualization

3. **Document Management**:
   - Upload company policy docs for support campaigns
   - Upload product pitch/USP docs for sales campaigns
   - Document categorization and tagging

## Orchestrated Flow

### Step-by-Step Process
1. **User speaks** → ASR → transcript
2. **Extractor LLM** parses input → outputs structured signals + optional filler
3. **Session Manager** stores signals
4. **Decision Engine** reads signals → determines:
   - Tool calls required?
   - Stage updates?
   - Use filler?
5. **If filler** → Response LLM (or filler from extractor) streamed to TTS immediately
6. **Tool Orchestrator** runs async queries
7. **Tool completes** → Response Generator LLM combines context + tool result → streams final response
8. **Session Manager** updates state (conversation history, campaign stage)
9. **User can barge-in** → interrupts filler / response → go back to step 1 with new input

### Integration Points
- **Call Orchestrator** creates sessions and manages telephony
- **Conversation Orchestrator** coordinates the entire flow
- **Session Manager** maintains state throughout
- **All Pipeline services** work together seamlessly



