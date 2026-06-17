"""Battlefield Map Agent — Predicts the exact interview questions."""

from __future__ import annotations
import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import CandidateProfile, JobProfile, BattlefieldMap

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "battlefield_map_prompt.txt"

class BattlefieldMapAgent:
    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "battlefield_map_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, candidate: CandidateProfile, job: JobProfile) -> BattlefieldMap:
        prompt = self._prompt_template.format(
            candidate_profile=candidate.model_dump_json(indent=2),
            job_profile=job.model_dump_json(indent=2),
        )
        try:
            data = self._llm.generate_json(task_type=TaskType.BATTLEFIELD_MAP, prompt=prompt, temperature=0.5)
            return BattlefieldMap(**data)
        except Exception as exc:
            logger.error("BattlefieldMapAgent failed: %s", exc)
            return BattlefieldMap()
