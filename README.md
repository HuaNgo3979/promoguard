# PromoGuard 🛒🔒
### Ambient Promotion-Integrity & Loyalty Agent for Australian supermarkets

**Kaggle 5-Day AI Agents Intensive — Capstone (Track: Agents for Business)**

PromoGuard is an event-driven ADK 2.0 agent that triages loyalty promotion redemptions
for grocers like **Coles (Flybuys)** and **Woolworths (Everyday Rewards)**. It auto-approves
low-value redemptions deterministically (no LLM cost), and routes high-value or suspicious
ones through a security screen, a Gemini risk review, and a human-in-the-loop manager
decision — cutting promotion leakage and coupon/loyalty fraud while keeping a clean audit trail.

```
event ─▶ ingest ─▶ route ──< AUD 100 ─────────────────────────▶ auto_approve ✅ (no LLM)
                       └──≥ AUD 100 ─▶ security_check ─▶ review_agent (Gemini) ─▶ human_review ⏸️ ─▶ record_outcome
                                              └─(PII redacted; injection ⇒ straight to human) ─────────────┘
```

## Why it matters (2026, Australia)
Cost-of-living pressure has pushed loyalty discounting to record highs, and with it
promotion leakage: code stacking, multi-redemption, guest-account abuse, and adversarial
notes. PromoGuard keeps the money rules in deterministic Python and uses the LLM only for
genuine ambiguity — fast, cheap, auditable, and secure-by-default.

## Demonstrated course concepts (≥3)
1. **ADK 2.0 graph workflow** — multi-node graph with conditional edges + `RequestInput` human-in-the-loop.
2. **Agent tools** — `redeem_promotion` with strict Pydantic validation and business guardrails.
3. **Agent skill** — custom `stride-threat-model` skill producing `threat_model.md`.
4. **Security** — PII redaction, prompt-injection defence, Semgrep pre-commit gate + agent hooks.
5. **Evaluation** — `agents-cli` LLM-as-judge eval set.

## Quickstart
```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"        # or: uv sync
cp .env.example .env              # add your GEMINI_API_KEY
uv run pytest -q                  # business + security tests (GREEN)
python demo_events.py             # fire 3 demo events, print each path (great for the video)
agents-cli run                    # local ADK Playground
agents-cli eval eval/promoguard.evalset.json
```

## Submitting (Kaggle)
See **[SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)**. Record using
**[docs/VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md)** (~3 min, timed) and publish the code with
`push_to_github.sh`.

## Build it yourself (vibe coding)
See **[docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md)** for the full Antigravity / Antigravity IDE /
Antigravity CLI step-by-step.

## Layout
```
promoguard/
├── app/
│   ├── agent.py        # ADK 2.0 graph: ingest→route→{auto_approve | security→review→human→record}
│   ├── config.py       # threshold, model, velocity (env-driven; no hardcoded secrets)
│   └── security.py     # PII redaction + prompt-injection detection
├── tests/test_agent.py # outcome-based security & business-logic tests
├── eval/promoguard.evalset.json
├── .agents/            # CONTEXT.md, hooks.json, validate_tool_call.py, skills/stride-threat-model
├── .semgrep/rules.yaml
├── .pre-commit-config.yaml
├── threat_model.md     # sample STRIDE output
└── docs/BUILD_GUIDE.md
```

## Disclaimer
Not affiliated with or endorsed by Coles, Woolworths, Flybuys, or Everyday Rewards;
those names are used illustratively. In-memory stores are for the lab — use a
transactional DB with row locking in production.
