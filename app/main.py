"""
Finance Intelligence Copilot — Application Entry Point.

Usage:
    streamlit run app/main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path for reliable imports when
# Streamlit is launched from any working directory.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.ui.dashboard import render_dashboard  # noqa: E402

render_dashboard()
