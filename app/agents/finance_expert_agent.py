"""
Finance Expert Agent — Institutional-Quality Answer Generation.

Takes the transcript, classification, retrieved knowledge, and session
context, then uses Gemini to produce a structured, interview-ready
answer.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import (
    ExpertAnswer,
    KnowledgeResult,
    QuestionClassification,
    SessionContext,
)

logger = logging.getLogger(__name__)

_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "finance_expert_prompt.txt"


class FinanceExpertAgent:
    """Generates institutional-quality answers to finance interview questions."""

    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "finance_expert_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(
        self,
        question: str,
        classification: QuestionClassification,
        knowledge: KnowledgeResult,
        context: SessionContext,
        candidate_context: str = "",
    ) -> ExpertAnswer:
        """Generate an expert answer for *question*."""
        prompt = self._prompt_template.format(
            question=question,
            category=classification.category.value,
            subcategory=classification.subcategory,
            knowledge=knowledge.combined_text() or "No specific reference material available.",
            context=context.summary_for_prompt(),
            candidate_context=candidate_context,
        )

        try:
            data = self._llm.generate_json(task_type=TaskType.EXPERT_ANSWER, prompt=prompt, temperature=0.3)
            result = ExpertAnswer(
                answer=data.get("answer", ""),
                key_points=data.get("key_points", []),
                frameworks_used=data.get("frameworks_used", []),
            )
            logger.info(
                "FinanceExpertAgent generated answer  chars=%d  key_points=%d  frameworks=%d",
                len(result.answer),
                len(result.key_points),
                len(result.frameworks_used),
            )
            return result

        except Exception as exc:
            logger.error("FinanceExpertAgent failed: %s", exc, exc_info=True)
            return ExpertAnswer(
                answer="We encountered an issue generating the answer. Please try again.",
            )
