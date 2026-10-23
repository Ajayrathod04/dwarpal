# Friction log — preparation-environment observation (verify before submission)

**Do not submit this entry as your own unless you personally encountered the same issue.** It records a failure in the isolated preparation environment. The hackathon bonus depends on honest, specific friction from the participant's actual workflow.

## F-001 — MCP SDK installation blocked by environment network resolution

- **Task attempted:** Install the optional MCP requirements (`requirements-mcp.txt`) so the MCP Streamable HTTP server could be started and tested.
- **Steps:** Ran `python -m pip install -q -r /mnt/data/dwarpal/requirements.txt` in the preparation environment.
- **Expected:** pip downloads and installs the `mcp` package and dependencies.
- **Actual:** repeated `Temporary failure in name resolution` errors; pip reported that no matching distribution could be found because it could not reach the package index.
- **Severity:** High for verifying the MCP track path; low for the browser-simulation path.
- **Workaround used:** made the browser simulator and REST API runnable without the MCP SDK, and changed `/api/health` to report `mcp_sdk_available: false` and omit the MCP endpoint instead of implying it works.
- **Actionable suggestion:** provide an offline dependency cache or a clear dependency-install diagnostic in developer setup instructions; keep the SDK version pinned to a documented protocol-compatible release line.
- **Evidence:** local terminal output from the attempted pip install; the app health endpoint reported `mcp_sdk_available: false`.
