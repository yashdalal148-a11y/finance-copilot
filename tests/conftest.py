"""
Shared test fixtures for the Finance Intelligence Copilot test suite.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.core.config import AppConfig
from app.core.llm_client import GeminiClient
from app.core.models import (
    EvaluationScore,
    ExpertAnswer,
    FollowUpPrediction,
    KnowledgeResult,
    KnowledgeSection,
    QuestionCategory,
    QuestionClassification,
    SessionContext,
    TranscriptionResult,
)
from app.core.session import SessionMemory
from app.core.speech_client import SpeechClient


# ── Paths ─────────────────────────────────────────────────────────────

@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def knowledge_dir(project_root: Path) -> Path:
    return project_root / "knowledge"


@pytest.fixture
def prompts_dir(project_root: Path) -> Path:
    return project_root / "app" / "prompts"


# ── Mock Clients ──────────────────────────────────────────────────────

@pytest.fixture
def mock_llm() -> MagicMock:
    """A mocked GeminiClient."""
    llm = MagicMock(spec=GeminiClient)
    return llm


@pytest.fixture
def mock_speech() -> MagicMock:
    """A mocked SpeechClient."""
    speech = MagicMock(spec=SpeechClient)
    speech.transcribe_bytes.return_value = TranscriptionResult(
        text="Walk me through a DCF analysis",
        language="en",
        duration_seconds=5.0,
    )
    return speech


# ── Sample Data ───────────────────────────────────────────────────────

@pytest.fixture
def sample_transcription() -> TranscriptionResult:
    return TranscriptionResult(
        text="Walk me through a DCF analysis",
        language="en",
        duration_seconds=5.0,
    )


@pytest.fixture
def sample_context() -> SessionContext:
    return SessionContext(
        current_question="Walk me through a DCF analysis",
        question_number=1,
    )


@pytest.fixture
def sample_classification() -> QuestionClassification:
    return QuestionClassification(
        category=QuestionCategory.VALUATION,
        subcategory="DCF",
        confidence=0.95,
        reasoning="Question asks about DCF methodology",
    )


@pytest.fixture
def sample_knowledge() -> KnowledgeResult:
    return KnowledgeResult(
        passages=[
            KnowledgeSection(
                title="Discounted Cash Flow (DCF)",
                content="A DCF values a company by projecting future free cash flows...",
                source_file="valuation.md",
                relevance_score=0.85,
            )
        ],
        category="valuation",
    )


@pytest.fixture
def sample_answer() -> ExpertAnswer:
    return ExpertAnswer(
        answer="A DCF analysis values a company by projecting its future free cash flows and discounting them back to present value using the WACC.",
        key_points=["Project FCF", "Calculate terminal value", "Discount at WACC"],
        frameworks_used=["DCF", "WACC", "Terminal Value"],
    )


@pytest.fixture
def sample_evaluation() -> EvaluationScore:
    return EvaluationScore(
        confidence_score=85,
        completeness_score=80,
        accuracy_score=90,
        overall_score=85,
        feedback="Strong answer with good structure.",
        strengths=["Clear structure", "Correct formulas"],
        improvements=["Could mention sensitivity analysis"],
    )


@pytest.fixture
def sample_follow_ups() -> FollowUpPrediction:
    return FollowUpPrediction(
        questions=[
            "What discount rate would you use?",
            "How do you calculate terminal value?",
            "When would you not use a DCF?",
        ],
        reasoning="Probing deeper into DCF mechanics.",
    )


@pytest.fixture
def session_memory() -> SessionMemory:
    return SessionMemory()
