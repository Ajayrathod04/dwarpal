from app.policy import local_decide
from app.service import request_access, get_case_status, propose_maintenance_action

def test_visitor_access_denied():
    d=local_decide("visitor","request_access","door",{"verified_identity":False})
    assert not d.allowed and "denied" in d.reason.lower()

def test_access_requires_both_identity_and_homeowner_approval():
    d=local_decide("resident","request_access","door",{"verified_identity":True,"homeowner_approved":True})
    assert d.allowed

def test_unknown_action_fails_closed():
    assert not local_decide("admin","delete_everything","db").allowed

def test_resident_can_read_demo_case():
    r=get_case_status("CASE-1042","resident")
    assert r["ok"] and r["case"]["id"]=="CASE-1042"

def test_unknown_case_is_not_found():
    assert not get_case_status("CASE-9999","resident")["ok"]

def test_maintenance_is_proposal_not_execution():
    r=propose_maintenance_action("CASE-1042","Assign inspection","Need an inspection","support_agent")
    assert r["ok"] and r["status"]=="PROPOSED_NOT_EXECUTED"
    assert "No external service" in r["safety_note"]


def test_identity_without_homeowner_approval_is_denied():
    d = local_decide("resident", "request_access", "door", {"verified_identity": True, "homeowner_approved": False})
    assert not d.allowed
    assert "approval" in d.reason.lower()


def test_avp_mode_fails_closed_without_policy_store(monkeypatch):
    from app.policy import authorize
    monkeypatch.setenv('POLICY_MODE', 'aws_avp')
    monkeypatch.delenv('AVP_POLICY_STORE_ID', raising=False)
    d = authorize('resident', 'request_access', 'door', {'verified_identity': True, 'homeowner_approved': True})
    assert not d.allowed
    assert d.engine == 'aws-avp'
    assert 'missing' in d.reason.lower()


def test_avp_adapter_passes_boolean_context_to_sdk(monkeypatch):
    import sys, types
    from app.policy import authorize
    captured = {}
    class FakeClient:
        def is_authorized(self, **kwargs):
            captured.update(kwargs)
            return {'decision': 'DENY'}
    fake_boto3 = types.SimpleNamespace(client=lambda *args, **kwargs: FakeClient())
    monkeypatch.setitem(sys.modules, 'boto3', fake_boto3)
    monkeypatch.setenv('POLICY_MODE', 'aws_avp')
    monkeypatch.setenv('AVP_POLICY_STORE_ID', 'test-store')
    monkeypatch.setenv('AWS_REGION', 'us-east-1')
    d = authorize('resident', 'request_access', 'door', {'verified_identity': True, 'homeowner_approved': False})
    assert not d.allowed
    assert captured['context']['contextMap']['verified_identity'] == {'boolean': True}
    assert captured['context']['contextMap']['homeowner_approved'] == {'boolean': False}
