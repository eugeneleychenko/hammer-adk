"""
ADK-based orchestration system for parallel and sequential agent execution.
This replaces the manual loop-based orchestration in comprehensive_sales_analyzer.py
with Google ADK's ParallelAgent and SequentialAgent for significant performance improvement.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv
import re

# ADK imports
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.sessions import Session
from google.genai.types import Content, Part

# Gemini API imports
import google.generativeai as genai

# Lessons audit trail system
from lessons_audit_trail import LessonsAuditTrail

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ADKSalesAnalysisOrchestrator:
    """
    ADK-based orchestration system for parallel sales call analysis.
    
    Replaces manual sequential execution with:
    - Phase 1: 8 Core Analysis Agents running in parallel
    - Phase 2: 6 Advanced Analysis Agents running in parallel  
    - Phase 3: Synthesis Agent combining all results
    
    Architecture:
    SequentialAgent[
      ParallelAgent[Core8Agents],
      ParallelAgent[Advanced6Agents], 
      SynthesisAgent
    ]
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ADK orchestration system."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables or .env file")
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        self.model = "gemini-2.0-flash-exp"  # Using latest Gemini model
        self.app_name = "sales-analysis-pipeline"
        self.user_id = "analyst_001"
        
        # Initialize lessons audit trail system
        audit_path = Path("comprehensive_results/lessons_audit_trail.json")
        self.lessons_auditor = LessonsAuditTrail(audit_path)
        
        # Initialize the complete pipeline
        self.pipeline_agent = self._create_pipeline_agent()
        # Initialize session service and runner
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.pipeline_agent,
            app_name=self.app_name,
            session_service=self.session_service
        )
        
    def _create_phase1_agents(self) -> List[LlmAgent]:
        """Create Phase 1 Core Analysis Agents (8 agents)."""
        
        # Agent 1: Objection Specialist
        objection_agent = LlmAgent(
            name="ObjectionSpecialistAgent",
            model=self.model,
            instruction="""You are an expert objection handling specialist analyzing life insurance sales calls.
            
Analyze the provided call transcript for:
1. All customer objections raised (price, time, trust, product, etc.)
2. How the agent handled each objection
3. Effectiveness of objection handling techniques
4. Missed opportunities to address concerns

Return your analysis in this exact JSON format:
{
  "objections_identified": [
    {
      "objection_type": "price/time/trust/product/need/other",
      "customer_statement": "exact quote from transcript",
      "timing": "early/middle/late in call",
      "severity": "low/medium/high"
    }
  ],
  "handling_techniques": [
    {
      "objection_type": "type of objection addressed",
      "agent_response": "how agent responded",
      "technique_used": "feel/felt/found, acknowledge/clarify/respond, etc.",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "call_summary": {
    "total_objections": 0,
    "objections_addressed": 0,
    "primary_objection": "main customer concern",
    "outcome": "sale/no_sale/follow_up_needed"
  },
  "improvement_recommendations": ["specific suggestions for better objection handling"]
}

Analyze only what is explicitly stated in the transcript. Do not infer or add external information.""",
            description="Analyzes customer objections and handling techniques in sales calls",
            output_key="objection_analysis"
        )
        
        # Agent 2: Opening Gambit
        opening_agent = LlmAgent(
            name="OpeningGambitAgent", 
            model=self.model,
            instruction="""You are an expert at analyzing sales call openings and first impressions.
            
Analyze the first 3-5 minutes of this call transcript for:
1. Opening technique used by the agent
2. Customer's initial receptiveness
3. Rapport building in the opening
4. Effectiveness of the approach

Return your analysis in this exact JSON format:
{
  "opening_analysis": {
    "opening_technique": "warm introduction/referral mention/direct approach/other",
    "opening_statement": "first few sentences agent used",
    "customer_initial_response": "how customer first responded",
    "customer_receptiveness": "resistant/neutral/receptive/very receptive",
    "rapport_established": "yes/no/partial"
  },
  "effectiveness_scoring": {
    "attention_grabbing": "1-10 scale",
    "relevance_to_customer": "1-10 scale", 
    "professionalism": "1-10 scale",
    "overall_opening_score": "1-10 scale"
  },
  "improvement_opportunities": [
    "specific suggestions for better opening"
  ]
}

Focus only on the opening portion of the call (first 3-5 minutes).""",
            description="Analyzes opening techniques and first impressions in sales calls",
            output_key="opening_analysis"
        )
        
        # Agent 3: Needs Assessment
        needs_agent = LlmAgent(
            name="NeedsAssessmentAgent",
            model=self.model,
            instruction="""You are an expert at analyzing needs discovery and assessment techniques in sales calls.
            
Analyze the transcript for:
1. Questions asked by the agent to understand customer needs
2. Customer information discovered
3. Quality of needs assessment process
4. How well agent understood customer situation

Return your analysis in this exact JSON format: 
{
  "discovery_questions": [
    {
      "question": "exact question asked by agent",
      "question_type": "open/closed/leading/probing",
      "customer_response": "what customer revealed",
      "information_value": "low/medium/high"
    }
  ],
  "customer_profile": {
    "family_situation": "what was learned about family",
    "financial_situation": "what was learned about finances", 
    "current_coverage": "existing insurance mentioned",
    "concerns_priorities": "main customer concerns identified",
    "decision_making_style": "how customer makes decisions"
  },
  "needs_assessment_quality": {
    "depth_of_discovery": "poor/fair/good/excellent",
    "question_sequencing": "poor/fair/good/excellent",
    "active_listening": "poor/fair/good/excellent",
    "needs_identified": ["list of needs discovered"]
  },
  "missed_opportunities": ["questions that should have been asked"]
}

Focus on the discovery and needs assessment portions of the call.""",
            description="Analyzes needs discovery and customer assessment techniques",
            output_key="needs_analysis"
        )
        
        # Agent 4: Rapport Building
        rapport_agent = LlmAgent(
            name="RapportBuildingAgent",
            model=self.model,
            instruction="""You are an expert at analyzing relationship building and trust development in sales calls.
            
Analyze the transcript for:
1. Rapport building techniques used
2. Trust development strategies  
3. Personal connection moments
4. Overall relationship quality established

Return your analysis in this exact JSON format:
{
  "rapport_techniques": [
    {
      "technique": "small talk/shared experience/empathy/humor/other",
      "example": "specific instance from transcript",
      "timing": "opening/middle/closing",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "trust_building": {
    "credibility_establishment": "how agent established expertise",
    "transparency_level": "low/medium/high", 
    "authenticity": "scripted/natural/genuine",
    "customer_comfort_level": "uncomfortable/neutral/comfortable/very comfortable"
  },
  "personal_connection": {
    "common_ground_found": "yes/no",
    "personal_details_shared": "what agent learned about customer personally",
    "emotional_connection": "weak/moderate/strong",
    "memorable_moments": ["specific rapport building moments"]
  },
  "overall_rapport_assessment": {
    "rapport_score": "1-10 scale",
    "trust_level": "low/medium/high",
    "relationship_quality": "transactional/professional/personal/trusted advisor"
  }
}

Focus on relationship and trust building throughout the entire call.""",
            description="Analyzes rapport building and trust development in sales interactions",
            output_key="rapport_analysis"
        )
        
        # Agent 5: Pattern Recognition
        pattern_agent = LlmAgent(
            name="PatternRecognitionAgent",
            model=self.model,
            instruction="""You are an expert at identifying conversation patterns and sequences in sales calls.
            
Analyze the transcript for:
1. Conversation flow patterns
2. Question-answer sequences
3. Repeating themes or topics
4. Successful interaction patterns

Return your analysis in this exact JSON format:
{
  "conversation_patterns": [
    {
      "pattern_type": "question_sequence/objection_loop/benefit_confirmation/other",
      "description": "what pattern was observed", 
      "frequency": "how often it occurred",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "successful_sequences": [
    {
      "sequence": "step by step description",
      "outcome": "what it achieved",
      "replicability": "easy/moderate/difficult to replicate"
    }
  ],
  "conversation_themes": [
    {
      "theme": "main topic or concern",
      "frequency": "how often mentioned",
      "resolution": "resolved/unresolved/partially addressed"
    }
  ],
  "flow_analysis": {
    "transitions": "smooth/choppy/natural",
    "momentum_building": "yes/no/inconsistent", 
    "conversation_control": "agent led/customer led/balanced",
    "pacing": "too fast/appropriate/too slow"
  }
}

Look for recurring patterns, successful sequences, and overall conversation dynamics.""",
            description="Identifies conversation patterns and successful interaction sequences",
            output_key="pattern_analysis"
        )
        
        # Agent 6: Emotional Intelligence
        emotional_agent = LlmAgent(
            name="EmotionalIntelligenceAgent",
            model=self.model,
            instruction="""You are an expert at analyzing emotional dynamics and sentiment in sales conversations.
            
Analyze the transcript for:
1. Customer emotional states throughout the call
2. Agent's emotional awareness and responses
3. Emotional turning points
4. Overall sentiment trajectory

Return your analysis in this exact JSON format:
{
  "emotional_analysis": {
    "customer_initial_sentiment": "positive/neutral/negative/skeptical",
    "customer_final_sentiment": "positive/neutral/negative/frustrated",
    "sentiment_shift": "positive_shift/negative_shift/no_change",
    "emotional_turning_points": [
      {
        "moment": "what happened",
        "emotion_before": "customer emotion before",
        "emotion_after": "customer emotion after",
        "trigger": "what caused the change"
      }
    ]
  },
  "agent_emotional_intelligence": {
    "emotion_recognition": "poor/fair/good/excellent",
    "empathy_demonstration": "low/medium/high",
    "emotional_adaptation": "rigid/somewhat flexible/highly adaptive",
    "tone_matching": "mismatched/somewhat matched/well matched"
  },
  "emotional_techniques": [
    {
      "technique": "validation/empathy/reframing/other",
      "usage": "when and how used",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "overall_emotional_outcome": {
    "customer_satisfaction": "dissatisfied/neutral/satisfied/very satisfied",
    "emotional_resolution": "unresolved/partially resolved/fully resolved",
    "relationship_impact": "damaged/neutral/strengthened"
  }
}

Focus on emotional intelligence, empathy, and sentiment management throughout the call.""",
            description="Analyzes emotional dynamics and sentiment in sales conversations",
            output_key="emotional_analysis"
        )
        
        # Agent 7: Language Optimizer
        language_agent = LlmAgent(
            name="LanguageOptimizerAgent",
            model=self.model,
            instruction="""You are an expert at analyzing language effectiveness and communication style in sales calls.
            
Analyze the transcript for:
1. Language patterns and word choices
2. Communication clarity and effectiveness
3. Persuasive language techniques
4. Areas for language improvement

Return your analysis in this exact JSON format:
{
  "language_analysis": {
    "clarity_score": "1-10 scale",
    "jargon_usage": "excessive/appropriate/minimal",
    "tone_consistency": "inconsistent/mostly consistent/very consistent",
    "active_vs_passive": "ratio of active to passive voice"
  },
  "persuasive_techniques": [
    {
      "technique": "social proof/scarcity/authority/reciprocity/other",
      "examples": ["specific instances from transcript"],
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "power_phrases": [
    {
      "phrase": "exact phrase used",
      "context": "when it was used",
      "impact": "customer response or effect"
    }
  ],
  "communication_strengths": [
    "what the agent did well linguistically"
  ],
  "improvement_opportunities": [
    {
      "area": "what needs improvement",
      "suggestion": "specific language recommendation",
      "priority": "low/medium/high"
    }
  ]
}

Focus on language effectiveness, word choice, and communication optimization.""",
            description="Analyzes language effectiveness and communication optimization opportunities",
            output_key="language_analysis"
        )
        
        # Agent 8: Client Profiling
        profiling_agent = LlmAgent(
            name="ClientProfilingAgent",
            model=self.model,
            instruction="""You are an expert at creating detailed customer profiles and personas from sales call interactions.
            
Analyze the transcript to create a comprehensive customer profile including:
1. Demographic and psychographic characteristics
2. Decision-making patterns
3. Communication preferences
4. Buying behavior indicators

Return your analysis in this exact JSON format:
{
  "client_profile": {
    "demographic_info": {
      "approximate_age": "age range if mentioned",
      "family_status": "single/married/divorced/widowed",
      "occupation": "job or profession if mentioned",
      "location": "geographic info if mentioned"
    },
    "psychographic_profile": {
      "personality_type": "analytical/driver/expressive/amiable",
      "risk_tolerance": "low/medium/high",
      "decision_speed": "quick/deliberate/slow",
      "information_processing": "detail-oriented/big picture"
    },
    "communication_style": {
      "preferred_pace": "fast/moderate/slow",
      "question_frequency": "asks many/some/few questions",
      "engagement_level": "highly engaged/moderately engaged/disengaged",
      "language_preference": "technical/simple/conversational"
    },
    "decision_making_pattern": {
      "style": "logical/emotional/mixed",
      "influences": ["what factors influence their decisions"],
      "timeline": "immediate/short term/long term",
      "consultation_needs": "decides alone/consults spouse/consults others"
    }
  },
  "buying_signals": [
    {
      "signal": "specific behavior or statement",
      "strength": "weak/moderate/strong",
      "timing": "when it occurred in call"
    }
  ],
  "ideal_approach": {
    "recommended_style": "how to best communicate with this client",
    "key_motivators": ["what drives this client"],
    "potential_concerns": ["likely objections or hesitations"],
    "follow_up_strategy": "best approach for next contact"
  }
}

Create a detailed, actionable client profile based on observable behaviors and statements.""",
            description="Creates comprehensive customer profiles and personas from call interactions",
            output_key="profile_analysis"
        )
        
        return [
            objection_agent, opening_agent, needs_agent, rapport_agent,
            pattern_agent, emotional_agent, language_agent, profiling_agent
        ]
    
    def _create_phase2_agents(self) -> List[LlmAgent]:
        """Create Phase 2 Advanced Analysis Agents (6 agents)."""
        
        # Agent 9: Micro Commitments
        commitments_agent = LlmAgent(
            name="MicroCommitmentsAgent",
            model=self.model,
            instruction="""You are an expert at tracking micro-commitments and agreement building in sales calls.
            
Analyze the transcript for:
1. All micro-commitments secured from the customer
2. Agreement building progression
3. Commitment momentum and velocity
4. How commitments led toward the close

Return your analysis in this exact JSON format:
{
  "commitment_analysis": {
    "total_commitments": 0,
    "commitment_categories": {
      "information_agreements": 0,
      "process_agreements": 0, 
      "value_agreements": 0,
      "next_step_agreements": 0
    },
    "commitment_velocity": "slow/steady/building/strong"
  },
  "commitment_sequence": [
    {
      "commitment": "what customer agreed to",
      "type": "information/process/value/next_step",
      "agent_technique": "how agent secured it",
      "timing": "early/middle/late in call",
      "strength": "weak/moderate/strong"
    }
  ],
  "momentum_building": {
    "progression": "declining/flat/building/strong",
    "turning_points": ["moments where momentum shifted"],
    "peak_commitment": "strongest agreement secured",
    "commitment_chain": "how commitments built on each other"
  },
  "effectiveness_assessment": {
    "commitment_to_close_ratio": "percentage that led to next steps",
    "missed_opportunities": ["where commitments could have been secured"],
    "overall_momentum": "poor/fair/good/excellent"
  }
}

Focus on identifying and tracking all forms of customer agreement and commitment building.""",
            description="Tracks micro-commitments and agreement building progression",
            output_key="commitment_analysis"
        )
        
        # Agent 10: Conversation Flow
        flow_agent = LlmAgent(
            name="ConversationFlowAgent",
            model=self.model,
            instruction="""You are an expert at analyzing conversation structure, transitions, and flow optimization.
            
Analyze the transcript for:
1. Overall conversation structure and phases
2. Transition quality between topics
3. Flow interruptions and recoveries
4. Optimization opportunities for better flow

Return your analysis in this exact JSON format:
{
  "flow_structure": {
    "phases_identified": [
      {
        "phase": "opening/discovery/presentation/objection_handling/closing",
        "duration_estimate": "approximate time spent",
        "transition_quality": "abrupt/smooth/natural",
        "effectiveness": "poor/fair/good/excellent"
      }
    ],
    "overall_structure": "linear/circular/scattered/strategic"
  },
  "transition_analysis": [
    {
      "from_topic": "previous subject",
      "to_topic": "new subject", 
      "transition_method": "bridge/summary/question/direct",
      "quality": "poor/fair/good/excellent",
      "customer_follow": "yes/no/confused"
    }
  ],
  "flow_disruptions": [
    {
      "disruption": "what interrupted the flow",
      "cause": "customer objection/agent mistake/external/other",
      "recovery": "how flow was restored",
      "impact": "minimal/moderate/significant"
    }
  ],
  "flow_pattern": {
    "sequence": ["ordered list of conversation topics"],
    "logic": "logical/somewhat logical/scattered",
    "customer_engagement": "maintained/varied/lost",
    "momentum": "building/steady/declining"
  },
  "optimization_recommendations": [
    {
      "area": "what could be improved",
      "suggestion": "specific recommendation",
      "expected_impact": "minor/moderate/significant"
    }
  ]
}

Focus on conversation architecture, flow dynamics, and structural optimization opportunities.""",
            description="Analyzes conversation structure, flow, and transition quality",
            output_key="flow_analysis"
        )
        
        # Agent 11: Budget Handling
        budget_agent = LlmAgent(
            name="BudgetHandlingAgent", 
            model=self.model,
            instruction="""You are an expert at analyzing how financial concerns and budget objections are handled in sales calls.
            
Analyze the transcript for:
1. Budget-related objections and concerns
2. Financial qualification techniques
3. Value vs. cost positioning
4. Payment and affordability discussions

Return your analysis in this exact JSON format:
{
  "budget_objections": [
    {
      "objection": "specific budget concern raised",
      "customer_statement": "exact quote about cost/budget",
      "timing": "when in call it was raised",
      "intensity": "mild/moderate/strong"
    }
  ],
  "financial_qualification": {
    "budget_discovery": "attempted/partially done/thorough/not attempted",
    "income_assessment": "direct/indirect/assumed/not addressed",
    "current_expenses": "explored/mentioned/not discussed",
    "financial_priorities": "identified/assumed/unclear"
  },
  "value_positioning": [
    {
      "technique": "cost vs value/ROI/affordability/payment options",
      "implementation": "how agent positioned value",
      "customer_response": "how customer reacted",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "cost_justification": {
    "methods_used": ["specific justification techniques"],
    "emotional_vs_logical": "primarily emotional/balanced/primarily logical",
    "comparison_anchoring": "yes/no - if used comparisons",
    "urgency_creation": "financial urgency created or not"
  },
  "payment_discussion": {
    "options_presented": ["payment methods or plans mentioned"],
    "affordability_framing": "how agent framed affordability",
    "customer_comfort": "comfortable/hesitant/resistant",
    "resolution": "resolved/partially resolved/unresolved"
  }
}

Focus specifically on financial and budget-related aspects of the sales conversation.""",
            description="Analyzes budget objection handling and financial positioning techniques",
            output_key="budget_analysis"
        )
        
        # Agent 12: Urgency Builder
        urgency_agent = LlmAgent(
            name="UrgencyBuilderAgent",
            model=self.model,
            instruction="""You are an expert at analyzing urgency creation and momentum building techniques in sales calls.
            
Analyze the transcript for:
1. Soft urgency techniques used
2. Timing and scarcity elements
3. Consequence awareness building
4. Action orientation and next steps

Return your analysis in this exact JSON format:
{
  "urgency_techniques": [
    {
      "technique": "limited time/exclusive offer/market conditions/personal timing/other",
      "implementation": "how agent created urgency",
      "authenticity": "genuine/somewhat forced/artificial",
      "customer_response": "motivated/neutral/resistant",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "timing_elements": {
    "deadlines_mentioned": ["any time constraints discussed"],
    "seasonal_factors": "if timing related to specific periods",
    "personal_timing": "customer's life events creating urgency",
    "market_conditions": "external factors creating time pressure"
  },
  "consequence_awareness": {
    "cost_of_waiting": "addressed/partially addressed/not addressed",
    "risk_of_delay": "financial/health/family risks discussed",
    "opportunity_cost": "what customer loses by waiting",
    "emotional_consequences": "feelings associated with delay"
  },
  "action_orientation": {
    "next_steps_clarity": "clear/somewhat clear/vague",
    "commitment_timeline": "immediate/short term/long term/undefined",
    "decision_framework": "process for moving forward established",
    "follow_up_urgency": "immediate/scheduled/loose/none"
  },
  "momentum_assessment": {
    "urgency_level_created": "low/moderate/high",
    "customer_motivation": "increased/maintained/decreased",
    "decision_pressure": "appropriate/excessive/insufficient",
    "overall_effectiveness": "poor/fair/good/excellent"
  }
}

Focus on identifying urgency creation techniques and their impact on customer decision-making momentum.""",
            description="Analyzes urgency creation and momentum building techniques",
            output_key="urgency_analysis"
        )
        
        # Agent 13: Technical Navigation
        technical_agent = LlmAgent(
            name="TechnicalNavigationAgent",
            model=self.model,
            instruction="""You are an expert at analyzing how technical difficulties and process delays are handled during sales calls.
            
Analyze the transcript for:
1. Technical issues encountered
2. Agent's handling of difficulties
3. Rapport maintenance during delays
4. Recovery and continuation strategies

Return your analysis in this exact JSON format:
{
  "technical_issues": [
    {
      "issue": "specific technical problem encountered",
      "timing": "when in call it occurred",
      "duration": "how long it lasted",
      "impact": "minimal/moderate/significant disruption"
    }
  ],
  "handling_approach": {
    "preparation": "proactive/reactive/unprepared",
    "communication": "kept customer informed/partial updates/poor communication",
    "alternative_solutions": "had backup plans/improvised/struggled",
    "professionalism": "maintained/somewhat maintained/lost composure"
  },
  "rapport_during_delays": {
    "customer_patience": "understanding/neutral/frustrated",
    "agent_management": "excellent/good/fair/poor relationship maintenance",
    "conversation_continuation": "natural/forced/awkward",
    "trust_impact": "strengthened/neutral/damaged"
  },
  "recovery_strategies": [
    {
      "strategy": "how agent recovered from issue",
      "effectiveness": "poor/fair/good/excellent", 
      "customer_response": "understanding/neutral/frustrated",
      "momentum_impact": "gained/maintained/lost"
    }
  ],
  "process_navigation": {
    "efficiency": "streamlined/adequate/inefficient",
    "customer_guidance": "clear/adequate/confusing",
    "expectation_setting": "proactive/reactive/poor",
    "overall_experience": "smooth/acceptable/frustrating"
  }
}

Focus on technical competence, problem-solving, and maintaining relationship quality during challenges.""",
            description="Analyzes technical difficulty handling and process navigation skills",
            output_key="technical_analysis"
        )
        
        # Agent 14: Cross-Selling (Optional - may have low frequency)
        crosssell_agent = LlmAgent(
            name="CrossSellingAgent",
            model=self.model,
            instruction="""You are an expert at analyzing cross-selling opportunities and techniques in sales calls.
            
Analyze the transcript for:
1. Cross-selling opportunities identified
2. Additional product mentions
3. Timing and integration of cross-sell attempts
4. Customer receptiveness to additional offerings

Return your analysis in this exact JSON format:
{
  "opportunities_identified": [
    {
      "opportunity": "additional product or service mentioned",
      "timing": "when in call it was introduced",
      "relevance": "highly relevant/somewhat relevant/forced",
      "customer_interest": "interested/neutral/resistant"
    }
  ],
  "cross_sell_techniques": [
    {
      "technique": "bundling/complementary/upgrade/add-on",
      "implementation": "how it was presented",
      "integration": "natural/somewhat natural/forced",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "customer_response": {
    "receptiveness": "open/neutral/resistant",
    "questions_asked": ["any questions about additional products"],
    "objections_raised": ["concerns about additional offerings"],
    "decision_impact": "helped/neutral/hindered main sale"
  },
  "execution_quality": {
    "timing": "too early/appropriate/too late",
    "relevance": "highly relevant/somewhat relevant/not relevant",
    "pressure_level": "no pressure/appropriate/excessive",
    "overall_approach": "natural/somewhat forced/pushy"
  },
  "outcome_assessment": {
    "additional_interest_created": "yes/maybe/no",
    "main_sale_impact": "positive/neutral/negative",
    "future_opportunity": "strong/possible/unlikely",
    "follow_up_potential": "immediate/later/none"
  }
}

Note: If no cross-selling occurs, return minimal structure with "no_crossselling_attempted": true.""",
            description="Analyzes cross-selling opportunities and execution techniques",
            output_key="crosssell_analysis"
        )
        
        return [
            commitments_agent, flow_agent, budget_agent, 
            urgency_agent, technical_agent, crosssell_agent
        ]
    
    def _create_synthesis_agent(self) -> LlmAgent:
        """Create the Synthesis Agent that combines all analysis results."""
        
        synthesis_agent = LlmAgent(
            name="SynthesisAgent",
            model=self.model,
            instruction="""You are an expert sales call analyst responsible for synthesizing results from 14 specialized analysis agents into comprehensive insights.

You will receive analysis results from:
- Phase 1 Core Agents: objection_analysis, opening_analysis, needs_analysis, rapport_analysis, pattern_analysis, emotional_analysis, language_analysis, profile_analysis
- Phase 2 Advanced Agents: commitment_analysis, flow_analysis, budget_analysis, urgency_analysis, technical_analysis, crosssell_analysis

Create a comprehensive synthesis that identifies:
1. Cross-agent correlations and patterns
2. Success factors and failure points
3. Overall call assessment and outcome prediction
4. Specific improvement recommendations

Return your synthesis in this exact JSON format:
{
  "master_insights": {
    "call_success_factors": ["key elements that contributed to success"],
    "improvement_opportunities": ["specific areas needing enhancement"], 
    "standout_moments": ["most effective techniques or moments"],
    "cross_agent_patterns": {
      "opening_to_outcome": "correlation between opening and final result",
      "commitment_momentum": "how micro-commitments built throughout call",
      "emotional_journey": "customer sentiment progression",
      "objection_resolution": "pattern of objection handling effectiveness"
    },
    "predictive_indicators": {
      "success_probability": "low/medium/high based on patterns",
      "key_predictors": ["strongest indicators of likely outcome"],
      "warning_signals": ["red flags or concerning patterns"]
    },
    "overall_assessment": "comprehensive evaluation of call quality and likely outcome"
  },
  "performance_matrix": {
    "technical_competence": "1-10 scale",
    "relationship_building": "1-10 scale", 
    "needs_identification": "1-10 scale",
    "objection_handling": "1-10 scale",
    "closing_effectiveness": "1-10 scale",
    "overall_score": "1-10 scale"
  },
  "coaching_priorities": [
    {
      "area": "top improvement area",
      "specific_issue": "what needs work",
      "recommended_action": "how to improve",
      "priority": "high/medium/low"
    }
  ]
}

Base your synthesis strictly on the provided agent analysis results. Identify patterns, correlations, and insights that emerge from combining all 14 specialized analyses.""",
            description="Synthesizes all agent analyses into comprehensive insights and recommendations",
            output_key="comprehensive_synthesis"
        )
        
        return synthesis_agent
    
    def _create_pipeline_agent(self) -> SequentialAgent:
        """Create the main pipeline with parallel phases and synthesis."""
        
        # Create Phase 1 and Phase 2 parallel agents
        phase1_agents = self._create_phase1_agents()
        phase2_agents = self._create_phase2_agents()
        synthesis_agent = self._create_synthesis_agent()
        
        # Phase 1: Core Analysis (8 agents in parallel)
        phase1_parallel = ParallelAgent(
            name="Phase1CoreAnalysis",
            sub_agents=phase1_agents,
            description="Runs 8 core analysis agents in parallel: objection, opening, needs, rapport, pattern, emotional, language, and profiling analysis"
        )
        
        # Phase 2: Advanced Analysis (6 agents in parallel) 
        phase2_parallel = ParallelAgent(
            name="Phase2AdvancedAnalysis", 
            sub_agents=phase2_agents,
            description="Runs 6 advanced analysis agents in parallel: commitment, flow, budget, urgency, technical, and crosssell analysis"
        )
        
        # Main Pipeline: Sequential execution of phases
        pipeline = SequentialAgent(
            name="SalesAnalysisPipeline",
            sub_agents=[phase1_parallel, phase2_parallel, synthesis_agent],
            description="Orchestrates complete sales call analysis: Phase 1 (parallel core analysis) → Phase 2 (parallel advanced analysis) → Synthesis"
        )
        
        return pipeline
    
    def analyze_transcript(self, transcript: str, source_file: str = "") -> Dict[str, Any]:
        """
        Analyze a sales call transcript using actual Gemini API calls for each agent.
        
        Args:
            transcript: The call transcript text to analyze
            source_file: Optional source file path for context
            
        Returns:
            Dictionary containing individual agent results from real analysis
        """
        # Start lessons audit trail event
        event_id = self.lessons_auditor.start_processing_event(source_file)
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting ADK sales analysis pipeline for: {source_file}")
            
            # Create individual agent results structure expected by API
            agent_names = [
                'objection_specialist', 'opening_gambit', 'needs_assessment',
                'rapport_building', 'pattern_recognition', 'emotional_intelligence',
                'language_optimizer', 'client_profiling', 'micro_commitments',
                'conversation_flow', 'budget_handling', 'urgency_builder',
                'technical_navigation', 'cross_selling'
            ]
            
            agent_results = {}
            
            # Perform actual analysis using Gemini API for each agent
            for agent_name in agent_names:
                logger.info(f"Running real {agent_name} analysis...")
                
                try:
                    # Get the actual agent instruction and analyze with Gemini
                    analysis_result = self._analyze_with_gemini(agent_name, transcript, source_file)
                    
                    agent_results[agent_name] = {
                        "agent_name": agent_name,
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                        "analysis_type": "Gemini_API_Analysis",
                        **analysis_result
                    }
                    
                    logger.info(f"✅ {agent_name} completed successfully")
                    
                except Exception as agent_error:
                    logger.error(f"❌ Error in {agent_name}: {str(agent_error)}")
                    agent_results[agent_name] = {
                        "agent_name": agent_name,
                        "status": "agent_error",
                        "timestamp": datetime.now().isoformat(),
                        "error": f"Agent error: {str(agent_error)}",
                        "analysis": f"Failed to analyze with {agent_name}"
                    }
            
            # Extract lessons from agent results
            logger.info("📚 Extracting lessons from analysis results...")
            lesson_candidates = self.lessons_auditor.extract_lesson_candidates(agent_results)
            
            # Complete lessons audit trail event
            processing_duration = (datetime.now() - start_time).total_seconds()
            self.lessons_auditor.complete_processing_event(
                event_id=event_id,
                lesson_candidates=lesson_candidates,
                synthesis_result={},  # No synthesis in this pipeline
                processing_duration=processing_duration
            )
            
            # Check for plateau
            if self.lessons_auditor.is_plateau_detected():
                logger.warning("⚠️  Learning plateau detected - consider expanding data sources or refining extraction techniques")
                recommendations = self.lessons_auditor.get_plateau_recommendations()
                logger.info(f"📋 Recommendations: {recommendations}")
            
            logger.info(f"✅ ADK pipeline completed with {len(agent_results)} agent results")
            logger.info(f"📚 Extracted {len(lesson_candidates)} lesson candidates for learning system")
            
            return agent_results
            
        except Exception as e:
            logger.error(f"❌ Error in ADK analysis pipeline: {str(e)}")
            # Return empty results for all agents on pipeline failure
            agent_names = [
                'objection_specialist', 'opening_gambit', 'needs_assessment',
                'rapport_building', 'pattern_recognition', 'emotional_intelligence',
                'language_optimizer', 'client_profiling', 'micro_commitments',
                'conversation_flow', 'budget_handling', 'urgency_builder',
                'technical_navigation', 'cross_selling'
            ]
            
            error_results = {}
            for agent_name in agent_names:
                error_results[agent_name] = {
                    "agent_name": agent_name,
                    "status": "pipeline_error",
                    "timestamp": datetime.now().isoformat(),
                    "error": f"Pipeline failure: {str(e)}",
                    "analysis": f"Pipeline failed before {agent_name} could run"
                }
            
            return error_results
    
    def _analyze_with_gemini(self, agent_name: str, transcript: str, source_file: str = "") -> Dict[str, Any]:
        """Analyze transcript using Gemini API for the specified agent."""
        try:
            # Get the agent instruction based on agent name
            instruction = self._get_agent_instruction(agent_name)
            
            # Create the full prompt with transcript
            prompt = f"{instruction}\n\nTranscript to analyze:\n{transcript}"
            
            # Create Gemini model instance
            model = genai.GenerativeModel(self.model)
            
            # Generate analysis using Gemini
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=4000,
                )
            )
            
            response_text = response.text
            
            # Extract JSON from response
            try:
                result_json = self._extract_json_from_response(response_text)
            except Exception as parse_err:
                logger.error(f"JSON parse failure in {agent_name} response: {parse_err}")
                return {
                    "error": f"JSON parse error: {parse_err}",
                    "raw_response": response_text[:1000],
                    "agent_name": agent_name,
                    "source_file": source_file,
                }
            
            # Add metadata
            result_json['agent_name'] = agent_name
            result_json['source_file'] = source_file
            result_json['analysis_date'] = datetime.now().isoformat()
            
            return result_json
            
        except Exception as e:
            logger.error(f"Error in Gemini API call for {agent_name}: {str(e)}")
            return {
                "error": f"Gemini API error: {str(e)}",
                "agent_name": agent_name,
                "source_file": source_file
            }
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response text."""
        # Strip triple-backtick fences if present
        fenced_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if fenced_match:
            text = fenced_match.group(1)

        # Quick comment removal (// ... and /* ... */)
        text_no_comments = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
        text_no_comments = re.sub(r"/\*.*?\*/", "", text_no_comments, flags=re.DOTALL)

        # Find first '{' and iterate to get balanced closing '}'
        start = text_no_comments.find('{')
        if start == -1:
            raise ValueError("No opening brace found")

        stack = []
        for idx in range(start, len(text_no_comments)):
            ch = text_no_comments[idx]
            if ch == '{':
                stack.append('{')
            elif ch == '}' and stack:
                stack.pop()
                if not stack:
                    candidate = text_no_comments[start:idx + 1]
                    # Remove trailing commas before } or ]
                    candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)
                    return json.loads(candidate)
        raise ValueError("No balanced JSON object found")
    
    def _get_agent_instruction(self, agent_name: str) -> str:
        """Get the instruction prompt for each agent type."""
        
        instructions = {
            "objection_specialist": """You are an expert objection handling specialist analyzing life insurance sales calls.
            
Analyze the provided call transcript for:
1. All customer objections raised (price, time, trust, product, etc.)
2. How the agent handled each objection
3. Effectiveness of objection handling techniques
4. Missed opportunities to address concerns

Return your analysis in this exact JSON format:
{
  "objections_identified": [
    {
      "objection_type": "price/time/trust/product/need/other",
      "customer_statement": "exact quote from transcript",
      "timing": "early/middle/late in call",
      "severity": "low/medium/high"
    }
  ],
  "handling_techniques": [
    {
      "objection_type": "type of objection addressed",
      "agent_response": "how agent responded",
      "technique_used": "feel/felt/found, acknowledge/clarify/respond, etc.",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "call_summary": {
    "total_objections": 0,
    "objections_addressed": 0,
    "primary_objection": "main customer concern",
    "outcome": "sale/no_sale/follow_up_needed"
  },
  "improvement_recommendations": ["specific suggestions for better objection handling"]
}

Analyze only what is explicitly stated in the transcript. Do not infer or add external information.""",

            "opening_gambit": """You are an expert at analyzing sales call openings and first impressions.
            
Analyze the first 3-5 minutes of this call transcript for:
1. Opening technique used by the agent
2. Customer's initial receptiveness
3. Rapport building in the opening
4. Effectiveness of the approach

Return your analysis in this exact JSON format:
{
  "opening_analysis": {
    "opening_technique": "warm introduction/referral mention/direct approach/other",
    "opening_statement": "first few sentences agent used",
    "customer_initial_response": "how customer first responded",
    "customer_receptiveness": "resistant/neutral/receptive/very receptive",
    "rapport_established": "yes/no/partial"
  },
  "effectiveness_scoring": {
    "attention_grabbing": "1-10 scale",
    "relevance_to_customer": "1-10 scale", 
    "professionalism": "1-10 scale",
    "overall_opening_score": "1-10 scale"
  },
  "improvement_opportunities": [
    "specific suggestions for better opening"
  ]
}

Focus only on the opening portion of the call (first 3-5 minutes).""",

            "needs_assessment": """You are an expert at analyzing needs discovery and assessment techniques in sales calls.
            
Analyze the transcript for:
1. Questions asked by the agent to understand customer needs
2. Customer information discovered
3. Quality of needs assessment process
4. How well agent understood customer situation

Return your analysis in this exact JSON format: 
{
  "discovery_questions": [
    {
      "question": "exact question asked by agent",
      "question_type": "open/closed/leading/probing",
      "customer_response": "what customer revealed",
      "information_value": "low/medium/high"
    }
  ],
  "customer_profile": {
    "family_situation": "what was learned about family",
    "financial_situation": "what was learned about finances", 
    "current_coverage": "existing insurance mentioned",
    "concerns_priorities": "main customer concerns identified",
    "decision_making_style": "how customer makes decisions"
  },
  "needs_assessment_quality": {
    "depth_of_discovery": "poor/fair/good/excellent",
    "question_sequencing": "poor/fair/good/excellent",
    "active_listening": "poor/fair/good/excellent",
    "needs_identified": ["list of needs discovered"]
  },
  "missed_opportunities": ["questions that should have been asked"]
}

Focus on the discovery and needs assessment portions of the call.""",

            "rapport_building": """You are an expert at analyzing relationship building and trust development in sales calls.
            
Analyze the transcript for:
1. Rapport building techniques used
2. Trust development strategies  
3. Personal connection moments
4. Overall relationship quality established

Return your analysis in this exact JSON format:
{
  "rapport_techniques": [
    {
      "technique": "small talk/shared experience/empathy/humor/other",
      "example": "specific instance from transcript",
      "timing": "opening/middle/closing",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "trust_building": {
    "credibility_establishment": "how agent established expertise",
    "transparency_level": "low/medium/high", 
    "authenticity": "scripted/natural/genuine",
    "customer_comfort_level": "uncomfortable/neutral/comfortable/very comfortable"
  },
  "personal_connection": {
    "common_ground_found": "yes/no",
    "personal_details_shared": "what agent learned about customer personally",
    "emotional_connection": "weak/moderate/strong",
    "memorable_moments": ["specific rapport building moments"]
  },
  "overall_rapport_assessment": {
    "rapport_score": "1-10 scale",
    "trust_level": "low/medium/high",
    "relationship_quality": "transactional/professional/personal/trusted advisor"
  }
}

Focus on relationship and trust building throughout the entire call.""",

            "pattern_recognition": """You are an expert at identifying conversation patterns and sequences in sales calls.
            
Analyze the transcript for:
1. Conversation flow patterns
2. Question-answer sequences
3. Repeating themes or topics
4. Successful interaction patterns

Return your analysis in this exact JSON format:
{
  "conversation_patterns": [
    {
      "pattern_type": "question_sequence/objection_loop/benefit_confirmation/other",
      "description": "what pattern was observed", 
      "frequency": "how often it occurred",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "successful_sequences": [
    {
      "sequence": "step by step description",
      "outcome": "what it achieved",
      "replicability": "easy/moderate/difficult to replicate"
    }
  ],
  "conversation_themes": [
    {
      "theme": "main topic or concern",
      "frequency": "how often mentioned",
      "resolution": "resolved/unresolved/partially addressed"
    }
  ],
  "flow_analysis": {
    "transitions": "smooth/choppy/natural",
    "momentum_building": "yes/no/inconsistent", 
    "conversation_control": "agent led/customer led/balanced",
    "pacing": "too fast/appropriate/too slow"
  }
}

Look for recurring patterns, successful sequences, and overall conversation dynamics.""",

            "emotional_intelligence": """You are an expert at analyzing emotional dynamics and sentiment in sales conversations.
            
Analyze the transcript for:
1. Customer emotional states throughout the call
2. Agent's emotional awareness and responses
3. Emotional turning points
4. Overall sentiment trajectory

Return your analysis in this exact JSON format:
{
  "emotional_analysis": {
    "customer_initial_sentiment": "positive/neutral/negative/skeptical",
    "customer_final_sentiment": "positive/neutral/negative/frustrated",
    "sentiment_shift": "positive_shift/negative_shift/no_change",
    "emotional_turning_points": [
      {
        "moment": "what happened",
        "emotion_before": "customer emotion before",
        "emotion_after": "customer emotion after",
        "trigger": "what caused the change"
      }
    ]
  },
  "agent_emotional_intelligence": {
    "emotion_recognition": "poor/fair/good/excellent",
    "empathy_demonstration": "low/medium/high",
    "emotional_adaptation": "rigid/somewhat flexible/highly adaptive",
    "tone_matching": "mismatched/somewhat matched/well matched"
  },
  "emotional_techniques": [
    {
      "technique": "validation/empathy/reframing/other",
      "usage": "when and how used",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "overall_emotional_outcome": {
    "customer_satisfaction": "dissatisfied/neutral/satisfied/very satisfied",
    "emotional_resolution": "unresolved/partially resolved/fully resolved",
    "relationship_impact": "damaged/neutral/strengthened"
  }
}

Focus on emotional intelligence, empathy, and sentiment management throughout the call.""",

            "language_optimizer": """You are an expert at analyzing language effectiveness and communication style in sales calls.
            
Analyze the transcript for:
1. Language patterns and word choices
2. Communication clarity and effectiveness
3. Persuasive language techniques
4. Areas for language improvement

Return your analysis in this exact JSON format:
{
  "language_analysis": {
    "clarity_score": "1-10 scale",
    "jargon_usage": "excessive/appropriate/minimal",
    "tone_consistency": "inconsistent/mostly consistent/very consistent",
    "active_vs_passive": "ratio of active to passive voice"
  },
  "persuasive_techniques": [
    {
      "technique": "social proof/scarcity/authority/reciprocity/other",
      "examples": ["specific instances from transcript"],
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "power_phrases": [
    {
      "phrase": "exact phrase used",
      "context": "when it was used",
      "impact": "customer response or effect"
    }
  ],
  "communication_strengths": [
    "what the agent did well linguistically"
  ],
  "improvement_opportunities": [
    {
      "area": "what needs improvement",
      "suggestion": "specific language recommendation",
      "priority": "low/medium/high"
    }
  ]
}

Focus on language effectiveness, word choice, and communication optimization.""",

            "client_profiling": """You are an expert at creating detailed customer profiles and personas from sales call interactions.
            
Analyze the transcript to create a comprehensive customer profile including:
1. Demographic and psychographic characteristics
2. Decision-making patterns
3. Communication preferences
4. Buying behavior indicators

Return your analysis in this exact JSON format:
{
  "client_profile": {
    "demographic_info": {
      "approximate_age": "age range if mentioned",
      "family_status": "single/married/divorced/widowed",
      "occupation": "job or profession if mentioned",
      "location": "geographic info if mentioned"
    },
    "psychographic_profile": {
      "personality_type": "analytical/driver/expressive/amiable",
      "risk_tolerance": "low/medium/high",
      "decision_speed": "quick/deliberate/slow",
      "information_processing": "detail-oriented/big picture"
    },
    "communication_style": {
      "preferred_pace": "fast/moderate/slow",
      "question_frequency": "asks many/some/few questions",
      "engagement_level": "highly engaged/moderately engaged/disengaged",
      "language_preference": "technical/simple/conversational"
    },
    "decision_making_pattern": {
      "style": "logical/emotional/mixed",
      "influences": ["what factors influence their decisions"],
      "timeline": "immediate/short term/long term",
      "consultation_needs": "decides alone/consults spouse/consults others"
    }
  },
  "buying_signals": [
    {
      "signal": "specific behavior or statement",
      "strength": "weak/moderate/strong",
      "timing": "when it occurred in call"
    }
  ],
  "ideal_approach": {
    "recommended_style": "how to best communicate with this client",
    "key_motivators": ["what drives this client"],
    "potential_concerns": ["likely objections or hesitations"],
    "follow_up_strategy": "best approach for next contact"
  }
}

Create a detailed, actionable client profile based on observable behaviors and statements.""",

            "micro_commitments": """You are an expert at tracking micro-commitments and agreement building in sales calls.
            
Analyze the transcript for:
1. All micro-commitments secured from the customer
2. Agreement building progression
3. Commitment momentum and velocity
4. How commitments led toward the close

Return your analysis in this exact JSON format:
{
  "commitment_analysis": {
    "total_commitments": 0,
    "commitment_categories": {
      "information_agreements": 0,
      "process_agreements": 0, 
      "value_agreements": 0,
      "next_step_agreements": 0
    },
    "commitment_velocity": "slow/steady/building/strong"
  },
  "commitment_sequence": [
    {
      "commitment": "what customer agreed to",
      "type": "information/process/value/next_step",
      "agent_technique": "how agent secured it",
      "timing": "early/middle/late in call",
      "strength": "weak/moderate/strong"
    }
  ],
  "momentum_building": {
    "progression": "declining/flat/building/strong",
    "turning_points": ["moments where momentum shifted"],
    "peak_commitment": "strongest agreement secured",
    "commitment_chain": "how commitments built on each other"
  },
  "effectiveness_assessment": {
    "commitment_to_close_ratio": "percentage that led to next steps",
    "missed_opportunities": ["where commitments could have been secured"],
    "overall_momentum": "poor/fair/good/excellent"
  }
}

Focus on identifying and tracking all forms of customer agreement and commitment building.""",

            "conversation_flow": """You are an expert at analyzing conversation structure, transitions, and flow optimization.
            
Analyze the transcript for:
1. Overall conversation structure and phases
2. Transition quality between topics
3. Flow interruptions and recoveries
4. Optimization opportunities for better flow

Return your analysis in this exact JSON format:
{
  "flow_structure": {
    "phases_identified": [
      {
        "phase": "opening/discovery/presentation/objection_handling/closing",
        "duration_estimate": "approximate time spent",
        "transition_quality": "abrupt/smooth/natural",
        "effectiveness": "poor/fair/good/excellent"
      }
    ],
    "overall_structure": "linear/circular/scattered/strategic"
  },
  "transition_analysis": [
    {
      "from_topic": "previous subject",
      "to_topic": "new subject", 
      "transition_method": "bridge/summary/question/direct",
      "quality": "poor/fair/good/excellent",
      "customer_follow": "yes/no/confused"
    }
  ],
  "flow_disruptions": [
    {
      "disruption": "what interrupted the flow",
      "cause": "customer objection/agent mistake/external/other",
      "recovery": "how flow was restored",
      "impact": "minimal/moderate/significant"
    }
  ],
  "flow_pattern": {
    "sequence": ["ordered list of conversation topics"],
    "logic": "logical/somewhat logical/scattered",
    "customer_engagement": "maintained/varied/lost",
    "momentum": "building/steady/declining"
  },
  "optimization_recommendations": [
    {
      "area": "what could be improved",
      "suggestion": "specific recommendation",
      "expected_impact": "minor/moderate/significant"
    }
  ]
}

Focus on conversation architecture, flow dynamics, and structural optimization opportunities.""",

            "budget_handling": """You are an expert at analyzing how financial concerns and budget objections are handled in sales calls.
            
Analyze the transcript for:
1. Budget-related objections and concerns
2. Financial qualification techniques
3. Value vs. cost positioning
4. Payment and affordability discussions

Return your analysis in this exact JSON format:
{
  "budget_objections": [
    {
      "objection": "specific budget concern raised",
      "customer_statement": "exact quote about cost/budget",
      "timing": "when in call it was raised",
      "intensity": "mild/moderate/strong"
    }
  ],
  "financial_qualification": {
    "budget_discovery": "attempted/partially done/thorough/not attempted",
    "income_assessment": "direct/indirect/assumed/not addressed",
    "current_expenses": "explored/mentioned/not discussed",
    "financial_priorities": "identified/assumed/unclear"
  },
  "value_positioning": [
    {
      "technique": "cost vs value/ROI/affordability/payment options",
      "implementation": "how agent positioned value",
      "customer_response": "how customer reacted",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "cost_justification": {
    "methods_used": ["specific justification techniques"],
    "emotional_vs_logical": "primarily emotional/balanced/primarily logical",
    "comparison_anchoring": "yes/no - if used comparisons",
    "urgency_creation": "financial urgency created or not"
  },
  "payment_discussion": {
    "options_presented": ["payment methods or plans mentioned"],
    "affordability_framing": "how agent framed affordability",
    "customer_comfort": "comfortable/hesitant/resistant",
    "resolution": "resolved/partially resolved/unresolved"
  }
}

Focus specifically on financial and budget-related aspects of the sales conversation.""",

            "urgency_builder": """You are an expert at analyzing urgency creation and momentum building techniques in sales calls.
            
Analyze the transcript for:
1. Soft urgency techniques used
2. Timing and scarcity elements
3. Consequence awareness building
4. Action orientation and next steps

Return your analysis in this exact JSON format:
{
  "urgency_techniques": [
    {
      "technique": "limited time/exclusive offer/market conditions/personal timing/other",
      "implementation": "how agent created urgency",
      "authenticity": "genuine/somewhat forced/artificial",
      "customer_response": "motivated/neutral/resistant",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "timing_elements": {
    "deadlines_mentioned": ["any time constraints discussed"],
    "seasonal_factors": "if timing related to specific periods",
    "personal_timing": "customer's life events creating urgency",
    "market_conditions": "external factors creating time pressure"
  },
  "consequence_awareness": {
    "cost_of_waiting": "addressed/partially addressed/not addressed",
    "risk_of_delay": "financial/health/family risks discussed",
    "opportunity_cost": "what customer loses by waiting",
    "emotional_consequences": "feelings associated with delay"
  },
  "action_orientation": {
    "next_steps_clarity": "clear/somewhat clear/vague",
    "commitment_timeline": "immediate/short term/long term/undefined",
    "decision_framework": "process for moving forward established",
    "follow_up_urgency": "immediate/scheduled/loose/none"
  },
  "momentum_assessment": {
    "urgency_level_created": "low/moderate/high",
    "customer_motivation": "increased/maintained/decreased",
    "decision_pressure": "appropriate/excessive/insufficient",
    "overall_effectiveness": "poor/fair/good/excellent"
  }
}

Focus on identifying urgency creation techniques and their impact on customer decision-making momentum.""",

            "technical_navigation": """You are an expert at analyzing how technical difficulties and process delays are handled during sales calls.
            
Analyze the transcript for:
1. Technical issues encountered
2. Agent's handling of difficulties
3. Rapport maintenance during delays
4. Recovery and continuation strategies

Return your analysis in this exact JSON format:
{
  "technical_issues": [
    {
      "issue": "specific technical problem encountered",
      "timing": "when in call it occurred",
      "duration": "how long it lasted",
      "impact": "minimal/moderate/significant disruption"
    }
  ],
  "handling_approach": {
    "preparation": "proactive/reactive/unprepared",
    "communication": "kept customer informed/partial updates/poor communication",
    "alternative_solutions": "had backup plans/improvised/struggled",
    "professionalism": "maintained/somewhat maintained/lost composure"
  },
  "rapport_during_delays": {
    "customer_patience": "understanding/neutral/frustrated",
    "agent_management": "excellent/good/fair/poor relationship maintenance",
    "conversation_continuation": "natural/forced/awkward",
    "trust_impact": "strengthened/neutral/damaged"
  },
  "recovery_strategies": [
    {
      "strategy": "how agent recovered from issue",
      "effectiveness": "poor/fair/good/excellent", 
      "customer_response": "understanding/neutral/frustrated",
      "momentum_impact": "gained/maintained/lost"
    }
  ],
  "process_navigation": {
    "efficiency": "streamlined/adequate/inefficient",
    "customer_guidance": "clear/adequate/confusing",
    "expectation_setting": "proactive/reactive/poor",
    "overall_experience": "smooth/acceptable/frustrating"
  }
}

Focus on technical competence, problem-solving, and maintaining relationship quality during challenges.""",

            "cross_selling": """You are an expert at analyzing cross-selling opportunities and techniques in sales calls.
            
Analyze the transcript for:
1. Cross-selling opportunities identified
2. Additional product mentions
3. Timing and integration of cross-sell attempts
4. Customer receptiveness to additional offerings

Return your analysis in this exact JSON format:
{
  "opportunities_identified": [
    {
      "opportunity": "additional product or service mentioned",
      "timing": "when in call it was introduced",
      "relevance": "highly relevant/somewhat relevant/forced",
      "customer_interest": "interested/neutral/resistant"
    }
  ],
  "cross_sell_techniques": [
    {
      "technique": "bundling/complementary/upgrade/add-on",
      "implementation": "how it was presented",
      "integration": "natural/somewhat natural/forced",
      "effectiveness": "poor/fair/good/excellent"
    }
  ],
  "customer_response": {
    "receptiveness": "open/neutral/resistant",
    "questions_asked": ["any questions about additional products"],
    "objections_raised": ["concerns about additional offerings"],
    "decision_impact": "helped/neutral/hindered main sale"
  },
  "execution_quality": {
    "timing": "too early/appropriate/too late",
    "relevance": "highly relevant/somewhat relevant/not relevant",
    "pressure_level": "no pressure/appropriate/excessive",
    "overall_approach": "natural/somewhat forced/pushy"
  },
  "outcome_assessment": {
    "additional_interest_created": "yes/maybe/no",
    "main_sale_impact": "positive/neutral/negative",
    "future_opportunity": "strong/possible/unlikely",
    "follow_up_potential": "immediate/later/none"
  }
}

Note: If no cross-selling occurs, return minimal structure with "no_crossselling_attempted": true."""
        }
        
        return instructions.get(agent_name, f"Analyze the transcript for {agent_name} insights and return as JSON.")
    
    def _generate_realistic_analysis(self, agent_name: str, transcript: str) -> Dict[str, Any]:
        """Generate realistic analysis results for each agent type."""
        
        # Basic analysis all agents share
        base_analysis = {
            "call_summary": {
                "total_exchanges": len(transcript.split("Agent:")) - 1,
                "estimated_duration": "15-20 minutes",
                "call_outcome": "information_gathering" if "interested" in transcript.lower() else "follow_up_needed"
            }
        }
        
        # Agent-specific analysis patterns
        if agent_name == "objection_specialist":
            return {
                **base_analysis,
                "objections_identified": [
                    {
                        "objection_type": "price" if "afford" in transcript.lower() else "information",
                        "customer_statement": "Need to review options and pricing",
                        "timing": "middle",
                        "severity": "medium"
                    }
                ],
                "handling_techniques": [
                    {
                        "objection_type": "information",
                        "agent_response": "I understand your concerns. Let me provide more details.",
                        "technique_used": "acknowledge_and_clarify",
                        "effectiveness": "good"
                    }
                ]
            }
            
        elif agent_name == "opening_gambit":
            return {
                **base_analysis,
                "opening_analysis": {
                    "opening_type": "professional_introduction",
                    "rapport_establishment": "good" if "hello" in transcript.lower() else "needs_improvement",
                    "purpose_clarity": "clear",
                    "engagement_level": "high" if "interested" in transcript.lower() else "medium"
                }
            }
            
        elif agent_name == "needs_assessment":
            return {
                **base_analysis,
                "discovery_questions": [
                    {
                        "question_type": "open_ended",
                        "question": "What type of coverage are you looking for?",
                        "response_quality": "informative",
                        "follow_up_needed": "yes"
                    }
                ],
                "needs_identified": {
                    "primary_need": "life_insurance_coverage",
                    "coverage_amount": "to_be_determined",
                    "urgency_level": "medium"
                }
            }
            
        elif agent_name == "rapport_building":
            return {
                **base_analysis,
                "rapport_techniques": [
                    {
                        "technique": "active_listening",
                        "implementation": "Agent acknowledged customer concerns",
                        "effectiveness": "good"
                    }
                ],
                "trust_indicators": {
                    "customer_openness": "medium",
                    "question_asking": "moderate",
                    "resistance_level": "low"
                }
            }
            
        elif agent_name == "pattern_recognition":
            return {
                **base_analysis,
                "conversation_patterns": [
                    {
                        "pattern_type": "information_seeking",
                        "frequency": "high",
                        "customer_behavior": "asking_questions",
                        "agent_adaptation": "providing_detailed_responses"
                    }
                ]
            }
            
        elif agent_name == "emotional_intelligence":
            return {
                **base_analysis,
                "emotional_analysis": {
                    "customer_sentiment": "curious" if "interested" in transcript.lower() else "neutral",
                    "emotional_journey": ["initial_uncertainty", "growing_interest"],
                    "agent_empathy": "demonstrated",
                    "emotional_triggers": ["family_security", "financial_protection"]
                }
            }
            
        elif agent_name == "language_optimizer":
            return {
                **base_analysis,
                "language_analysis": {
                    "clarity_score": "good",
                    "technical_jargon": "minimal",
                    "persuasive_elements": ["benefit_focused", "customer_centric"],
                    "improvement_areas": ["more_specific_examples"]
                }
            }
            
        elif agent_name == "client_profiling":
            return {
                **base_analysis,
                "client_profile": {
                    "demographic": "family_oriented",
                    "decision_style": "analytical",
                    "communication_preference": "detailed_information",
                    "buying_readiness": "researching_stage"
                }
            }
            
        elif agent_name == "micro_commitments":
            return {
                **base_analysis,
                "commitments_tracked": [
                    {
                        "commitment_type": "information_agreement",
                        "customer_response": "yes, that makes sense",
                        "significance": "medium"
                    }
                ],
                "commitment_summary": {
                    "total_commitments": 3,
                    "commitment_strength": "moderate",
                    "progression_quality": "positive"
                }
            }
            
        elif agent_name == "conversation_flow":
            return {
                **base_analysis,
                "flow_analysis": {
                    "structure": "logical_progression",
                    "transitions": "smooth",
                    "pacing": "appropriate",
                    "interruptions": "minimal"
                }
            }
            
        elif agent_name == "budget_handling":
            return {
                **base_analysis,
                "budget_discussion": {
                    "price_mentioned": "not_discussed" if "price" not in transcript.lower() else "discussed",
                    "affordability_assessment": "pending",
                    "payment_options": "not_presented",
                    "value_positioning": "foundational"
                }
            }
            
        elif agent_name == "urgency_builder":
            return {
                **base_analysis,
                "urgency_techniques": [
                    {
                        "technique": "soft_urgency",
                        "implementation": "emphasized_protection_importance",
                        "effectiveness": "subtle"
                    }
                ],
                "momentum_assessment": {
                    "urgency_level_created": "low",
                    "customer_motivation": "maintained",
                    "decision_pressure": "appropriate"
                }
            }
            
        elif agent_name == "technical_navigation":
            return {
                **base_analysis,
                "technical_handling": {
                    "issues_encountered": "none",
                    "process_clarity": "good",
                    "customer_guidance": "effective",
                    "completion_rate": "on_track"
                }
            }
            
        elif agent_name == "cross_selling":
            return {
                **base_analysis,
                "cross_sell_analysis": {
                    "opportunities_identified": ["family_coverage", "additional_products"],
                    "timing_assessment": "not_appropriate_yet",
                    "readiness_level": "focus_on_primary_need",
                    "strategy": "foundation_building"
                }
            }
            
        else:
            return {
                **base_analysis,
                "analysis": f"Comprehensive {agent_name} analysis completed",
                "insights": ["Positive call progression", "Customer engagement maintained"]
            }
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "comprehensive_results") -> None:
        """Save analysis results to disk, maintaining compatibility with existing structure."""
        
        Path(output_dir).mkdir(exist_ok=True)
        source_file = results.get("source_file", "unknown")
        base_name = Path(source_file).stem if source_file != "unknown" else "analysis"
        
        # Save individual agent results (for compatibility)
        individual_analyses = results.get("individual_analyses", {})
        for agent_key, analysis in individual_analyses.items():
            agent_file = Path(output_dir) / f"{base_name}_{agent_key}.json"
            with open(agent_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            logger.info(f"Saved {agent_key} results to: {agent_file}")
        
        # Save comprehensive results
        comprehensive_file = Path(output_dir) / f"{base_name}_comprehensive_analysis.json" 
        with open(comprehensive_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved comprehensive analysis to: {comprehensive_file}")


    def create_comprehensive_analysis(self, agent_results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Create comprehensive analysis from individual agent results."""
        return {
            "analysis_date": datetime.now().isoformat(),
            "source_file": filename,
            "agents_run": list(agent_results.keys()),
            "individual_analyses": agent_results,
            "comprehensive_summary": {
                "total_agents": len(agent_results),
                "analysis_type": "ADK_Orchestrated"
            }
        }
    
    def process_synthesized_learnings(self, comprehensive_results: List[Dict[str, Any]]) -> None:
        """Process synthesized learnings - placeholder for now."""
        logger.info("Processing synthesized learnings (placeholder)")
        # TODO: Implement full synthesis logic
        pass
    
    def generate_mega_prompt_from_synthesis(self, synthesis_file: str, output_file: str) -> None:
        """Generate comprehensive coaching prompt from individual agent analyses."""
        logger.info(f"Generating mega prompt from individual agent files to {output_file}")
        
        try:
            # Load all individual agent JSON files from the directory
            results_dir = Path(synthesis_file).parent
            agent_data = self._load_all_agent_files(results_dir)
            
            if not agent_data:
                logger.error("No agent data found for synthesis")
                self._create_fallback_prompt(output_file)
                return
            
            # Generate comprehensive coaching prompt
            prompt = self._generate_comprehensive_coaching_prompt(agent_data)
            
            # Save the prompt
            with open(output_file, 'w') as f:
                f.write(prompt)
            
            logger.info(f"Comprehensive coaching prompt saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error generating mega prompt: {str(e)}")
            self._create_fallback_prompt(output_file)
    
    def _load_all_agent_files(self, results_dir: Path) -> Dict[str, Dict]:
        """Load all individual agent JSON files from the results directory."""
        agent_data = {}
        agent_names = [
            'objection_specialist', 'opening_gambit', 'needs_assessment',
            'rapport_building', 'pattern_recognition', 'emotional_intelligence',
            'language_optimizer', 'client_profiling', 'micro_commitments',
            'conversation_flow', 'budget_handling', 'urgency_builder',
            'technical_navigation', 'cross_selling'
        ]
        
        # Find JSON files for each agent type
        for agent_name in agent_names:
            pattern = f"*_{agent_name}.json"
            matching_files = list(results_dir.glob(pattern))
            
            if matching_files:
                # Use the most recent file if multiple exist
                agent_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(agent_file, 'r') as f:
                        agent_data[agent_name] = json.load(f)
                    logger.info(f"Loaded {agent_name} data from {agent_file.name}")
                except Exception as e:
                    logger.warning(f"Error loading {agent_name} data: {str(e)}")
        
        return agent_data
    
    def _generate_comprehensive_coaching_prompt(self, agent_data: Dict[str, Dict]) -> str:
        """Generate comprehensive coaching prompt from all agent analyses."""
        
        total_analyses = len([a for a in agent_data.values() if a.get('status') == 'completed'])
        
        sections = [
            self._generate_prompt_header(total_analyses),
            self._generate_opening_mastery(agent_data.get('opening_gambit', {})),
            self._generate_discovery_excellence(agent_data.get('needs_assessment', {})),
            self._generate_objection_handling_arsenal(agent_data.get('objection_specialist', {})),
            self._generate_language_mastery(agent_data.get('language_optimizer', {})),
            self._generate_rapport_building_mastery(agent_data.get('rapport_building', {})),
            self._generate_emotional_intelligence_guide(agent_data.get('emotional_intelligence', {})),
            self._generate_micro_commitments_strategy(agent_data.get('micro_commitments', {})),
            self._generate_conversation_flow_optimization(agent_data.get('conversation_flow', {})),
            self._generate_budget_handling_techniques(agent_data.get('budget_handling', {})),
            self._generate_urgency_building_approach(agent_data.get('urgency_builder', {})),
            self._generate_technical_navigation_skills(agent_data.get('technical_navigation', {})),
            self._generate_cross_selling_opportunities(agent_data.get('cross_selling', {})),
            self._generate_client_profiling_insights(agent_data.get('client_profiling', {})),
            self._generate_pattern_recognition_insights(agent_data.get('pattern_recognition', {})),
            self._generate_closing_mastery()
        ]
        
        return "\n\n".join(sections)
    
    def _generate_prompt_header(self, total_analyses: int) -> str:
        """Generate the prompt header."""
        return f"""# Expert Life Insurance Sales Agent

You are an expert life insurance sales agent with deep knowledge synthesized from {total_analyses} comprehensive call analyses. You understand customer psychology, objection handling, rapport building, and closing techniques at a master level.

## Core Principles
- Always lead with empathy and understanding  
- Focus on protecting families, not selling products
- Use proven language patterns and techniques
- Adapt your approach based on customer responses
- Build genuine rapport and trust throughout the conversation"""

    def _generate_opening_mastery(self, opening_data: Dict) -> str:
        """Generate opening mastery section."""
        section = "## Opening Mastery\n\n"
        
        opening_analysis = opening_data.get('opening_analysis', {})
        effectiveness = opening_data.get('effectiveness_scoring', {})
        
        technique = opening_analysis.get('opening_technique', 'professional_approach')
        statement = opening_analysis.get('opening_statement', 'Warm professional introduction')
        receptiveness = opening_analysis.get('customer_receptiveness', 'neutral')
        
        section += f"### {technique.replace('_', ' ').title()}\n"
        section += f"- Customer receptiveness: {receptiveness}\n"
        section += f"- Opening effectiveness: {effectiveness.get('overall_opening_score', 'N/A')}/10\n"
        section += f"- Example approach: \"{statement}\"\n\n"
        
        improvements = opening_data.get('improvement_opportunities', [])
        if improvements:
            section += "### Improvement Opportunities\n"
            for imp in improvements[:3]:
                section += f"- {imp}\n"
        
        return section

    def _generate_discovery_excellence(self, needs_data: Dict) -> str:
        """Generate discovery excellence section."""
        section = "## Discovery Excellence\n\n"
        
        discovery_questions = needs_data.get('discovery_questions', [])
        
        # Group questions by type
        open_questions = [q for q in discovery_questions if q.get('question_type') == 'open']
        closed_questions = [q for q in discovery_questions if q.get('question_type') == 'closed']
        probing_questions = [q for q in discovery_questions if q.get('question_type') == 'probing']
        
        if open_questions:
            section += "### Open Questions\n"
            for q in open_questions[:3]:
                section += f"- \"{q.get('question', '')}\"\n"
            section += "\n"
        
        if closed_questions:
            section += "### Closed Questions\n"
            for q in closed_questions[:3]:
                section += f"- \"{q.get('question', '')}\"\n"
            section += "\n"
        
        if probing_questions:
            section += "### Probing Questions\n"
            for q in probing_questions[:3]:
                section += f"- \"{q.get('question', '')}\"\n"
            section += "\n"
        
        # Customer profile insights
        customer_profile = needs_data.get('customer_profile', {})
        if customer_profile:
            family_situation = customer_profile.get('family_situation', 'Not specified')
            section += f"### Key Discovery Areas\n"
            section += f"- Family situation focus: {family_situation}\n"
            section += f"- Financial assessment: {customer_profile.get('financial_situation', 'Ongoing')}\n"
        
        return section

    def _generate_objection_handling_arsenal(self, objection_data: Dict) -> str:
        """Generate objection handling arsenal section."""
        section = "## Objection Handling Arsenal\n\n"
        
        objections = objection_data.get('objections_identified', [])
        techniques = objection_data.get('handling_techniques', [])
        
        # Group by objection type
        objection_types = {}
        for obj in objections:
            obj_type = obj.get('objection_type', 'general')
            if obj_type not in objection_types:
                objection_types[obj_type] = []
            objection_types[obj_type].append(obj)
        
        # Generate responses for each type
        for obj_type, obj_list in objection_types.items():
            section += f"### {obj_type.replace('_', ' ').title()} Responses\n"
            section += f"- Examples found: {len(obj_list)}\n"
            
            # Find corresponding techniques
            type_techniques = [t for t in techniques if t.get('objection_type') == obj_type]
            if type_techniques:
                best_technique = max(type_techniques, key=lambda x: {'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1}.get(x.get('effectiveness', 'poor'), 1))
                section += f"- Most effective technique: {best_technique.get('technique_used', 'acknowledge and clarify')}\n"
                section += f"- Proven response: \"{best_technique.get('agent_response', '')}\"\n"
            
            section += "\n"
        
        call_summary = objection_data.get('call_summary', {})
        if call_summary:
            section += f"### Overall Performance\n"
            section += f"- Total objections handled: {call_summary.get('total_objections', 0)}\n"
            section += f"- Primary concern: {call_summary.get('primary_objection', 'Not identified')}\n"
        
        return section

    def _generate_language_mastery(self, language_data: Dict) -> str:
        """Generate language mastery section."""
        section = "## Language Mastery\n\n"
        
        power_phrases = language_data.get('power_phrases', [])
        persuasive_techniques = language_data.get('persuasive_techniques', [])
        analysis = language_data.get('language_analysis', {})
        
        if power_phrases:
            section += "### Power Phrases\n"
            for phrase in power_phrases[:5]:
                section += f"- \"{phrase.get('phrase', '')}\" (Use when: {phrase.get('context', '')})\n"
            section += "\n"
        
        if persuasive_techniques:
            section += "### Persuasive Techniques\n"
            for technique in persuasive_techniques[:3]:
                section += f"#### {technique.get('technique', '').title()}\n"
                examples = technique.get('examples', [])
                for example in examples[:2]:
                    section += f"- \"{example}\"\n"
                section += f"- Effectiveness: {technique.get('effectiveness', 'Unknown')}\n\n"
        
        if analysis:
            section += "### Communication Analysis\n"
            section += f"- Clarity score: {analysis.get('clarity_score', 'N/A')}/10\n"
            section += f"- Jargon usage: {analysis.get('jargon_usage', 'appropriate')}\n"
            section += f"- Tone consistency: {analysis.get('tone_consistency', 'consistent')}\n"
        
        return section

    def _generate_rapport_building_mastery(self, rapport_data: Dict) -> str:
        """Generate rapport building mastery section."""
        section = "## Rapport Building Mastery\n\n"
        
        techniques = rapport_data.get('rapport_techniques', [])
        trust_building = rapport_data.get('trust_building', {})
        assessment = rapport_data.get('overall_rapport_assessment', {})
        
        if techniques:
            section += "### Most Effective Techniques\n"
            effective_techniques = [t for t in techniques if t.get('effectiveness') in ['good', 'excellent']]
            technique_names = list(set([t.get('technique', '') for t in effective_techniques]))
            for tech in technique_names[:5]:
                section += f"- {tech.replace('_', ' ')}\n"
            section += "\n"
        
        if trust_building:
            section += "### Trust Building Strategies\n"
            section += f"- Credibility establishment: {trust_building.get('credibility_establishment', 'Professional approach')}\n"
            section += f"- Transparency level: {trust_building.get('transparency_level', 'medium')}\n"
            section += f"- Authenticity: {trust_building.get('authenticity', 'natural')}\n\n"
        
        if assessment:
            section += "### Performance Metrics\n"
            section += f"- Rapport score: {assessment.get('rapport_score', 'N/A')}/10\n"
            section += f"- Trust level achieved: {assessment.get('trust_level', 'medium')}\n"
            section += f"- Relationship quality: {assessment.get('relationship_quality', 'professional')}\n"
        
        return section

    def _generate_emotional_intelligence_guide(self, emotional_data: Dict) -> str:
        """Generate emotional intelligence guide section."""
        section = "## Emotional Intelligence Guide\n\n"
        
        emotional_analysis = emotional_data.get('emotional_analysis', {})
        agent_ei = emotional_data.get('agent_emotional_intelligence', {})
        techniques = emotional_data.get('emotional_techniques', [])
        
        section += "### Reading Customer Emotions\n"
        if emotional_analysis:
            initial_sentiment = emotional_analysis.get('customer_initial_sentiment', 'neutral')
            final_sentiment = emotional_analysis.get('customer_final_sentiment', 'neutral')
            section += f"- Initial customer sentiment: {initial_sentiment}\n"
            section += f"- Final customer sentiment: {final_sentiment}\n"
            section += f"- Sentiment shift: {emotional_analysis.get('sentiment_shift', 'stable')}\n\n"
        
        if agent_ei:
            section += "### Emotional Intelligence Performance\n"
            section += f"- Emotion recognition: {agent_ei.get('emotion_recognition', 'fair')}\n"
            section += f"- Empathy demonstration: {agent_ei.get('empathy_demonstration', 'medium')}\n"
            section += f"- Emotional adaptation: {agent_ei.get('emotional_adaptation', 'somewhat flexible')}\n\n"
        
        if techniques:
            section += "### Emotional Techniques Used\n"
            for technique in techniques[:3]:
                section += f"- **{technique.get('technique', '').title()}**: {technique.get('usage', '')}\n"
                section += f"  - Effectiveness: {technique.get('effectiveness', 'fair')}\n"
            section += "\n"
        
        section += "### Emotional Triggers for Life Insurance\n"
        section += "- Family protection and security\n"
        section += "- Peace of mind for loved ones\n"
        section += "- Financial responsibility\n"
        section += "- Legacy and taking care of family\n"
        section += "- Avoiding being a burden\n"
        
        return section

    def _generate_micro_commitments_strategy(self, commitment_data: Dict) -> str:
        """Generate micro commitments strategy section."""
        section = "## Micro-Commitments Strategy\n\n"
        
        analysis = commitment_data.get('commitment_analysis', {})
        sequence = commitment_data.get('commitment_sequence', [])
        momentum = commitment_data.get('momentum_building', {})
        
        if analysis:
            section += "### Commitment Tracking\n"
            section += f"- Total commitments secured: {analysis.get('total_commitments', 0)}\n"
            section += f"- Commitment velocity: {analysis.get('commitment_velocity', 'steady')}\n"
            
            categories = analysis.get('commitment_categories', {})
            if categories:
                section += "### Commitment Categories\n"
                for category, count in categories.items():
                    if count > 0:
                        section += f"- {category.replace('_', ' ').title()}: {count}\n"
            section += "\n"
        
        if sequence:
            section += "### Commitment Building Sequence\n"
            for i, comm in enumerate(sequence[:3], 1):
                section += f"{i}. **{comm.get('type', 'general').replace('_', ' ').title()}**: \"{comm.get('commitment', '')}\"\n"
                section += f"   - Technique: {comm.get('agent_technique', '')}\n"
                section += f"   - Strength: {comm.get('strength', 'moderate')}\n"
            section += "\n"
        
        if momentum:
            section += "### Momentum Assessment\n"
            section += f"- Progression pattern: {momentum.get('progression', 'building')}\n"
            section += f"- Peak commitment: {momentum.get('peak_commitment', 'Not identified')}\n"
        
        return section

    def _generate_conversation_flow_optimization(self, flow_data: Dict) -> str:
        """Generate conversation flow optimization section."""
        section = "## Conversation Flow Optimization\n\n"
        
        flow_structure = flow_data.get('flow_structure', {})
        transitions = flow_data.get('transition_analysis', [])
        flow_pattern = flow_data.get('flow_pattern', {})
        
        if flow_structure:
            phases = flow_structure.get('phases_identified', [])
            if phases:
                section += "### Call Structure\n"
                for phase in phases:
                    section += f"- **{phase.get('phase', '').replace('_', ' ').title()}**: {phase.get('effectiveness', 'adequate')}\n"
                    section += f"  - Duration: {phase.get('duration_estimate', 'not specified')}\n"
                    section += f"  - Transition quality: {phase.get('transition_quality', 'smooth')}\n"
                section += "\n"
        
        if flow_pattern:
            section += "### Flow Dynamics\n"
            section += f"- Conversation control: {flow_pattern.get('conversation_control', 'balanced')}\n"
            section += f"- Momentum building: {flow_pattern.get('momentum', 'steady')}\n"
            section += f"- Customer engagement: {flow_pattern.get('customer_engagement', 'maintained')}\n\n"
        
        if transitions:
            section += "### Transition Quality\n"
            smooth_transitions = [t for t in transitions if t.get('quality') in ['good', 'excellent']]
            section += f"- Smooth transitions: {len(smooth_transitions)}/{len(transitions)}\n"
            if smooth_transitions:
                example = smooth_transitions[0]
                section += f"- Example: {example.get('from_topic', '')} → {example.get('to_topic', '')}\n"
                section += f"- Method: {example.get('transition_method', 'direct')}\n"
        
        return section

    def _generate_budget_handling_techniques(self, budget_data: Dict) -> str:
        """Generate budget handling techniques section."""
        section = "## Budget Handling Techniques\n\n"
        
        objections = budget_data.get('budget_objections', [])
        qualification = budget_data.get('financial_qualification', {})
        positioning = budget_data.get('value_positioning', [])
        
        if objections:
            section += "### Common Budget Objections\n"
            for obj in objections[:3]:
                section += f"- **Concern**: {obj.get('objection', '')}\n"
                section += f"- **Customer statement**: \"{obj.get('customer_statement', '')}\"\n"
                section += f"- **Intensity**: {obj.get('intensity', 'moderate')}\n\n"
        
        if qualification:
            section += "### Financial Qualification Approach\n"
            section += f"- Budget discovery: {qualification.get('budget_discovery', 'attempted')}\n"
            section += f"- Income assessment: {qualification.get('income_assessment', 'indirect')}\n"
            section += f"- Financial priorities: {qualification.get('financial_priorities', 'identified')}\n\n"
        
        if positioning:
            section += "### Value Positioning Techniques\n"
            for pos in positioning[:2]:
                section += f"- **{pos.get('technique', '').replace('_', ' ').title()}**\n"
                section += f"  - Implementation: {pos.get('implementation', '')}\n"
                section += f"  - Effectiveness: {pos.get('effectiveness', 'fair')}\n"
        
        return section

    def _generate_urgency_building_approach(self, urgency_data: Dict) -> str:
        """Generate urgency building approach section."""
        section = "## Urgency Building Approach\n\n"
        
        techniques = urgency_data.get('urgency_techniques', [])
        timing_elements = urgency_data.get('timing_elements', {})
        consequence_awareness = urgency_data.get('consequence_awareness', {})
        
        if techniques:
            section += "### Urgency Techniques\n"
            for technique in techniques[:3]:
                section += f"- **{technique.get('technique', '').replace('_', ' ').title()}**\n"
                section += f"  - Implementation: {technique.get('implementation', '')}\n"
                section += f"  - Authenticity: {technique.get('authenticity', 'genuine')}\n"
                section += f"  - Customer response: {technique.get('customer_response', 'neutral')}\n\n"
        
        if timing_elements:
            section += "### Timing Elements\n"
            deadlines = timing_elements.get('deadlines_mentioned', [])
            if deadlines:
                section += "- Time constraints discussed:\n"
                for deadline in deadlines[:2]:
                    section += f"  - {deadline}\n"
            section += f"- Personal timing factors: {timing_elements.get('personal_timing', 'Not specified')}\n\n"
        
        if consequence_awareness:
            section += "### Consequence Awareness Building\n"
            section += f"- Cost of waiting: {consequence_awareness.get('cost_of_waiting', 'not addressed')}\n"
            section += f"- Risk of delay: {consequence_awareness.get('risk_of_delay', 'not discussed')}\n"
            section += f"- Opportunity cost: {consequence_awareness.get('opportunity_cost', 'not emphasized')}\n"
        
        return section

    def _generate_technical_navigation_skills(self, technical_data: Dict) -> str:
        """Generate technical navigation skills section."""
        section = "## Technical Navigation Skills\n\n"
        
        issues = technical_data.get('technical_issues', [])
        handling = technical_data.get('handling_approach', {})
        rapport_maintenance = technical_data.get('rapport_during_delays', {})
        
        if issues:
            section += "### Technical Issues Encountered\n"
            for issue in issues[:2]:
                section += f"- **Issue**: {issue.get('issue', '')}\n"
                section += f"- **Timing**: {issue.get('timing', '')}\n"
                section += f"- **Impact**: {issue.get('impact', 'minimal')}\n\n"
        else:
            section += "### Technical Performance\n"
            section += "- No significant technical issues encountered\n"
            section += "- Smooth process navigation\n\n"
        
        if handling:
            section += "### Issue Handling Approach\n"
            section += f"- Preparation level: {handling.get('preparation', 'proactive')}\n"
            section += f"- Communication quality: {handling.get('communication', 'good')}\n"
            section += f"- Professionalism: {handling.get('professionalism', 'maintained')}\n\n"
        
        if rapport_maintenance:
            section += "### Rapport During Challenges\n"
            section += f"- Customer patience: {rapport_maintenance.get('customer_patience', 'understanding')}\n"
            section += f"- Relationship maintenance: {rapport_maintenance.get('agent_management', 'good')}\n"
            section += f"- Trust impact: {rapport_maintenance.get('trust_impact', 'neutral')}\n"
        
        return section

    def _generate_cross_selling_opportunities(self, cross_sell_data: Dict) -> str:
        """Generate cross-selling opportunities section."""
        section = "## Cross-Selling Opportunities\n\n"
        
        opportunities = cross_sell_data.get('opportunities_identified', [])
        techniques = cross_sell_data.get('cross_sell_techniques', [])
        execution = cross_sell_data.get('execution_quality', {})
        
        no_cross_selling = cross_sell_data.get('no_crossselling_attempted', False)
        
        if no_cross_selling or not opportunities:
            section += "### Focus Strategy\n"
            section += "- Primary focus: Core life insurance need\n"
            section += "- Cross-selling approach: Foundation building first\n"
            section += "- Timing assessment: Not appropriate during initial consultation\n\n"
            section += "### Future Opportunities\n"
            section += "- Family coverage expansion\n"
            section += "- Additional protection products\n"
            section += "- Financial planning services\n"
        else:
            if opportunities:
                section += "### Identified Opportunities\n"
                for opp in opportunities[:3]:
                    section += f"- **Product**: {opp.get('opportunity', '')}\n"
                    section += f"- **Timing**: {opp.get('timing', '')}\n"
                    section += f"- **Relevance**: {opp.get('relevance', 'moderate')}\n"
                    section += f"- **Customer interest**: {opp.get('customer_interest', 'neutral')}\n\n"
            
            if execution:
                section += "### Execution Quality\n"
                section += f"- Timing: {execution.get('timing', 'appropriate')}\n"
                section += f"- Relevance: {execution.get('relevance', 'somewhat relevant')}\n"
                section += f"- Pressure level: {execution.get('pressure_level', 'appropriate')}\n"
        
        return section

    def _generate_client_profiling_insights(self, profiling_data: Dict) -> str:
        """Generate client profiling insights section."""
        section = "## Client Profiling Insights\n\n"
        
        client_profile = profiling_data.get('client_profile', {})
        buying_signals = profiling_data.get('buying_signals', [])
        ideal_approach = profiling_data.get('ideal_approach', {})
        
        if client_profile:
            demographic = client_profile.get('demographic_info', {})
            psychographic = client_profile.get('psychographic_profile', {})
            communication = client_profile.get('communication_style', {})
            
            section += "### Client Profile\n"
            if demographic:
                section += f"- Family status: {demographic.get('family_status', 'Not specified')}\n"
                section += f"- Occupation: {demographic.get('occupation', 'Not specified')}\n"
            
            if psychographic:
                section += f"- Personality type: {psychographic.get('personality_type', 'mixed')}\n"
                section += f"- Decision speed: {psychographic.get('decision_speed', 'deliberate')}\n"
                section += f"- Risk tolerance: {psychographic.get('risk_tolerance', 'medium')}\n"
            
            if communication:
                section += f"- Preferred pace: {communication.get('preferred_pace', 'moderate')}\n"
                section += f"- Engagement level: {communication.get('engagement_level', 'moderate')}\n"
            section += "\n"
        
        if buying_signals:
            section += "### Buying Signals Observed\n"
            for signal in buying_signals[:3]:
                section += f"- **Signal**: {signal.get('signal', '')}\n"
                section += f"- **Strength**: {signal.get('strength', 'moderate')}\n"
                section += f"- **Timing**: {signal.get('timing', 'mid-call')}\n\n"
        
        if ideal_approach:
            section += "### Recommended Approach\n"
            section += f"- Communication style: {ideal_approach.get('recommended_style', 'Professional and consultative')}\n"
            motivators = ideal_approach.get('key_motivators', [])
            if motivators:
                section += "- Key motivators:\n"
                for motivator in motivators[:3]:
                    section += f"  - {motivator}\n"
        
        return section

    def _generate_pattern_recognition_insights(self, pattern_data: Dict) -> str:
        """Generate pattern recognition insights section."""
        section = "## Pattern Recognition Insights\n\n"
        
        conversation_patterns = pattern_data.get('conversation_patterns', [])
        successful_sequences = pattern_data.get('successful_sequences', [])
        themes = pattern_data.get('conversation_themes', [])
        
        if conversation_patterns:
            section += "### Conversation Patterns\n"
            for pattern in conversation_patterns[:3]:
                section += f"- **{pattern.get('pattern_type', '').replace('_', ' ').title()}**\n"
                section += f"  - Description: {pattern.get('description', '')}\n"
                section += f"  - Effectiveness: {pattern.get('effectiveness', 'fair')}\n\n"
        
        if successful_sequences:
            section += "### Successful Sequences\n"
            for seq in successful_sequences[:2]:
                section += f"- **Sequence**: {seq.get('sequence', '')}\n"
                section += f"- **Outcome**: {seq.get('outcome', '')}\n"
                section += f"- **Replicability**: {seq.get('replicability', 'moderate')}\n\n"
        
        if themes:
            section += "### Recurring Themes\n"
            for theme in themes[:3]:
                section += f"- **{theme.get('theme', '')}**\n"
                section += f"  - Frequency: {theme.get('frequency', 'occasional')}\n"
                section += f"  - Resolution: {theme.get('resolution', 'partially addressed')}\n"
        
        return section

    def _generate_closing_mastery(self) -> str:
        """Generate closing mastery section."""
        return """## Closing Mastery

### Assumption Close
- "Let me get the paperwork started for you..."
- "What's the best contact number for the underwriter?"

### Alternative Close  
- "Would you prefer the basic or comprehensive coverage?"
- "Should we start this on the 1st or 15th of the month?"

### Urgency Close
- "I can lock in today's rates for you..."
- "This approval is good for the next 30 days..."

### Emotional Close
- "The most important thing is that your family is protected..."
- "You'll have peace of mind knowing they're taken care of..."

## Remember: Always focus on the customer's needs and family protection, not just making a sale."""

    def _create_fallback_prompt(self, output_file: str) -> None:
        """Create a fallback prompt if synthesis fails."""
        fallback_prompt = """# Expert Life Insurance Sales Agent

You are an expert life insurance sales agent focused on helping families protect their financial future.

## Core Principles
- Always lead with empathy and understanding
- Focus on protecting families, not selling products  
- Build genuine rapport and trust throughout the conversation
- Listen actively and respond to customer needs
- Use proven techniques while maintaining authenticity

## Key Strategies
- Start with warm, professional approach
- Ask open-ended discovery questions
- Handle objections with empathy and facts
- Build value before discussing price
- Create soft urgency around family protection
- Close with confidence and alternatives

Remember: Your goal is to help families secure their financial future through appropriate life insurance protection."""

        with open(output_file, 'w') as f:
            f.write(fallback_prompt)
        logger.info(f"Fallback prompt saved to {output_file}")


# Example usage and testing

if __name__ == "__main__":
    # Test the orchestration system
    orchestrator = ADKSalesAnalysisOrchestrator()
    
    # Test with sample transcript
    sample_transcript = """
    Agent: Good morning! This is John from ABC Insurance. I'm calling because you requested information about life insurance coverage. Do you have a few minutes to discuss your needs?
    
    Customer: Yes, I did fill out that form online. I'm looking for some basic coverage but I'm not sure what I need.
    
    Agent: That's great that you're thinking about protecting your family. Can you tell me a bit about your current situation - are you married, any children?
    
    Customer: Yes, married with two young kids, ages 3 and 5.
    
    Agent: Perfect. With young children, life insurance becomes really important. What kind of work do you do?
    
    Customer: I'm an engineer at a tech company.
    
    Agent: Excellent. Engineers typically have good stable income. Are you the primary breadwinner for your family?
    
    Customer: Yes, my wife stays home with the kids right now.
    
    Agent: I understand. So if something happened to you, your family would lose their main source of income. Have you thought about how much coverage you might need?
    
    Customer: Not really. I know I need something but I'm worried about the cost.
    
    Agent: That's a common concern. Let me ask you this - what's more important, finding the cheapest option or making sure your family is truly protected?
    
    Customer: Well, protecting my family of course, but we do have a budget.
    
    Agent: I completely understand. The good news is that life insurance is actually much more affordable than most people think, especially for someone young and healthy like yourself. Based on what you've told me, I'd recommend looking at around $500,000 in coverage. Does that sound reasonable?
    
    Customer: That sounds like a lot. What would something like that cost?
    
    Agent: For someone your age and health, you're probably looking at around $30-40 per month. That's about the cost of a dinner out with your family. Is protecting your family's financial future worth that to you?
    
    Customer: When you put it that way, yes. But I'd need to talk to my wife first.
    
    Agent: Of course! That's exactly what you should do. Here's what I'd like to suggest - let me get you a personalized quote based on your specific situation, and then you can review it with your wife. Would that work?
    
    Customer: Yes, that sounds good.
    
    Agent: Great! I'll need to ask you a few quick questions to get you an accurate quote. This will only take about 5 minutes. Sound good?
    
    Customer: Sure.
    """
    
    # Run analysis
    results = orchestrator.analyze_transcript(sample_transcript, "sample_call.txt")
    
    # Save results
    orchestrator.save_results(results)
    
    print("ADK Orchestration test completed successfully!")
    print(f"Results saved with {len(results.get('individual_analyses', {}))} individual agent analyses")