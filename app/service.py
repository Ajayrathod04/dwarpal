"""Shared business logic used by HTTP routes and MCP tools."""
from .policy import authorize
from .store import log_event, list_events

CASES = {
 "CASE-1042": {"id":"CASE-1042","title":"Leaking kitchen sink","status":"Plumber assigned","location":"Kitchen","updated":"Demo snapshot A","evidence":"Fictional service ticket HOME-8841; no real provider is connected."},
 "CASE-1088": {"id":"CASE-1088","title":"Smoke alarm battery","status":"Awaiting homeowner approval","location":"Hallway","updated":"Demo snapshot B","evidence":"Fictional service ticket HOME-8893; status is simulated."},
 "CASE-1101": {"id":"CASE-1101","title":"Package handoff","status":"Needs human review","location":"Front porch","updated":"Demo snapshot C","evidence":"Fictional service ticket HOME-8910; no real delivery provider is connected."}
}

def get_case_status(case_id: str, principal_role: str = "resident"):
    case = CASES.get(case_id.upper())
    d = authorize(principal_role, "get_case_status", "case", {})
    if not case:
        return {"ok":False,"error":"Unknown demo case ID."}
    log_event(principal_role, "get_case_status", case_id.upper(), d.allowed, d.reason, d.engine)
    if not d.allowed:
        return {"ok":False,"decision":"DENY","reason":d.reason,"engine":d.engine}
    return {"ok":True,"decision":"ALLOW","engine":d.engine,"case":case,"reason":d.reason}

def propose_maintenance_action(case_id: str, action: str, rationale: str, principal_role: str = "support_agent"):
    if case_id.upper() not in CASES:
        return {"ok":False,"error":"Unknown demo case ID."}
    d = authorize(principal_role, "propose_maintenance_action", "maintenance_proposal", {"rationale":rationale})
    event = log_event(principal_role, "propose_maintenance_action", case_id.upper(), d.allowed, d.reason, d.engine,
                      {"action":action,"rationale":rationale})
    if not d.allowed:
        return {"ok":False,"decision":"DENY","reason":d.reason,"engine":d.engine,"audit":event}
    return {"ok":True,"decision":"ALLOW","status":"PROPOSED_NOT_EXECUTED","case_id":case_id.upper(),
            "proposed_action":action,"rationale":rationale,"reason":d.reason,"engine":d.engine,"audit":event,
            "safety_note":"Proposal recorded only. No external service was contacted."}

def request_access(principal_role: str, door_id: str, reason: str, verified_identity: bool = False, homeowner_approved: bool = False):
    d = authorize(principal_role, "request_access", "door", {"verified_identity":verified_identity, "homeowner_approved":homeowner_approved})
    event = log_event(principal_role, "request_access", door_id, d.allowed, d.reason, d.engine,
                      {"reason":reason, "verified_identity":verified_identity, "homeowner_approved":homeowner_approved})
    grant_preview = ({"resource_scope":door_id, "max_entries":1, "valid_for_minutes":15,
                      "mode":"PREVIEW_ONLY_NOT_ENFORCED"} if d.allowed else None)
    return {"ok":d.allowed,"decision":"ALLOW" if d.allowed else "DENY","door_id":door_id,
            "reason":d.reason,"engine":d.engine,"audit":event,
            "simulated_grant_preview":grant_preview,
            "execution":"SIMULATED_ONLY","homeowner_approved":homeowner_approved,"safety_note":"This prototype never controls a physical lock; identity and approval inputs are simulated."}

def audit_events(limit: int = 30):
    return list_events(limit)
