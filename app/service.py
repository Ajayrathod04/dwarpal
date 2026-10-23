"""Shared business logic used by HTTP routes and MCP tools."""
from .policy import authorize
from .store import log_event, list_events

CASES = {
 "CASE-1042": {"id":"CASE-1042","title":"Leaking kitchen sink","status":"Plumber assigned","location":"Kitchen","updated":"Demo snapshot A","evidence":"Fictional service ticket HOME-8841; no real provider is connected."},
 "CASE-1088": {"id":"CASE-1088","title":"Smoke alarm battery","status":"Awaiting homeowner approval","location":"Hallway","updated":"Demo snapshot B","evidence":"Fictional service ticket HOME-8893; status is simulated."},
 "CASE-1101": {"id":"CASE-1101","title":"Package handoff","status":"Needs human review","location":"Front porch","updated":"Demo snapshot C","evidence":"Fictional service ticket HOME-8910; no real delivery provider is connected."}
}

def get_case_status(case_id: str, principal_role: str = "resident", correlation_id: str | None = None):
    case = CASES.get(case_id.upper())
    d = authorize(principal_role, "get_case_status", "case", {})
    if not case:
        log_event(principal_role, "get_case_status", case_id.upper(), False, "Unknown demo case ID.", d.engine,
                  {"case_id": case_id.upper()}, correlation_id=correlation_id, event_type="POLICY_DENIED", reason_code="UNKNOWN_CASE_ID")
        return {"ok":False,"decision":"DENY","reason_code":"UNKNOWN_CASE_ID","error":"Unknown demo case ID.","engine":d.engine}
    event = log_event(principal_role, "get_case_status", case_id.upper(), d.allowed, d.reason, d.engine,
                      {"case_id": case_id.upper()}, correlation_id=correlation_id,
                      event_type="CASE_READ" if d.allowed else "POLICY_DENIED", reason_code=d.reason_code)
    if not d.allowed:
        return {"ok":False,"decision":"DENY","reason_code":d.reason_code,"reason":d.reason,"engine":d.engine,"audit":event}
    return {"ok":True,"decision":"ALLOW","reason_code":d.reason_code,"engine":d.engine,"case":case,"reason":d.reason,"audit":event}

def propose_maintenance_action(case_id: str, action: str, rationale: str, principal_role: str = "support_agent", correlation_id: str | None = None):
    if case_id.upper() not in CASES:
        return {"ok":False,"decision":"DENY","reason_code":"UNKNOWN_CASE_ID","error":"Unknown demo case ID."}
    d = authorize(principal_role, "propose_maintenance_action", "maintenance_proposal", {"rationale":rationale})
    event = log_event(principal_role, "propose_maintenance_action", case_id.upper(), d.allowed, d.reason, d.engine,
                      {"action":action,"rationale":rationale}, correlation_id=correlation_id,
                      event_type="PROPOSAL_CREATED" if d.allowed else "POLICY_DENIED", reason_code=d.reason_code)
    if not d.allowed:
        return {"ok":False,"decision":"DENY","reason_code":d.reason_code,"reason":d.reason,"engine":d.engine,"audit":event}
    return {"ok":True,"decision":"ALLOW","reason_code":d.reason_code,"status":"PROPOSED_NOT_EXECUTED","case_id":case_id.upper(),
            "proposed_action":action,"rationale":rationale,"reason":d.reason,"engine":d.engine,"audit":event,
            "safety_note":"Proposal recorded only. No external service was contacted."}

def request_access(principal_role: str, door_id: str, reason: str, verified_identity: bool = False,
                   homeowner_approved: bool = False, correlation_id: str | None = None, plan_hash: str | None = None):
    d = authorize(principal_role, "request_access", "door", {"verified_identity":verified_identity, "homeowner_approved":homeowner_approved})
    event = log_event(principal_role, "request_access", door_id, d.allowed, d.reason, d.engine,
                      {"reason":reason, "verified_identity":verified_identity, "homeowner_approved":homeowner_approved},
                      correlation_id=correlation_id,
                      event_type="ACCESS_PREVIEW_CREATED" if d.allowed else "POLICY_DENIED",
                      reason_code=d.reason_code, plan_hash=plan_hash)
    grant_preview = ({"resource_scope":door_id, "max_entries":1, "valid_for_minutes":15,
                      "mode":"PREVIEW_ONLY_NOT_ENFORCED"} if d.allowed else None)
    return {"ok":d.allowed,"decision":"ALLOW" if d.allowed else "DENY","reason_code":d.reason_code,"door_id":door_id,
            "reason":d.reason,"engine":d.engine,"audit":event,
            "simulated_grant_preview":grant_preview,
            "execution":"SIMULATED_ONLY","homeowner_approved":homeowner_approved,
            "safety_note":"This prototype never controls a physical lock; identity and approval inputs are simulated."}

def audit_events(limit: int = 30):
    return list_events(limit)

