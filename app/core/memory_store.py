import json
import logging
from pathlib import Path
from typing import Optional

from app.core.models import (
    ResearchMemory,
    CandidateMemory,
    CandidateEvolution,
    InterviewMemory,
    LearningMemory,
    StockPitchMemory,
)

logger = logging.getLogger(__name__)

class MemoryStore:
    """
    Manages non-monolithic persistent storage for OS V1.5 Research Memory.
    Saves and loads individual domain memories to/from JSON files.
    """

    def __init__(self, data_dir: str = "data/research_memory"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._candidate_file = self.data_dir / "candidate_memory.json"
        self._evolution_file = self.data_dir / "candidate_evolution.json"
        self._interview_file = self.data_dir / "interview_memory.json"
        self._learning_file = self.data_dir / "learning_memory.json"
        self._stock_pitch_file = self.data_dir / "stock_pitch_memory.json"

    def load_memory(self) -> ResearchMemory:
        """Loads all fragmented memories into a single ResearchMemory object."""
        return ResearchMemory(
            candidate=self._load_fragment(self._candidate_file, CandidateMemory),
            evolution=self._load_fragment(self._evolution_file, CandidateEvolution),
            interview=self._load_fragment(self._interview_file, InterviewMemory),
            learning=self._load_fragment(self._learning_file, LearningMemory),
            stock_pitch=self._load_fragment(self._stock_pitch_file, StockPitchMemory),
        )

    def save_memory(self, memory: ResearchMemory) -> None:
        """Saves a ResearchMemory object into fragmented non-monolithic files."""
        self._save_fragment(self._candidate_file, memory.candidate)
        self._save_fragment(self._evolution_file, memory.evolution)
        self._save_fragment(self._interview_file, memory.interview)
        self._save_fragment(self._learning_file, memory.learning)
        self._save_fragment(self._stock_pitch_file, memory.stock_pitch)

    def _load_fragment(self, filepath: Path, model_cls: type) -> any:
        if not filepath.exists():
            return model_cls()
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return model_cls(**data)
        except Exception as exc:
            logger.error(f"Failed to load memory fragment {filepath.name}: {exc}")
            return model_cls()

    def _save_fragment(self, filepath: Path, data_obj: any) -> None:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data_obj.model_dump(), f, indent=2)
        except Exception as exc:
            logger.error(f"Failed to save memory fragment {filepath.name}: {exc}")
