"""Small SQLite audit trail for the local demo."""
import os, sqlite3, json, hashlib, uuid
from datetime import datetime, timezone
from pathlib import Path

def _db():
    path = os.getenv("DATABASE_PATH", "./dwarpal_audit.sqlite3")
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS audit (
      id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, principal TEXT NOT NULL,
      action TEXT NOT NULL, resource TEXT NOT NULL, decision TEXT NOT NULL,
      reason TEXT NOT NULL, engine TEXT NOT NULL, details TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS workflow_previews (
      run_id TEXT PRIMARY KEY, case_id TEXT NOT NULL, request TEXT NOT NULL,
      action_hash TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
      result_json TEXT NOT NULL DEFAULT '{}'
    )""")
    con.commit()
    return con

def log_event(principal, action, resource, decision, reason, engine, details=None):
    con = _db()
    ts = datetime.now(timezone.utc).isoformat()
    con.execute("INSERT INTO audit(ts,principal,action,resource,decision,reason,engine,details) VALUES(?,?,?,?,?,?,?,?)",
      (ts, principal, action, resource, "ALLOW" if decision else "DENY", reason, engine, json.dumps(details or {})))
    con.commit()
    con.close()
    return {"timestamp": ts, "decision": "ALLOW" if decision else "DENY"}

def list_events(limit=30):
    con = _db()
    rows = con.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (max(1, min(int(limit),100)),)).fetchall()
    con.close()
    return [dict(r) for r in rows]


def create_workflow_preview(case_id: str, request: str):
    """Persist a one-time preview bound to a canonical plan hash."""
    plan = {
        "case_id": case_id,
        "request": request,
        "proposed_action": "Prepare a home-service visit",
        "door_id": "FRONT-01",
        "scope": {"max_entries": 1, "valid_for_minutes": 15},
    }
    action_hash = hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    run_id = uuid.uuid4().hex[:16]
    created_at = datetime.now(timezone.utc).isoformat()
    con = _db()
    con.execute("INSERT INTO workflow_previews(run_id,case_id,request,action_hash,status,created_at,result_json) VALUES(?,?,?,?,?,?,?)",
                (run_id, case_id, request, action_hash, "AWAITING_HUMAN_APPROVAL", created_at, "{}"))
    con.commit()
    con.close()
    return {"run_id": run_id, "action_hash": action_hash, "status": "AWAITING_HUMAN_APPROVAL", "created_at": created_at, "plan": plan}


def get_workflow_preview(run_id: str):
    con = _db()
    row = con.execute("SELECT * FROM workflow_previews WHERE run_id = ?", (run_id,)).fetchone()
    con.close()
    return dict(row) if row else None


def finish_workflow_preview(run_id: str, status: str, result: dict):
    con = _db()
    con.execute("UPDATE workflow_previews SET status = ?, result_json = ? WHERE run_id = ?",
                (status, json.dumps(result, sort_keys=True), run_id))
    con.commit()
    con.close()
