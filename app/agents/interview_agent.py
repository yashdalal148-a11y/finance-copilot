"""
Interview Agent — Question Classification.

Uses Gemini to classify a transcribed interview question into a
finance category (valuation, accounting, equity_research, markets,
behavioral, technical).
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import QuestionCategory, QuestionClassification, SessionContext

logger = logging.getLogger(__name__)

_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "classification_prompt.txt"


class InterviewAgent:
    """Classifies interview questions by category."""

    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "classification_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(
        self,
        question: str,
        context: SessionContext,
    ) -> QuestionClassification:
        """Classify *question* and return a ``QuestionClassification``."""
        prompt = self._prompt_template.format(
            question=question,
            context=context.summary_for_prompt(),
        )

        try:
            data = self._llm.generate_json(task_type=TaskType.CLASSIFICATION, prompt=prompt, temperature=0.1)
            category_raw = data.get("category", "unknown").lower().strip()

            # Map to enum (fall back to UNKNOWN for unexpected values)
            try:
                category = QuestionCategory(category_raw)
            except ValueError:
                logger.warning("Unknown category from LLM: '%s'", category_raw)
                category = QuestionCategory.UNKNOWN

            result = QuestionClassification(
                category=category,
                subcategory=data.get("subcategory", ""),
                confidence=float(data.get("confidence", 0.0)),
                reasoning=data.get("reasoning", ""),
            )
            logger.info(
                "InterviewAgent classified  category=%s  sub=%s  conf=%.2f",
                result.category.value,
                result.subcategory,
                result.confidence,
            )
            return result

        except Exception as exc:
            logger.error("InterviewAgent classification failed: %s", exc, exc_info=True)
            return QuestionClassification(
                category=QuestionCategory.UNKNOWN,
                reasoning=f"Classification error: {exc}",
            )
