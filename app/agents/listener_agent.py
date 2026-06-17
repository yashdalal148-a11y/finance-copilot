"""
Listener Agent — Audio → Transcript.

Accepts raw audio bytes (from the Streamlit recorder or file upload),
delegates to the SpeechClient for Faster-Whisper transcription, and
returns a strongly-typed ``TranscriptionResult``.
"""

from __future__ import annotations

import logging

from app.core.models import TranscriptionResult
from app.core.speech_client import SpeechClient

logger = logging.getLogger(__name__)


class ListenerAgent:
    """Transcribes audio input into text."""

    def __init__(self, speech_client: SpeechClient) -> None:
        self._speech = speech_client

    def run(self, audio_bytes: bytes) -> TranscriptionResult:
        """Transcribe *audio_bytes* and return a ``TranscriptionResult``.

        On failure the result contains an empty ``text`` field so
        downstream agents can detect the issue without catching
        exceptions.
        """
        if not audio_bytes:
            logger.warning("ListenerAgent received empty audio input")
            return TranscriptionResult()

        logger.info("ListenerAgent processing %d bytes of audio", len(audio_bytes))
        try:
            result = self._speech.transcribe_bytes(audio_bytes)
            if result.is_empty:
                logger.warning("Transcription produced empty text")
            return result
        except Exception as exc:
            logger.error("ListenerAgent transcription failed: %s", exc, exc_info=True)
            return TranscriptionResult()
