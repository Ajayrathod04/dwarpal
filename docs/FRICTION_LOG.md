# Friction Log — Real Observations Encountered During Build

This friction log contains real technical obstacles encountered during the development, testing, and hardening of DWARPAL in the current workspace.

---

### Friction Item 01: MCP SDK v2.x Class Renaming & Backward Compatibility Break

- **Tool / API:** Model Context Protocol (MCP) Python SDK
- **Exact Action Attempted:** Imported `FastMCP` via `from mcp.server.fastmcp import FastMCP` in an environment where `mcp` 2.1.1 was installed.
- **Expected Result:** `FastMCP` class imported successfully to define server tools and mount Streamable HTTP.
- **Actual Result / Error:**
  ```text
  ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed to MCPServer
  (from mcp.server.mcpserver import MCPServer) and other APIs changed; see the migration guide...
  ```
- **Impact on Build:** The application fell back to `MCP_SDK_AVAILABLE = False`, disabling the `/mcp` mount.
- **Workaround Implemented:** Implemented a robust dual-version import pattern in `app/main.py`:
  ```python
  try:
      from mcp.server.fastmcp import FastMCP
      mcp = FastMCP("dwarpal-action-governance", stateless_http=True, json_response=True)
      MCP_SDK_AVAILABLE = True
  except (ImportError, ModuleNotFoundError):
      try:
          from mcp.server.mcpserver import MCPServer
          mcp = MCPServer("dwarpal-action-governance")
          MCP_SDK_AVAILABLE = True
      except Exception:
          mcp = None
          MCP_SDK_AVAILABLE = False
  ```
- **Evidence:** Terminal output from task checking `from mcp.server.fastmcp import FastMCP`.
- **Suggestion for Developer / SDK Authors:** Provide a compatibility shim in `mcp.server.fastmcp` with a `DeprecationWarning` rather than raising a hard `ModuleNotFoundError` on major version transitions.

---

### Friction Item 02: `StreamableHTTPSessionManager.run()` Cannot Be Re-run Across TestClient Instances

- **Tool / API:** `mcp.server.streamable_http_manager.StreamableHTTPSessionManager`
- **Exact Action Attempted:** Executed multiple pytest tests using `with TestClient(app) as client:` against the FastAPI app.
- **Expected Result:** Each test client enters and exits the FastAPI lifespan context manager cleanly.
- **Actual Result / Error:**
  ```text
  RuntimeError: StreamableHTTPSessionManager .run() can only be called once per instance. Create a new instance if you need to run again.
  ```
- **Impact on Build:** 5 API test cases failed with `RuntimeError` during lifespan startup on subsequent tests.
- **Workaround Implemented:** Guarded the session manager invocation in `app/main.py` lifespan:
  ```python
  if mcp is not None and hasattr(mcp, "session_manager") and not getattr(mcp.session_manager, "_has_started", False):
      try:
          async with mcp.session_manager.run():
              yield
      except RuntimeError:
          yield
  else:
      yield
  ```
- **Evidence:** Pytest failure log from `task-134` trace.
- **Suggestion for Developer / SDK Authors:** Make `StreamableHTTPSessionManager.run()` idempotent or allow graceful re-entry when the previous context manager has exited.

---

### Friction Item 03: Route Prefix Duplication When Mounting Streamable HTTP in ASGI Sub-Applications

- **Tool / API:** `MCPServer.streamable_http_app()`
- **Exact Action Attempted:** Mounted `mcp.streamable_http_app()` at prefix `/mcp` in FastAPI via `app.mount("/mcp", mcp_http_app)`.
- **Expected Result:** Incoming requests to `POST http://127.0.0.1:8000/mcp` route directly to the MCP server.
- **Actual Result / Error:** `streamable_http_app()` defaults its internal route to `/mcp`, creating an effective URL path of `/mcp/mcp`. Requests to `/mcp` returned HTTP 307 redirect and 404 on `/mcp/`.
- **Impact on Build:** Health checks and client requests to `/mcp` failed routing.
- **Workaround Implemented:** Explicitly passed `streamable_http_path="/"` when constructing the sub-app:
  ```python
  mcp_http_app = mcp.streamable_http_app(streamable_http_path="/", stateless_http=True, json_response=True)
  ```
- **Evidence:** Route introspection showing path changed from `/mcp` to `/`.
- **Suggestion for Developer / SDK Authors:** In documentation for mounting to FastAPI/Starlette, explicitly mention setting `streamable_http_path="/"` when mounting at a custom path prefix.
