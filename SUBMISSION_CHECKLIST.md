# Kaggle Submission Checklist — PromoGuard

Kaggle requires: *"a Kaggle writeup documenting the agent, including a video explaining the
agent, a brief description of your rationale for building it, and a link to your code used to
build the agent."* Plus: demonstrate ≥3 course concepts; team of up to 4; one submission;
deadline **July 6, 2026, 11:59 PM PT**.

| Requirement | Artefact | Status |
|---|---|---|
| Kaggle writeup documenting the agent | `KAGGLE_WRITEUP.md` | ✅ done — paste into the Kaggle writeup editor |
| Video explaining the agent | `PromoGuard_video_slides.pptx` + `docs/VIDEO_SCRIPT.md` | ⬜ **you record** (~3 min) and add the URL |
| Brief rationale | `RATIONALE.md` (also writeup §1–2) | ✅ done |
| Link to your code | repo via `push_to_github.sh` | ✅ done |
| ≥3 course concepts | writeup §4 (shows 5) | ✅ done |
| Track selected | Agents for Business | ✅ |

## The only one things left for you
2. **Record the video** → get the URL
   - Open `PromoGuard_video_slides.pptx`, present full-screen.
   - Read `docs/VIDEO_SCRIPT.md` (timed, ~3 min).
   - For the live-demo segment, run: `python demo_events.py` (clean terminal output of all
     three paths) — or send the events through the ADK Playground (`agents-cli run`).
   - Upload (YouTube unlisted / Drive) and copy the link.

## Then finalise
- In `KAGGLE_WRITEUP.md` §9, replace `<your GitHub URL>` and `<your video URL>`.
- Create the writeup on the competition page, paste the writeup, attach/link the video and repo.
- Submit before the deadline. One submission per person/team.

## Pre-submit sanity checks
```bash
uv run pytest -q                              # tests GREEN
uv run semgrep --error --config .semgrep/rules.yaml app/agent.py   # no hardcoded key
python demo_events.py                         # three paths print correctly
```
