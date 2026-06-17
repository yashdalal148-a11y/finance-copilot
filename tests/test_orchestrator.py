"""Tests for the Orchestrator pipeline."""

from unittest.mock import MagicMock, patch

from app.agents.context_agent import ContextAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.finance_expert_agent import FinanceExpertAgent
from app.agents.follow_up_agent import FollowUpAgent
from app.agents.interview_agent import InterviewAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.listener_agent import ListenerAgent
from app.agents.orchestrator import Orchestrator
from app.core.models import (
    EvaluationScore,
    ExpertAnswer,
    FollowUpPrediction,
    KnowledgeResult,
    KnowledgeSection,
    PipelineResult,
    QuestionCategory,
    QuestionClassification,
    SessionContext,
    TranscriptionResult,
)
from app.core.session import SessionMemory


def _build_orchestrator(
    session_memory: SessionMemory,
) -> Orchestrator:
    """Build an orchestrator with fully mocked agents."""
    listener = MagicMock(spec=ListenerAgent)
    listener.run.return_value = TranscriptionResult(
        text="Walk me through a DCF",
        language="en",
        duration_seconds=5.0,
    )

    context = ContextAgent(memory=session_memory)

    interview = MagicMock(spec=InterviewAgent)
    interview.run.return_value = QuestionClassification(
        category=QuestionCategory.VALUATION,
        subcategory="DCF",
        confidence=0.95,
    )

    knowledge = MagicMock(spec=KnowledgeAgent)
    knowledge.run.return_value = KnowledgeResult(
        passages=[KnowledgeSection(title="DCF", content="...")],
        category="valuation",
    )

    expert = MagicMock(spec=FinanceExpertAgent)
    expert.run.return_value = ExpertAnswer(
        answer="A DCF analysis values a company...",
        key_points=["Project FCF", "Terminal Value"],
        frameworks_used=["DCF"],
    )

    follow_up = MagicMock(spec=FollowUpAgent)
    follow_up.run.return_value = FollowUpPrediction(
        questions=["What discount rate?", "How to calculate TV?"],
        reasoning="Probing deeper",
    )

    evaluation = MagicMock(spec=EvaluationAgent)
    evaluation.run.return_value = EvaluationScore(
        confidence_score=85,
        completeness_score=80,
        accuracy_score=90,
        overall_score=85,
        feedback="Good answer.",
    )

    return Orchestrator(
        listener=listener,
        context=context,
        interview=interview,
        knowledge=knowledge,
        expert=expert,
        follow_up=follow_up,
        evaluation=evaluation,
        memory=session_memory,
    )


class TestOrchestrator:
    def test_full_pipeline(self, session_memory: SessionMemory) -> None:
        orch = _build_orchestrator(session_memory)
        result = orch.run(b"fake-audio")

        assert isinstance(result, PipelineResult)
        assert result.success is True
        assert result.transcription is not None
        assert result.transcription.text == "Walk me through a DCF"
        assert result.classification is not None
        assert result.classification.category == QuestionCategory.VALUATION
        assert result.answer is not None
        assert result.follow_ups is not None
        assert result.evaluation is not None
        assert len(result.timings) == 7  # All 7 agents
        assert result.total_duration_ms > 0

    def test_pipeline_updates_session_memory(
        self, session_memory: SessionMemory
    ) -> None:
        orch = _build_orchestrator(session_memory)
        orch.run(b"fake-audio")

        assert session_memory.question_count == 1
        assert session_memory.previous_questions == ["Walk me through a DCF"]

    def test_pipeline_empty_transcription(
        self, session_memory: SessionMemory
    ) -> None:
        orch = _build_orchestrator(session_memory)
        orch._listener.run.return_value = TranscriptionResult(text="")
        result = orch.run(b"silence")

        assert result.success is False
        assert result.error is not None
        assert "transcription" in result.error.lower()

    def test_text_pipeline(self, session_memory: SessionMemory) -> None:
        orch = _build_orchestrator(session_memory)
        result = orch.run_text("What is enterprise value?")

        assert isinstance(result, PipelineResult)
        assert result.success is True
        assert result.transcription is not None
        assert result.transcription.text == "What is enterprise value?"

    def test_status_callback(self, session_memory: SessionMemory) -> None:
        orch = _build_orchestrator(session_memory)
        statuses: list[str] = []
        orch.run(b"fake-audio", status_callback=statuses.append)

        assert len(statuses) == 6
        assert any("Transcribing" in s for s in statuses)
        assert any("Classifying" in s for s in statuses)
        assert any("Generating" in s for s in statuses)

    def test_multiple_runs_accumulate_memory(
        self, session_memory: SessionMemory
    ) -> None:
        orch = _build_orchestrator(session_memory)
        orch.run(b"audio1")
        orch.run(b"audio2")

        assert session_memory.question_count == 2
