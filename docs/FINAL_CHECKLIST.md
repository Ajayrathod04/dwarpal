# Final Submission Checklist — DWARPAL

## 1. Deadlines & Milestones
- **Official Deadline:** Friday, October 23, 2026, 12:00 PM PDT = Saturday, October 24, 2026, 12:30 AM IST.
- **Code Freeze Target:** October 23, 11:20 PM IST (Achieved ahead of target).
- **Target Submission:** October 23, 11:45 PM IST.
- **Post-Deadline Policy:** No code commits permitted after portal submission.

---

## 2. Engineering Verification Gate

- [x] Baseline captured prior to edits (`docs/EXECUTION_REPORT.md`).
- [x] All source files, docs, and dependencies inspected.
- [x] Python compilation passed (`python -m compileall -q app tests` -> 0 errors).
- [x] Full automated test suite passed (`python -m pytest -q` -> 24 passed in 13.20s).
- [x] JavaScript syntax check passed (`node --check app/static/app.js` -> 0 errors).
- [x] Live uvicorn server verified (`/` and `/api/health` return HTTP 200).
- [x] Dual MCP SDK support implemented and `/mcp` Streamable HTTP endpoint mounted.
- [x] 7-stage lifecycle state machine implemented and verified.
- [x] Deterministic rules-based explainable risk assessment implemented.
- [x] Canonical SHA-256 plan integrity binding (`dwarpal-plan-v1`) implemented with constant-time check (`hmac.compare_digest`).
- [x] Server-side tamper detection (`PLAN_TAMPERED`) verified by test suite.
- [x] Atomic single-use approval transition and replay rejection (`ALREADY_FINALIZED`) verified.
- [x] 10-minute validity expiry enforced server-side.
- [x] Structured audit logging with event IDs, correlation IDs, reason codes, and sanitization verified.
- [x] 4 bounded scenario presets (`safe_approved`, `missing_approval`, `tampered_plan`, `replayed_plan`) tested.
- [x] End-to-end browser UI verified via automated browser testing (0 console errors; video recording saved).
- [x] Clean release hygiene: runtime `.sqlite3` files purged, `.env` excluded in `.gitignore`.

---

## 3. Devpost Submission & Track Governance

- [x] **Primary Track Selected:** **Alexa+** (Simulated experience & self-hosted Streamable HTTP MCP server route).
- [x] **AWS Builder Mini-Challenge:** **Not Selected / Disclosed as Not Configured** (Honest disclosure: Amazon Verified Permissions and Bedrock adapters present in source code but not connected to live cloud resources).
- [x] **Open Source Mini-Challenge:** Open-source MIT repository created in hackathon window.
- [x] **Honest Disclosures & Simulation Badges:** Prominently visible in UI header, hero, footer, and README. No fake locks, real contractor dispatch, or fake ML scores.
- [x] **Product Feedback Complete:** Honest observations recorded for Python, FastAPI, MCP SDK, SQLite, and Pytest in `docs/PRODUCT_FEEDBACK.md`.
- [x] **Friction Log Complete:** Real technical friction items recorded in `docs/FRICTION_LOG.md`.
- [x] **Demo Script Complete:** Under-3-minute walkthrough script prepared in `docs/DEMO_SCRIPT.md`.
- [x] **MIT License Visible:** In `LICENSE`.

---

## 4. Remaining Participant Actions Before Cutoff

1. **Commit & Tag Release Candidate:**
   - Commit all hardened source files and docs: `git commit -m "release: DWARPAL v1.2.0 hardened release candidate"`.
2. **Push to Public GitHub Repository:**
   - Push repository to public GitHub repository URL.
3. **Record Video Demo:**
   - Follow `docs/DEMO_SCRIPT.md` (target duration: 2:40–2:50; under 3:00 max).
   - Upload to YouTube / Vimeo as Public / Unlisted (no sign-in required).
4. **Submit on Devpost:**
   - Copy short and long descriptions from `SUBMISSION.md`.
   - Select Alexa+ primary track.
   - Paste video and GitHub repository URLs.
   - Confirm submission before the 11:45 PM IST target buffer.
