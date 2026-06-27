# promoguard/app/agent.py
# PromoGuard — Ambient Promotion-Integrity & Loyalty Agent for Australian supermarkets.
# Built on Google ADK 2.0 (graph Workflow API), mirroring the patterns taught in the
# Kaggle 5-Day AI Agents Intensive (shopping-assistant + ambient-expense-agent codelabs).
#
# Routing philosophy (deterministic where possible, LLM only for genuine ambiguity):
#   - Low-risk redemption (single code, registered user, value < THRESHOLD)
#         -> auto_approve  (plain Python, no LLM cost/latency)
#   - High-value / suspicious redemption (value >= THRESHOLD, stacking, velocity)
#         -> security_check -> review_agent (Gemini risk analysis) -> human_review
#
# NOTE on credentials: the API key is loaded from the environment via config.py.
# An earlier draft hardcoded a mock key to demonstrate the Semgrep pre-commit gate;
# it has since been remediated to read from GEMINI_API_KEY (see docs/BUILD_GUIDE.md).

from __future__ import annotations

import json
import time
from typing import Any, Dict

from google.adk.apps.app import App
from google.adk.models.google_llm import Gemini
from google.adk.workflow import Edge, Workflow
from google.adk.workflow.agents.llm_agent import LlmAgent
from google.adk.workflow.node import node
from google.adk.workflow.request_input import RequestInput
from pydantic import BaseModel, Field

from app.config import settings
from app.security import redact_pii, detect_prompt_injection

# --------------------------------------------------------------------------- #
# Model (secure-by-default: key comes from the environment, never hardcoded)
# --------------------------------------------------------------------------- #
model = Gemini(model=settings.model_name, api_key=settings.gemini_api_key)

# --------------------------------------------------------------------------- #
# In-memory promotion + loyalty store (simulates the promotions DB / loyalty
# ledger that would sit behind Flybuys / Everyday Rewards in production).
# Each code carries a per-customer single-use rule and a dollar value.
# --------------------------------------------------------------------------- #
PROMO_STORE: Dict[str, Dict[str, Any]] = {
    "WELCOME50":   {"value": 50.0, "single_use": True,  "redeemed_by": set()},
    "SUMMER20":    {"value": 20.0, "single_use": True,  "redeemed_by": set()},
    "FRESH10":     {"value": 10.0, "single_use": False, "redeemed_by": set()},
    "BULKBUY200":  {"value": 200.0, "single_use": True, "redeemed_by": set()},  # high value
}

# Loyalty ledger: customer_id -> list of redemption events (memory / repudiation defence)
LOYALTY_LEDGER: Dict[str, list] = {}


class RedemptionRequest(BaseModel):
    """Strict schema for an incoming promotion redemption (Tampering defence)."""
    code: str = Field(description="The promotion / discount code to redeem.")
    customer_id: str = Field(description="Loyalty member ID (e.g. Flybuys / Everyday Rewards).")
    basket_total: float = Field(description="Total basket value in AUD.", ge=0)
    store_id: str = Field(description="Store identifier where redemption occurs.")
    description: str = Field(default="", description="Free-text note attached to the redemption.")


def _log_event(customer_id: str, event: Dict[str, Any]) -> None:
    """Append an immutable-ish audit record (Repudiation defence)."""
    LOYALTY_LEDGER.setdefault(customer_id, []).append({"ts": time.time(), **event})


# --------------------------------------------------------------------------- #
# Agent tool: redeem_promotion
# Enforces the same guardrails taught for redeem_discount, extended for grocery
# loyalty: invalid code, already redeemed (single-use), registered-member-only,
# and velocity (anti-abuse) checks.
# --------------------------------------------------------------------------- #
def redeem_promotion(code: str, customer_id: str, store_id: str = "UNKNOWN") -> str:
    """Agent Tool: Redeem a single-use promotion code for a registered loyalty member."""
    code = (code or "").strip().upper()
    if code not in PROMO_STORE:
        return "Error: Invalid promotion code."

    promo = PROMO_STORE[code]

    # Elevation-of-Privilege defence: guests / unauthenticated cannot redeem.
    if not customer_id or customer_id.startswith("guest_"):
        return "Error: Registered loyalty account required to redeem promotions."

    # Single-use enforcement (per customer).
    if promo["single_use"] and customer_id in promo["redeemed_by"]:
        return "Error: This promotion code has already been redeemed by this member."

    # Velocity / anti-abuse: block obvious code-farming within a short window.
    recent = [e for e in LOYALTY_LEDGER.get(customer_id, [])
              if e.get("type") == "redeem" and time.time() - e["ts"] < 60]
    if len(recent) >= settings.velocity_limit_per_minute:
        return "Error: Redemption velocity limit exceeded. Flagged for review."

    promo["redeemed_by"].add(customer_id)
    _log_event(customer_id, {"type": "redeem", "code": code, "value": promo["value"],
                             "store_id": store_id})
    return (f"Success: Promotion {code} (${promo['value']:.2f} AUD) redeemed for "
            f"member {customer_id} at store {store_id}.")


# --------------------------------------------------------------------------- #
# Graph nodes
# --------------------------------------------------------------------------- #
@node
def ingest(context) -> Dict[str, Any]:
    """Parse the inbound event. Supports base64 Pub/Sub payloads or plain JSON
    (local testing), mirroring the ambient-expense-agent ingest pattern."""
    raw = context.input
    data = raw.get("data", raw) if isinstance(raw, dict) else raw
    if isinstance(data, str):
        try:
            import base64
            data = base64.b64decode(data).decode("utf-8")
        except Exception:
            pass
        data = json.loads(data)
    req = RedemptionRequest(**data)
    context.state["request"] = req.model_dump()
    return context.state["request"]


@node
def route(context) -> str:
    """Deterministic router: keep money rules in code, send only ambiguous /
    high-value cases to the LLM. Returns the next node label."""
    req = context.state["request"]
    promo = PROMO_STORE.get(req["code"].strip().upper(), {})
    promo_value = promo.get("value", 0.0)
    high_value = promo_value >= settings.high_value_threshold
    context.state["promo_value"] = promo_value
    if not high_value:
        return "auto_approve"
    return "security_check"


@node
def auto_approve(context) -> Dict[str, Any]:
    """Low-risk path: redeem instantly with no LLM call."""
    req = context.state["request"]
    result = redeem_promotion(req["code"], req["customer_id"], req["store_id"])
    context.state["result"] = result
    context.state["path"] = "auto_approve"
    return {"status": "auto_approved", "detail": result}


@node
def security_check(context) -> str:
    """Pre-LLM screen: redact PII from the free-text note and short-circuit
    prompt-injection attempts straight to human review (never let the model
    see adversarial instructions)."""
    req = context.state["request"]
    clean, redacted = redact_pii(req.get("description", ""))
    req["description"] = clean
    context.state["request"] = req
    context.state["redacted_categories"] = redacted

    if detect_prompt_injection(clean):
        context.state["security_event"] = True
        context.state["result"] = "SECURITY: prompt-injection detected — routed to human."
        return "human_review"
    return "review_agent"


# LLM risk reviewer — only sees clean, high-value cases.
review_agent = LlmAgent(
    name="PromoRiskReviewer",
    model=model,
    instruction=(
        "You are a promotion-integrity analyst for an Australian supermarket "
        "(e.g. Coles/Woolworths). You are given a high-value loyalty redemption. "
        "Assess fraud/abuse risk: code stacking, mismatched basket value, unusual "
        "store/member pairing, or terms-of-service violations. Respond with a short "
        "risk rating (LOW/MEDIUM/HIGH) and one-sentence justification. Never approve "
        "or execute a redemption yourself — you only advise the human reviewer."
    ),
    tools=[],  # advisory only; redemption stays under deterministic human control
)


@node
def record_outcome(context) -> Dict[str, Any]:
    """After the human decides, persist the outcome to the loyalty ledger."""
    req = context.state["request"]
    decision = context.state.get("human_decision", {"approved": False})
    approved = bool(decision.get("approved"))
    if approved:
        result = redeem_promotion(req["code"], req["customer_id"], req["store_id"])
    else:
        result = "Rejected by store manager."
    _log_event(req["customer_id"], {"type": "decision", "approved": approved,
                                    "code": req["code"]})
    context.state["result"] = result
    return {"status": "approved" if approved else "rejected", "detail": result}


# Human-in-the-loop pause (ADK 2.0 RequestInput): a store manager / promotions
# desk approves or rejects high-value or flagged redemptions.
human_review = RequestInput(
    name="human_review",
    prompt="High-value or flagged promotion redemption needs a manager decision.",
    output_key="human_decision",
)


# --------------------------------------------------------------------------- #
# Wire the graph
# --------------------------------------------------------------------------- #
root_workflow = Workflow(
    name="promoguard_workflow",
    edges=[
        *Edge.chain("START", ingest, route),
        Edge(route, auto_approve, condition=lambda c: c.state.get("_route") == "auto_approve"),
        Edge(route, security_check, condition=lambda c: c.state.get("_route") == "security_check"),
        Edge(security_check, review_agent,
             condition=lambda c: c.state.get("_route") == "review_agent"),
        Edge(security_check, human_review,
             condition=lambda c: c.state.get("_route") == "human_review"),
        Edge(review_agent, human_review),
        Edge(human_review, record_outcome),
    ],
)

app = App(name="promoguard", root_agent=root_workflow)
