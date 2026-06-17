import time
import logging
import json
from typing import Any, Protocol, Optional
from app.core.models import ProviderName

logger = logging.getLogger(__name__)

class ProviderClient(Protocol):
    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        ...
        
    def generate_json(self, prompt: str, temperature: float = 0.2) -> dict[str, Any]:
        ...

# ── Helpers ───────────────────────────────────────────────────────────────
import re

def parse_llm_json(text: str) -> dict[str, Any]:
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    match = re.search(r"\{.*}", text, re.DOTALL)
    if match:
        text = match.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse JSON response: {exc}\nRaw: {text}")
        return {}


# ── Concrete Providers ─────────────────────────────────────────────────────

class GeminiProvider:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash", timeout: float = 30.0):
        self._api_key = api_key
        self._model_name = model_name
        self._timeout = timeout
        self._client = None
        
    def _ensure_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key, http_options={"timeout": self._timeout})
        return self._client

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        client = self._ensure_client()
        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = client.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=config,
        )
        try:
            return response.text or ""
        except ValueError:
            return ""

    def generate_json(self, prompt: str, temperature: float = 0.2) -> dict[str, Any]:
        client = self._ensure_client()
        from google.genai import types
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
        )
        response = client.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=config,
        )
        try:
            raw = response.text or ""
        except ValueError:
            raw = ""
        return parse_llm_json(raw)


class GroqProvider:
    def __init__(self, api_key: str, model_name: str = "llama3-70b-8192", timeout: float = 30.0):
        self._api_key = api_key
        self._model_name = model_name
        self._timeout = timeout
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=self._api_key, timeout=self._timeout)
        return self._client

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        client = self._ensure_client()
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self._model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return chat_completion.choices[0].message.content or ""

    def generate_json(self, prompt: str, temperature: float = 0.2) -> dict[str, Any]:
        client = self._ensure_client()
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self._model_name,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        raw = chat_completion.choices[0].message.content or ""
        return parse_llm_json(raw)


class OpenRouterProvider:
    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3-haiku", timeout: float = 30.0):
        self._api_key = api_key
        self._model_name = model_name
        self._timeout = timeout
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self._api_key,
                timeout=self._timeout
            )
        return self._client

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        client = self._ensure_client()
        completion = client.chat.completions.create(
            model=self._model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return completion.choices[0].message.content or ""

    def generate_json(self, prompt: str, temperature: float = 0.2) -> dict[str, Any]:
        client = self._ensure_client()
        completion = client.chat.completions.create(
            model=self._model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            # OpenRouter passes this down to models that support it
            response_format={"type": "json_object"},
        )
        raw = completion.choices[0].message.content or ""
        return parse_llm_json(raw)


class ProviderRegistry:
    def __init__(self, gemini_key: str, groq_key: str, openrouter_key: str):
        self._providers = {}
        if gemini_key:
            self._providers[ProviderName.GEMINI] = GeminiProvider(api_key=gemini_key)
        if groq_key:
            self._providers[ProviderName.GROQ] = GroqProvider(api_key=groq_key)
        if openrouter_key:
            self._providers[ProviderName.OPENROUTER] = OpenRouterProvider(api_key=openrouter_key)
            
    def get_provider(self, name: ProviderName) -> Optional[ProviderClient]:
        return self._providers.get(name)
