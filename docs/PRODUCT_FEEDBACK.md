# Product Feedback — Amazon Developer Hackathon

This document provides honest, detailed product feedback for each tool, API, and SDK actually used in building DWARPAL. In accordance with hackathon rules, integrations that were not actively configured (e.g., live Amazon Verified Permissions and Amazon Bedrock calls) are excluded.

---

### 1. Model Context Protocol (MCP) Python SDK (v1.x & v2.x)

1. **What did you use it for?**
   - Mounting a self-hosted Streamable HTTP server at `/mcp` in FastAPI to expose three guarded tools (`get_case_status_tool`, `propose_maintenance_action_tool`, `request_access_tool`) conforming to the Alexa+ 2025-11-25+ protocol specification.
2. **What worked well?**
   - The `@mcp.tool()` decorator makes registering callable Python functions and auto-generating tool schemas straightforward. The `streamable_http_app()` helper cleanly produces a Starlette application mountable directly onto FastAPI.
3. **What was confusing or limited?**
   - Between `mcp` 1.x and 2.x, `FastMCP` was renamed to `MCPServer`, and `StreamableHTTPSessionManager.run()` can only be called once per instance. In test suites where `TestClient(app)` is instantiated multiple times, the lifespan hook raises a `RuntimeError` unless guarded (`_has_started` check). Additionally, `streamable_http_app()` defaults its internal path to `/mcp`, which caused a path duplication (`/mcp/mcp`) when mounted at `/mcp` unless `streamable_http_path="/"` is explicitly passed.
4. **What documentation/onboarding would help?**
   - A dedicated guide on mounting FastMCP / MCPServer as a sub-application within existing FastAPI/Starlette applications, including recommended lifespan patterns for multi-test test runners.
5. **Would you use it again, and why?**
   - Yes. The ability to expose deterministic, policy-checked tools via Streamable HTTP makes it a robust standard for agentic tool governance.

---

### 2. FastAPI & Starlette

1. **What did you use it for?**
   - Serving the core REST API (`/api/workflow`, `/api/preset`, `/api/access`, `/api/health`, `/api/audit`), managing sub-application lifespans, and serving static assets for the browser simulation.
2. **What worked well?**
   - Pydantic v2 integration provides immediate schema validation and bounds checking. The `@asynccontextmanager` lifespan design allows clean startup and teardown of background task groups.
3. **What was confusing or limited?**
   - Mounted Starlette sub-applications do not automatically trigger their own lifespan events when mounted to a parent FastAPI application; developers must explicitly invoke the sub-app's session manager inside the parent lifespan.
4. **What documentation/onboarding would help?**
   - Official documentation callouts highlighting that mounted sub-apps require manual lifespan forwarding in ASGI.
5. **Would you use it again, and why?**
   - Yes. FastAPI is lightweight, standards-compliant, and well-suited for high-throughput policy gateways.

---

### 3. SQLite3 (Standard Library)

1. **What did you use it for?**
   - Persisting workflow plans, canonical hashes, single-use approval states, and structured audit receipts.
2. **What worked well?**
   - Zero-configuration local storage that is easy to inspect and reset during development. Atomic SQL statements (`UPDATE ... WHERE run_id = ? AND status = 'AWAITING_HUMAN_APPROVAL'`) allow robust single-use transition guarantees without external distributed locks.
3. **What was confusing or limited?**
   - SQLite file locking on Windows requires disciplined connection closing to avoid file access locks during test teardown. It is also not tamper-proof for enterprise compliance.
4. **What documentation/onboarding would help?**
   - Best-practice guidance on lightweight append-only hashing schemas for local audit logs.
5. **Would you use it again, and why?**
   - Yes for local prototypes, development sandboxes, and edge devices; no for multi-tenant production compliance (where Amazon CloudWatch/CloudTrail and DynamoDB are appropriate).

---

### 4. Pytest & Starlette TestClient

1. **What did you use it for?**
   - Executing the 24-test automated test suite covering policy fail-closed behavior, plan tampering, expiry, replay rejection, API schemas, and audit ordering.
2. **What worked well?**
   - In-memory HTTP dispatch without spinning up network ports makes test execution fast (24 tests in ~13 seconds). `monkeypatch` and `tmp_path` fixtures ensure test isolation.
3. **What was confusing or limited?**
   - Running repeated `with TestClient(app):` blocks triggers the FastAPI lifespan on each test, which uncovered the MCP singleton session manager re-initialization issue.
4. **What documentation/onboarding would help?**
   - Recommendations on managing singleton lifecycle state across parameterized pytest runs.
5. **Would you use it again, and why?**
   - Yes. Essential for establishing regression confidence and verifying security boundaries.
