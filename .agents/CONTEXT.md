# Local Project Context & Secure Coding Standards — PromoGuard

This file is the "paved road" for Antigravity. Follow these pre-approved, secure-by-default
conventions instead of writing raw implementation logic from scratch.

## Core Paved Roads
1. **Tool Input Validation**: Every agent tool must validate incoming parameters against
   strict Pydantic schemas (e.g. `RedemptionRequest`) rather than parsing raw dicts/strings.
2. **No Hardcoded Secrets**: API keys and credentials are read from the environment
   (`GEMINI_API_KEY`). Never inline a literal key — the Semgrep pre-commit gate will block it.
3. **No Shell Execution**: Never use `run_command` or raw shell execution tools unless
   explicitly approved by `hooks.json`.
4. **Money Rules in Code**: Deterministic routing (the AUD threshold, single-use, velocity)
   stays in Python. The LLM is advisory only and must never execute a redemption.
5. **Pre-Commit Remediation Loop**: If a git commit fails due to a pre-commit hook error
   (such as a Semgrep finding), treat the violation as a refactoring task: apply targeted
   fixes, run `pytest` to verify no regressions, and attempt the commit again.

## TDD Planning Gate
During the Plan phase, decompose the workspace task into logical, modular stages.
Every implementation plan MUST include a dedicated **Security Boundaries & Assertions**
section outlining specific edge cases that could exploit the feature (e.g. double-redemption
race conditions, guest-account privilege escalation, negative basket totals, code stacking).
