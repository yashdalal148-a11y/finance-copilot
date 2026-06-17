"""
Session memory for the Context Agent.

Stores the conversation history (questions, answers, topics) across
multiple interactions within a single user session.  Designed to be
backed by Streamlit ``session_state`` — the ``SessionMemory`` object is
stored there so it survives Streamlit reruns.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from pydantic import BaseModel, Field

from app.core.models import (
    CandidateProfile, JobProfile, FitAnalysis, CareerStory, BattlefieldMap,
    RedFlagAnalysis, CareerGapAnalysis, OfferProbabilityAnalysis
)

logger = logging.getLogger(__name__)


class SessionEntry(BaseModel):
    """One question-answer pair in the session."""

    question: str
    answer: str
    category: str = ""


class SessionMemory(BaseModel):
    """In-memory conversation history for a single user session."""

    entries: List[SessionEntry] = Field(default_factory=list)
    candidate_profile: Optional[CandidateProfile] = None
    job_profile: Optional[JobProfile] = None
    fit_analysis: Optional[FitAnalysis] = None
    
    # V1.3
    career_stories: List[CareerStory] = Field(default_factory=list)
    battlefield_map: Optional[BattlefieldMap] = None
    red_flag_analysis: Optional[RedFlagAnalysis] = None
    career_gap_analysis: Optional[CareerGapAnalysis] = None
    offer_probability: Optional[OfferProbabilityAnalysis] = None

    # ── Read API ──────────────────────────────────────────────────────

    @property
    def question_count(self) -> int:
        return len(self.entries)

    @property
    def previous_questions(self) -> List[str]:
        return [e.question for e in self.entries]

    @property
    def previous_answers(self) -> List[str]:
        return [e.answer for e in self.entries]

    @property
    def session_topics(self) -> List[str]:
        seen: set[str] = set()
        topics: list[str] = []
        for e in self.entries:
            if e.category and e.category not in seen:
                seen.add(e.category)
                topics.append(e.category)
        return topics

    # ── Write API ─────────────────────────────────────────────────────

    def add_entry(self, question: str, answer: str, category: str = "") -> None:
        """Record a completed Q&A pair."""
        entry = SessionEntry(question=question, answer=answer, category=category)
        self.entries.append(entry)
        logger.debug(
            "Session entry added  count=%d  category=%s",
            len(self.entries),
            category,
        )

    def clear(self) -> None:
        """Reset the session history."""
        self.entries.clear()
        self.candidate_profile = None
        self.job_profile = None
        self.fit_analysis = None
        self.career_stories.clear()
        self.battlefield_map = None
        self.red_flag_analysis = None
        self.career_gap_analysis = None
        self.offer_probability = None
        logger.info("Session memory cleared")
