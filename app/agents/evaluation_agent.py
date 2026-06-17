"""
Evaluation Agent — Confidence & Completeness Scoring.

Uses Gemini to evaluate the generated answer against the reference
knowledge and the original question.  Returns scores and actionable
feedback.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import (
    EvaluationScore,
    ExpertAnswer,
    KnowledgeResult,
    QuestionClassification,
)

logger = logging.getLogger(__name__)

_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "evaluation_prompt.txt"


class EvaluationAgent:
    """Scores interview answers for confidence, completeness, and accuracy."""

    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "evaluation_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(
        self,
        question: str,
        answer: ExpertAnswer,
        knowledge: KnowledgeResult,
        classification: QuestionClassification,
    ) -> EvaluationScore:
        """Evaluate *answer* and return an ``EvaluationScore``."""
        prompt = self._prompt_template.format(
            question=question,
            category=classification.category.value,
            answer=answer.answer,
            knowledge=knowledge.combined_text() or "No reference material available.",
        )

        try:
            data = self._llm.generate_json(task_type=TaskType.EVALUATION, prompt=prompt, temperature=0.1)

            def _clamp(val, lo=0.0, hi=100.0) -> float:
                return max(lo, min(hi, float(val)))

            result = EvaluationScore(
                confidence_score=_clamp(data.get("confidence_score", 0)),
                completeness_score=_clamp(data.get("completeness_score", 0)),
                accuracy_score=_clamp(data.get("accuracy_score", 0)),
                overall_score=_clamp(data.get("overall_score", 0)),
                feedback=data.get("feedback", ""),
                strengths=data.get("strengths", []),
                improvements=data.get("improvements", []),
            )
            logger.info(
                "EvaluationAgent scored  overall=%.0f  conf=%.0f  complete=%.0f  acc=%.0f",
                result.overall_score,
                result.confidence_score,
                result.completeness_score,
                result.accuracy_score,
            )
            return result

        except Exception as exc:
            logger.error("EvaluationAgent failed: %s", exc, exc_info=True)
            return EvaluationScore(feedback="Evaluation unavailable at this time. Please try again.")
