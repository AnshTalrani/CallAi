"""
Mid-Conversation Brain Module
Analyzes extracted information and forms strategic instructions for the LLM
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

class AnalysisType(Enum):
    STAGE_TRANSITION = "stage_transition"
    OBJECTION_HANDLING = "objection_handling"
    OPPORTUNITY_DETECTION = "opportunity_detection"
    RISK_ASSESSMENT = "risk_assessment"
    NEXT_ACTION = "next_action"

@dataclass
class ConversationAnalysis:
    analysis_type: AnalysisType
    confidence: float
    reasoning: str
    recommended_action: str
    priority: int  # 1-10, higher is more important
    data_points: Dict[str, Any]

@dataclass
class StrategicInstruction:
    primary_goal: str
    secondary_goals: List[str]
    tone_adjustment: str
    focus_areas: List[str]
    avoid_topics: List[str]
    next_questions: List[str]
    urgency_level: int  # 1-10
    risk_level: int  # 1-10

class MidConversationBrain:
    """Analyzes conversation context and forms strategic instructions"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.extracted_data_history: List[Dict[str, Any]] = []
        self.analysis_results: List[ConversationAnalysis] = []
        
    def analyze_conversation(self, 
                           user_input: str,
                           extracted_data: Dict[str, Any],
                           campaign_context: Dict[str, Any],
                           conversation_state: Dict[str, Any]) -> StrategicInstruction:
        """Analyze the conversation and generate strategic instructions"""
        
        # Store conversation data
        self.conversation_history.append({
            'user_input': user_input,
            'timestamp': conversation_state.get('timestamp'),
            'stage': conversation_state.get('current_stage')
        })
        
        self.extracted_data_history.append(extracted_data)
        
        # Perform various analyses
        analyses = []
        
        # Stage transition analysis
        stage_analysis = self._analyze_stage_transition(extracted_data, conversation_state)
        if stage_analysis:
            analyses.append(stage_analysis)
        
        # Objection handling analysis
        objection_analysis = self._analyze_objections(extracted_data, user_input)
        if objection_analysis:
            analyses.append(objection_analysis)
        
        # Opportunity detection
        opportunity_analysis = self._analyze_opportunities(extracted_data, conversation_state)
        if opportunity_analysis:
            analyses.append(opportunity_analysis)
        
        # Risk assessment
        risk_analysis = self._analyze_risks(extracted_data, user_input)
        if risk_analysis:
            analyses.append(risk_analysis)
        
        # Store analyses
        self.analysis_results.extend(analyses)
        
        # Generate strategic instruction
        return self._generate_strategic_instruction(analyses, campaign_context, conversation_state)
    
    def _analyze_stage_transition(self, extracted_data: Dict[str, Any], conversation_state: Dict[str, Any]) -> Optional[ConversationAnalysis]:
        """Analyze if we should transition to next stage"""
        current_stage = conversation_state.get('current_stage')
        required_data = conversation_state.get('required_data', {})
        
        # Check if we have all required data for current stage
        missing_required = []
        for field, required in required_data.items():
            if required and field not in extracted_data:
                missing_required.append(field)
        
        if not missing_required:
            # All required data collected, consider transition
            confidence = 0.8
            reasoning = f"All required data for {current_stage} stage has been collected"
            recommended_action = "transition_to_next_stage"
            priority = 7
            
            return ConversationAnalysis(
                analysis_type=AnalysisType.STAGE_TRANSITION,
                confidence=confidence,
                reasoning=reasoning,
                recommended_action=recommended_action,
                priority=priority,
                data_points={'missing_required': missing_required, 'current_stage': current_stage}
            )
        
        return None
    
    def _analyze_objections(self, extracted_data: Dict[str, Any], user_input: str) -> Optional[ConversationAnalysis]:
        """Analyze customer objections"""
        objection_keywords = ['expensive', 'cost', 'price', 'budget', 'think about it', 'not sure', 'concerned']
        user_input_lower = user_input.lower()
        
        found_objections = []
        for keyword in objection_keywords:
            if keyword in user_input_lower:
                found_objections.append(keyword)
        
        if found_objections:
            confidence = len(found_objections) / len(objection_keywords) * 0.8
            reasoning = f"Customer expressed objections: {', '.join(found_objections)}"
            recommended_action = "address_objections"
            priority = 9  # High priority for objections
            
            return ConversationAnalysis(
                analysis_type=AnalysisType.OBJECTION_HANDLING,
                confidence=confidence,
                reasoning=reasoning,
                recommended_action=recommended_action,
                priority=priority,
                data_points={'objections': found_objections, 'user_input': user_input}
            )
        
        return None
    
    def _analyze_opportunities(self, extracted_data: Dict[str, Any], conversation_state: Dict[str, Any]) -> Optional[ConversationAnalysis]:
        """Analyze opportunities in the conversation"""
        opportunities = []
        
        # Check for buying signals
        if 'intent' in extracted_data and extracted_data['intent'].get('value') == 'interested':
            opportunities.append('buying_signal')
        
        # Check for budget information
        if 'budget_range' in extracted_data:
            opportunities.append('budget_disclosed')
        
        # Check for decision maker
        if 'decision_maker' in extracted_data:
            opportunities.append('decision_maker_identified')
        
        # Check for urgency
        if 'timeline' in extracted_data and 'urgent' in str(extracted_data['timeline'].get('value', '')).lower():
            opportunities.append('urgency_indicated')
        
        if opportunities:
            confidence = 0.7
            reasoning = f"Detected opportunities: {', '.join(opportunities)}"
            recommended_action = "capitalize_on_opportunities"
            priority = 8
            
            return ConversationAnalysis(
                analysis_type=AnalysisType.OPPORTUNITY_DETECTION,
                confidence=confidence,
                reasoning=reasoning,
                recommended_action=recommended_action,
                priority=priority,
                data_points={'opportunities': opportunities}
            )
        
        return None
    
    def _analyze_risks(self, extracted_data: Dict[str, Any], user_input: str) -> Optional[ConversationAnalysis]:
        """Analyze risks in the conversation"""
        risks = []
        
        # Check for negative sentiment
        if 'sentiment' in extracted_data and extracted_data['sentiment'].get('value') == 'negative':
            risks.append('negative_sentiment')
        
        # Check for disinterest
        if 'intent' in extracted_data and extracted_data['intent'].get('value') == 'not_interested':
            risks.append('disinterest')
        
        # Check for time pressure
        if 'busy' in user_input.lower() or 'time' in user_input.lower():
            risks.append('time_pressure')
        
        if risks:
            confidence = 0.6
            reasoning = f"Identified risks: {', '.join(risks)}"
            recommended_action = "mitigate_risks"
            priority = 6
            
            return ConversationAnalysis(
                analysis_type=AnalysisType.RISK_ASSESSMENT,
                confidence=confidence,
                reasoning=reasoning,
                recommended_action=recommended_action,
                priority=priority,
                data_points={'risks': risks}
            )
        
        return None
    
    def _generate_strategic_instruction(self, 
                                      analyses: List[ConversationAnalysis],
                                      campaign_context: Dict[str, Any],
                                      conversation_state: Dict[str, Any]) -> StrategicInstruction:
        """Generate strategic instruction based on analyses"""
        
        # Sort analyses by priority
        sorted_analyses = sorted(analyses, key=lambda x: x.priority, reverse=True)
        
        # Determine primary goal
        primary_goal = self._determine_primary_goal(sorted_analyses, campaign_context)
        
        # Determine secondary goals
        secondary_goals = self._determine_secondary_goals(sorted_analyses, campaign_context)
        
        # Determine tone adjustment
        tone_adjustment = self._determine_tone_adjustment(sorted_analyses)
        
        # Determine focus areas
        focus_areas = self._determine_focus_areas(sorted_analyses)
        
        # Determine topics to avoid
        avoid_topics = self._determine_avoid_topics(sorted_analyses)
        
        # Generate next questions
        next_questions = self._generate_next_questions(sorted_analyses, conversation_state)
        
        # Determine urgency and risk levels
        urgency_level = self._calculate_urgency_level(sorted_analyses)
        risk_level = self._calculate_risk_level(sorted_analyses)
        
        return StrategicInstruction(
            primary_goal=primary_goal,
            secondary_goals=secondary_goals,
            tone_adjustment=tone_adjustment,
            focus_areas=focus_areas,
            avoid_topics=avoid_topics,
            next_questions=next_questions,
            urgency_level=urgency_level,
            risk_level=risk_level
        )
    
    def _determine_primary_goal(self, analyses: List[ConversationAnalysis], campaign_context: Dict[str, Any]) -> str:
        """Determine the primary goal based on analyses"""
        if not analyses:
            return "continue_conversation"
        
        top_analysis = analyses[0]
        
        if top_analysis.analysis_type == AnalysisType.OBJECTION_HANDLING:
            return "address_objections"
        elif top_analysis.analysis_type == AnalysisType.OPPORTUNITY_DETECTION:
            return "capitalize_on_opportunities"
        elif top_analysis.analysis_type == AnalysisType.STAGE_TRANSITION:
            return "transition_stage"
        elif top_analysis.analysis_type == AnalysisType.RISK_ASSESSMENT:
            return "mitigate_risks"
        
        return "continue_conversation"
    
    def _determine_secondary_goals(self, analyses: List[ConversationAnalysis], campaign_context: Dict[str, Any]) -> List[str]:
        """Determine secondary goals"""
        goals = []
        
        for analysis in analyses[1:3]:  # Take next 2 analyses
            if analysis.analysis_type == AnalysisType.OBJECTION_HANDLING:
                goals.append("build_trust")
            elif analysis.analysis_type == AnalysisType.OPPORTUNITY_DETECTION:
                goals.append("gather_more_info")
            elif analysis.analysis_type == AnalysisType.STAGE_TRANSITION:
                goals.append("prepare_next_stage")
        
        return goals
    
    def _determine_tone_adjustment(self, analyses: List[ConversationAnalysis]) -> str:
        """Determine tone adjustment based on analyses"""
        for analysis in analyses:
            if analysis.analysis_type == AnalysisType.OBJECTION_HANDLING:
                return "empathetic_and_understanding"
            elif analysis.analysis_type == AnalysisType.RISK_ASSESSMENT:
                return "calm_and_reassuring"
            elif analysis.analysis_type == AnalysisType.OPPORTUNITY_DETECTION:
                return "enthusiastic_and_engaging"
        
        return "professional_and_friendly"
    
    def _determine_focus_areas(self, analyses: List[ConversationAnalysis]) -> List[str]:
        """Determine areas to focus on"""
        focus_areas = []
        
        for analysis in analyses:
            if analysis.analysis_type == AnalysisType.OBJECTION_HANDLING:
                focus_areas.append("addressing_concerns")
            elif analysis.analysis_type == AnalysisType.OPPORTUNITY_DETECTION:
                focus_areas.append("exploring_opportunities")
            elif analysis.analysis_type == AnalysisType.STAGE_TRANSITION:
                focus_areas.append("stage_progression")
        
        return focus_areas
    
    def _determine_avoid_topics(self, analyses: List[ConversationAnalysis]) -> List[str]:
        """Determine topics to avoid"""
        avoid_topics = []
        
        for analysis in analyses:
            if analysis.analysis_type == AnalysisType.RISK_ASSESSMENT:
                avoid_topics.append("pricing_details")
                avoid_topics.append("pressure_tactics")
        
        return avoid_topics
    
    def _generate_next_questions(self, analyses: List[ConversationAnalysis], conversation_state: Dict[str, Any]) -> List[str]:
        """Generate next questions to ask"""
        questions = []
        
        for analysis in analyses:
            if analysis.analysis_type == AnalysisType.OBJECTION_HANDLING:
                questions.append("What specific concerns do you have about our solution?")
            elif analysis.analysis_type == AnalysisType.OPPORTUNITY_DETECTION:
                questions.append("What would be the ideal timeline for implementation?")
            elif analysis.analysis_type == AnalysisType.STAGE_TRANSITION:
                questions.append("Are you ready to discuss the next steps?")
        
        return questions
    
    def _calculate_urgency_level(self, analyses: List[ConversationAnalysis]) -> int:
        """Calculate urgency level (1-10)"""
        urgency = 5  # Base level
        
        for analysis in analyses:
            if analysis.analysis_type == AnalysisType.OPPORTUNITY_DETECTION:
                urgency += 2
            elif analysis.analysis_type == AnalysisType.RISK_ASSESSMENT:
                urgency += 1
        
        return min(urgency, 10)
    
    def _calculate_risk_level(self, analyses: List[ConversationAnalysis]) -> int:
        """Calculate risk level (1-10)"""
        risk = 3  # Base level
        
        for analysis in analyses:
            if analysis.analysis_type == AnalysisType.RISK_ASSESSMENT:
                risk += 3
            elif analysis.analysis_type == AnalysisType.OBJECTION_HANDLING:
                risk += 2
        
        return min(risk, 10)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation analysis"""
        return {
            'total_analyses': len(self.analysis_results),
            'conversation_turns': len(self.conversation_history),
            'recent_analyses': [
                {
                    'type': analysis.analysis_type.value,
                    'priority': analysis.priority,
                    'action': analysis.recommended_action
                }
                for analysis in self.analysis_results[-5:]  # Last 5 analyses
            ]
        }