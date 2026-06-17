"""Stock Pitch Intelligence Agent — Generates Institutional Equity Research."""

from __future__ import annotations
import logging
from pathlib import Path

from app.core.llm_router import LLMRouter
from app.core.models import TaskType, StockPitch, InvestmentMemo

logger = logging.getLogger(__name__)
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "stock_pitch_prompt.txt"

class StockPitchAgent:
    def __init__(self, llm: LLMRouter, prompts_dir: Path | None = None) -> None:
        self._llm = llm
        prompt_path = (prompts_dir / "stock_pitch_prompt.txt") if prompts_dir else _PROMPT_FILE
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def run(self, company_name: str, ticker: str, thesis: str) -> StockPitch:
        """Generates an institutional stock pitch memo."""
        prompt = self._prompt_template.format(
            company_name=company_name,
            ticker=ticker,
            thesis=thesis
        )
        
        pitch = StockPitch(company_name=company_name, ticker=ticker)
        try:
            data = self._llm.generate_json(prompt=prompt, temperature=0.4, task_type=TaskType.STOCK_PITCH)
            pitch.memo = InvestmentMemo(**data)
            return pitch
        except Exception as exc:
            logger.error("StockPitchAgent failed: %s", exc)
            return pitch
