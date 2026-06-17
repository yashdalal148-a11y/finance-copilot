"""
Strongly-typed domain models for the entire agent pipeline.

Every inter-agent data exchange uses one of these Pydantic models.
No loose dictionaries anywhere in the codebase.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────

class QuestionCategory(str, Enum):
    """Finance interview question categories."""

    VALUATION = "valuation"
    ACCOUNTING = "accounting"
    EQUITY_RESEARCH = "equity_research"
    MARKETS = "markets"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    UNKNOWN = "unknown"

class TaskType(str, Enum):
    """Types of LLM tasks for routing purposes."""
    CLASSIFICATION = "classification"
    BATTLEFIELD_MAP = "battlefield_map"
    FOLLOW_UP = "follow_up"
    EVALUATION = "evaluation"
    STORY_INTELLIGENCE = "story_intelligence"
    RED_FLAG = "red_flag"
    EXPERT_ANSWER = "expert_answer"
    RESUME_PARSING = "resume_parsing"
    JD_PARSING = "jd_parsing"
    FIT_ANALYSIS = "fit_analysis"
    INTENT_ANALYSIS = "intent_analysis"
    GAP_ANALYSIS = "gap_analysis"
    OFFER_PROBABILITY = "offer_probability"
    MEMORY_CONSOLIDATION = "memory_consolidation"
    STOCK_PITCH = "stock_pitch"
    WEAKNESS_ANALYSIS = "weakness_analysis"
    GENERAL = "general"

class ProviderName(str, Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    GROQ = "groq"
    OPENROUTER = "openrouter"


# ── Agent Data Models ─────────────────────────────────────────────────────

class TranscriptionResult(BaseModel):
    """Output of the Listener Agent."""

    text: str = ""
    language: str = "en"
    duration_seconds: float = 0.0

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


class SessionContext(BaseModel):
    """Output of the Context Agent — enriched session context."""

    current_question: str = ""
    question_number: int = 1
    previous_questions: List[str] = Field(default_factory=list)
    previous_answers: List[str] = Field(default_factory=list)
    session_topics: List[str] = Field(default_factory=list)

    def summary_for_prompt(self) -> str:
        """Return a concise string suitable for injecting into LLM prompts."""
        if not self.previous_questions:
            return "This is the first question in this session."
        lines = [f"This is question #{self.question_number} in the session."]
        lines.append(f"Topics covered so far: {', '.join(self.session_topics)}.")
        for i, (q, a) in enumerate(
            zip(self.previous_questions[-3:], self.previous_answers[-3:]), 1
        ):
            lines.append(f"  Q{i}: {q[:120]}")
            lines.append(f"  A{i}: {a[:200]}...")
        return "\n".join(lines)


class QuestionClassification(BaseModel):
    """Output of the Interview Agent."""

    category: QuestionCategory = QuestionCategory.UNKNOWN
    subcategory: str = ""
    confidence: float = 0.0
    reasoning: str = ""


class KnowledgeSection(BaseModel):
    """A single section extracted from a knowledge markdown file."""

    title: str = ""
    content: str = ""
    source_file: str = ""
    relevance_score: float = 0.0


class KnowledgeResult(BaseModel):
    """Output of the Knowledge Agent."""

    passages: List[KnowledgeSection] = Field(default_factory=list)
    category: str = ""

    def combined_text(self) -> str:
        """Merge passages into a single context block for LLM prompts."""
        parts: list[str] = []
        for p in self.passages:
            parts.append(f"### {p.title}\n{p.content}")
        return "\n\n".join(parts)


class ExpertAnswer(BaseModel):
    """Output of the Finance Expert Agent."""

    answer: str = ""
    key_points: List[str] = Field(default_factory=list)
    frameworks_used: List[str] = Field(default_factory=list)


class FollowUpPrediction(BaseModel):
    """Output of the Follow-Up Agent."""

    questions: List[str] = Field(default_factory=list)
    reasoning: str = ""


class EvaluationScore(BaseModel):
    """Output of the Evaluation Agent."""

    confidence_score: float = 0.0
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    readiness_score: float = 0.0
    overall_score: float = 0.0
    feedback: str = ""
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    improvement_plan: List[str] = Field(default_factory=list)


# ── Intelligence Layer Models ─────────────────────────────────────────────

class CandidateProfile(BaseModel):
    """Output of the Resume Intelligence Agent."""
    
    experience: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    sector_expertise: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class JobProfile(BaseModel):
    """Output of the Job Description Intelligence Agent."""
    
    role: str = ""
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    seniority: str = ""
    domain: str = ""


class FitAnalysis(BaseModel):
    """Output of the Fit Analysis Agent."""
    
    match_score: float = 0.0
    strengths: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    likely_interview_topics: List[str] = Field(default_factory=list)


# ── Career Intelligence Models (V1.3) ─────────────────────────────────────

class CareerStory(BaseModel):
    title: str = ""
    duration_target: str = ""
    narrative: str = ""
    key_signals: List[str] = Field(default_factory=list)

class InterviewerIntent(BaseModel):
    core_test: str = ""
    technical_depth: str = ""
    communication_signals: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)

class HiringManagerVerdict(BaseModel):
    passing_criteria: str = ""
    red_flag_triggers: List[str] = Field(default_factory=list)
    differentiation_factors: List[str] = Field(default_factory=list)

class BattlefieldQuestion(BaseModel):
    question: str = ""
    probability: float = 0.0
    difficulty: float = 0.0
    importance: float = 0.0
    preparation_priority: str = ""
    intent: Optional[InterviewerIntent] = None
    verdict: Optional[HiringManagerVerdict] = None

class BattlefieldMap(BaseModel):
    top_questions: List[BattlefieldQuestion] = Field(default_factory=list)

class RedFlag(BaseModel):
    flag: str = ""
    interviewer_worry: str = ""
    suggested_response: str = ""
    recovery_strategy: str = ""

class RedFlagAnalysis(BaseModel):
    flags: List[RedFlag] = Field(default_factory=list)

class CareerGapAnalysis(BaseModel):
    missing_experiences: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    suggested_development_plan: List[str] = Field(default_factory=list)

class OfferProbabilityAnalysis(BaseModel):
    offer_probability: float = 0.0
    top_risks: List[str] = Field(default_factory=list)
    highest_leverage_improvements: List[str] = Field(default_factory=list)


# ── Provider Metrics & Health ─────────────────────────────────────────────

class ProviderMetrics(BaseModel):
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0

class ProviderHealthStatus(str, Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"

class ProviderHealth(BaseModel):
    status: ProviderHealthStatus = ProviderHealthStatus.ONLINE
    consecutive_failures: int = 0
    last_failure_time: Optional[float] = None
    last_error_message: str = ""

class ProviderConfig(BaseModel):
    name: ProviderName
    model_id: str
    api_key: str
    temperature: float = 0.3
    timeout: float = 30.0
    max_retries: int = 2


# ── OS V1.5 Memory Models ──────────────────────────────────────────────────

class CandidateMemory(BaseModel):
    strength_trends: List[str] = Field(default_factory=list)
    weakness_trends: List[str] = Field(default_factory=list)
    career_goals: List[str] = Field(default_factory=list)

class CandidateEvolution(BaseModel):
    timeline_events: List[str] = Field(default_factory=list)
    overall_trajectory: str = ""

class InterviewMemory(BaseModel):
    best_answers: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    readiness_history: List[float] = Field(default_factory=list)

class LearningMemory(BaseModel):
    learning_priorities: List[str] = Field(default_factory=list)
    improvement_history: List[str] = Field(default_factory=list)

class StockPitchMemory(BaseModel):
    pitch_history: List[str] = Field(default_factory=list)

class ResearchNotebookEntry(BaseModel):
    id: str = ""
    timestamp: float = 0.0
    category: str = ""  # e.g., Company, Sector, Interview, Personal
    title: str = ""
    content: str = ""

class ResearchMemory(BaseModel):
    """Root representation of distilled intelligence (not raw logs)."""
    candidate: CandidateMemory = Field(default_factory=CandidateMemory)
    evolution: CandidateEvolution = Field(default_factory=CandidateEvolution)
    interview: InterviewMemory = Field(default_factory=InterviewMemory)
    learning: LearningMemory = Field(default_factory=LearningMemory)
    stock_pitch: StockPitchMemory = Field(default_factory=StockPitchMemory)


# ── OS V1.5 Stock Pitch Intelligence ───────────────────────────────────────

class MDCritique(BaseModel):
    blunt_feedback: str = ""
    fatal_flaws: List[str] = Field(default_factory=list)

class InvestmentCommitteeVerdict(BaseModel):
    decision: str = "" # e.g. "PASS", "GREENLIGHT"
    key_debate_points: List[str] = Field(default_factory=list)

class InvestmentMemo(BaseModel):
    business_overview: str = ""
    industry_structure: str = ""
    competitive_landscape: str = ""
    management_assessment: str = ""
    investment_thesis: str = ""
    bull_case: str = ""
    bear_case: str = ""
    catalysts: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    valuation_framework: str = ""
    md_critique: Optional[MDCritique] = None
    ic_verdict: Optional[InvestmentCommitteeVerdict] = None

class StockPitch(BaseModel):
    company_name: str = ""
    ticker: str = ""
    memo: Optional[InvestmentMemo] = None


# ── OS V1.5 Weakness Intelligence ──────────────────────────────────────────

class LearningRoadmap(BaseModel):
    immediate_actions: List[str] = Field(default_factory=list)
    short_term_goals: List[str] = Field(default_factory=list)
    long_term_goals: List[str] = Field(default_factory=list)

class WeaknessAnalysis(BaseModel):
    strength_map: Dict[str, str] = Field(default_factory=dict)
    weakness_map: Dict[str, str] = Field(default_factory=dict)
    skill_gap_analysis: List[str] = Field(default_factory=list)
    roadmap: Optional[LearningRoadmap] = None


# ── Pipeline Envelope ─────────────────────────────────────────────────────

class AgentTiming(BaseModel):
    """Execution timing for a single agent in the pipeline."""

    agent_name: str
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class PipelineResult(BaseModel):
    """Complete output of one pipeline run through the orchestrator."""

    transcription: Optional[TranscriptionResult] = None
    context: Optional[SessionContext] = None
    classification: Optional[QuestionClassification] = None
    knowledge: Optional[KnowledgeResult] = None
    answer: Optional[ExpertAnswer] = None
    follow_ups: Optional[FollowUpPrediction] = None
    evaluation: Optional[EvaluationScore] = None
    timings: List[AgentTiming] = Field(default_factory=list)
    total_duration_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error: Optional[str] = None
