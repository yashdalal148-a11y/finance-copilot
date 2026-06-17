"""Tests for Pydantic models and the SessionMemory."""

from app.core.models import (
    EvaluationScore,
    ExpertAnswer,
    KnowledgeResult,
    KnowledgeSection,
    PipelineResult,
    QuestionCategory,
    QuestionClassification,
    SessionContext,
    TranscriptionResult,
)
from app.core.session import SessionMemory


class TestTranscriptionResult:
    def test_is_empty_when_blank(self) -> None:
        assert TranscriptionResult(text="").is_empty
        assert TranscriptionResult(text="  ").is_empty

    def test_is_not_empty_with_text(self) -> None:
        assert not TranscriptionResult(text="Hello").is_empty


class TestSessionContext:
    def test_summary_first_question(self) -> None:
        ctx = SessionContext(current_question="test", question_number=1)
        assert "first question" in ctx.summary_for_prompt().lower()

    def test_summary_with_history(self) -> None:
        ctx = SessionContext(
            current_question="test",
            question_number=3,
            previous_questions=["q1", "q2"],
            previous_answers=["a1", "a2"],
            session_topics=["valuation", "accounting"],
        )
        summary = ctx.summary_for_prompt()
        assert "3" in summary
        assert "valuation" in summary


class TestKnowledgeResult:
    def test_combined_text_empty(self) -> None:
        assert KnowledgeResult().combined_text() == ""

    def test_combined_text_with_passages(self) -> None:
        kr = KnowledgeResult(
            passages=[
                KnowledgeSection(title="A", content="Content A"),
                KnowledgeSection(title="B", content="Content B"),
            ]
        )
        combined = kr.combined_text()
        assert "### A" in combined
        assert "Content A" in combined
        assert "### B" in combined


class TestQuestionCategory:
    def test_all_categories(self) -> None:
        expected = {
            "valuation", "accounting", "equity_research",
            "markets", "behavioral", "technical", "unknown",
        }
        actual = {c.value for c in QuestionCategory}
        assert actual == expected


class TestSessionMemory:
    def test_empty(self) -> None:
        mem = SessionMemory()
        assert mem.question_count == 0
        assert mem.previous_questions == []
        assert mem.session_topics == []

    def test_add_and_retrieve(self) -> None:
        mem = SessionMemory()
        mem.add_entry("Q1", "A1", "valuation")
        mem.add_entry("Q2", "A2", "accounting")

        assert mem.question_count == 2
        assert mem.previous_questions == ["Q1", "Q2"]
        assert mem.previous_answers == ["A1", "A2"]
        assert mem.session_topics == ["valuation", "accounting"]

    def test_duplicate_topics(self) -> None:
        mem = SessionMemory()
        mem.add_entry("Q1", "A1", "valuation")
        mem.add_entry("Q2", "A2", "valuation")

        assert mem.session_topics == ["valuation"]  # No duplicates

    def test_clear(self) -> None:
        mem = SessionMemory()
        mem.add_entry("Q1", "A1", "valuation")
        mem.clear()

        assert mem.question_count == 0
        assert mem.previous_questions == []


class TestPipelineResult:
    def test_default_success(self) -> None:
        result = PipelineResult()
        assert result.success is True
        assert result.error is None
        assert result.timings == []

    def test_timestamp_auto_set(self) -> None:
        result = PipelineResult()
        assert result.timestamp is not None
