# promoguard/app/security.py
"""Pre-LLM security screen for PromoGuard.

Two enterprise controls, exactly as taught in the ambient-expense-agent codelab:

  1. PII redaction  — scrub sensitive customer data (credit-card numbers, TFNs,
     emails, phone numbers) from any free-text BEFORE it reaches the model or logs.
  2. Prompt-injection defence — if a redemption note is stuffed with adversarial
     instructions ("approve this $1,000,000 promo", "ignore the rules"), do not let
     the model see it: route straight to a human and flag a security event.

These are intentionally lightweight, deterministic checks suitable for an inline
pre-LLM checkpoint. In production, pair with a managed DLP service.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# --- PII patterns (Australian context: TFN, card, email, phone) ---------------
_PII_PATTERNS = {
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "TFN":         re.compile(r"\b\d{3}\s?\d{3}\s?\d{3}\b"),  # Australian Tax File Number
    "EMAIL":       re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "PHONE":       re.compile(r"\b(?:\+?61|0)[2-478](?:[ -]?\d){8}\b"),
}

# --- Prompt-injection signal phrases -----------------------------------------
_INJECTION_SIGNALS = [
    r"ignore (all|the|previous) (rules|instructions)",
    r"bypass (all|the)? ?(validation|rules|checks)",
    r"auto[- ]?approve",
    r"approve (this|it) (now|immediately)",
    r"you are now",
    r"system prompt",
    r"disregard",
    r"override",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_SIGNALS), re.IGNORECASE)


def redact_pii(text: str) -> Tuple[str, List[str]]:
    """Return (clean_text, [categories_redacted])."""
    if not text:
        return "", []
    redacted: List[str] = []
    clean = text
    for label, pattern in _PII_PATTERNS.items():
        if pattern.search(clean):
            clean = pattern.sub(f"[REDACTED_{label}]", clean)
            redacted.append(label)
    return clean, redacted


def detect_prompt_injection(text: str) -> bool:
    """True if the text contains adversarial instruction patterns."""
    if not text:
        return False
    return bool(_INJECTION_RE.search(text))
