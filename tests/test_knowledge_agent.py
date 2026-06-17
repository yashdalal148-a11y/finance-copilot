"""Tests for KnowledgeAgent."""

from pathlib import Path

from app.agents.knowledge_agent import KnowledgeAgent
from app.core.models import KnowledgeResult, QuestionCategory


class TestKnowledgeAgent:
    def test_retrieve_valuation_knowledge(self, knowledge_dir: Path) -> None:
        agent = KnowledgeAgent(knowledge_dir=knowledge_dir, max_passages=3)
        result = agent.run("Walk me through a DCF analysis", QuestionCategory.VALUATION)

        assert isinstance(result, KnowledgeResult)
        assert result.category == "valuation"
        assert len(result.passages) > 0
        assert len(result.passages) <= 3

    def test_retrieve_accounting_knowledge(self, knowledge_dir: Path) -> None:
        agent = KnowledgeAgent(knowledge_dir=knowledge_dir, max_passages=5)
        result = agent.run(
            "Walk me through the three financial statements",
            QuestionCategory.ACCOUNTING,
        )

        assert len(result.passages) > 0
        # At least one passage should mention financial statements
        combined = result.combined_text().lower()
        assert "financial" in combined or "statement" in combined

    def test_relevance_ranking(self, knowledge_dir: Path) -> None:
        agent = KnowledgeAgent(knowledge_dir=knowledge_dir, max_passages=5)
        result = agent.run("What is WACC?", QuestionCategory.VALUATION)

        # The most relevant passage should have the highest score
        if len(result.passages) > 1:
            assert result.passages[0].relevance_score >= result.passages[1].relevance_score

    def test_unknown_category(self, knowledge_dir: Path) -> None:
        agent = KnowledgeAgent(knowledge_dir=knowledge_dir, max_passages=5)
        result = agent.run("something random", QuestionCategory.UNKNOWN)

        assert isinstance(result, KnowledgeResult)
        # Should still return results from interview_questions.md

    def test_combined_text(self, knowledge_dir: Path) -> None:
        agent = KnowledgeAgent(knowledge_dir=knowledge_dir, max_passages=2)
        result = agent.run("DCF", QuestionCategory.VALUATION)
        combined = result.combined_text()

        assert isinstance(combined, str)
        if result.passages:
            assert len(combined) > 0

    def test_nonexistent_knowledge_dir(self, tmp_path: Path) -> None:
        fake_dir = tmp_path / "nonexistent"
        agent = KnowledgeAgent(knowledge_dir=fake_dir, max_passages=5)
        result = agent.run("test", QuestionCategory.VALUATION)

        assert len(result.passages) == 0

    def test_caching(self, knowledge_dir: Path) -> None:
        agent = KnowledgeAgent(knowledge_dir=knowledge_dir, max_passages=3)

        # First call populates cache
        agent.run("DCF", QuestionCategory.VALUATION)
        assert len(agent._cache) > 0

        # Second call should use cache (verify by checking cache size doesn't change)
        cache_keys_before = set(agent._cache.keys())
        agent.run("LBO analysis", QuestionCategory.VALUATION)
        cache_keys_after = set(agent._cache.keys())
        assert cache_keys_before == cache_keys_after
