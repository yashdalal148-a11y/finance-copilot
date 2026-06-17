"""Red Flag Agent — Identifies critical weaknesses and provides recovery strategies."""

from __future__ import annotations
import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import CandidateProfile, FitAnalysis, RedFlagAnalysis

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "red_flag_prompt.txt"

class RedFlagAgent:
    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "red_flag_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, candidate: CandidateProfile, fit: FitAnalysis) -> RedFlagAnalysis:
        prompt = self._prompt_template.format(
            candidate_profile=candidate.model_dump_json(indent=2),
            fit_analysis=fit.model_dump_json(indent=2),
        )
        try:
            data = self._llm.generate_json(task_type=TaskType.RED_FLAG, prompt=prompt, temperature=0.3)
            return RedFlagAnalysis(**data)
        except Exception as exc:
            logger.error("RedFlagAgent failed: %s", exc)
            return RedFlagAnalysis()
