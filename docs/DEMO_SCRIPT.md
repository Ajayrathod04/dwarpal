# Under-3-minute demo script — DWARPAL

**Target runtime: 2:40. Record the actual running application, not slides alone.** This script is for the simulated Alexa+-style web experience path. Do not claim native Alexa+ integration, a live MCP endpoint, or live AWS integration unless you actually verify those separately.

**0:00–0:18 — Hook**
Screen: hero landing page.
Say: “AI assistants are moving from answers to actions. In a home, a request to arrange a repair can turn into a contractor visit and a request for entry. DWARPAL shows the boundary between intent, approval, and action.”

**0:18–0:55 — Run the three-step workflow**
Screen: multi-step orchestration panel. Keep simulated identity unchecked. Click **PREPARE EXACT PLAN**.
Say: “One request prepares three steps: read the fictional service case, create a maintenance proposal, and pause for approval. The server persists a preview with a SHA-256 hash over the exact case, request, proposed action, door and scope. Nothing grants access yet.”

**0:55–1:20 — Prove denial and no replay**
With simulated identity unchecked, click **APPROVE THIS PLAN**. Show the denial, then point out that the same preview is finalized and cannot be replayed.
Say: “A separate approval click is not enough by itself: the simulated identity condition is also required. This preview is one-time, and a failed attempt cannot be replayed. The identity input is a demo control, not real authentication.”

**1:20–1:45 — Show the allowed preview**
Prepare a new exact plan, check “Simulated identity evidence”, then click **APPROVE THIS PLAN**. Show the one-entry/15-minute preview.
Say: “The approval is bound to the exact plan hash. When the demo identity condition is present, the system returns a narrowly scoped preview—but still does not operate a physical lock or contact a contractor.”

**1:45–2:10 — Audit receipt**
Refresh the audit trail. Show allow and deny records.
Say: “Each tool call leaves a receipt with the principal, action, resource, policy result, reason and timestamp. This local SQLite log persists for the demo, but it is not tamper-proof production audit storage.”

**2:10–2:40 — Honest close**
Show the health endpoint and README.
Say: “DWARPAL is a simulated Alexa+-style experience. The optional MCP server and AWS adapters are in the source, but they are not claimed as verified unless the live tests succeed. The core contribution is the approval-aware workflow and visible safety boundary.”

## Recording checks
- Public YouTube or Vimeo link, English, strictly under 3 minutes.
- Show the actual running application and real interactions.
- Do not show secrets, AWS keys, private data, copyrighted music, or unlicensed footage.
- If the app health endpoint reports `mcp_sdk_available: false`, present the web simulation path, not an MCP-server claim.
- If AWS integrations are not configured and verified, do not show fake console activity or claim the AWS Builder mini-challenge.
