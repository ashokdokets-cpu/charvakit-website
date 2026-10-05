"""
Assessment Integrity Engine (Session 27, Anti-Cheating Layer A).

Records deterministic environment signals during an assessment:
- paste events (with byte count)
- tab switches (window blur / visibilitychange)
- contextmenu (right-click)
- focus_out (input loses focus mid-answer)
- rapid_input (synthetic typing detection)

Design principles:
- RECORD ONLY. We never block. Employers decide.
- Deterministic signals only. No ML, no behavioral analytics (that's Layer C).
- Self-healing DDL. No manual migration required.
- The engine is stateless between calls; all state lives in Postgres.

Provides:
- record_event(assessment_id, email, event_type, metadata) -> dict
- get_events(assessment_id, limit=500) -> list
- get_summary(assessment_id) -> dict with counts + risk_level
- compute_risk_level(counts) -> "clean"|"minor"|"moderate"|"elevated"
- update_parent_summary(assessment_id) -> writes integrity_summary to parent
- _ensure_tables() (self-healing DDL)
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Recognised event types. Anything else is recorded but counted as "other".
VALID_EVENT_TYPES = {
    "paste",
    "tab_switch",
    "contextmenu",
    "focus_out",
    "rapid_input",
}

# Risk thresholds (total events across the whole assessment).
RISK_MINOR = 1
RISK_MODERATE = 6
RISK_ELEVATED = 16

# Specific high-signal combos that always elevate risk regardless of count.
HIGH_SIGNAL_PASTE_THRESHOLD = 2      # 2+ pastes into free-text
HIGH_SIGNAL_TAB_SWITCH_THRESHOLD = 3  # 3+ tab switches


class IntegrityEngine:
    def __init__(self):
        self._tables_ready = False

    # ---------------------------------------------------------------- schema

    def _ensure_tables(self) -> None:
        """Self-healing DDL. Idempotent. Called before any read/write."""
        if self._tables_ready:
            return
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Detailed event log — one row per event.
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS charvak_assessment_integrity_events (
                    event_id      TEXT PRIMARY KEY,
                    assessment_id TEXT NOT NULL,
                    email         TEXT NOT NULL,
                    event_type    TEXT NOT NULL,
                    metadata      JSONB DEFAULT '{}'::jsonb,
                    occurred_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_integrity_events_assessment
                    ON charvak_assessment_integrity_events (assessment_id, occurred_at DESC)
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_integrity_events_email
                    ON charvak_assessment_integrity_events (email)
                """
            )

            # Fast-display summary on the parent assessment row.
            cur.execute(
                """
                ALTER TABLE charvak_career_assessments
                    ADD COLUMN IF NOT EXISTS integrity_summary JSONB DEFAULT '{}'::jsonb
                """
            )

            conn.commit()
            cur.close()
            conn.close()
            self._tables_ready = True
            logger.info("[integrity] tables ready")
        except Exception as e:
            logger.warning(f"[integrity] _ensure_tables failed: {e}")

    # ---------------------------------------------------------------- write

    def record_event(
        self,
        assessment_id: str,
        email: str,
        event_type: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Record one integrity event. Returns {status, event_id} or error.
        Caller is responsible for verifying the assessment belongs to email.
        """
        assessment_id = (assessment_id or "").strip()
        email = (email or "").strip().lower()
        event_type = (event_type or "").strip()

        if not assessment_id or not email or not event_type:
            return {"status": "error", "message": "assessment_id, email, event_type required"}

        if event_type not in VALID_EVENT_TYPES:
            # Record it anyway, but tag it so we can audit the frontend later.
            metadata = dict(metadata or {})
            metadata["_unrecognized_type"] = True

        self._ensure_tables()
        event_id = "INT-" + uuid.uuid4().hex[:12].upper()

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO charvak_assessment_integrity_events
                    (event_id, assessment_id, email, event_type, metadata, occurred_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    event_id,
                    assessment_id,
                    email,
                    event_type,
                    json.dumps(metadata or {}),
                    datetime.utcnow(),
                ),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.warning(f"[integrity] record_event failed: {e}")
            return {"status": "error", "message": str(e)}

        # Keep the parent summary in sync (best-effort).
        try:
            self.update_parent_summary(assessment_id)
        except Exception as e:
            logger.warning(f"[integrity] summary update failed (non-fatal): {e}")

        return {"status": "success", "event_id": event_id}

    # ---------------------------------------------------------------- read

    def get_events(self, assessment_id: str, limit: int = 500) -> List[Dict]:
        """Return all events for an assessment, newest first."""
        self._ensure_tables()
        assessment_id = (assessment_id or "").strip()
        if not assessment_id:
            return []

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT event_id, event_type, metadata, occurred_at
                FROM charvak_assessment_integrity_events
                WHERE assessment_id = %s
                ORDER BY occurred_at DESC
                LIMIT %s
                """,
                (assessment_id, limit),
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            logger.warning(f"[integrity] get_events failed: {e}")
            return []

        out = []
        for r in rows:
            out.append(
                {
                    "event_id": r[0],
                    "event_type": r[1],
                    "metadata": r[2] if isinstance(r[2], dict) else json.loads(r[2] or "{}"),
                    "occurred_at": r[3].isoformat() if r[3] else None,
                }
            )
        return out

    def get_summary(self, assessment_id: str) -> Dict:
        """
        Return a summary dict: counts per event type + total + risk_level.
        Reads from the events table directly (source of truth).
        """
        self._ensure_tables()
        assessment_id = (assessment_id or "").strip()
        if not assessment_id:
            return {"status": "error", "message": "assessment_id required"}

        counts = {
            "paste": 0,
            "tab_switch": 0,
            "contextmenu": 0,
            "focus_out": 0,
            "rapid_input": 0,
            "other": 0,
        }
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT event_type, COUNT(*)
                FROM charvak_assessment_integrity_events
                WHERE assessment_id = %s
                GROUP BY event_type
                """,
                (assessment_id,),
            )
            for etype, cnt in cur.fetchall():
                if etype in counts:
                    counts[etype] = int(cnt)
                else:
                    counts["other"] += int(cnt)
            cur.close()
            conn.close()
        except Exception as e:
            logger.warning(f"[integrity] get_summary failed: {e}")
            return {"status": "error", "message": str(e)}

        total = sum(counts.values())
        risk = self.compute_risk_level(counts)

        return {
            "status": "success",
            "assessment_id": assessment_id,
            "counts": counts,
            "total_events": total,
            "risk_level": risk,
            "computed_at": datetime.utcnow().isoformat(),
        }

    # ---------------------------------------------------------------- risk

    def compute_risk_level(self, counts: Dict) -> str:
        """
        Deterministic risk classification.

        clean:    0 events
        minor:    1-5 events
        moderate: 6-15 events
        elevated: >15 events OR (>=3 tab switches + >=2 pastes)
        """
        total = sum(v for v in counts.values() if isinstance(v, int))

        if total == 0:
            return "clean"
        if total > RISK_ELEVATED - 1:
            return "elevated"

        pastes = counts.get("paste", 0)
        tabs = counts.get("tab_switch", 0)
        if tabs >= HIGH_SIGNAL_TAB_SWITCH_THRESHOLD and pastes >= HIGH_SIGNAL_PASTE_THRESHOLD:
            return "elevated"
        if total >= RISK_MODERATE:
            return "moderate"
        if total >= RISK_MINOR:
            return "minor"
        return "clean"

    # ---------------------------------------------------------------- summary writeback

    def update_parent_summary(self, assessment_id: str) -> Dict:
        """
        Write the computed summary to charvak_career_assessments.integrity_summary.
        Called after every record_event (best-effort).
        """
        summary = self.get_summary(assessment_id)
        if summary.get("status") != "success":
            return summary

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE charvak_career_assessments
                SET integrity_summary = %s::jsonb
                WHERE assessment_id = %s
                """,
                (json.dumps(summary), assessment_id),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.warning(f"[integrity] update_parent_summary failed: {e}")
            return {"status": "error", "message": str(e)}

        return summary


# Singleton, matching the codebase convention (see ai_credit_engine, payment_engine).
integrity_engine = IntegrityEngine()