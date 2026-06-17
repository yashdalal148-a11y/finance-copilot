"""
Faster-Whisper speech-to-text client.

Wraps the ``faster_whisper.WhisperModel`` with:
 - Lazy loading (model is heavy; only loaded on first transcription)
 - Temporary file management for in-memory audio bytes
 - Structured ``TranscriptionResult`` output
"""

from __future__ import annotations

import logging
import os
import tempfile
import time
from pathlib import Path

from app.core.models import TranscriptionResult

logger = logging.getLogger(__name__)


class SpeechClient:
    """Lazy-loading wrapper around Faster-Whisper."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._model = None  # lazy

    # ── Lazy init ─────────────────────────────────────────────────────

    def _ensure_model(self):
        if self._model is not None:
            return self._model

        logger.info(
            "Loading Whisper model  size=%s  device=%s  compute=%s  (this may take a moment)",
            self._model_size,
            self._device,
            self._compute_type,
        )
        t0 = time.perf_counter()

        from faster_whisper import WhisperModel

        self._model = WhisperModel(
            self._model_size,
            device=self._device,
            compute_type=self._compute_type,
        )
        elapsed = time.perf_counter() - t0
        logger.info("Whisper model loaded in %.1fs", elapsed)
        return self._model

    # ── Public API ────────────────────────────────────────────────────

    def transcribe_file(self, audio_path: str | Path) -> TranscriptionResult:
        """Transcribe an audio file on disk."""
        model = self._ensure_model()
        t0 = time.perf_counter()

        segments, info = model.transcribe(str(audio_path), beam_size=5)
        text = " ".join(seg.text.strip() for seg in segments)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        result = TranscriptionResult(
            text=text.strip(),
            language=info.language or "en",
            duration_seconds=info.duration or 0.0,
        )
        logger.info(
            "Transcription complete  chars=%d  lang=%s  audio=%.1fs  took=%.0fms",
            len(result.text),
            result.language,
            result.duration_seconds,
            elapsed_ms,
        )
        return result

    def transcribe_bytes(self, audio_bytes: bytes) -> TranscriptionResult:
        """Transcribe raw audio bytes by writing to a temp file first."""
        if not audio_bytes:
            logger.warning("Empty audio bytes received")
            return TranscriptionResult()

        fd, temp_path = tempfile.mkstemp(suffix=".wav")
        try:
            os.write(fd, audio_bytes)
            os.close(fd)
            return self.transcribe_file(temp_path)
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
