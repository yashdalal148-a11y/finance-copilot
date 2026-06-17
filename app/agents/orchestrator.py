"""
Orchestrator — Agent Pipeline Coordinator.

Runs all agents in sequence, captures per-agent timing, handles
individual agent failures gracefully, and updates session memory
on completion.
"""

from __future__ import annotations

import concurrent.futures
import logging
import time

from app.agents.context_agent import ContextAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.finance_expert_agent import FinanceExpertAgent
from app.agents.follow_up_agent import FollowUpAgent
from app.agents.interview_agent import InterviewAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.listener_agent import ListenerAgent
from app.core.models import AgentTiming, PipelineResult, TranscriptionResult
from app.core.session import SessionMemory

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates the full interview-intelligence pipeline."""

    def __init__(
        self,
        listener: ListenerAgent,
        context: ContextAgent,
        interview: InterviewAgent,
        knowledge: KnowledgeAgent,
        expert: FinanceExpertAgent,
        follow_up: FollowUpAgent,
        evaluation: EvaluationAgent,
        memory: SessionMemory,
    ) -> None:
        self._listener = listener
        self._context = context
        self._interview = interview
        self._knowledge = knowledge
        self._expert = expert
        self._follow_up = follow_up
        self._evaluation = evaluation
        self._memory = memory

    # ── Pipeline ──────────────────────────────────────────────────────

    def run(self, audio_bytes: bytes, status_callback=None) -> PipelineResult:
        """Execute the full pipeline and return a ``PipelineResult``.

        ``status_callback`` is an optional callable that receives a
        status string each time a new agent starts (used by the UI to
        show progress).
        """
        result = PipelineResult()
        pipeline_start = time.perf_counter()

        def _status(msg: str) -> None:
            if status_callback:
                status_callback(msg)

        # ── 1. Listener ──────────────────────────────────────────────
        _status("🎙️ Transcribing audio…")
        t0 = time.perf_counter()
        transcription = self._listener.run(audio_bytes)
        result.timings.append(self._timing("ListenerAgent", t0))
        result.transcription = transcription

        if transcription.is_empty:
            result.success = False
            result.error = "Transcription produced no text. Please try again with clearer audio."
            logger.warning("Pipeline aborted: empty transcription")
            return self._finalise(result, pipeline_start)

        question = transcription.text
        return self._run_pipeline_core(question, result, pipeline_start, _status)

    # ── Text-Only Pipeline (Bypass Listener) ─────────────────────────

    def run_text(self, question_text: str, status_callback=None) -> PipelineResult:
        """Execute the pipeline from a typed question (skip transcription).

        Useful for text-based input and for testing.
        """
        result = PipelineResult()
        pipeline_start = time.perf_counter()

        def _status(msg: str) -> None:
            if status_callback:
                status_callback(msg)

        result.transcription = TranscriptionResult(text=question_text)
        return self._run_pipeline_core(question_text, result, pipeline_start, _status)

    # ── Core Pipeline Logic ──────────────────────────────────────────

    def _run_pipeline_core(
        self, question: str, result: PipelineResult, pipeline_start: float, _status
    ) -> PipelineResult:
        # ── 2. Context ───────────────────────────────────────────────
        _status("🧠 Building session context…")
        t0 = time.perf_counter()
        context = self._context.run(question)
        result.timings.append(self._timing("ContextAgent", t0))
        result.context = context

        # ── 3. Interview (Classification) ────────────────────────────
        _status("🏷️ Classifying question…")
        t0 = time.perf_counter()
        classification = self._interview.run(question, context)
        result.timings.append(self._timing("InterviewAgent", t0))
        result.classification = classification

        # ── 4. Knowledge Retrieval ───────────────────────────────────
        _status("📚 Retrieving knowledge…")
        t0 = time.perf_counter()
        knowledge = self._knowledge.run(question, classification.category)
        result.timings.append(self._timing("KnowledgeAgent", t0))
        result.knowledge = knowledge

        # ── 5. Finance Expert (Answer Generation) ────────────────────
        _status("💡 Generating expert answer…")
        t0 = time.perf_counter()
        
        from app.core.candidate_context_builder import build_candidate_context
        candidate_context_str = build_candidate_context(
            candidate=self._memory.candidate_profile,
            job=self._memory.job_profile,
            fit=self._memory.fit_analysis,
        )
        
        answer = self._expert.run(
            question, 
            classification, 
            knowledge, 
            context,
            candidate_context=candidate_context_str,
        )
        result.timings.append(self._timing("FinanceExpertAgent", t0))
        result.answer = answer

        # ── 6. Evaluation ───────────────
        _status("⚖️ Evaluating answer…")
        t0 = time.perf_counter()
        evaluation = self._evaluation.run(question, answer, knowledge, classification)
        result.timings.append(self._timing("EvaluationAgent", t0))
        result.evaluation = evaluation

        # ── 7. Adaptive Follow-Up ───────────────
        _status("⚡ Generating adaptive follow-ups…")
        t0 = time.perf_counter()
        follow_ups = self._follow_up.run(question, answer, classification, evaluation)
        result.timings.append(self._timing("FollowUpAgent", t0))
        result.follow_ups = follow_ups

        # ── 8. Update Session Memory ─────────────────────────────────
        # Only add to memory if we successfully got an answer without an error fallback
        if not answer.answer.startswith("We encountered an issue"):
            self._memory.add_entry(
                question=question,
                answer=answer.answer,
                category=classification.category.value,
            )

        return self._finalise(result, pipeline_start)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _timing(agent_name: str, start: float) -> AgentTiming:
        elapsed = (time.perf_counter() - start) * 1000
        return AgentTiming(agent_name=agent_name, duration_ms=elapsed)

    @staticmethod
    def _finalise(result: PipelineResult, pipeline_start: float) -> PipelineResult:
        result.total_duration_ms = (time.perf_counter() - pipeline_start) * 1000
        logger.info(
            "Pipeline complete  success=%s  total=%.0fms  agents=%s",
            result.success,
            result.total_duration_ms,
            " | ".join(
                f"{t.agent_name}={t.duration_ms:.0f}ms" for t in result.timings
            ),
        )
        return result
