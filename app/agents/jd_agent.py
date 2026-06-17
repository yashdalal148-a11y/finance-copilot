"""
Job Description Intelligence Agent.

Parses raw JD text and extracts a structured JobProfile.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import JobProfile

logger = logging.getLogger(__name__)


class JobDescriptionIntelligenceAgent:
    """Agent that converts raw JD text into a JobProfile."""

    def __init__(self, llm: LLMRouter, prompts_dir: Path) -> None:
        self._llm = llm
        prompt_path = prompts_dir / "job_intelligence_prompt.txt"
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, raw_text: str) -> JobProfile:
        """Parse raw JD text into a structured profile."""
        logger.info("JobDescriptionIntelligenceAgent: Extracting profile from JD text")
        
        prompt = self._prompt_template.format(raw_text=raw_text)
        
        try:
            data = self._llm.generate_json(task_type=TaskType.JD_PARSING, prompt=prompt, temperature=0.1)
            return JobProfile(**data)
        except Exception as exc:
            logger.error("JobDescriptionIntelligenceAgent failed: %s", exc)
            return JobProfile(
                role="Error parsing Job Description",
                domain="Unknown",
            )
