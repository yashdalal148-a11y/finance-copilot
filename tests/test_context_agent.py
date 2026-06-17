"""Tests for ContextAgent."""

from app.agents.context_agent import ContextAgent
from app.core.models import SessionContext
from app.core.session import SessionMemory


class TestContextAgent:
    def test_first_question(self, session_memory: SessionMemory) -> None:
        agent = ContextAgent(memory=session_memory)
        result = agent.run("What is a DCF?")

        assert isinstance(result, SessionContext)
        assert result.current_question == "What is a DCF?"
        assert result.question_number == 1
        assert result.previous_questions == []
        assert result.previous_answers == []

    def test_with_history(self, session_memory: SessionMemory) -> None:
        session_memory.add_entry(
            question="What is a DCF?",
            answer="A DCF is...",
            category="valuation",
        )
        agent = ContextAgent(memory=session_memory)
        result = agent.run("What about WACC?")

        assert result.question_number == 2
        assert result.previous_questions == ["What is a DCF?"]
        assert result.previous_answers == ["A DCF is..."]
        assert result.session_topics == ["valuation"]

    def test_summary_for_prompt_first_question(self, session_memory: SessionMemory) -> None:
        agent = ContextAgent(memory=session_memory)
        result = agent.run("Tell me about yourself")
        summary = result.summary_for_prompt()

        assert "first question" in summary.lower()

    def test_summary_for_prompt_with_history(self, session_memory: SessionMemory) -> None:
        session_memory.add_entry("Q1", "A1", "valuation")
        session_memory.add_entry("Q2", "A2", "accounting")
        agent = ContextAgent(memory=session_memory)
        result = agent.run("Q3")
        summary = result.summary_for_prompt()

        assert "3" in summary
        assert "valuation" in summary
        assert "accounting" in summary
