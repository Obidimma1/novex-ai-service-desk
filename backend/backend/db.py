import sqlite3
from typing import Optional, Dict, Any
from datetime import datetime

DB_PATH = "novex.db"

def _conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            stage TEXT,
            machine_name TEXT,
            state TEXT,
            updated_at TEXT
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            event_type TEXT,
            payload TEXT,
            created_at TEXT
        )
        """)
        c.commit()

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    with _conn() as c:
        row = c.execute(
            "SELECT session_id, stage, machine_name, state FROM sessions WHERE session_id=?",
            (session_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "session_id": row[0],
            "stage": row[1],
            "machine_name": row[2],
            "state": row[3]
        }

def save_session(session_id: str, stage: str, machine_name: str, state: str):
    with _conn() as c:
        c.execute("""
        INSERT INTO sessions (session_id, stage, machine_name, state, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            stage=excluded.stage,
            machine_name=excluded.machine_name,
            state=excluded.state,
            updated_at=excluded.updated_at
        """, (session_id, stage, machine_name, state, datetime.utcnow().isoformat()))
        c.commit()

def log_event(session_id: str, event_type: str, payload: str):
    with _conn() as c:
        c.execute("""
        INSERT INTO audit_logs (session_id, event_type, payload, created_at)
        VALUES (?, ?, ?, ?)
        """, (session_id, event_type, payload, datetime.utcnow().isoformat()))
        c.commit()
