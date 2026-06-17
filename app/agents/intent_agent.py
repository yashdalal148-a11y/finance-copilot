"""Intent & Verdict Agent — Determines what the interviewer is actually testing (On-Demand)."""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Tuple

from app.core.llm_router import LLMRouter
from app.core.models import TaskType
from app.core.models import InterviewerIntent, HiringManagerVerdict

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "intent_verdict_prompt.txt"

class IntentVerdictAgent:
    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "intent_verdict_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, question: str) -> Tuple[InterviewerIntent, HiringManagerVerdict]:
        prompt = self._prompt_template.format(question=question)
        try:
            data = self._llm.generate_json(task_type=TaskType.INTENT_ANALYSIS, prompt=prompt, temperature=0.3)
            intent = InterviewerIntent(**data.get("intent", {}))
            verdict = HiringManagerVerdict(**data.get("verdict", {}))
            return intent, verdict
        except Exception as exc:
            logger.error("IntentVerdictAgent failed: %s", exc)
            return InterviewerIntent(), HiringManagerVerdict()
