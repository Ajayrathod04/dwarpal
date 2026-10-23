"""Policy decision adapter. Local mode is a deterministic demo, not AVP."""
import os
from dataclasses import dataclass
from typing import Any

@dataclass
class Decision:
    allowed: bool
    reason: str
    engine: str
    policy_id: str = "local-demo-v1"
    reason_code: str = "ALLOW"

VALID_ROLES = {"resident", "support_agent", "engineer", "visitor"}

def evaluate_risk(action: str, resource: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Deterministic, rules-based risk assessment (P1.2). Not a fake ML score."""
    context = context or {}
    factors: list[str] = []
    
    is_physical_access = action in {"request_access", "door_unlock", "grant_entry"} or "door" in resource.lower()
    verified_identity = context.get("verified_identity") is True
    homeowner_approved = context.get("homeowner_approved") is True
    has_tamper = context.get("tampered") is True or context.get("hash_mismatch") is True
    has_expired = context.get("expired") is True
    already_finalized = context.get("already_finalized") is True

    if has_tamper:
        factors.append("INTEGRITY_HASH_MISMATCH")
        return {
            "risk_level": "HIGH",
            "risk_factors": factors,
            "recommended_next_step": "DENY",
            "explanation": "Plan integrity compromised: submitted hash does not match canonical plan digest.",
            "is_simulation": True,
        }
    if has_expired:
        factors.append("APPROVAL_WINDOW_EXPIRED")
        return {
            "risk_level": "HIGH",
            "risk_factors": factors,
            "recommended_next_step": "DENY",
            "explanation": "Approval validity window has expired. A fresh plan must be prepared.",
            "is_simulation": True,
        }
    if already_finalized:
        factors.append("REPLAY_ATTEMPT_DETECTED")
        return {
            "risk_level": "HIGH",
            "risk_factors": factors,
            "recommended_next_step": "DENY",
            "explanation": "This plan preview has already been finalized and cannot be replayed.",
            "is_simulation": True,
        }

    if is_physical_access:
        factors.append("SENSITIVE_PHYSICAL_ENTRY")
        if not homeowner_approved:
            factors.append("AWAITING_HOMEOWNER_APPROVAL")
        if not verified_identity:
            factors.append("MISSING_IDENTITY_EVIDENCE")

        if not homeowner_approved:
            return {
                "risk_level": "ELEVATED",
                "risk_factors": factors,
                "recommended_next_step": "REQUEST_APPROVAL",
                "explanation": "Consequential door entry requested without explicit homeowner approval gate.",
                "is_simulation": True,
            }
        if not verified_identity:
            return {
                "risk_level": "ELEVATED",
                "risk_factors": factors,
                "recommended_next_step": "VERIFY_IDENTITY_DEMO",
                "explanation": "Homeowner approved entry, but simulated resident identity verification is missing.",
                "is_simulation": True,
            }
        return {
            "risk_level": "LOW",
            "risk_factors": factors,
            "recommended_next_step": "EXECUTE_SIMULATED_PREVIEW",
            "explanation": "Both homeowner approval and identity evidence present. Narrow scoped 15-minute preview allowed.",
            "is_simulation": True,
        }

    if action == "propose_maintenance_action":
        return {
            "risk_level": "LOW",
            "risk_factors": ["PROPOSAL_ONLY_NO_DISPATCH"],
            "recommended_next_step": "PREPARE_PLAN",
            "explanation": "Maintenance proposal records intent without external service dispatch.",
            "is_simulation": True,
        }

    if action == "get_case_status":
        return {
            "risk_level": "LOW",
            "risk_factors": ["READ_ONLY_ACCESS"],
            "recommended_next_step": "PROCEED",
            "explanation": "Read-only case lookup of fictional demo records.",
            "is_simulation": True,
        }

    factors.append("UNKNOWN_UNGOVERNED_ACTION")
    return {
        "risk_level": "HIGH",
        "risk_factors": factors,
        "recommended_next_step": "DENY",
        "explanation": f"Action '{action}' is unmodeled and untrusted.",
        "is_simulation": True,
    }

def local_decide(principal_role: str, action: str, resource_type: str, context: dict[str, Any] | None = None) -> Decision:
    context = context or {}
    role = (principal_role or "guest").lower()

    if role not in VALID_ROLES:
        return Decision(False, f"Access denied: role '{role}' is not a recognized demo role.", "local-demo", reason_code="UNAUTHORIZED_ROLE")

    # Fail closed for physical/security-sensitive actions.
    if action == "request_access":
        if role != "resident":
            return Decision(False, "Access denied: this demo role is not authorized to approve resident-controlled entry.", "local-demo", reason_code="UNAUTHORIZED_ROLE")
        if context.get("homeowner_approved") is not True:
            return Decision(False, "Access denied: explicit homeowner approval is required before this simulated request can proceed.", "local-demo", reason_code="MISSING_APPROVAL")
        if context.get("verified_identity") is not True:
            return Decision(False, "Access denied: simulated identity evidence is required for resident approval.", "local-demo", reason_code="MISSING_IDENTITY_EVIDENCE")
        return Decision(True, "Simulated identity evidence and explicit homeowner approval are both present.", "local-demo", reason_code="ALLOW")

    if action == "get_case_status":
        if role in {"resident", "support_agent", "engineer"}:
            return Decision(True, "Read-only case lookup is allowed for this role.", "local-demo", reason_code="ALLOW")
        return Decision(False, "This role cannot read case details.", "local-demo", reason_code="UNAUTHORIZED_ROLE")

    if action == "propose_maintenance_action":
        if role not in {"resident", "support_agent", "engineer"}:
            return Decision(False, "This role cannot propose maintenance actions.", "local-demo", reason_code="UNAUTHORIZED_ROLE")
        rationale = context.get("rationale")
        if not rationale or len(str(rationale).strip()) < 5:
            return Decision(False, "A permitted role and a non-empty rationale (minimum 5 chars) are required.", "local-demo", reason_code="MISSING_RATIONALE")
        return Decision(True, "A proposal may be recorded; no external action is executed.", "local-demo", reason_code="ALLOW")

    return Decision(False, f"Unknown action '{action}': deny by default.", "local-demo", reason_code="UNKNOWN_ACTION")

def authorize(principal_role: str, action: str, resource_type: str, context: dict[str, Any] | None = None) -> Decision:
    mode = os.getenv("POLICY_MODE", "local").lower()
    if mode != "aws_avp":
        return local_decide(principal_role, action, resource_type, context)
    store_id = os.getenv("AVP_POLICY_STORE_ID", "")
    policy_id = os.getenv("AVP_POLICY_ID", "")
    if not store_id:
        return Decision(False, "AVP mode configured but AVP_POLICY_STORE_ID is missing; failed closed.", "aws-avp", reason_code="MISSING_POLICY_STORE")
    try:
        import boto3
        client = boto3.client("verifiedpermissions", region_name=os.getenv("AWS_REGION", "us-east-1"))
        cedar_context = {}
        for key, value in (context or {}).items():
            if isinstance(value, bool):
                cedar_context[key] = {"boolean": value}
            elif isinstance(value, str):
                cedar_context[key] = {"string": value}
        response = client.is_authorized(
            policyStoreId=store_id,
            principal={"entityType": "DWARPAL::Principal", "entityId": principal_role.lower()},
            action={"actionType": "DWARPAL::Action", "actionId": action},
            resource={"entityType": "DWARPAL::Resource", "entityId": resource_type},
            context={"contextMap": cedar_context}
        )
        allowed = response.get("decision") == "ALLOW"
        reason_code = "ALLOW" if allowed else "AVP_DENY"
        return Decision(allowed, f"Amazon Verified Permissions returned {response.get('decision', 'UNKNOWN')}.", "aws-avp", policy_id or "policy-store-evaluation", reason_code=reason_code)
    except Exception as exc:
        # Do not leak credentials or detailed AWS errors into user-facing responses.
        return Decision(False, f"Amazon Verified Permissions unavailable; fail-closed ({type(exc).__name__}).", "aws-avp", reason_code="ENGINE_EXCEPTION")

