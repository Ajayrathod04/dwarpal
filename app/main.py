from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import json, hmac, os
from dotenv import load_dotenv

# Dual-version MCP SDK support: supports v1.x (FastMCP) and v2.x (MCPServer)
MCP_SDK_AVAILABLE = False
mcp = None
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

from .service import get_case_status, propose_maintenance_action, request_access, audit_events
from .store import create_workflow_preview, get_workflow_preview, finish_workflow_preview, log_event, canonical_plan_digest
from .policy import evaluate_risk
from .agent import ask_agent

load_dotenv()
BASE = Path(__file__).parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # A mounted Starlette sub-application's lifespan does not run automatically.
    # Explicitly start the MCP session manager in the host FastAPI lifespan if available and not already started.
    if mcp is not None and hasattr(mcp, "session_manager") and not getattr(mcp.session_manager, "_has_started", False):
        try:
            async with mcp.session_manager.run():
                yield
        except RuntimeError:
            yield
    else:
        yield

app = FastAPI(title="DWARPAL Action Governance Gateway", version="1.2.0", lifespan=lifespan)

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

# Mount MCP Streamable HTTP endpoint if SDK is available
if mcp is not None and hasattr(mcp, "streamable_http_app"):
    try:
        mcp_http_app = mcp.streamable_http_app(streamable_http_path="/", stateless_http=True, json_response=True)
    except TypeError:
        mcp_http_app = mcp.streamable_http_app()
else:
    mcp_http_app = None

if mcp_http_app is not None:
    app.mount("/mcp", mcp_http_app)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    return {
        "ok": True,
        "project": "DWARPAL",
        "version": "1.2.0",
        "policy_mode": os.getenv("POLICY_MODE", "local"),
        "local_policy_available": True,
        "mcp_endpoint": "/mcp" if MCP_SDK_AVAILABLE else None,
        "mcp_sdk_available": MCP_SDK_AVAILABLE,
        "mcp_protocol_requirement": "2025-11-25 or later" if MCP_SDK_AVAILABLE else None,
        "aws_avp_configured": bool(os.getenv("AVP_POLICY_STORE_ID")),
        "strands_enabled": os.getenv("ENABLE_STRANDS", "false").lower() == "true",
        "audit_storage": "SQLite (local demo storage; not tamper-proof)",
        "simulation_notice": "Identity evidence and lock control are simulated for demo purposes.",
        "note": "AWS integrations are not implied by these flags; verify live calls independently."
    }

class AccessInput(BaseModel):
    principal_role: str = Field(default="visitor", max_length=50)
    door_id: str = Field(default="FRONT-01", max_length=50)
    reason: str = Field(default="Package delivery", min_length=3, max_length=300)
    verified_identity: bool = False
    homeowner_approved: bool = False

class ProposalInput(BaseModel):
    case_id: str = Field(default="CASE-1042", max_length=50)
    action: str = Field(default="Assign inspection", min_length=3, max_length=200)
    rationale: str = Field(default="Inspect the reported issue and attach evidence.", min_length=5, max_length=500)
    principal_role: str = Field(default="support_agent", max_length=50)

class CaseInput(BaseModel):
    case_id: str = Field(default="CASE-1042", max_length=50)
    principal_role: str = Field(default="resident", max_length=50)

class AskInput(BaseModel):
    question: str = Field(min_length=3, max_length=500)

class WorkflowInput(BaseModel):
    case_id: str = Field(default="CASE-1042", max_length=50)
    request: str = Field(default="Arrange a plumber visit and ask before granting entry.", min_length=5, max_length=500)

class WorkflowApprovalInput(BaseModel):
    run_id: str = Field(min_length=8, max_length=32)
    action_hash: str = Field(min_length=64, max_length=64)
    verified_identity: bool = False

class PresetInput(BaseModel):
    name: str = Field(min_length=3, max_length=50)

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
    return {"events": audit_events(limit)}

@app.post("/api/ask")
def api_ask(x: AskInput):
    return ask_agent(x.question)

@app.post("/api/workflow")
def api_workflow(x: WorkflowInput):
    """Prepare a plan and wait for a separate approval bound to its exact hash (P1.1 State Machine)."""
    case = get_case_status(x.case_id, "resident")
    if not case.get("ok"):
        return {"ok": False, "status": "CASE_NOT_AVAILABLE", "reason_code": case.get("reason_code", "DENIED"), "case": case}
    
    proposal = propose_maintenance_action(
        x.case_id, "Prepare a home-service visit", x.request, "support_agent"
    )
    if not proposal.get("ok"):
        return {"ok": False, "status": "PROPOSAL_REJECTED", "reason_code": proposal.get("reason_code", "DENIED"), "proposal": proposal}

    preview = create_workflow_preview(x.case_id, x.request)
    risk = evaluate_risk("request_access", "door:FRONT-01", {"verified_identity": False, "homeowner_approved": False})

    # Log explicit approval gate required
    log_event(
        principal="system_governor",
        action="workflow_approval_gate",
        resource=f"workflow:{preview['run_id']}",
        decision=False,
        reason="Plan prepared and persisted. Waiting for human approval bound to plan digest.",
        engine="local-demo",
        details={"plan_hash": preview["action_hash"], "case_id": x.case_id.upper()},
        correlation_id=preview["run_id"],
        event_type="APPROVAL_REQUIRED",
        reason_code="AWAITING_APPROVAL",
        plan_hash=preview["action_hash"]
    )

    lifecycle_steps = [
        {"step_id": 1, "name": "CASE_CONTEXT_LOADED", "status": "COMPLETED", "summary": f"Case {x.case_id.upper()} read and authorized for resident.", "timestamp": preview["created_at"], "simulated": True, "evidence_refs": [f"case:{x.case_id.upper()}"]},
        {"step_id": 2, "name": "MAINTENANCE_PROPOSAL_CREATED", "status": "COMPLETED", "summary": f"Proposal recorded: '{proposal.get('proposed_action')}'. No external dispatch.", "timestamp": preview["created_at"], "simulated": True, "evidence_refs": [f"proposal:{preview['run_id']}"]},
        {"step_id": 3, "name": "PLAN_PREVIEW_READY", "status": "COMPLETED", "summary": f"Canonical SHA-256 digest bound: {preview['action_hash'][:16]}…", "timestamp": preview["created_at"], "simulated": True, "evidence_refs": [f"hash:{preview['action_hash']}"]},
        {"step_id": 4, "name": "AWAITING_HOMEOWNER_APPROVAL", "status": "PENDING", "summary": "Waiting for explicit human approval gate.", "timestamp": None, "simulated": True, "evidence_refs": []},
        {"step_id": 5, "name": "POLICY_EVALUATED", "status": "WAITING", "summary": "Policy check pending approval input.", "timestamp": None, "simulated": True, "evidence_refs": []},
        {"step_id": 6, "name": "ACCESS_SCOPE_PREVIEWED", "status": "WAITING", "summary": "Awaiting policy authorization for 15-minute scoped preview.", "timestamp": None, "simulated": True, "evidence_refs": []},
        {"step_id": 7, "name": "AUDIT_RECEIPT_READY", "status": "WAITING", "summary": "Receipts will finalize upon approval evaluation.", "timestamp": None, "simulated": True, "evidence_refs": []}
    ]

    return {
        "ok": True,
        "workflow": "home_service_with_approval_gate",
        "status": "AWAITING_HUMAN_APPROVAL",
        **preview,
        "risk_assessment": risk,
        "lifecycle_steps": lifecycle_steps,
        "steps": [
            {"step": 1, "name": "Read home-service case", "result": case},
            {"step": 2, "name": "Create maintenance proposal", "result": proposal},
            {"step": 3, "name": "Approval required", "result": {"decision": "PENDING", "action_hash": preview["action_hash"]}},
        ],
        "safety_boundary": "No contractor was contacted and no lock was operated. This is a deterministic simulation; identity is a demo input.",
    }

@app.post("/api/workflow/approve")
def api_workflow_approve(x: WorkflowApprovalInput):
    """Record a one-time approval attempt bound to a persisted plan hash (P0.2 Canonical Integrity)."""
    preview = get_workflow_preview(x.run_id)
    if not preview:
        log_event("untrusted_client", "workflow_approve", x.run_id, False, "Workflow preview not found.", "local-demo",
                  correlation_id=x.run_id, event_type="POLICY_DENIED", reason_code="NOT_FOUND")
        return {"ok": False, "status": "NOT_FOUND", "reason_code": "NOT_FOUND", "reason": "Workflow preview not found."}
    
    if preview["status"] != "AWAITING_HUMAN_APPROVAL":
        log_event("resident_demo", "workflow_approve", x.run_id, False,
                  "Replay rejected: this preview is already finalized.", "local-demo",
                  correlation_id=x.run_id, event_type="APPROVAL_REPLAY_REJECTED", reason_code="ALREADY_FINALIZED",
                  plan_hash=x.action_hash)
        return {"ok": False, "status": "ALREADY_FINALIZED", "reason_code": "ALREADY_FINALIZED", "reason": "This preview is no longer awaiting approval."}
    
    # Constant-time comparison for security hygiene
    if not hmac.compare_digest(preview["action_hash"], x.action_hash):
        log_event("resident_demo", "workflow_approve", x.run_id, False,
                  "Integrity failure: approval hash does not match canonical plan digest.", "local-demo",
                  correlation_id=x.run_id, event_type="POLICY_DENIED", reason_code="HASH_MISMATCH",
                  plan_hash=x.action_hash)
        return {"ok": False, "status": "HASH_MISMATCH", "reason_code": "HASH_MISMATCH", "reason": "The approval does not match the exact previewed plan."}
    
    # Recompute canonical digest from persisted plan to detect internal store tampering
    if preview.get("plan"):
        recomputed_hash = canonical_plan_digest(preview["plan"])
        if not hmac.compare_digest(recomputed_hash, x.action_hash):
            log_event("resident_demo", "workflow_approve", x.run_id, False,
                      "Tamper detected: persisted plan content does not match stored hash.", "local-demo",
                      correlation_id=x.run_id, event_type="POLICY_DENIED", reason_code="PLAN_TAMPERED",
                      plan_hash=x.action_hash)
            return {"ok": False, "status": "HASH_MISMATCH", "reason_code": "PLAN_TAMPERED", "reason": "Persisted plan content does not match canonical digest."}

    created = datetime.fromisoformat(preview["created_at"])
    age_seconds = (datetime.now(timezone.utc) - created).total_seconds()
    if age_seconds > 600:
        finish_workflow_preview(x.run_id, "EXPIRED", {"reason": "Approval window expired."})
        log_event("resident_demo", "workflow_approve", x.run_id, False,
                  "Approval window expired (10 minutes max).", "local-demo",
                  correlation_id=x.run_id, event_type="POLICY_DENIED", reason_code="EXPIRED",
                  plan_hash=x.action_hash)
        return {"ok": False, "status": "EXPIRED", "reason_code": "EXPIRED", "reason": "This preview expired after 10 minutes. Create a new plan."}
    
    access = request_access(
        "resident", "FRONT-01", "One-time approval for the exact previewed home-service plan",
        x.verified_identity, True, correlation_id=x.run_id, plan_hash=x.action_hash
    )
    allowed = access.get("decision") == "ALLOW"
    final_status = "APPROVED_SIMULATED" if allowed else "DENIED"

    # Atomic state transition in database
    updated = finish_workflow_preview(x.run_id, final_status, access)
    if not updated:
        return {"ok": False, "status": "ALREADY_FINALIZED", "reason_code": "CONCURRENT_FINALIZATION", "reason": "This preview was finalized concurrently."}

    log_event(
        principal="resident_demo",
        action="workflow_approve",
        resource=x.run_id,
        decision=allowed,
        reason=access.get("reason", "Decision recorded."),
        engine=access.get("engine", "local-demo"),
        details={"verified_identity": x.verified_identity, "homeowner_approved": True, "final_status": final_status},
        correlation_id=x.run_id,
        event_type="APPROVAL_ACCEPTED" if allowed else "POLICY_DENIED",
        reason_code=access.get("reason_code", "ALLOW" if allowed else "DENIED"),
        plan_hash=x.action_hash
    )

    risk = evaluate_risk("request_access", "door:FRONT-01", {"verified_identity": x.verified_identity, "homeowner_approved": True})
    now_ts = datetime.now(timezone.utc).isoformat()

    lifecycle_steps = [
        {"step_id": 1, "name": "CASE_CONTEXT_LOADED", "status": "COMPLETED", "summary": f"Case context locked to run.", "timestamp": preview["created_at"], "simulated": True, "evidence_refs": [f"case:{preview['case_id']}"]},
        {"step_id": 2, "name": "MAINTENANCE_PROPOSAL_CREATED", "status": "COMPLETED", "summary": "Proposal verified.", "timestamp": preview["created_at"], "simulated": True, "evidence_refs": [f"proposal:{x.run_id}"]},
        {"step_id": 3, "name": "PLAN_PREVIEW_READY", "status": "COMPLETED", "summary": "Hash match verified.", "timestamp": preview["created_at"], "simulated": True, "evidence_refs": [f"hash:{x.action_hash}"]},
        {"step_id": 4, "name": "AWAITING_HOMEOWNER_APPROVAL", "status": "COMPLETED", "summary": "Explicit approval received.", "timestamp": now_ts, "simulated": True, "evidence_refs": ["approval:recorded"]},
        {"step_id": 5, "name": "POLICY_EVALUATED", "status": "COMPLETED", "summary": f"Policy decision: {access.get('decision')} ({access.get('reason_code')}).", "timestamp": now_ts, "simulated": True, "evidence_refs": [f"reason:{access.get('reason_code')}"]},
        {"step_id": 6, "name": "ACCESS_SCOPE_PREVIEWED", "status": "COMPLETED" if allowed else "BLOCKED", "summary": "One-entry 15-minute preview issued." if allowed else "Access grant withheld.", "timestamp": now_ts, "simulated": True, "evidence_refs": ["scope:FRONT-01"] if allowed else []},
        {"step_id": 7, "name": "AUDIT_RECEIPT_READY", "status": "COMPLETED", "summary": "Immutable audit receipt written to local SQLite store.", "timestamp": now_ts, "simulated": True, "evidence_refs": [f"run:{x.run_id}"]}
    ]

    return {
        "ok": allowed,
        "workflow": "home_service_with_approval_gate",
        "status": final_status,
        "run_id": x.run_id,
        "action_hash": x.action_hash,
        "access_decision": access,
        "risk_assessment": risk,
        "lifecycle_steps": lifecycle_steps,
        "provenance": {
            "case_id": preview["case_id"],
            "proposal_action": preview.get("plan", {}).get("proposed_action", "Prepare a home-service visit"),
            "plan_hash": x.action_hash,
            "policy_reason_code": access.get("reason_code"),
            "policy_reason": access.get("reason"),
            "policy_engine": access.get("engine"),
            "simulated": True
        },
        "safety_boundary": "Approval is bound to the preview hash and is single-use in this demo. No contractor was contacted and no physical lock was operated; identity is simulated.",
    }

@app.post("/api/preset")
def api_preset(x: PresetInput):
    """Run safe, bounded scenario presets through real backend endpoints (P1.3)."""
    name = x.name.lower().strip()
    if name == "safe_approved":
        wf = api_workflow(WorkflowInput(case_id="CASE-1042", request="Arrange a plumber visit with approved entry."))
        appr = api_workflow_approve(WorkflowApprovalInput(run_id=wf["run_id"], action_hash=wf["action_hash"], verified_identity=True))
        return {
            "preset": "safe_approved",
            "title": "Safe Approved Demo Path",
            "narrative": "Homeowner prepares a plumber visit plan, verifies simulated identity, and approves the exact canonical plan hash.",
            "workflow_preview": wf,
            "approval_result": appr,
            "expected_decision": "ALLOW",
            "simulated": True
        }
    elif name == "missing_approval":
        wf = api_workflow(WorkflowInput(case_id="CASE-1088", request="Arrange battery replacement for hallway smoke alarm."))
        appr = api_workflow_approve(WorkflowApprovalInput(run_id=wf["run_id"], action_hash=wf["action_hash"], verified_identity=False))
        return {
            "preset": "missing_approval",
            "title": "Missing Identity Evidence Gate",
            "narrative": "Homeowner initiates repair, but simulated resident identity is missing. Policy fails closed and denies access preview.",
            "workflow_preview": wf,
            "approval_result": appr,
            "expected_decision": "DENY",
            "simulated": True
        }
    elif name == "tampered_plan":
        wf = api_workflow(WorkflowInput(case_id="CASE-1101", request="Arrange package inspection handoff."))
        tampered_hash = "f" * 64
        appr = api_workflow_approve(WorkflowApprovalInput(run_id=wf["run_id"], action_hash=tampered_hash, verified_identity=True))
        return {
            "preset": "tampered_plan",
            "title": "Tampered Plan / Hash Mismatch",
            "narrative": "The approval attempt supplies a mismatched action hash. The server detects the integrity violation and refuses approval.",
            "workflow_preview": wf,
            "approval_result": appr,
            "expected_decision": "DENY (HASH_MISMATCH)",
            "simulated": True
        }
    elif name == "replayed_plan":
        wf = api_workflow(WorkflowInput(case_id="CASE-1042", request="Arrange sink repair for replay demonstration."))
        appr1 = api_workflow_approve(WorkflowApprovalInput(run_id=wf["run_id"], action_hash=wf["action_hash"], verified_identity=True))
        appr2 = api_workflow_approve(WorkflowApprovalInput(run_id=wf["run_id"], action_hash=wf["action_hash"], verified_identity=True))
        return {
            "preset": "replayed_plan",
            "title": "Replay / Double Finalization Prevention",
            "narrative": "An approval is submitted and finalized once. A second approval attempt with the same ID and hash is immediately rejected as ALREADY_FINALIZED.",
            "workflow_preview": wf,
            "first_approval": appr1,
            "replay_attempt": appr2,
            "expected_decision": "ALREADY_FINALIZED",
            "simulated": True
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unknown preset '{x.name}'. Valid presets: safe_approved, missing_approval, tampered_plan, replayed_plan.")

