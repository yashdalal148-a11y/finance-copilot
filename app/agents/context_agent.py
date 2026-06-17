"""
Context Agent — Session History Enrichment.

A *deterministic* agent (no LLM calls).  It reads the SessionMemory,
combines it with the current question transcript, and outputs a
``SessionContext`` that downstream agents use for contextually aware
responses.
"""

from __future__ import annotations

import logging

from app.core.models import SessionContext
from app.core.session import SessionMemory

logger = logging.getLogger(__name__)


class ContextAgent:
    """Builds enriched context from session history."""

    def __init__(self, memory: SessionMemory) -> None:
        self._memory = memory

    def run(self, current_question: str) -> SessionContext:
        """Build a ``SessionContext`` for the current question.

        This is a pure-logic operation — no network calls, no LLM.
        """
        ctx = SessionContext(
            current_question=current_question,
            question_number=self._memory.question_count + 1,
            previous_questions=self._memory.previous_questions,
            previous_answers=self._memory.previous_answers,
            session_topics=self._memory.session_topics,
        )
        logger.info(
            "ContextAgent built context  question_number=%d  prior_topics=%s",
            ctx.question_number,
            ctx.session_topics,
        )
        return ctx
