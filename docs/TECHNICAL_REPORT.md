# DWARPAL technical report

## Problem
AI agents may be able to call tools without making authorization decisions transparent to the user. The project explores a policy boundary between a home-service request and a contractor-entry handoff.

## Approach
A FastAPI application exposes a browser simulation. If the optional MCP SDK is installed, the app mounts its Streamable HTTP application at `/mcp`; the endpoint was not verified in the preparation environment. The multi-step workflow prepares a home-service case lookup and maintenance proposal, persists an approval preview bound to a canonical SHA-256 plan hash, then requires a separate one-time approval attempt before returning a simulated access-scope preview. If the optional MCP SDK is installed, three MCP tools call the same service logic. The policy adapter defaults to a deterministic local simulator and can optionally call Amazon Verified Permissions. Audit events are written to SQLite. A separate optional adapter can call Strands with a Bedrock model.

## Data
Only fictional demo cases are embedded. No personal, private, real home, or device data is collected.

## Evaluation plan
- Verify access is denied unless both simulated identity evidence and explicit homeowner approval are present.
- Verify the three-step workflow pauses for human review by default.
- Verify unknown actions deny by default.
- Verify a case lookup returns a source/evidence note.
- Verify maintenance creates a proposal, not an external action.
- Verify every policy evaluation appears in the audit trail.
- Verify the optional AVP adapter fails closed without a configured policy store and maps boolean context correctly in a mocked SDK test (mocked test is not live AWS evidence).
- If AWS AVP is configured, test one real ALLOW and one real DENY against a known policy store and preserve the actual results.
- If Strands is configured, capture an actual invocation and disclose model/latency/cost context.

## Limitations
This is a prototype, not production access control. The local principal role is caller-supplied; SQLite is not tamper-proof; AWS integration requires resource configuration and testing; native Alexa+ partner integration is not claimed.
