# Product feedback — complete only with observations you actually made

This file records the tools used in the prepared local prototype. Before submitting, review it against your own development experience and remove or correct anything that does not match what you personally observed. Do not claim feedback for an SDK/API that you did not successfully use.

| Tool / API | What was actually used | Observed strengths | Observed limitations / friction | Would I use it again? |
|---|---|---|---|---|
| Python 3.13 | Application logic and policy tests | Fast iteration; clear separation of policy, service logic and persistence | Dependency installation can be blocked by the environment's network configuration | Yes |
| FastAPI | Local REST API and serving the browser app | Minimal route definitions; automatic request validation; easy local testing through TestClient | A route test alone does not validate external services or deployed behavior | Yes |
| SQLite | Local audit-event persistence | No separate service required; easy to inspect and reset during demos | Local file is not tamper-proof, managed, multi-user production audit storage | Yes for a local prototype; not for production audit requirements |
| MCP Python SDK | Optional extra (`requirements-mcp.txt`); not installed in the preparation environment because package installation failed with DNS/network resolution errors | Not evaluated in this environment | No successful SDK installation, MCP client connection, tool discovery or tool call has been verified here | Re-evaluate after a successful install and live MCP smoke test |
| Amazon Verified Permissions | Optional adapter is present in code but no live policy store was configured or invoked | Not evaluated | No AWS integration has been verified; schema and Cedar policies must match a real policy store | Re-evaluate after a live allow/deny test |
| Amazon Bedrock / Strands | Optional adapter is present but disabled | Not evaluated | No model invocation, latency, quality, or cost was measured | Re-evaluate only if configured and tested |

## Submission instruction

Use this as a starting record, not a substitute for the participant's own feedback. In the Devpost form, describe the actual onboarding experience, what worked, what needs improvement, and whether you would build with each tool again. For untested integrations, say they were not tested rather than inventing positive or negative feedback.
