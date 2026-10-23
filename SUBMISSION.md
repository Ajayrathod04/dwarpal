# Devpost Submission Pack — DWARPAL

## 1. Project Title
**DWARPAL — The Consent & Policy Layer for AI Actions**

## 2. Short Description
DWARPAL is an action-governance gateway for AI assistants. Before an assistant acts, DWARPAL proves what was requested, who approved it, and what scope is allowed. It orchestrates case lookup, maintenance proposals, canonical SHA-256 plan integrity binding, an explainable risk assessment, an explicit human approval gate, and structured audit receipts.

## 3. Long Description
### The Problem
As AI assistants transition from answering queries to executing real-world consequential tasks (e.g., booking repairs, granting contractor entry, dispatching services), single-turn interfaces obscure the boundary between a user's conversational intent and the physical actions the system is authorized to perform. Without explicit policy checks, integrity bindings, and human-in-the-loop review, assistants risk executing unauthorized actions, exceeding permitted scopes, or lacking auditable provenance.

### The Solution: DWARPAL
DWARPAL introduces a deterministic, fail-closed policy gateway that governs assistant actions before execution:
1. **Case Context & Maintenance Intent:** Reads fictional service cases with role checks (`get_case_status`) and records maintenance proposals (`propose_maintenance_action`) without external dispatch.
2. **Canonical Plan Integrity Binding:** Serializes the exact proposed action, target door, scope (1 entry, 15 minutes max), and intent into canonical JSON (`dwarpal-plan-v1`), generating a SHA-256 digest.
3. **Explainable Risk Assessment:** Evaluates physical entry sensitivity, approval status, and identity evidence deterministically, outputting risk levels (`LOW`, `ELEVATED`, `HIGH`), explicit reason codes, and recommended next steps.
4. **Explicit Human Gate & Replay Protection:** Halts execution until explicit homeowner approval is submitted. The server validates the canonical digest against the persisted plan, enforces a 10-minute validity window, and atomically finalizes the state to prevent double-execution or replay.
5. **Scoped Access Preview:** Returns a narrow 15-minute, single-entry preview only when simulated resident identity and homeowner approval conditions are met. (No physical lock is operated; all devices are simulated).
6. **Structured Audit Receipts:** Logs every read, proposal, approval, replay attempt, and denial into an append-oriented SQLite store with unique event IDs, correlation IDs, reason codes, and UTC timestamps.
7. **Interactive 7-Stage Stepper & Presets:** The UI features an interactive 7-step vertical timeline stepper, 4 one-click scenario presets, and a provenance panel explaining why every decision was made.

## 4. Track Selection
- **Primary Track:** **Alexa+** — Simulated Alexa+-style web experience path with self-hosted MCP Streamable HTTP server mounted at `/mcp`.
- **AWS Builder Mini-Challenge:** **Not Selected / Disclosed as Not Configured** (Honest disclosure: Amazon Verified Permissions and Amazon Bedrock adapters are present in source code but not configured with live AWS account resources).
- **Open Source Mini-Challenge:** Eligible under the hackathon window; published as an open-source MIT repository.

## 5. Technologies Used
- **Backend:** Python 3.14 / 3.11+, FastAPI, Uvicorn, SQLite, Pydantic, HMAC / Hashlib, MCP Python SDK (Streamable HTTP supporting both v1.x and v2.x).
- **Frontend:** Vanilla HTML5, CSS3 (Neo-brutalist / Y2K campaign aesthetic with Google Fonts Archivo Black & Space Grotesk), Vanilla JavaScript.
- **Testing:** Pytest (24 automated tests), Node.js syntax checker, Playwright-compatible browser automation.
- **AI Tooling Disclosure:** Developed in pair programming with Google Antigravity IDE (Agentic Assistant) for codebase scaffolding, test automation, and code hardening.

## 6. What Works & What is Simulated
- **What is Live & Verified:**
  - Deterministic local policy gate (24 automated tests passing).
  - SHA-256 canonical plan integrity binding and tamper detection.
  - Atomic single-use approval transition and replay rejection (`ALREADY_FINALIZED`).
  - 7-step lifecycle state machine and interactive vertical stepper.
  - Explainable rules-based risk assessment.
  - 4 bounded scenario presets (`safe_approved`, `missing_approval`, `tampered_plan`, `replayed_plan`).
  - Structured append-oriented SQLite audit trail.
  - MCP Streamable HTTP endpoint mounted at `/mcp`.
- **What is Simulated:**
  - Homeowner identity evidence (demo persona checkbox).
  - Smart locks and door-access hardware (grant preview only, no physical lock operated).
  - Contractor booking and service provider dispatch (fictional tickets).
- **What is Unconfigured:**
  - Live AWS Verified Permissions policy store (adapter present in code).
  - Amazon Bedrock / Strands live model calls (adapter present in code).
  - Native Alexa+ partner accounts (simulated web route used).

## 7. Submission Artifacts
- **Repository:** Public GitHub Repository (MIT Licensed)
- **Video Demo:** Under 3 minutes, English, demonstrating live app workflow (see `docs/DEMO_SCRIPT.md`).
- **Product Feedback:** See `docs/PRODUCT_FEEDBACK.md`.
- **Friction Log:** See `docs/FRICTION_LOG.md`.
- **Execution Report:** See `docs/EXECUTION_REPORT.md`.
