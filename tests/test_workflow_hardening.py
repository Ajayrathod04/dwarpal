"""Hardening and coverage tests for DWARPAL P0 and P1 criteria."""
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
import json
from app.main import app
from app.policy import local_decide, evaluate_risk
from app.store import _db, canonical_plan_digest

def test_unknown_role_fails_closed():
    d = local_decide("hacker_role", "request_access", "door", {"verified_identity": True, "homeowner_approved": True})
    assert not d.allowed
    assert d.reason_code == "UNAUTHORIZED_ROLE"

def test_unknown_action_fails_closed():
    d = local_decide("resident", "nuke_database", "server", {})
    assert not d.allowed
    assert d.reason_code == "UNKNOWN_ACTION"

def test_propose_maintenance_requires_sufficient_rationale():
    d = local_decide("resident", "propose_maintenance_action", "maintenance_proposal", {"rationale": "ok"})
    assert not d.allowed
    assert d.reason_code == "MISSING_RATIONALE"

def test_risk_assessment_rules():
    elevated = evaluate_risk("request_access", "door:FRONT-01", {"homeowner_approved": False, "verified_identity": False})
    assert elevated["risk_level"] == "ELEVATED"
    assert "AWAITING_HOMEOWNER_APPROVAL" in elevated["risk_factors"]
    assert elevated["is_simulation"] is True

    low = evaluate_risk("request_access", "door:FRONT-01", {"homeowner_approved": True, "verified_identity": True})
    assert low["risk_level"] == "LOW"
    assert low["recommended_next_step"] == "EXECUTE_SIMULATED_PREVIEW"

    tampered = evaluate_risk("request_access", "door:FRONT-01", {"tampered": True})
    assert tampered["risk_level"] == "HIGH"
    assert "INTEGRITY_HASH_MISMATCH" in tampered["risk_factors"]

def test_plan_tampering_detected(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "tamper_test.sqlite3"))
    with TestClient(app) as client:
        wf = client.post("/api/workflow", json={"case_id": "CASE-1042", "request": "Fix leaky pipe in kitchen"}).json()
        assert wf["ok"] is True
        run_id = wf["run_id"]
        action_hash = wf["action_hash"]

        # Directly tamper with the stored plan_json in SQLite
        con = _db()
        tampered_plan = wf["plan"].copy()
        tampered_plan["scope"]["max_entries"] = 999  # Tampered scope!
        con.execute("UPDATE workflow_previews SET plan_json = ? WHERE run_id = ?", (json.dumps(tampered_plan), run_id))
        con.commit()
        con.close()

        # Attempt approval
        res = client.post("/api/workflow/approve", json={"run_id": run_id, "action_hash": action_hash, "verified_identity": True}).json()
        assert res["ok"] is False
        assert res["status"] == "HASH_MISMATCH"
        assert res["reason_code"] == "PLAN_TAMPERED"

def test_expired_workflow_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "expiry_test.sqlite3"))
    with TestClient(app) as client:
        wf = client.post("/api/workflow", json={"case_id": "CASE-1042", "request": "Clean air filters"}).json()
        run_id = wf["run_id"]
        action_hash = wf["action_hash"]

        # Backdate creation time to 15 minutes ago
        past_time = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        con = _db()
        con.execute("UPDATE workflow_previews SET created_at = ? WHERE run_id = ?", (past_time, run_id))
        con.commit()
        con.close()

        res = client.post("/api/workflow/approve", json={"run_id": run_id, "action_hash": action_hash, "verified_identity": True}).json()
        assert res["ok"] is False
        assert res["status"] == "EXPIRED"

def test_workflow_lifecycle_steps_structure(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "lifecycle_test.sqlite3"))
    with TestClient(app) as client:
        wf = client.post("/api/workflow", json={"case_id": "CASE-1042", "request": "Inspect ceiling fan"}).json()
        assert "lifecycle_steps" in wf
        assert len(wf["lifecycle_steps"]) == 7
        assert wf["lifecycle_steps"][0]["name"] == "CASE_CONTEXT_LOADED"
        assert wf["lifecycle_steps"][3]["status"] == "PENDING"
        assert wf["risk_assessment"]["risk_level"] == "ELEVATED"

        appr = client.post("/api/workflow/approve", json={"run_id": wf["run_id"], "action_hash": wf["action_hash"], "verified_identity": True}).json()
        assert appr["ok"] is True
        assert appr["lifecycle_steps"][3]["status"] == "COMPLETED"
        assert appr["lifecycle_steps"][5]["status"] == "COMPLETED"
        assert "provenance" in appr

def test_preset_scenarios_all_pass(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "preset_test.sqlite3"))
    with TestClient(app) as client:
        safe = client.post("/api/preset", json={"name": "safe_approved"}).json()
        assert safe["preset"] == "safe_approved"
        assert safe["approval_result"]["ok"] is True

        missing = client.post("/api/preset", json={"name": "missing_approval"}).json()
        assert missing["preset"] == "missing_approval"
        assert missing["approval_result"]["ok"] is False

        tampered = client.post("/api/preset", json={"name": "tampered_plan"}).json()
        assert tampered["preset"] == "tampered_plan"
        assert tampered["approval_result"]["status"] == "HASH_MISMATCH"

        replay = client.post("/api/preset", json={"name": "replayed_plan"}).json()
        assert replay["preset"] == "replayed_plan"
        assert replay["replay_attempt"]["status"] == "ALREADY_FINALIZED"

def test_audit_event_ordering_and_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "audit_order_test.sqlite3"))
    with TestClient(app) as client:
        client.post("/api/preset", json={"name": "safe_approved"})
        events = client.get("/api/audit?limit=20").json()["events"]
        assert len(events) >= 4
        # Verify first event has structured attributes
        first = events[0]
        assert "event_id" in first
        assert "correlation_id" in first
        assert "event_type" in first
        assert "simulated" in first
        assert first["simulated"] is True
