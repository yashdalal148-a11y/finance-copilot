"""Tests for FollowUpAgent."""

from unittest.mock import MagicMock

from app.agents.follow_up_agent import FollowUpAgent
from app.core.models import (
    ExpertAnswer,
    FollowUpPrediction,
    QuestionCategory,
    QuestionClassification,
)


class TestFollowUpAgent:
    def test_predict_follow_ups(self, mock_llm: MagicMock, prompts_dir) -> None:
        mock_llm.generate_json.return_value = {
            "questions": [
                "What discount rate would you use?",
                "How do you calculate terminal value?",
                "When would you not use a DCF?",
            ],
            "reasoning": "Probing deeper into DCF mechanics",
        }
        agent = FollowUpAgent(llm=mock_llm, prompts_dir=prompts_dir)
        result = agent.run(
            question="Walk me through a DCF",
            answer=ExpertAnswer(answer="A DCF analysis..."),
            classification=QuestionClassification(
                category=QuestionCategory.VALUATION
            ),
        )

        assert isinstance(result, FollowUpPrediction)
        assert len(result.questions) == 3
        assert len(result.reasoning) > 0

    def test_handles_llm_error(self, mock_llm: MagicMock, prompts_dir) -> None:
        mock_llm.generate_json.side_effect = RuntimeError("API error")
        agent = FollowUpAgent(llm=mock_llm, prompts_dir=prompts_dir)
        result = agent.run(
            question="test",
            answer=ExpertAnswer(answer="test"),
            classification=QuestionClassification(),
        )

        assert isinstance(result, FollowUpPrediction)
        assert result.questions == []
