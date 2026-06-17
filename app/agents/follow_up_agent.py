"""
Follow-Up Agent — Predicts Likely Follow-Up Questions.

Uses Gemini to predict the 3 most probable follow-up questions an
interviewer would ask based on the candidate's answer.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import ExpertAnswer, FollowUpPrediction, QuestionClassification, EvaluationScore

logger = logging.getLogger(__name__)

_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "followup_prompt.txt"


class FollowUpAgent:
    """Predicts likely follow-up interview questions."""

    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "followup_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(
        self,
        question: str,
        answer: ExpertAnswer,
        classification: QuestionClassification,
        evaluation: EvaluationScore,
    ) -> FollowUpPrediction:
        """Predict follow-up questions for the given Q&A pair."""
        prompt = self._prompt_template.format(
            question=question,
            category=classification.category.value,
            answer=answer.answer,
            readiness_score=evaluation.readiness_score,
            md_feedback=evaluation.feedback
        )

        try:
            data = self._llm.generate_json(task_type=TaskType.FOLLOW_UP, prompt=prompt, temperature=0.4)
            result = FollowUpPrediction(
                questions=data.get("questions", []),
                reasoning=data.get("reasoning", ""),
            )
            logger.info(
                "FollowUpAgent predicted %d follow-ups", len(result.questions)
            )
            return result

        except Exception as exc:
            logger.error("FollowUpAgent failed: %s", exc, exc_info=True)
            return FollowUpPrediction()
