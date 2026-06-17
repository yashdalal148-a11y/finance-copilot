"""Weakness Intelligence Agent — Generates Skill Gap Analysis & Learning Roadmaps."""

from __future__ import annotations
import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType, WeaknessAnalysis, ResearchMemory

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "weakness_analysis_prompt.txt"

class WeaknessIntelligenceAgent:
    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "weakness_analysis_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, research_memory: ResearchMemory) -> WeaknessAnalysis:
        """Analyzes historical learning data to extract a weakness map."""
        history = {
            "learning_priorities": research_memory.learning.learning_priorities,
            "improvement_history": research_memory.learning.improvement_history,
            "weakness_trends": research_memory.candidate.weakness_trends,
            "strength_trends": research_memory.candidate.strength_trends,
            "common_mistakes": research_memory.interview.common_mistakes,
        }
        
        prompt = self._prompt_template.format(
            learning_memory=str(history)
        )
        
        try:
            data = self._llm.generate_json(prompt=prompt, temperature=0.2, task_type=TaskType.WEAKNESS_ANALYSIS)
            return WeaknessAnalysis(**data)
        except Exception as exc:
            logger.error("WeaknessIntelligenceAgent failed: %s", exc)
            return WeaknessAnalysis()
