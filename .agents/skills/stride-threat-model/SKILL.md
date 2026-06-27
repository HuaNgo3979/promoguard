---
name: stride-threat-model
description: Performs a systematic STRIDE threat modeling assessment on the
  current project's codebase and architecture. Use this when starting a new
  implementation phase or reviewing existing components.
---

# STRIDE Threat Modeling Skill

## Goal
Guide the agent to analyze the workspace directory structure, configuration
files, and code files to produce a structured `threat_model.md` assessment.

## Instructions
1. **Analyze System Boundaries**: Map the entry points (tools, workflow nodes,
   prompts) and data storage layers (PROMO_STORE, LOYALTY_LEDGER).
2. **STRIDE Evaluation**: Evaluate the system against the six STRIDE pillars:
   - **Spoofing**: Are caller identity boundaries (registered member vs guest)
     verified before executing sensitive tool logic?
   - **Tampering**: Can users manipulate data flows, parameters, or state
     (e.g. basket_total, code value)?
   - **Repudiation**: Are critical redemptions securely logged to the ledger?
   - **Information Disclosure**: Are we risking leakage of PII (card, TFN, email),
     internal tokens, or raw stack traces?
   - **Denial of Service**: Are there rate/velocity limits on expensive LLM or
     redemption operations?
   - **Elevation of Privilege**: Can an unauthenticated/guest user bypass access
     control to reach privileged redemption actions?
3. **Output**: Generate a highly structured `threat_model.md` saved into the
   workspace root.
