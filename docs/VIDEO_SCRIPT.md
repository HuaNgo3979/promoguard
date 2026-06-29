# PromoGuard — Video Script (~5:30 minutes)

Read this straight through while screen-recording. Timestamps are a guide; `[…]`
tells you what to have on screen. Slides 1–12 are in `PromoGuard_video_slides.pptx`
(the same wording lives in each slide's speaker notes).

---

### 0:00 – 0:32 · Intro  `[Slide 1]`
"Hi — this is PromoGuard, an ambient promotion-integrity and loyalty agent for Australian
supermarkets like Coles and Woolworths. It's my capstone for the 5-Day AI Agents Intensive,
in the Agents for Business track, and I built the whole thing by vibe coding in Google
Antigravity. In the next three minutes I'll cover the problem, the design, the security, and
a quick live demo."

### 0:32 – 1:10 · The problem  `[Slide 2]`
"Australian grocery competes on loyalty — Flybuys and Everyday Rewards. Cost-of-living
pressure pushed personalised discounting to record volume, and at that scale you get leakage:
single-use codes redeemed twice, code stacking, guest-account farming, scripted velocity
abuse, and adversarial notes trying to trick an automated approver. Routing everything through
an LLM is slow, costly, and itself attackable; approving everything in code leaks on the hard
cases."

### 1:10 – 1:47 · The agent  `[Slide 3]`
"PromoGuard keeps the money rules deterministic. Under a hundred dollars, it auto-approves
instantly in plain Python — no LLM — while still enforcing single-use, registered-member-only,
and a velocity limit. A hundred dollars or more goes through a security screen, a Gemini risk
review that's advisory only, and a human-in-the-loop manager decision. The model never executes
a redemption, so a manipulated model can't move money."

### 1:47 – 2:22 · Architecture  `[Slide 4]`
"It's one ADK 2.0 graph. Ingest parses the event — base64 Pub/Sub or plain JSON — and validates
it with Pydantic. Route reads the promotion's value server-side and branches: low value to
auto_approve, high value to security_check, then the Gemini reviewer, then the human pause, then
record_outcome. PII is redacted before the model, and injection short-circuits straight to a human."

### 2:22 – 2:54 · Security  `[Slide 5]`
"Security is shifted left. PII — card numbers, Australian TFNs, emails, phones — is scrubbed
before the LLM and before logs. Prompt injection never reaches the model. A Semgrep pre-commit
gate blocks hardcoded API keys from leaving the workstation — during the build it caught a
planted mock key and triggered the agent's own remediation loop. And a custom STRIDE skill
produces a structured threat model."

### 2:54 – 3:13 · Concepts  `[Slide 6]`
"The capstone asks for three course concepts. PromoGuard is met that by showing an ADK 2.0 graph workflow,
validated agent tools, a custom agent skill, layered security, and agents-cli evaluation."

### 3:13 – 4:55 · Live demo  `[Slide 7-10, ADK Playground]`
"Here is a live demo with 4 events. 

First, Case A: Low-Value Auto-Approval (Deterministic Python path). This tests a promotion value under AUD 100 (FRESH10 is worth AUD 10). The workflow will auto-approve instantly without calling the LLM or requesting manager input.

Second, Case B: High-Value Escalation (LLM Risk Assessment + Manager HITL). This tests a high-value promotion (BULKBUY200 is worth AUD 200). It runs a PII scrub, calls the LLM risk_review node, and pauses the Playground session asking: "Manager: Please reply with 'approve' or 'reject'..."

Third, Case C: Automatic Rejection Due to Duplicate Promotion. Because your current database already records member_878 redeeming the BULKBUY200 code, the Agent will immediately reject it at the first verification step, even payment conducted in different stores, without needing to call the LLM or ask the Manager.

Finally, Case D: Prompt Injection Defense (Security Checkpoint Bypass). This tests a high-value promotion where the description contains prompt injection. The security checkpoint flags the transaction, bypasses the LLM node entirely to prevent manipulation, sets the risk score to 10, and routes directly to the manager."

### 4:55 – 5:15 · How it was built `[Slide 11]`
"All of this was vibe-coded — I was the orchestrator, Antigravity did the typing, across Antigravity 2.0, the IDE, and the CLI; every prompt is reproducible in the build guide."

### 5:15 – 5:35 · Close `[Slide 12]`
"The low-value majority never touches the LLM, the common leakage paths are closed, and every
high-value case gets a human decision and an audit trail. The code, writeup, rationale, and
build guide are all in the repo. Thanks for watching."
