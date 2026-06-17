"""
Fit Analysis Agent.

Compares a CandidateProfile with a JobProfile to generate a FitAnalysis.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import CandidateProfile, FitAnalysis, JobProfile

logger = logging.getLogger(__name__)


class FitAnalysisAgent:
    """Agent that compares candidate vs job profiles."""

    def __init__(self, llm: LLMRouter, prompts_dir: Path) -> None:
        self._llm = llm
        prompt_path = prompts_dir / "fit_analysis_prompt.txt"
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, candidate: CandidateProfile, job: JobProfile) -> FitAnalysis:
        """Analyze fit between candidate and job."""
        logger.info("FitAnalysisAgent: Analyzing fit")
        
        prompt = self._prompt_template.format(
            candidate_profile=candidate.model_dump_json(indent=2),
            job_profile=job.model_dump_json(indent=2)
        )
        
        try:
            data = self._llm.generate_json(task_type=TaskType.FIT_ANALYSIS, prompt=prompt, temperature=0.2)
            return FitAnalysis(**data)
        except Exception as exc:
            logger.error("FitAnalysisAgent failed: %s", exc)
            return FitAnalysis(
                match_score=0.0,
                strengths=["Analysis unavailable"],
                skill_gaps=["Analysis unavailable"],
            )
