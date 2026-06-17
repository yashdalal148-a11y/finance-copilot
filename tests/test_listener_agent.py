"""Tests for ListenerAgent."""

from unittest.mock import MagicMock

from app.agents.listener_agent import ListenerAgent
from app.core.models import TranscriptionResult


class TestListenerAgent:
    def test_run_with_valid_audio(self, mock_speech: MagicMock) -> None:
        agent = ListenerAgent(speech_client=mock_speech)
        result = agent.run(b"fake-audio-bytes")

        assert isinstance(result, TranscriptionResult)
        assert result.text == "Walk me through a DCF analysis"
        mock_speech.transcribe_bytes.assert_called_once_with(b"fake-audio-bytes")

    def test_run_with_empty_audio(self, mock_speech: MagicMock) -> None:
        agent = ListenerAgent(speech_client=mock_speech)
        result = agent.run(b"")

        assert isinstance(result, TranscriptionResult)
        assert result.is_empty
        mock_speech.transcribe_bytes.assert_not_called()

    def test_run_handles_transcription_error(self, mock_speech: MagicMock) -> None:
        mock_speech.transcribe_bytes.side_effect = RuntimeError("Whisper crashed")
        agent = ListenerAgent(speech_client=mock_speech)
        result = agent.run(b"bad-audio")

        assert isinstance(result, TranscriptionResult)
        assert result.is_empty
