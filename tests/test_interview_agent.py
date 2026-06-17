"""Tests for InterviewAgent."""

import json
from unittest.mock import MagicMock

from app.agents.interview_agent import InterviewAgent
from app.core.models import QuestionCategory, QuestionClassification, SessionContext


class TestInterviewAgent:
    def test_classify_valuation_question(
        self, mock_llm: MagicMock, prompts_dir
    ) -> None:
        mock_llm.generate_json.return_value = {
            "category": "valuation",
            "subcategory": "DCF",
            "confidence": 0.95,
            "reasoning": "Question asks about DCF methodology",
        }
        agent = InterviewAgent(llm=mock_llm, prompts_dir=prompts_dir)
        context = SessionContext(current_question="Walk me through a DCF")
        result = agent.run("Walk me through a DCF", context)

        assert isinstance(result, QuestionClassification)
        assert result.category == QuestionCategory.VALUATION
        assert result.subcategory == "DCF"
        assert result.confidence == 0.95

    def test_classify_behavioral_question(
        self, mock_llm: MagicMock, prompts_dir
    ) -> None:
        mock_llm.generate_json.return_value = {
            "category": "behavioral",
            "subcategory": "motivation",
            "confidence": 0.9,
            "reasoning": "Behavioral question about career motivation",
        }
        agent = InterviewAgent(llm=mock_llm, prompts_dir=prompts_dir)
        context = SessionContext(current_question="Why investment banking?")
        result = agent.run("Why investment banking?", context)

        assert result.category == QuestionCategory.BEHAVIORAL

    def test_classify_unknown_category(
        self, mock_llm: MagicMock, prompts_dir
    ) -> None:
        mock_llm.generate_json.return_value = {
            "category": "quantum_physics",
            "subcategory": "",
            "confidence": 0.1,
            "reasoning": "Not a finance question",
        }
        agent = InterviewAgent(llm=mock_llm, prompts_dir=prompts_dir)
        context = SessionContext(current_question="random nonsense")
        result = agent.run("random nonsense", context)

        assert result.category == QuestionCategory.UNKNOWN

    def test_classify_handles_llm_error(
        self, mock_llm: MagicMock, prompts_dir
    ) -> None:
        mock_llm.generate_json.side_effect = RuntimeError("API error")
        agent = InterviewAgent(llm=mock_llm, prompts_dir=prompts_dir)
        context = SessionContext(current_question="test")
        result = agent.run("test", context)

        assert result.category == QuestionCategory.UNKNOWN
        assert "error" in result.reasoning.lower()
