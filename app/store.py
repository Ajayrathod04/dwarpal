"""Small SQLite audit trail and workflow store for the local demo.
NOTE: SQLite demo storage is local append-oriented demo storage, not tamper-proof storage.
"""
import os, sqlite3, json, hashlib, uuid, hmac
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SENSITIVE_KEY_SUBSTRINGS = {"password", "token", "secret", "key", "auth", "credential", "private"}

def _sanitize_details(data: Any) -> Any:
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(s in k.lower() for s in SENSITIVE_KEY_SUBSTRINGS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = _sanitize_details(v)
        return sanitized
    if isinstance(data, list):
        return [_sanitize_details(item) for item in data]
    return data

def _db():
    path = os.getenv("DATABASE_PATH", "./dwarpal_audit.sqlite3")
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS audit (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_id TEXT,
      ts TEXT NOT NULL,
      correlation_id TEXT,
      principal TEXT NOT NULL,
      event_type TEXT,
      action TEXT NOT NULL,
      resource TEXT NOT NULL,
      decision TEXT NOT NULL,
      reason_code TEXT,
      reason TEXT NOT NULL,
      plan_hash TEXT,
      engine TEXT NOT NULL,
      simulated INTEGER NOT NULL DEFAULT 1,
      details TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS workflow_previews (
      run_id TEXT PRIMARY KEY,
      case_id TEXT NOT NULL,
      request TEXT NOT NULL,
      action_hash TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL,
      plan_json TEXT NOT NULL DEFAULT '{}',
      result_json TEXT NOT NULL DEFAULT '{}'
    )""")
    # Check if existing table needs column migration
    audit_cols = [c["name"] for c in con.execute("PRAGMA table_info(audit)").fetchall()]
    for col, col_type in [("event_id", "TEXT"), ("correlation_id", "TEXT"), ("event_type", "TEXT"),
                           ("reason_code", "TEXT"), ("plan_hash", "TEXT"), ("simulated", "INTEGER DEFAULT 1")]:
        if col not in audit_cols:
            con.execute(f"ALTER TABLE audit ADD COLUMN {col} {col_type}")
    
    wf_cols = [c["name"] for c in con.execute("PRAGMA table_info(workflow_previews)").fetchall()]
    if "plan_json" not in wf_cols:
        con.execute("ALTER TABLE workflow_previews ADD COLUMN plan_json TEXT NOT NULL DEFAULT '{}'")

    con.commit()
    return con

def log_event(principal: str, action: str, resource: str, decision: bool | str, reason: str, engine: str,
              details: dict | None = None, correlation_id: str | None = None, event_type: str | None = None,
              reason_code: str | None = None, plan_hash: str | None = None):
    con = _db()
    ts = datetime.now(timezone.utc).isoformat()
    event_id = f"EVT-{uuid.uuid4().hex[:10]}"
    dec_str = "ALLOW" if (decision is True or str(decision).upper() == "ALLOW") else "DENY"
    clean_details = _sanitize_details(details or {})
    corr_id = correlation_id or "DEMO-SESSION"
    evt_type = event_type or ("POLICY_ALLOW" if dec_str == "ALLOW" else "POLICY_DENY")
    r_code = reason_code or ("ALLOW" if dec_str == "ALLOW" else "DENIED")

    con.execute("""INSERT INTO audit(
      event_id, ts, correlation_id, principal, event_type, action, resource,
      decision, reason_code, reason, plan_hash, engine, simulated, details
    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
      (event_id, ts, corr_id, principal, evt_type, action, resource,
       dec_str, r_code, reason, plan_hash, engine, 1, json.dumps(clean_details)))
    con.commit()
    con.close()
    return {
        "event_id": event_id,
        "timestamp": ts,
        "correlation_id": corr_id,
        "event_type": evt_type,
        "decision": dec_str,
        "reason_code": r_code,
        "simulated": True
    }

def list_events(limit: int = 30):
    con = _db()
    rows = con.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (max(1, min(int(limit), 100)),)).fetchall()
    con.close()
    results = []
    for r in rows:
        d = dict(r)
        d["simulated"] = bool(d.get("simulated", 1))
        results.append(d)
    return results

def canonical_plan_digest(plan: dict) -> str:
    """Build a deterministic SHA-256 digest from canonical JSON (sorted keys, stable UTF-8)."""
    canonical_bytes = json.dumps(plan, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()

def create_workflow_preview(case_id: str, request: str, door_id: str = "FRONT-01"):
    """Persist a one-time preview bound to a canonical plan hash (P0.2)."""
    plan = {
        "schema_version": "dwarpal-plan-v1",
        "case_id": case_id.upper(),
        "request": request.strip(),
        "proposed_action": "Prepare a home-service visit",
        "door_id": door_id,
        "reason": "One-time approval for the exact previewed home-service plan",
        "scope": {"max_entries": 1, "valid_for_minutes": 15, "mode": "PREVIEW_ONLY_NOT_ENFORCED"},
        "target_resource": f"door:{door_id}",
    }
    action_hash = canonical_plan_digest(plan)
    run_id = uuid.uuid4().hex[:16]
    created_at = datetime.now(timezone.utc).isoformat()
    plan_json = json.dumps(plan, sort_keys=True)
    con = _db()
    con.execute("""INSERT INTO workflow_previews(run_id,case_id,request,action_hash,status,created_at,plan_json,result_json)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (run_id, case_id.upper(), request.strip(), action_hash, "AWAITING_HUMAN_APPROVAL", created_at, plan_json, "{}"))
    con.commit()
    con.close()
    return {"run_id": run_id, "action_hash": action_hash, "status": "AWAITING_HUMAN_APPROVAL", "created_at": created_at, "plan": plan}

def get_workflow_preview(run_id: str):
    con = _db()
    row = con.execute("SELECT * FROM workflow_previews WHERE run_id = ?", (run_id,)).fetchone()
    con.close()
    if not row:
        return None
    d = dict(row)
    if d.get("plan_json"):
        try:
            d["plan"] = json.loads(d["plan_json"])
        except Exception:
            d["plan"] = {}
    return d

def finish_workflow_preview(run_id: str, status: str, result: dict) -> bool:
    """Atomically transition status from AWAITING_HUMAN_APPROVAL to finalized status."""
    con = _db()
    cursor = con.execute(
        "UPDATE workflow_previews SET status = ?, result_json = ? WHERE run_id = ? AND status = 'AWAITING_HUMAN_APPROVAL'",
        (status, json.dumps(result, sort_keys=True), run_id)
    )
    updated = cursor.rowcount > 0
    con.commit()
    con.close()
    return updated

