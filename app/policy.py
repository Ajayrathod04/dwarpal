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

def local_decide(principal_role: str, action: str, resource_type: str, context: dict[str, Any] | None = None) -> Decision:
    context = context or {}
    role = (principal_role or "guest").lower()
    # Fail closed for physical/security-sensitive actions.
    if action == "request_access":
        if (role == "resident" and context.get("verified_identity") is True
                and context.get("homeowner_approved") is True):
            return Decision(True, "Simulated identity evidence and explicit homeowner approval are both present.", "local-demo")
        if context.get("homeowner_approved") is not True:
            return Decision(False, "Access denied: explicit homeowner approval is required before this simulated request can proceed.", "local-demo")
        if role != "resident":
            return Decision(False, "Access denied: this demo role is not authorized to approve resident-controlled entry.", "local-demo")
        return Decision(False, "Access denied: both simulated identity evidence and explicit homeowner approval are required.", "local-demo")
    if action == "get_case_status":
        if role in {"resident", "support_agent", "engineer"}:
            return Decision(True, "Read-only case lookup is allowed for this role.", "local-demo")
        return Decision(False, "This role cannot read case details.", "local-demo")
    if action == "propose_maintenance_action":
        if role in {"resident", "support_agent", "engineer"} and context.get("rationale"):
            return Decision(True, "A proposal may be recorded; no external action is executed.", "local-demo")
        return Decision(False, "A permitted role and a non-empty rationale are required.", "local-demo")
    return Decision(False, "Unknown action: deny by default.", "local-demo")

def authorize(principal_role: str, action: str, resource_type: str, context: dict[str, Any] | None = None) -> Decision:
    mode = os.getenv("POLICY_MODE", "local").lower()
    if mode != "aws_avp":
        return local_decide(principal_role, action, resource_type, context)
    store_id = os.getenv("AVP_POLICY_STORE_ID", "")
    policy_id = os.getenv("AVP_POLICY_ID", "")
    if not store_id:
        return Decision(False, "AVP mode configured but AVP_POLICY_STORE_ID is missing; failed closed.", "aws-avp")
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
        return Decision(allowed, f"Amazon Verified Permissions returned {response.get('decision', 'UNKNOWN')}.", "aws-avp", policy_id or "policy-store-evaluation")
    except Exception as exc:
        # Do not leak credentials or detailed AWS errors into user-facing responses.
        return Decision(False, f"Amazon Verified Permissions unavailable; fail-closed ({type(exc).__name__}).", "aws-avp")
