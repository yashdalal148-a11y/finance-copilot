"""
Resume Intelligence Agent.

Parses raw resume text and extracts a structured CandidateProfile.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import CandidateProfile

logger = logging.getLogger(__name__)


class ResumeIntelligenceAgent:
    """Agent that converts raw resume text into a CandidateProfile."""

    def __init__(self, llm: LLMRouter, prompts_dir: Path) -> None:
        self._llm = llm
        prompt_path = prompts_dir / "resume_intelligence_prompt.txt"
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, raw_text: str) -> CandidateProfile:
        """Parse raw resume text into a structured profile."""
        logger.info("ResumeIntelligenceAgent: Extracting profile from resume text")
        
        prompt = self._prompt_template.format(raw_text=raw_text)
        
        try:
            data = self._llm.generate_json(task_type=TaskType.RESUME_PARSING, prompt=prompt, temperature=0.1)
            return CandidateProfile(**data)
        except Exception as exc:
            logger.error("ResumeIntelligenceAgent failed: %s", exc)
            return CandidateProfile(
                experience=["Error extracting experience"],
                skills=["Error parsing resume"],
            )
