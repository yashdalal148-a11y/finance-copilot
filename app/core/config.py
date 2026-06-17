"""
Application configuration.

Loads settings from environment variables (via .env file) with sensible
defaults for local-first, CPU-based deployment.  Every setting is
validated through Pydantic so the application fails fast on
misconfiguration rather than at runtime.
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Load .env from project root (two levels up from this file)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


class ProductMode(str, Enum):
    """Supported product modes.  V1 ships Interview Intelligence only;
    the rest are architecture placeholders for future expansion."""

    INTERVIEW_INTELLIGENCE = "interview_intelligence"
    EQUITY_RESEARCH_COACH = "equity_research_coach"
    STOCK_PITCH_ASSISTANT = "stock_pitch_assistant"
    VALUATION_COACH = "valuation_coach"
    ACCOUNTING_COACH = "accounting_coach"
    EARNINGS_CALL_INTELLIGENCE = "earnings_call_intelligence"
    MARKET_INTELLIGENCE = "market_intelligence"


class AppConfig(BaseModel):
    """Immutable application configuration."""

    # --- Gemini ---------------------------------------------------------
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key.",
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model identifier.",
    )
    gemini_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for Gemini.",
    )

    # --- Multi-Provider Keys --------------------------------------------
    groq_api_key: str = Field(
        default="",
        description="Groq API key.",
    )
    openrouter_api_key: str = Field(
        default="",
        description="OpenRouter API key.",
    )

    # --- Whisper --------------------------------------------------------
    whisper_model_size: str = Field(
        default="base",
        description="Faster-Whisper model size (tiny|base|small|medium|large-v3).",
    )
    whisper_device: str = Field(
        default="cpu",
        description="Compute device for Whisper (cpu|cuda).",
    )
    whisper_compute_type: str = Field(
        default="int8",
        description="Quantisation level (int8|float16|float32).",
    )

    # --- Paths ----------------------------------------------------------
    project_root: Path = Field(default=_PROJECT_ROOT)
    knowledge_dir: Path = Field(default=_PROJECT_ROOT / "knowledge")
    prompts_dir: Path = Field(default=_PROJECT_ROOT / "app" / "prompts")
    log_dir: Path = Field(default=_PROJECT_ROOT / "logs")

    # --- Logging --------------------------------------------------------
    log_level: str = Field(default="INFO")

    # --- Knowledge Retrieval -------------------------------------------
    max_knowledge_passages: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum knowledge passages returned per query.",
    )

    # --- Product -------------------------------------------------------
    active_mode: ProductMode = Field(
        default=ProductMode.INTERVIEW_INTELLIGENCE,
        description="Currently active product mode.",
    )

    @field_validator("gemini_api_key")
    @classmethod
    def _warn_missing_key(cls, v: str) -> str:
        if not v:
            import warnings
            warnings.warn(
                "GEMINI_API_KEY is not set. LLM agents will return fallback responses.",
                UserWarning,
                stacklevel=2,
            )
        return v

    model_config = {"frozen": True}


def load_config() -> AppConfig:
    """Build an ``AppConfig`` from environment variables."""
    return AppConfig(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.3")),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        whisper_model_size=os.getenv("WHISPER_MODEL_SIZE", "base"),
        whisper_device=os.getenv("WHISPER_DEVICE", "cpu"),
        whisper_compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
