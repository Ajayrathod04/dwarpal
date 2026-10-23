# DWARPAL Architecture & Threat Model

## 1. Trust Boundaries

```text
Untrusted Zone                  Trusted Application Boundary
┌─────────────────────────┐     ┌─────────────────────────────────────────────────────────┐
│ Browser Client          │     │ FastAPI Gateway (Port 8000)                             │
│ (User claims, checkboxes│────>│ - Request schema validation & input limits              │
│  caller role string)    │     │ - Lifespan session manager (MCP Streamable HTTP /mcp)   │
└─────────────────────────┘     └──────────────────────────┬──────────────────────────────┘
                                                           │
                                                           v
                                ┌─────────────────────────────────────────────────────────┐
                                │ Policy & Integrity Layer                                │
                                │ - Deterministic Local Policy (fail-closed)              │
                                │ - Canonical SHA-256 Digest Recomputation                │
                                │ - Constant-time comparison (hmac.compare_digest)        │
                                │ - Atomic status transition in SQLite                    │
                                └──────────────────────────┬──────────────────────────────┘
                                                           │
                                                           v
                                ┌─────────────────────────────────────────────────────────┐
                                │ Persistence & Receipts (SQLite Local Demo Store)        │
                                │ - workflow_previews (Plan, Hash, Expiry, Status)        │
                                │ - audit (Event ID, Correlation ID, Reason Code, Detail) │
                                └─────────────────────────────────────────────────────────┘
```

1. **Untrusted Client Layer:** Browser clients, form inputs, and caller-supplied roles (e.g. `principal_role`, `verified_identity`, `homeowner_approved`) are untrusted. They are handled as demo simulation controls, not authenticated identity claims.
2. **Server-Side Enforcement:** All authorization checks, hash bindings, expiry validations, and state transitions are enforced server-side. Disabled frontend buttons are not considered authorization gates.
3. **Fail-Closed Default:** Unknown actions, unrecognized roles, missing approvals, hash mismatches, expired windows, or policy engine exceptions always resolve to `DENY`.

---

## 2. Threat Analysis & Mitigations

| Threat | Impact | Server-Side Mitigation in DWARPAL |
|---|---|---|
| **Untrusted Role Injection** | Caller claims `admin` or spoofed role to unlock doors | Server checks against `VALID_ROLES`; `request_access` requires `role == 'resident'`, verified identity evidence, and explicit homeowner approval. Unknown roles return `UNAUTHORIZED_ROLE`. |
| **Plan Modification (Tampering)** | Attendant/assistant modifies scope or target door after preview | Plan is serialized into canonical JSON (`dwarpal-plan-v1`) with sorted keys. The SHA-256 digest is checked with `hmac.compare_digest`. The server recomputes the digest from the stored plan before finalization. Any discrepancy yields `HASH_MISMATCH` / `PLAN_TAMPERED`. |
| **Replay & Double Finalization** | Attacker resubmits a previously approved token/run | Database update uses `WHERE run_id = ? AND status = 'AWAITING_HUMAN_APPROVAL'`. If already finalized, `rowcount == 0` and the request is rejected with `ALREADY_FINALIZED` and logged as `APPROVAL_REPLAY_REJECTED`. |
| **Stale Approval Window** | Plan approved hours or days later without context | Server computes `age_seconds` from creation timestamp; previews expire after 600 seconds (10 minutes) with reason code `EXPIRED`. |
| **Timing Attacks on Digest** | Timing discrepancy reveals hash bytes | `hmac.compare_digest` is used for constant-time comparison of action hashes. |
| **Credential / Secret Leakage in Logs** | API tokens or credentials written to SQLite logs | Audit details pass through `_sanitize_details`, automatically redacting keys containing `password`, `token`, `secret`, `key`, `auth`, `credential`, or `private`. |
| **Cloud Adapter Failure Open** | AWS AVP or Bedrock unavailability falls back to allow | Exceptions in the AVP adapter are caught and explicitly return `allowed=False`, `reason_code='ENGINE_EXCEPTION'`, ensuring fail-closed safety. |

---

## 3. 7-Stage Lifecycle State Machine

1. **`CASE_CONTEXT_LOADED`**: Fictional maintenance case lookup with reader role check.
2. **`MAINTENANCE_PROPOSAL_CREATED`**: Proposal recorded with rationale; no external dispatch.
3. **`PLAN_PREVIEW_READY`**: Canonical JSON constructed and bound to SHA-256 action hash.
4. **`AWAITING_HOMEOWNER_APPROVAL`**: Workflow halts for human review; status locked in database.
5. **`POLICY_EVALUATED`**: Fail-closed authorization checks simulated identity and consent.
6. **`ACCESS_SCOPE_PREVIEWED / DENIED`**: Returns narrow 1-entry/15-minute preview or explicit denial.
7. **`AUDIT_RECEIPT_READY`**: Immutable receipt appended to local demo SQLite store.

---

## 4. Honest Architectural Disclosures

- **Local SQLite Store:** Append-oriented demo storage. Not tamper-proof or multi-tenant production storage. Production implementations would require managed identity (OIDC/Cognito), Amazon CloudWatch, CloudTrail, KMS, and durable distributed stores.
- **Simulated Hardware:** Smart locks, door hardware, and contractor dispatch are strictly simulated. No physical lock is unlocked.
- **Cloud Adapters:** Amazon Verified Permissions and Amazon Bedrock adapters are provided in source code but are marked unconfigured in the default deployment.
