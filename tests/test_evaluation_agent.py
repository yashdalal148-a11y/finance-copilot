"""Tests for EvaluationAgent."""

from unittest.mock import MagicMock

from app.agents.evaluation_agent import EvaluationAgent
from app.core.models import (
    EvaluationScore,
    ExpertAnswer,
    KnowledgeResult,
    QuestionCategory,
    QuestionClassification,
)


class TestEvaluationAgent:
    def test_evaluate_answer(self, mock_llm: MagicMock, prompts_dir) -> None:
        mock_llm.generate_json.return_value = {
            "confidence_score": 85,
            "completeness_score": 80,
            "accuracy_score": 90,
            "overall_score": 85,
            "feedback": "Strong answer with good structure.",
            "strengths": ["Clear structure", "Correct formulas"],
            "improvements": ["Could mention sensitivity analysis"],
        }
        agent = EvaluationAgent(llm=mock_llm, prompts_dir=prompts_dir)
        result = agent.run(
            question="Walk me through a DCF",
            answer=ExpertAnswer(answer="A DCF analysis..."),
            knowledge=KnowledgeResult(),
            classification=QuestionClassification(
                category=QuestionCategory.VALUATION
            ),
        )

        assert isinstance(result, EvaluationScore)
        assert result.overall_score == 85
        assert result.confidence_score == 85
        assert result.completeness_score == 80
        assert result.accuracy_score == 90
        assert len(result.strengths) == 2
        assert len(result.improvements) == 1

    def test_clamps_scores(self, mock_llm: MagicMock, prompts_dir) -> None:
        mock_llm.generate_json.return_value = {
            "confidence_score": 150,
            "completeness_score": -10,
            "accuracy_score": 90,
            "overall_score": 85,
            "feedback": "Test",
            "strengths": [],
            "improvements": [],
        }
        agent = EvaluationAgent(llm=mock_llm, prompts_dir=prompts_dir)
        result = agent.run(
            question="test",
            answer=ExpertAnswer(answer="test"),
            knowledge=KnowledgeResult(),
            classification=QuestionClassification(),
        )

        assert result.confidence_score == 100.0
        assert result.completeness_score == 0.0

    def test_handles_llm_error(self, mock_llm: MagicMock, prompts_dir) -> None:
        mock_llm.generate_json.side_effect = RuntimeError("API error")
        agent = EvaluationAgent(llm=mock_llm, prompts_dir=prompts_dir)
        result = agent.run(
            question="test",
            answer=ExpertAnswer(answer="test"),
            knowledge=KnowledgeResult(),
            classification=QuestionClassification(),
        )

        assert isinstance(result, EvaluationScore)
        assert "unavailable" in result.feedback.lower()
