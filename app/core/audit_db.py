import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "audit_trail.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_trail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            raw_input TEXT NOT NULL,
            num_final_results INTEGER NOT NULL,
            num_flagged INTEGER NOT NULL,
            audit_log_json TEXT NOT NULL,
            final_results_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_audit_entry(raw_input: str, final_results: list[dict], audit_log: list[dict]):
    conn = sqlite3.connect(DB_PATH)
    num_flagged = sum(1 for r in final_results if r["show_as"] == "verify_with_local_office")

    conn.execute(
        """INSERT INTO audit_trail
           (timestamp, raw_input, num_final_results, num_flagged, audit_log_json, final_results_json)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            datetime.now(timezone.utc).isoformat(),
            raw_input,
            len(final_results),
            num_flagged,
            json.dumps(audit_log),
            json.dumps(final_results),
        ),
    )
    conn.commit()
    conn.close()