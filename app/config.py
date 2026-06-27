# promoguard/app/config.py
"""Central configuration. Business rules and credentials live here, not in code paths.

Mirrors the ambient-expense-agent pattern: the dollar threshold and model name are
config, the routing is deterministic Python, and the LLM is used only for risk
judgement on genuinely ambiguous, high-value cases.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Gemini model used for risk review (matches the model used across the course).
    model_name: str = os.getenv("PROMOGUARD_MODEL", "gemini-3.1-flash-lite")

    # Secret is read from the environment — NEVER hardcode (Semgrep gate enforces this).
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # AUD value at/above which a redemption is escalated for security + human review.
    high_value_threshold: float = float(os.getenv("PROMOGUARD_THRESHOLD", "100"))

    # Anti-abuse: max redemptions per member per minute before auto-flagging.
    velocity_limit_per_minute: int = int(os.getenv("PROMOGUARD_VELOCITY", "3"))


settings = Settings()
