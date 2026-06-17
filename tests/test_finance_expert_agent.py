"""Tests for FinanceExpertAgent."""

from unittest.mock import MagicMock

from app.agents.finance_expert_agent import FinanceExpertAgent
from app.core.models import (
    ExpertAnswer,
    KnowledgeResult,
    KnowledgeSection,
    QuestionCategory,
    QuestionClassification,
    SessionContext,
)


class TestFinanceExpertAgent:
    def test_generate_answer(self, mock_llm: MagicMock, prompts_dir) -> None:
        mock_llm.generate_json.return_value = {
            "answer": "A DCF values a company by projecting future free cash flows...",
            "key_points": ["Project FCF", "Calculate TV", "Discount at WACC"],
            "frameworks_used": ["DCF", "WACC"],
        }
        agent = FinanceExpertAgent(llm=mock_llm, prompts_dir=prompts_dir)
        result = agent.run(
            question="Walk me through a DCF",
            classification=QuestionClassification(
                category=QuestionCategory.VALUATION, subcategory="DCF"
            ),
            knowledge=KnowledgeResult(
                passages=[KnowledgeSection(title="DCF", content="...")],
                category="valuation",
            ),
            context=SessionContext(current_question="Walk me through a DCF"),
        )

        assert isinstance(result, ExpertAnswer)
        assert len(result.answer) > 0
        assert len(result.key_points) == 3
        assert len(result.frameworks_used) == 2

    def test_handles_llm_error(self, mock_llm: MagicMock, prompts_dir) -> None:
        mock_llm.generate_json.side_effect = RuntimeError("API timeout")
        agent = FinanceExpertAgent(llm=mock_llm, prompts_dir=prompts_dir)
        result = agent.run(
            question="test",
            classification=QuestionClassification(),
            knowledge=KnowledgeResult(),
            context=SessionContext(),
        )

        assert isinstance(result, ExpertAnswer)
        assert "issue" in result.answer.lower() or "encountered" in result.answer.lower()
