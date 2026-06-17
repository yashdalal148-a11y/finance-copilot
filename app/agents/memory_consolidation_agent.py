"""Memory Consolidation Agent — Distills ephemeral session data into persistent Research Memory."""

from __future__ import annotations
import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType, ResearchMemory
from app.core.session import SessionMemory

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "memory_consolidation_prompt.txt"

class MemoryConsolidationAgent:
    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "memory_consolidation_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, current_memory: ResearchMemory, session: SessionMemory) -> ResearchMemory:
        """Consolidates the current session transcript into the persistent Research Memory."""
        # Convert session to text
        transcript = ""
        for entry in session.entries:
            transcript += f"[INTERVIEWER]: {entry.question}\n[CANDIDATE]: {entry.answer}\n"
        
        if not transcript.strip():
            logger.info("Session transcript empty. Skipping memory consolidation.")
            return current_memory
            
        prompt = self._prompt_template.format(
            current_memory=current_memory.model_dump_json(indent=2),
            session_transcript=transcript
        )
        
        try:
            data = self._llm.generate_json(prompt=prompt, temperature=0.2, task_type=TaskType.MEMORY_CONSOLIDATION)
            return ResearchMemory(**data)
        except Exception as exc:
            logger.error("MemoryConsolidationAgent failed: %s", exc)
            return current_memory
