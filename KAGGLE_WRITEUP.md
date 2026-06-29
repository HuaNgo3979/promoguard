# PromoGuard — Ambient Promotion-Integrity & Loyalty Agent for Australian Supermarkets
### Kaggle 5-Day AI Agents Intensive — Capstone Writeup
**Track:** Agents for Business

---

## 1. The problem (Australia, 2026)
Australian grocery is a duopoly fight fought on loyalty. Coles runs **Flybuys**, Woolworths
runs **Everyday Rewards**, and in a prolonged cost-of-living squeeze, personalised digital
promotions have become the primary lever for basket share. That scale creates a quiet but
expensive failure mode: **promotion leakage and loyalty fraud** — single-use codes redeemed
multiple times, code stacking beyond terms, guest/throwaway accounts farming offers,
velocity abuse from scripts, and adversarial free-text notes attempting to manipulate any
automated approver. Every leaked dollar is straight margin in a low-margin business.

The naive fix — route every redemption through an LLM — is slow, costly, and itself
attackable (prompt injection). The naive opposite — approve everything in code — leaks on
the genuinely ambiguous, high-value cases that need judgement.

## 2. The agent
**PromoGuard** is an event-driven (ambient) ADK 2.0 agent that acts as a triage queue for
redemption events. It keeps the money rules deterministic and spends LLM tokens only where
judgement is actually required:

- **Value < AUD 100 →** `auto_approve` instantly in plain Python (no LLM call).
- **Value ≥ AUD 100 →** a pre-LLM **security screen** (PII redaction + prompt-injection
  defence) → a **Gemini risk review** (LOW/MEDIUM/HIGH, advisory only) → a
  **human-in-the-loop** manager decision via ADK 2.0 `RequestInput` → `record_outcome`
  written to the loyalty ledger.

Injection attempts never reach the model: the security node short-circuits them straight to
a human and flags a security event. The LLM is strictly advisory — it never executes a
redemption, so a manipulated model cannot move money.

## 3. Architecture
```
event ─▶ ingest ─▶ route ──< AUD 100 ──────────────────────────────▶ auto_approve ✅
                       └──≥ AUD 100 ─▶ security_check ─▶ review_agent (Gemini) ─▶ human_review ⏸️ ─▶ record_outcome
                                              └─ PII redacted; injection ⇒ human ──────────────────────┘
```
- **Tool:** `redeem_promotion(code, customer_id, store_id)` — strict Pydantic input, with
  guardrails for invalid code, single-use-per-member, registered-member-only (guests
  rejected), and a per-minute velocity limit.
- **State/memory:** `PROMO_STORE` (server-side promotion values + redemption set) and
  `LOYALTY_LEDGER` (timestamped audit of every redemption and decision — repudiation defence).

## 4. Course concepts demonstrated (≥3 required)
| # | Concept | Where |
|---|---------|-------|
| 1 | **ADK 2.0 multi-node graph workflow** with conditional edges + `RequestInput` HITL | `app/agent.py` |
| 2 | **Agent tools** with Pydantic validation + business guardrails | `redeem_promotion` |
| 3 | **Custom agent skill** (STRIDE threat model → `threat_model.md`) | `.agents/skills/stride-threat-model/` |
| 4 | **Security features** — PII redaction, prompt-injection defence, Semgrep pre-commit gate + agent hooks | `app/security.py`, `.semgrep/`, `.pre-commit-config.yaml`, `.agents/hooks.json` |
| 5 | **Evaluation** — `agents-cli` LLM-as-judge eval set | `eval/promoguard.evalset.json` |

## 5. How it was built — vibe coding
Built entirely by prompting **Google Antigravity** (and the Antigravity IDE / CLI); I acted
as the architect and reviewed/approved each plan. Flow: `uvx google-agents-cli setup` to load
ADK skills → scaffold the project → vibe-code the graph core → add the security checkpoint →
author the STRIDE skill and run it → configure Semgrep + the pre-commit gate (which caught a
deliberately-planted mock API key and triggered an autonomous remediation loop) → generate
outcome-based pytest tests (GREEN) → evaluate with `agents-cli`. Full reproducible prompts are
in `docs/BUILD_GUIDE.md`.

## 6. Security posture (STRIDE summary)
Spoofing — guests rejected; Tampering — promo value read server-side, not from the request;
Repudiation — append-only ledger; Information Disclosure — PII scrubbed pre-LLM and pre-log;
DoS — velocity limit + deterministic routing keeps the LLM off the hot path; Elevation of
Privilege — injection short-circuits to human, LLM never executes redemptions. Full table in
`threat_model.md`.

## 7. Results & impact
- **Cost/latency:** the majority of redemptions (low value) never touch the LLM.
- **Fraud control:** single-use, registered-member, and velocity rules close the common leakage paths; high-value cases always get human eyes.
- **Auditability:** every decision is logged for dispute resolution and compliance.
- **Tests:** outcome-based pytest suite passes for all guardrails and the security screen.

## 8. Limitations & next steps
In-memory stores are for the lab; production needs a transactional DB with pessimistic
locking to remove the double-redemption race window, gateway-level member authentication
(OIDC/mTLS), a managed DLP service for broader PII coverage, and an append-only audit sink.
Next: wire a live Pub/Sub topic to Agent Runtime and ship the FastAPI manager dashboard for
approving paused high-value redemptions.

## 9. Submission artefacts
- **Code:** https://github.com/HuaNgo3979/promoguard (see `docs/BUILD_GUIDE.md` to reproduce).
- **Video:** https://youtu.be/U7rQ7wWo4Wg — walkthrough of the four live demos (auto-approve, manager escalation, injection duplicated, injection blocked).
- **Rationale:** see `RATIONALE.md` (also summarised in §1–2 above).

*Not affiliated with Coles, Woolworths, Flybuys, or Everyday Rewards; names used illustratively.*
