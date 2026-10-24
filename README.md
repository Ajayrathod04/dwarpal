# DWARPAL — The Consent & Policy Layer for Consequential AI Actions

> **Amazon Developer Hackathon Submission**  
> *Track: Alexa+ (Simulated Experience & Streamable HTTP MCP Server Route)*  
> *AWS Builder mini-challenge: Not claimed (honest disclosure: no live AWS Verified Permissions or Bedrock resources configured).*  
> *"Before an assistant acts, DWARPAL proves what was requested, who approved it, and what scope is allowed."*

---

## 1. What is DWARPAL?

AI assistants are rapidly advancing from answering questions to coordinating consequential actions across physical and digital spaces—such as scheduling home repairs, granting contractor entry, or dispatching services. A standard single-turn chatbot or unconstrained agent tool loop frequently obscures the boundary between a user's initial intent and the irreversible real-world actions the system is authorized to execute.

**DWARPAL** solves this by establishing a deterministic, fail-closed action governance gateway. Before an action takes place:
1. **Context & Intent:** DWARPAL reads the case context and records a maintenance proposal without external dispatch.
2. **Canonical Integrity Binding:** The exact proposed action, target door, scope (1 entry, 15 minutes max), and reason are serialized into canonical JSON and bound to a deterministic SHA-256 digest (`dwarpal-plan-v1`).
3. **Explicit Human Gate:** The system halts at an explicit human approval gate. Any change in the plan fields changes the hash and fails closed.
4. **Explainable Risk Assessment:** A rules-based, deterministic assessment details risk levels (`LOW`, `ELEVATED`, `HIGH`), machine-readable reason codes, and recommended next steps.
5. **Scoped Access Preview:** If and only if all policy conditions are met (resident role, simulated identity evidence, explicit homeowner approval, and valid plan digest), a narrow single-entry/15-minute access-scope preview is returned. No physical lock is ever operated in this demo.
6. **Structured Audit Receipts:** Every evaluation, approval, replay attempt, and denial is logged to an append-oriented SQLite store with unique event IDs, correlation IDs, reason codes, and UTC timestamps.

---

## 2. Key Features

- **7-Stage Lifecycle State Machine (P1.1):**
  1. `CASE_CONTEXT_LOADED`
  2. `MAINTENANCE_PROPOSAL_CREATED`
  3. `PLAN_PREVIEW_READY`
  4. `AWAITING_HOMEOWNER_APPROVAL`
  5. `POLICY_EVALUATED`
  6. `ACCESS_SCOPE_PREVIEWED / DENIED`
  7. `AUDIT_RECEIPT_READY`
- **Canonical Plan Hashing & Replay Protection (P0.2):**
  - Uses `hmac.compare_digest` for constant-time hash comparison.
  - Server recomputes canonical digest from the persisted plan to detect internal database tampering.
  - Atomic database transition prevents race conditions and rejects replay attempts (`ALREADY_FINALIZED`).
  - 10-minute expiry window enforced server-side.
- **Explainable Risk Assessment (P1.2):**
  - Deterministic evaluation of action sensitivity, identity evidence, and approval state. No unvalidated ML scores.
- **Bounded Scenario Presets (P1.3):**
  - **Safe Approved Path:** Valid case, proposal, simulated identity present, exact hash match -> `APPROVED_SIMULATED`.
  - **Missing Approval Gate:** Missing identity -> `DENIED` (`MISSING_IDENTITY_EVIDENCE`).
  - **Tampered Plan Hash:** Mismatched hash -> `HASH_MISMATCH` / `PLAN_TAMPERED`.
  - **Replay Prevention:** Double submission -> `ALREADY_FINALIZED`.
- **Decision Provenance Panel (P1.4):**
  - "Why did DWARPAL decide this?" panel tracing source Case ID, proposal action, canonical hash, policy reason code, engine, and audit receipt ID.
- **Architecture & Trace Transparency (P1.5):**
  - In-app interactive architecture view detailing live, simulated, and unconfigured layers.
- **Dual MCP SDK Support (P2.1):**
  - Compatible with both MCP v1.x (`FastMCP`) and v2.x (`MCPServer`) with Streamable HTTP mounted at `/mcp`; external client connection and tool invocation verified (`protocol 2025-11-25`).

---

## 3. Architecture

```text
Browser Simulator / MCP Client
              |
              v
FastAPI Application (Port 8000)
  + Lifespan Session Manager
  + MCP Streamable HTTP Endpoint (/mcp)
  + Static Neo-Brutalist Web UI (/)
              |
              +--> Action Catalog (3 Guarded Tools)
              |      - get_case_status (read-only, role-checked)
              |      - propose_maintenance_action (intent only, no dispatch)
              |      - request_access (fail-closed, 15-min scope preview)
              |
              +--> Policy Adapter
              |      +--> Local Deterministic Policy (default, verified)
              |      +--> Amazon Verified Permissions IsAuthorized (optional)
              |
              +--> Workflow & Plan Store (SQLite, canonical SHA-256 digest)
              |
              +--> Structured Audit Store (SQLite, append-oriented)
              |
              +--> Optional Strands / Amazon Bedrock Agent Adapter
```

---

## 4. Run Locally

Requires Python 3.11+.

```bash
# Clone or enter project directory
cd d:/DWARPAL

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install base dependencies
pip install -r requirements.txt

# (Optional) Install MCP SDK support
pip install -r requirements-mcp.txt

# Copy environment configuration
copy .env.example .env    # Windows PowerShell / CMD
# cp .env.example .env    # macOS / Linux

# Start the application
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` in any browser.  
Inspect `/api/health` at `http://127.0.0.1:8000/api/health`.

### Live Deployment
- **Public Demo URL:** [https://dwarpal-neon.vercel.app](https://dwarpal-neon.vercel.app)
- **Live Health Endpoint:** [https://dwarpal-neon.vercel.app/api/health](https://dwarpal-neon.vercel.app/api/health)
*(Deployed on Vercel; uses ephemeral serverless SQLite storage in `/tmp`).*

---

## 5. Automated Verification & Test Suite

Run the full automated test suite (24 tests covering API, policy, security, lifecycle, presets, and audit verification):

```bash
# Verify Python compilation
python -m compileall -q app tests

# Run all 24 pytest tests
python -m pytest -q

# Verify JavaScript syntax
node --check app/static/app.js
```

### Test Results in Current Workspace:
- Compilation: **0 errors**
- Pytest: **24 passed in 13.20s**
- Node Syntax: **Clean exit code 0**
- Browser UI Session: **100% verified via automated browser testing (0 console errors)**

---

## 6. Safety Boundaries & Honest Disclosures

1. **Simulation Only:** DWARPAL is an action-governance prototype. It does **not** unlock physical doors, operate smart locks, contact real contractors, or dispatch emergency services.
2. **Demo Persona Inputs:** Browser checkboxes (`verified_identity`, `homeowner_approved`) are simulated demo persona controls, not cryptographic authentication or OAuth/OIDC tokens.
3. **Audit Log Persistence:** SQLite demo storage is local and append-oriented, not tamper-proof or multi-tenant production storage.
4. **Cloud Adapters:** Amazon Verified Permissions and Amazon Bedrock adapters are provided in source code as integration points but are marked **not configured** because no live AWS account resources were connected. The AWS Builder mini-challenge is therefore not claimed.
5. **Typeface Attribution:** The interface uses **Archivo Black** and **Space Grotesk** (open-source Google Fonts) inspired by bold neo-brutalist campaign design. The proprietary Spotify Mix font is not bundled or used.

---

## 7. Submission Materials Checklist

- **`SUBMISSION.md`**: Devpost submission description and track disclosure.
- **`docs/EXECUTION_REPORT.md`**: Baseline, test run outputs, and release gate verification.
- **`docs/ARCHITECTURE.md`**: Threat model, trust boundaries, and security invariants.
- **`docs/TECHNICAL_REPORT.md`**: Problem statement, architecture, evaluation plan, and limits.
- **`docs/DEMO_SCRIPT.md`**: Under-3-minute video recording walkthrough script.
- **`docs/PRODUCT_FEEDBACK.md`**: Honest observations on tools used (FastAPI, Python, MCP SDK, SQLite).
- **`docs/FRICTION_LOG.md`**: Real friction encountered during build.
- **`docs/FINAL_CHECKLIST.md`**: Step-by-step submission verification checklist.
- **`LICENSE`**: MIT License.
