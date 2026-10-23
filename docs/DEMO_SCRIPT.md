# Under-3-Minute Video Demo Script — DWARPAL

> **Event:** Amazon Developer Hackathon  
> **Track:** Alexa+ (Simulated Experience & Streamable HTTP MCP Route)  
> **Target Duration:** 2:40 – 2:50 (Strictly under 3:00, English, public link without login)  
> **Format:** Continuous live application screen recording with voiceover (no slides-only presentation)

---

### 0:00 – 0:12 · Hook
- **On Screen:** Hero landing page (`http://127.0.0.1:8000`). Large display typography: *BEFORE AI ACTS. MAKE IT PROVE THE HANDOFF.* Visible status badge: `SIMULATED HOME-SERVICE WORKFLOW`.
- **Voiceover:**  
  *“AI assistants can coordinate real-world tasks. But before an action affects a home, we need to know exactly what was requested, what was approved, and what scope is permitted. This is DWARPAL.”*

---

### 0:12 – 0:35 · Case Context & Maintenance Proposal
- **On Screen:** Scroll to the interactive Action Orchestration section. Select `CASE-1042: Leaking kitchen sink`. Click **PREPARE EXACT PLAN**.
- **Visuals:** The 7-step vertical timeline activates. Steps 1, 2, and 3 turn green (`CASE_CONTEXT_LOADED`, `MAINTENANCE_PROPOSAL_CREATED`, `PLAN_PREVIEW_READY`). Step 4 shows `PENDING` (`AWAITING_HOMEOWNER_APPROVAL`).
- **Voiceover:**  
  *“One homeowner request begins the flow: DWARPAL reads the fictional service ticket, records a maintenance proposal without external dispatch, and computes a unique workflow run ID and plan preview. Execution halts immediately at a human approval gate.”*

---

### 0:35 – 1:00 · Exact-Plan Integrity Binding (Tamper Test)
- **On Screen:** Highlight the **CANONICAL SHA-256 INTEGRITY BINDING** card displaying the hexadecimal hash. Click the **TAMPER TEST (ALTER HASH)** button (or Scenario C preset).
- **Visuals:** The server evaluates the request, detects the hash mismatch, and immediately marks Step 5 as `COMPLETED (DENY)` and Step 6 as `BLOCKED`. The Provenance panel shows `× ACCESS REQUEST DENIED [HASH_MISMATCH]`.
- **Voiceover:**  
  *“The approval is bound to a canonical JSON digest of the exact action, door, and 15-minute scope. If an assistant or compromised process alters a single field or hash, the server detects the tampering and fails closed.”*

---

### 1:00 – 1:25 · Human Approval Gate (Missing Evidence Failure)
- **On Screen:** Click Scenario B: **RUN GATE SCENARIO** (or prepare a fresh plan with simulated identity unchecked, then click Approve).
- **Visuals:** Provenance displays `× ACCESS REQUEST DENIED` with reason code `[MISSING_IDENTITY_EVIDENCE]`. The Explainable Risk Assessment displays `ELEVATED` risk with recommended next step `VERIFY_IDENTITY_DEMO`.
- **Voiceover:**  
  *“Even with homeowner consent, resident entry requires verified identity evidence. Here, simulated evidence is absent. DWARPAL halts at the gate, logs the denial reason, and explains what is required before proceeding.”*

---

### 1:25 – 1:55 · Safe Allowed Simulation (Narrow Scope Preview)
- **On Screen:** Click Scenario A: **RUN SAFE SCENARIO** (or prepare plan, check Simulated Identity, and click Approve).
- **Visuals:** All 7 timeline steps complete in green. The Provenance panel updates to `✓ ACCESS SCOPE PREVIEW ALLOWED [APPROVED_SIMULATED]`. The scope preview confirms: `FRONT-01 · 1 entry · 15 minutes · preview only`.
- **Voiceover:**  
  *“When all required demo conditions match and the exact plan hash is approved, DWARPAL returns a narrow, single-entry 15-minute access preview. Importantly, this is a deterministic simulation: no physical lock is unlocked, and no contractor is contacted.”*

---

### 1:55 – 2:20 · Structured Audit Receipts & Replay Protection
- **On Screen:** Click **RUN REPLAY SCENARIO** to show immediate rejection as `ALREADY_FINALIZED`. Then scroll down to **SHOW ME THE RECEIPTS** and click **REFRESH LOG ↻**.
- **Visuals:** The SQLite audit table displays rows with UTC timestamps, event types (`CASE_READ`, `PROPOSAL_CREATED`, `APPROVAL_REQUIRED`, `APPROVAL_ACCEPTED`, `APPROVAL_REPLAY_REJECTED`), decision chips, and reason codes. Reload the page to prove persistence.
- **Voiceover:**  
  *“Approval tokens are strictly single-use; any replay attempt is rejected immediately. Every evaluation writes an append-oriented receipt with event IDs, correlation IDs, and policy reasons into local SQLite storage, persisting across reloads.”*

---

### 2:20 – 2:40 · Architecture & Honest Disclosures
- **On Screen:** Scroll to the **HOW IT WORKS** trace section. Highlight the Client -> Gateway -> Policy -> Store -> Audit flow. Point to the status panel in the hero.
- **Voiceover:**  
  *“DWARPAL implements a self-hosted Streamable HTTP MCP server at slash mcp alongside this web simulation. In the spirit of complete hackathon transparency: our local deterministic policy and plan binding are fully verified. Cloud adapters for Amazon Verified Permissions and Bedrock are present in code, but honestly disclosed as unconfigured without live AWS resources.”*

---

### 2:40 – 2:50 · Closing
- **On Screen:** Return to hero view showing the DWARPAL brand mark and value proposition.
- **Voiceover:**  
  *“DWARPAL makes the boundary visible before an assistant acts: the request, the approval, the permitted scope, and the audit trail. Thank you.”*
