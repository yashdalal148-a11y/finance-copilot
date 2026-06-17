"""Story Intelligence Agent — Generates targeted career narratives."""

from __future__ import annotations
import logging
from pathlib import Path
from typing import List

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import CandidateProfile, JobProfile, CareerStory

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "story_intelligence_prompt.txt"

class StoryIntelligenceAgent:
    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "story_intelligence_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, candidate: CandidateProfile, job: JobProfile) -> List[CareerStory]:
        prompt = self._prompt_template.format(
            candidate_profile=candidate.model_dump_json(indent=2),
            job_profile=job.model_dump_json(indent=2),
        )
        try:
            data_list = self._llm.generate_json(task_type=TaskType.STORY_INTELLIGENCE, prompt=prompt, temperature=0.7)
            if not isinstance(data_list, list):
                data_list = []
            return [CareerStory(**item) for item in data_list]
        except Exception as exc:
            logger.error("StoryIntelligenceAgent failed: %s", exc)
            return []
