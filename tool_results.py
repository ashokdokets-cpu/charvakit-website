"""tool_results.py - persistence helper for AI Tools Suite runs.

Every successful tool call INSERTs one row here. Non-fatal on failure:
if the table is missing or the DB is down, the tool still returns its
result to the user. This is intentional - persistence is nice-to-have,
not a hard dependency.

Run the migration first:
    migrations/20260929_tool_results.sql
"""

import json
import logging
import secrets
from typing import Any, Dict, Optional

logger = logging.getLogger("charvakit.tool_results")

_ENSURED = False


def _ensure_table():
    """Idempotent table create on first use."""
    global _ENSURED
    if _ENSURED:
        return
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_tool_results (
                result_id     TEXT PRIMARY KEY,
                email         TEXT NOT NULL,
                tool_name     TEXT NOT NULL,
                inputs_json   JSONB,
                result_json   JSONB,
                credits_used  INTEGER NOT NULL DEFAULT 0,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close(); conn.close()
        _ENSURED = True
    except Exception as e:
        logger.warning(f"tool_results._ensure_table failed (non-fatal): {e}")


def record_tool_result(
    email: str,
    tool_name: str,
    inputs: Dict[str, Any],
    result: Dict[str, Any],
    credits_used: int = 0,
) -> Optional[str]:
    """Insert one tool run. Returns result_id or None on failure.

    Never raises. The tool call that triggered this must not fail just
    because persistence failed.
    """
    _ensure_table()
    try:
        from database import db
        result_id = f"TR-{secrets.token_hex(6).upper()}"

        # Strip email from the stored inputs (it's already the PK column)
        clean_inputs = {k: v for k, v in (inputs or {}).items() if k != "email"}

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO charvak_tool_results
                (result_id, email, tool_name, inputs_json, result_json, credits_used)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            result_id,
            email,
            tool_name,
            json.dumps(clean_inputs, default=str),
            json.dumps(result or {}, default=str),
            int(credits_used or 0),
        ))
        conn.commit()
        cur.close(); conn.close()
        return result_id
    except Exception as e:
        logger.warning(f"tool_results.record_tool_result failed for {tool_name}: {e}")
        return None


def get_tool_history(email: str, limit: int = 100) -> list:
    """Return the user's most recent tool runs, newest first."""
    _ensure_table()
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT result_id, tool_name, inputs_json, result_json,
                   credits_used, created_at
            FROM charvak_tool_results
            WHERE email = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (email, int(limit)))
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [
            {
                "result_id": r[0],
                "tool_name": r[1],
                "inputs": r[2] or {},
                "result": r[3] or {},
                "credits_used": r[4],
                "created_at": r[5].isoformat() if r[5] else None,
            }
            for r in rows
        ]
    except Exception as e:
        logger.warning(f"tool_results.get_tool_history failed: {e}")
        return []
