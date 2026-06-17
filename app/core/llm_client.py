"""
Gemini LLM client wrapper.

Provides a thin, retry-aware wrapper around the Google GenAI SDK.
All LLM calls in the application go through this client so that:
 - API key configuration is centralised
 - Retry / error handling lives in one place
 - Swapping the LLM backend only requires changing this file
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Maximum retries on transient Gemini errors
_MAX_RETRIES = 2
_RETRY_DELAY_S = 1.0


class GeminiClient:
    """Wrapper around the Google GenAI SDK."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash", timeout: float = 30.0) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._timeout = timeout
        self._client: genai.Client | None = None

    # ── Lazy init ─────────────────────────────────────────────────────

    def _ensure_client(self) -> genai.Client:
        if self._client is None:
            if not self._api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured.  "
                    "Set it in your .env file to enable LLM agents."
                )
            self._client = genai.Client(
                api_key=self._api_key, 
                http_options={"timeout": self._timeout}
            )
            logger.info("Gemini client initialised  model=%s", self._model_name)
        return self._client

    # ── Public API ────────────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_output_tokens: int = 4096,
        response_mime_type: str | None = None,
    ) -> str:
        """Send *prompt* to Gemini and return the response text.

        Retries up to ``_MAX_RETRIES`` times on transient errors.
        """
        client = self._ensure_client()
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type,
        )

        last_error: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 2):
            try:
                t0 = time.perf_counter()
                response = client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                )
                elapsed_ms = (time.perf_counter() - t0) * 1000
                
                try:
                    text = response.text or ""
                except ValueError:
                    text = ""
                    
                logger.debug(
                    "Gemini response  attempt=%d  chars=%d  %.0fms",
                    attempt,
                    len(text),
                    elapsed_ms,
                )
                return text
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Gemini call failed  attempt=%d/%d  error=%s",
                    attempt,
                    _MAX_RETRIES + 1,
                    exc,
                )
                if attempt <= _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY_S * attempt)

        raise RuntimeError(
            f"Gemini call failed after {_MAX_RETRIES + 1} attempts: {last_error}"
        ) from last_error

    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Call ``generate`` and parse the result as JSON.

        Handles the common case where the LLM wraps its JSON in a
        markdown code fence.
        """
        raw = self.generate(
            prompt, 
            temperature=temperature, 
            response_mime_type="application/json"
        )
        try:
            return parse_llm_json(raw)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse JSON response: %s\nRaw: %s", exc, raw)
            return {}


# ── Helpers ───────────────────────────────────────────────────────────────

def parse_llm_json(text: str) -> dict[str, Any]:
    """Extract and parse JSON from an LLM response.

    Handles markdown-wrapped ````` ```json ... ``` ````` blocks and bare
    JSON objects.
    """
    # 1. Try markdown code block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    # 2. Try to isolate the outermost { … }
    match = re.search(r"\{.*}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)
