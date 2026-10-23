# DWARPAL — The consent layer for AI actions

**Primary target: Alexa+ simulated-experience path**

AWS Builder mini-challenge is conditional on a verified live AWS integration.  
*Every action has a boundary. Every decision leaves a trail.*

DWARPAL is a local-first prototype for safer agent actions. Its primary submission path is the explicitly permitted **simulated Alexa+-style web experience**. The source also contains an optional MCP Streamable HTTP server that is mounted only when the MCP SDK is installed; that endpoint has not been verified in this preparation environment. Every proposed action passes a policy decision before it can execute. The UI makes the decision, policy reason, and audit trail visible.

> **Honesty note:** local demo mode uses a deterministic policy simulator and fictional sample data. AWS Verified Permissions and Amazon Bedrock/Strands integrations are optional and only count as real AWS integration after you configure credentials/resources and verify the live calls. This repository does not claim native Alexa+ partner integration. The demo experience is a self-contained web simulation; do not claim a working MCP server unless `/api/health` reports `mcp_sdk_available: true` and a compatible MCP client successfully lists and calls the tools.

## Why this is different

Most demos show an agent completing a task. DWARPAL shows **whether it should be allowed to complete the task, why, and what evidence was recorded**. The core product is not a chatbot: it is an action gateway with explicit policy evaluation, safe defaults, human escalation, and an append-only local audit trail.

### Demo scenarios
1. **Multi-step orchestration:** one homeowner request prepares a case lookup, a maintenance proposal, and a pending approval gate in sequence; the approval is separately bound to a persisted plan hash and is single-use in the demo.
2. **Approval gate:** without both simulated identity evidence and explicit homeowner approval, access is denied and the workflow stops at human review. After a separate approval click, the app checks the exact plan hash and returns a one-entry / 15-minute access-scope preview—but does not enforce it on any real device.
3. **Proposal, not execution:** a home-service visit is proposed, but no contractor is contacted and no lock is operated.
4. **Persistent audit:** reload the page and inspect the SQLite-backed event trail from previous demo actions.

## Architecture

```text
Browser simulator / MCP client
          |
          v
FastAPI app + simulated Alexa+-style web experience
          + optional MCP Streamable HTTP endpoint (/mcp) when SDK is installed
          |
          +--> action catalog (three guarded tools)
          +--> policy adapter
          |      +--> local deterministic demo policy (default)
          |      +--> Amazon Verified Permissions IsAuthorized (optional)
          +--> audit store (SQLite, local)
          +--> optional Strands / Bedrock agent adapter
```

### Intended tools exposed over MCP (only when the SDK is installed)
- `get_case_status(case_id)` — read-only, allowed only for the fictional demo homeowner/support roles.
- `propose_maintenance_action(case_id, action, rationale)` — creates a proposal; never dispatches a real service.
- `request_access(principal_role, door_id, reason, verified_identity, homeowner_approved)` — policy-checked simulation; both identity evidence and explicit approval are required for the resident allow-path.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
# Optional: install MCP server support (only if you want to test the MCP path)
pip install -r requirements-mcp.txt
# Optional: AWS adapter dependencies
# pip install -r requirements-aws.txt
copy .env.example .env  # Windows; on macOS/Linux use cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Health: http://127.0.0.1:8000/api/health. The `/mcp` endpoint exists only after installing `requirements-mcp.txt` and verifying the health response.

The UI and policy simulator work without cloud keys. The base requirements intentionally do not install the optional MCP SDK. `/api/health` reports `mcp_sdk_available: false` until `requirements-mcp.txt` is installed; this does **not** count as a verified MCP server. For a quick local test:
```bash
pytest -q
```

## MCP client example

Configure a compatible MCP client to connect to `http://127.0.0.1:8000/mcp` using **Streamable HTTP**. Client configuration varies by host. The Alexa+ public docs describe Streamable HTTP and MCP spec version 2025-11-25+ as the required transport/version for native integrations. This project implements an MCP server using the official Python MCP SDK; the dependency is constrained to the v1.x SDK line at 1.28+ because that line supports the required 2025-11-25 protocol revision. Still verify the actual endpoint with an MCP client and show a successful tool call before claiming compatibility.

## Optional AWS integrations (do not claim as live until tested)

### Amazon Verified Permissions
1. Create an Amazon Verified Permissions policy store and define an entity schema / Cedar policies matching your principal, action, and resource types.
2. Set `AWS_REGION`, `AVP_POLICY_STORE_ID`, and `AVP_POLICY_ID` in `.env`.
3. Set `POLICY_MODE=aws_avp`.
4. Configure AWS credentials using the normal AWS SDK credential chain.
5. The adapter invokes `IsAuthorized` and fails closed on errors. Check CloudTrail/console and verify an allow and a deny before claiming live AVP use.

This adapter expects a policy store whose schema accepts the `principal`, `action`, and `resource` entities sent in `app/policy.py`; tailor entity type names to your actual Cedar schema. A placeholder policy ID/store ID is not a working setup.

### Amazon Bedrock / Strands
The optional adapter in `app/agent.py` attempts to create a Strands Agent with a Bedrock model when enabled. It is not needed for deterministic local scenarios. Set `ENABLE_STRANDS=true` only after installing the optional package, configuring AWS credentials and model access, and testing an actual invocation. Do not describe it as working unless you have captured real output.

## Judge-proof evidence (must be generated on your machine)

Run these checks and keep the actual outputs/screenshots:

```bash
python -m compileall -q app
pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then open `/api/health`. For the Alexa+ MCP path, verify `mcp_sdk_available: true`, connect a compatible MCP client to `/mcp`, list the tools, and call `get_case_status_tool`. Record the real result. If you cannot do this, submit and describe the project as the **simulated Alexa+-style web experience** path and do not claim MCP endpoint verification.

## Safety and scope
- Fictional case data only; no real resident records.
- The prototype never controls a physical lock, contacts a resident, or dispatches a contractor.
- All external actions are simulated; proposal creation is not execution.
- Local audit trail is a demo SQLite database, not tamper-proof storage.
- A local policy decision is not Amazon Verified Permissions.
- Not a production access-control system.

## Submission checklist
See `SUBMISSION.md`, `docs/DEMO_SCRIPT.md`, `docs/PRODUCT_FEEDBACK.md`, and `docs/FRICTION_LOG.md`. Replace every unverified claim with evidence from your own tests. Publish the repository publicly with this MIT license, record an English video under 3 minutes, and complete product feedback for every tool actually used.

## Important security boundary

The demo deliberately uses fictional, client-selected roles and a simulated identity checkbox so a judge can explore allow/deny cases quickly. This is not an authentication design: a real deployment must derive the principal from a trusted identity provider, validate claims server-side, and never trust role/identity fields supplied by the browser. The optional AVP adapter is a starting point only; its entity schema and policies must match an actual policy store and be tested against real allow/deny cases before any AWS claim.

## Design notes
The visual language takes inspiration from the uploaded references: Spotify campaign-like oversized type, neon gradient, editorial bento cards, and the peach/black neo-brutalist portfolio. The proprietary Spotify Mix typeface is not bundled; the interface uses **Archivo Black** as a close, openly available display substitute with **Space Grotesk** for UI copy. This is a style reference, not a Spotify product or affiliation.
