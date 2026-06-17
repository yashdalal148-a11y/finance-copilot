"""
Knowledge Agent — Markdown Knowledge Retrieval.

Reads finance knowledge from ``knowledge/*.md`` files, parses them into
sections, and retrieves the most relevant passages for a given question
using keyword-overlap scoring.

Designed for V1 simplicity.  The retrieval interface
(``run() → KnowledgeResult``) is stable; the implementation can be
swapped to a vector-DB backend without changing any downstream agent.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List

from app.core.models import KnowledgeResult, KnowledgeSection, QuestionCategory

logger = logging.getLogger(__name__)

# Map categories to the knowledge files they should search.
_CATEGORY_FILES: Dict[QuestionCategory, List[str]] = {
    QuestionCategory.VALUATION: ["valuation.md", "interview_questions.md"],
    QuestionCategory.ACCOUNTING: ["accounting.md", "interview_questions.md"],
    QuestionCategory.EQUITY_RESEARCH: ["equity_research.md", "interview_questions.md"],
    QuestionCategory.MARKETS: ["markets.md", "interview_questions.md"],
    QuestionCategory.BEHAVIORAL: ["behavioral.md", "interview_questions.md"],
    QuestionCategory.TECHNICAL: ["technical.md", "interview_questions.md"],
    QuestionCategory.UNKNOWN: ["interview_questions.md"],
}

# Words to exclude from relevance scoring (they add noise).
_STOP_WORDS = frozenset(
    "a an the is are was were be been being have has had do does did "
    "will would shall should may might can could of in to for on with "
    "at by from as into about between through after before during "
    "and or but not so if then than that this these those it its "
    "i me my we our you your he she they them what which who whom how "
    "very much many most also just only even still already yet".split()
)


class KnowledgeAgent:
    """Retrieves relevant knowledge passages from the markdown knowledge base."""

    def __init__(self, knowledge_dir: Path, max_passages: int = 5) -> None:
        self._knowledge_dir = knowledge_dir
        self._max_passages = max_passages
        # In-memory cache of parsed sections (populated on first access)
        self._cache: Dict[str, List[KnowledgeSection]] = {}

    # ── Public API ────────────────────────────────────────────────────

    def run(
        self,
        question: str,
        category: QuestionCategory,
    ) -> KnowledgeResult:
        """Retrieve the most relevant knowledge passages for *question*."""
        file_names = _CATEGORY_FILES.get(category, ["interview_questions.md"])

        all_sections: List[KnowledgeSection] = []
        for fname in file_names:
            all_sections.extend(self._load_sections(fname))

        if not all_sections:
            logger.warning("No knowledge sections found for category=%s", category.value)
            return KnowledgeResult(category=category.value)

        # Score and rank
        scored = self._rank_sections(question, all_sections)
        top = scored[: self._max_passages]

        logger.info(
            "KnowledgeAgent retrieved %d/%d passages  category=%s  top_score=%.3f",
            len(top),
            len(all_sections),
            category.value,
            top[0].relevance_score if top else 0.0,
        )
        return KnowledgeResult(passages=top, category=category.value)

    # ── Parsing ───────────────────────────────────────────────────────

    def _load_sections(self, file_name: str) -> List[KnowledgeSection]:
        if file_name in self._cache:
            return self._cache[file_name]

        file_path = self._knowledge_dir / file_name
        if not file_path.exists():
            logger.debug("Knowledge file not found: %s", file_path)
            return []

        content = file_path.read_text(encoding="utf-8")
        sections = self._parse_markdown(content, file_name)
        self._cache[file_name] = sections
        logger.debug("Parsed %d sections from %s", len(sections), file_name)
        return sections

    @staticmethod
    def _parse_markdown(content: str, source_file: str) -> List[KnowledgeSection]:
        """Split markdown content on ``## `` headers into sections."""
        sections: List[KnowledgeSection] = []
        current_title = ""
        current_lines: List[str] = []

        for line in content.split("\n"):
            if line.startswith("## "):
                if current_title:
                    sections.append(
                        KnowledgeSection(
                            title=current_title,
                            content="\n".join(current_lines).strip(),
                            source_file=source_file,
                        )
                    )
                current_title = line[3:].strip()
                current_lines = []
            elif line.startswith("# ") and not line.startswith("## "):
                # Top-level heading — skip (it's just the file title)
                continue
            else:
                current_lines.append(line)

        # Flush last section
        if current_title:
            sections.append(
                KnowledgeSection(
                    title=current_title,
                    content="\n".join(current_lines).strip(),
                    source_file=source_file,
                )
            )

        return sections

    # ── Relevance Scoring ─────────────────────────────────────────────

    def _rank_sections(
        self, question: str, sections: List[KnowledgeSection]
    ) -> List[KnowledgeSection]:
        """Score each section by keyword overlap with the question."""
        question_tokens = self._tokenise(question)
        if not question_tokens:
            return sections

        scored: List[KnowledgeSection] = []
        for section in sections:
            section_tokens = self._tokenise(section.title + " " + section.content)
            overlap = question_tokens & section_tokens
            score = len(overlap) / len(question_tokens) if question_tokens else 0.0
            scored.append(section.model_copy(update={"relevance_score": score}))

        scored.sort(key=lambda s: s.relevance_score, reverse=True)
        return scored

    @staticmethod
    def _tokenise(text: str) -> set[str]:
        """Lowercase, strip punctuation, remove stop words."""
        words = re.findall(r"[a-z0-9]+", text.lower())
        return {w for w in words if w not in _STOP_WORDS and len(w) > 1}
