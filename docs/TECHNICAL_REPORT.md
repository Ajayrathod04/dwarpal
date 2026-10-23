# DWARPAL Technical Report

## 1. Problem Definition & Research Context
Conversational AI assistants (including Alexa+ and tool-using LLM agents) increasingly coordinate tasks that carry significant real-world consequence—from reading household maintenance tickets to unlocking physical entry doors for third-party contractors. Conventional architectures suffer from three critical safety shortcomings:
1. **Unbounded Intent-Action Coupling:** Natural language intent is often converted directly into tool invocations without an explicit, inspectable intermediate authorization gate.
2. **Lack of Cryptographic Plan Binding:** When an assistant presents a plan to a user for confirmation, the subsequent execution phase often relies on simple boolean flags rather than verifying that the executed parameters match the exact approved plan.
3. **Opaque Provenance:** When actions fail or succeed, audit receipts are either omitted or scattered, making post-incident forensic attribution impossible.

---

## 2. Technical Approach & Innovations

### 2.1 Deterministic Fail-Closed Policy Engine
DWARPAL implements a deterministic policy layer that evaluates every proposed tool call against a strict specification before execution. Role authorization, required intent rationales, and dual-condition requirements (identity evidence + explicit homeowner consent) are enforced server-side.

### 2.2 Canonical JSON Plan Hashing (`dwarpal-plan-v1`)
To ensure plan integrity:
- Plan parameters (case ID, request, target door, proposed action, time window, max entries, mode) are serialized into canonical JSON with sorted keys and UTF-8 encoding.
- A deterministic SHA-256 digest is generated upon preview creation and persisted in SQLite.
- Upon approval submission, the server retrieves the persisted plan, recomputes the canonical digest, and compares it to the client-submitted hash using `hmac.compare_digest`.
- If a single character, entry count, or time window has been altered, the server refuses approval with `HASH_MISMATCH` / `PLAN_TAMPERED`.

### 2.3 Atomic Single-Use Lifecycle State Transitions
Approval tokens are single-use. The server performs an atomic database state update:
```sql
UPDATE workflow_previews
SET status = ?, result_json = ?
WHERE run_id = ? AND status = 'AWAITING_HUMAN_APPROVAL';
```
If a request is replayed, or if concurrent requests attempt double-finalization, only one succeeds; subsequent attempts receive an immediate `ALREADY_FINALIZED` denial and log an `APPROVAL_REPLAY_REJECTED` event.

### 2.4 Dual MCP SDK Server Architecture
DWARPAL supports both MCP specification lines:
- v1.x (`FastMCP`)
- v2.x (`MCPServer`)
Mounted at `/mcp` using Streamable HTTP with session management hooked into FastAPI's lifespan context.

---

## 3. Evaluation & Experimental Results

The project was evaluated through an automated test suite across 24 test cases, regression testing, and live browser automation.

| Evaluation Dimension | Test Target | Result | Evidence |
|---|---|---|---|
| **Fail-Closed Authorization** | Unknown role, unknown action, missing rationale | **100% Denied** | `test_unknown_role_fails_closed`, `test_unknown_action_fails_closed` |
| **Dual-Condition Gate** | Identity without approval, approval without identity | **100% Denied** | `test_identity_without_homeowner_approval_is_denied`, `test_visitor_access_denied` |
| **Integrity & Tamper Detection** | Modified plan content in database, mismatched hash | **100% Caught** | `test_plan_tampering_detected`, `test_approved_workflow_returns_scoped_preview_but_never_executes` |
| **Replay Protection** | Duplicate approval submission with identical hash | **100% Rejected** | `test_workflow_preview_requires_separate_one_time_approval`, `test_preset_scenarios_all_pass` |
| **Expiry Window Enforcement** | Plan approval attempted after 10-minute window | **100% Expired** | `test_expired_workflow_rejected` |
| **Structured Audit Logging** | Event IDs, correlation IDs, reason codes, sanitization | **100% Appended** | `test_audit_event_ordering_and_fields`, `test_access_denial_and_allow_are_audited` |
| **Browser UI & Console** | End-to-end interactive flow across all 4 presets | **Zero Errors** | Live browser subagent run; WebP video artifact captured |

---

## 4. Limitations & Future Work

1. **Identity Provider Integration:** The current demo uses a resident persona checkbox to simulate identity verification. In production, this would integrate with AWS Cognito, Passkeys (WebAuthn), or an OpenID Connect identity provider.
2. **Distributed Audit Storage:** SQLite demo storage is local and append-oriented. Production deployments should stream audit events to AWS CloudTrail / CloudWatch Logs with AWS KMS encryption and retention policies.
3. **Live Amazon Verified Permissions:** The codebase includes an AVP adapter mapping Cedar context entities. Future work would deploy an active policy store in AWS to test cross-region latency and Cedar schema evolution.
