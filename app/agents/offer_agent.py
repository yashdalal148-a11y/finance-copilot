"""Offer Probability Agent — Predicts offer likelihood based on full intelligence."""

from __future__ import annotations
import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import CandidateProfile, JobProfile, FitAnalysis, BattlefieldMap, OfferProbabilityAnalysis

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "offer_probability_prompt.txt"

class OfferProbabilityAgent:
    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "offer_probability_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(
        self,
        candidate: CandidateProfile,
        job: JobProfile,
        fit: FitAnalysis,
        battlefield: BattlefieldMap
    ) -> OfferProbabilityAnalysis:
        prompt = self._prompt_template.format(
            candidate_profile=candidate.model_dump_json(indent=2),
            job_profile=job.model_dump_json(indent=2),
            fit_analysis=fit.model_dump_json(indent=2),
            battlefield_map=battlefield.model_dump_json(indent=2),
        )
        try:
            data = self._llm.generate_json(task_type=TaskType.OFFER_PROBABILITY, prompt=prompt, temperature=0.3)
            return OfferProbabilityAnalysis(**data)
        except Exception as exc:
            logger.error("OfferProbabilityAgent failed: %s", exc)
            return OfferProbabilityAnalysis()
