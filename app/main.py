from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import json
from dotenv import load_dotenv
# MCP is optional for the browser-simulation path. When installed (as declared in
# requirements.txt), the official SDK server is mounted at /mcp. This fallback
# lets the UI and deterministic tests run in restricted environments without it.
try:
    from mcp.server.fastmcp import FastMCP
    MCP_SDK_AVAILABLE = True
except ImportError:
    FastMCP = None
    MCP_SDK_AVAILABLE = False
from .service import get_case_status, propose_maintenance_action, request_access, audit_events
from .store import create_workflow_preview, get_workflow_preview, finish_workflow_preview
from .agent import ask_agent

load_dotenv()
BASE = Path(__file__).parent
mcp = FastMCP("dwarpal-action-governance", stateless_http=True, json_response=True) if MCP_SDK_AVAILABLE else None

@asynccontextmanager
async def lifespan(app):
    # A mounted Starlette sub-application's lifespan does not run automatically.
    # Explicitly start the MCP session manager in the host FastAPI lifespan.
    if mcp is not None:
        async with mcp.session_manager.run():
            yield
    else:
        yield

app = FastAPI(title="DWARPAL", version="1.1.0", lifespan=lifespan)

if mcp is not None:
    @mcp.tool()
    def get_case_status_tool(case_id: str, principal_role: str = "resident") -> dict:
        """Read a fictional home-service case after policy authorization; returns evidence and decision."""
        return get_case_status(case_id, principal_role)

    @mcp.tool()
    def propose_maintenance_action_tool(case_id: str, action: str, rationale: str, principal_role: str = "support_agent") -> dict:
        """Record a policy-checked maintenance proposal; never dispatches it externally."""
        return propose_maintenance_action(case_id, action, rationale, principal_role)

    @mcp.tool()
    def request_access_tool(principal_role: str, door_id: str, reason: str, verified_identity: bool = False, homeowner_approved: bool = False) -> dict:
        """Simulate a door-access request with fail-closed authorization; never controls a real lock."""
        return request_access(principal_role, door_id, reason, verified_identity, homeowner_approved)

# Create and mount the official MCP SDK's Streamable HTTP app only after registering tools.
mcp_http_app = mcp.streamable_http_app() if mcp is not None else None
if mcp_http_app is not None:
    app.mount("/mcp", mcp_http_app)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    import os
    return {"ok":True,"project":"DWARPAL","policy_mode":os.getenv("POLICY_MODE","local"),
            "mcp_endpoint":"/mcp" if MCP_SDK_AVAILABLE else None, "mcp_sdk_available":MCP_SDK_AVAILABLE,
            "mcp_protocol_requirement":"2025-11-25 or later" if MCP_SDK_AVAILABLE else None,
            "aws_avp_configured":bool(os.getenv("AVP_POLICY_STORE_ID")),
            "strands_enabled":os.getenv("ENABLE_STRANDS","false").lower()=="true",
            "note":"AWS integrations are not implied by these flags; verify live calls independently."}

class AccessInput(BaseModel):
    principal_role: str = "visitor"
    door_id: str = "FRONT-01"
    reason: str = "Package delivery"
    verified_identity: bool = False
    homeowner_approved: bool = False
class ProposalInput(BaseModel):
    case_id: str = "CASE-1042"
    action: str = "Assign inspection"
    rationale: str = Field(default="Inspect the reported issue and attach evidence.", min_length=5)
    principal_role: str = "support_agent"
class CaseInput(BaseModel):
    case_id: str = "CASE-1042"
    principal_role: str = "resident"
class AskInput(BaseModel):
    question: str = Field(min_length=3, max_length=500)
class WorkflowInput(BaseModel):
    case_id: str = "CASE-1042"
    request: str = Field(default="Arrange a plumber visit and ask before granting entry.", min_length=8, max_length=500)
class WorkflowApprovalInput(BaseModel):
    run_id: str = Field(min_length=8, max_length=32)
    action_hash: str = Field(min_length=64, max_length=64)
    verified_identity: bool = False

@app.post("/api/access")
def api_access(x: AccessInput):
    return request_access(x.principal_role, x.door_id, x.reason, x.verified_identity, x.homeowner_approved)
@app.post("/api/proposal")
def api_proposal(x: ProposalInput):
    return propose_maintenance_action(x.case_id, x.action, x.rationale, x.principal_role)
@app.post("/api/case")
def api_case(x: CaseInput):
    return get_case_status(x.case_id, x.principal_role)
@app.get("/api/audit")
def api_audit(limit: int = 30):
    return {"events":audit_events(limit)}
@app.post("/api/ask")
def api_ask(x: AskInput):
    return ask_agent(x.question)

@app.post("/api/workflow")
def api_workflow(x: WorkflowInput):
    """Prepare a plan and wait for a separate approval bound to its exact hash."""
    case = get_case_status(x.case_id, "resident")
    if not case.get("ok"):
        return {"ok": False, "status": "CASE_NOT_AVAILABLE", "case": case}
    proposal = propose_maintenance_action(
        x.case_id, "Prepare a home-service visit", x.request, "support_agent"
    )
    preview = create_workflow_preview(x.case_id, x.request)
    return {
        "ok": True,
        "workflow": "home_service_with_approval_gate",
        "status": "AWAITING_HUMAN_APPROVAL",
        **preview,
        "steps": [
            {"step": 1, "name": "Read home-service case", "result": case},
            {"step": 2, "name": "Create maintenance proposal", "result": proposal},
            {"step": 3, "name": "Approval required", "result": {"decision": "PENDING", "action_hash": preview["action_hash"]}},
        ],
        "safety_boundary": "No contractor was contacted and no lock was operated. This is a deterministic simulation; identity is a demo input.",
    }

@app.post("/api/workflow/approve")
def api_workflow_approve(x: WorkflowApprovalInput):
    """Record a one-time approval attempt bound to a persisted plan hash."""
    preview = get_workflow_preview(x.run_id)
    if not preview:
        return {"ok": False, "status": "NOT_FOUND", "reason": "Workflow preview not found."}
    if preview["status"] != "AWAITING_HUMAN_APPROVAL":
        return {"ok": False, "status": "ALREADY_FINALIZED", "reason": "This preview is no longer awaiting approval."}
    if preview["action_hash"] != x.action_hash:
        return {"ok": False, "status": "HASH_MISMATCH", "reason": "The approval does not match the exact previewed plan."}
    created = datetime.fromisoformat(preview["created_at"])
    age_seconds = (datetime.now(timezone.utc) - created).total_seconds()
    if age_seconds > 600:
        finish_workflow_preview(x.run_id, "EXPIRED", {"reason": "Approval window expired."})
        return {"ok": False, "status": "EXPIRED", "reason": "This preview expired after 10 minutes. Create a new plan."}
    access = request_access(
        "resident", "FRONT-01", "One-time approval for the exact previewed home-service plan",
        x.verified_identity, True
    )
    final_status = "APPROVED_SIMULATED" if access.get("decision") == "ALLOW" else "DENIED"
    finish_workflow_preview(x.run_id, final_status, access)
    return {
        "ok": access.get("decision") == "ALLOW",
        "workflow": "home_service_with_approval_gate",
        "status": final_status,
        "run_id": x.run_id,
        "action_hash": x.action_hash,
        "access_decision": access,
        "safety_boundary": "Approval is bound to the preview hash and is single-use in this demo. No contractor was contacted and no physical lock was operated; identity is simulated.",
    }
