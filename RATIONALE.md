# Rationale — Why PromoGuard

**One paragraph.** In 2026, Australia's grocery duopoly competes primarily through loyalty
discounting (Coles/Flybuys, Woolworths/Everyday Rewards), and the cost-of-living squeeze has
pushed personalised promotions to record volume. That scale leaks margin: single-use codes
redeemed twice, code stacking, guest-account farming, scripted velocity abuse, and adversarial
notes that try to manipulate any automated approver. PromoGuard fixes this with an ambient
triage agent that keeps the money rules deterministic in Python (so the common low-value case
is instant and free of LLM cost) and reserves a Gemini risk review plus a human-in-the-loop
manager decision for the genuinely ambiguous, high-value cases — with PII scrubbed and prompt
injection short-circuited before the model ever runs. It's a real enterprise problem with
measurable dollar impact, it maps directly onto the retail shopping-assistant and
ambient-expense patterns, and it naturally demonstrates the required
concepts: an ADK 2.0 graph workflow, validated agent tools, a custom STRIDE skill, layered
security (PII + injection + Semgrep pre-commit gating), and agents-cli evaluation.

**Why this over the alternatives:**
- *vs. the corporate expense agent* — same ambient/HITL pattern, but a sharper, more
  defensible Australian-retail business case (loyalty fraud) rather than generic expenses.
- *vs. a plain shopping assistant* — adds the security, evaluation, and human-in-the-loop
  depth the rubric rewards, instead of a single-tool chatbot.
- *vs. a waste/markdown agent (runner-up)* — strong too, but promotion integrity reuses the
  taught `redeem_discount` guardrails almost 1:1, making it faster to build well and easier to
  evaluate rigorously.
