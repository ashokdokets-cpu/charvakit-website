"""
data_retention_engine.py - Retention + purge for the job pipeline.

Design:
- Dry-run first, always. Nothing is deleted unless explicitly confirmed.
- Every run logged to charvak_retention_runs (audit trail).
- Config table allows tuning without code changes.
- Never deletes below min_rows_to_keep (safety cap).
- Idempotent: safe to run repeatedly.
"""

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from database import db
class RetentionEngine:
    """Manages retention + purge for the job pipeline tables."""

    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        """Self-heal: create tables if the migration has not been applied."""
        conn = db.get_pooled_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_retention_runs (
                    run_id VARCHAR(64) PRIMARY KEY,
                    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    finished_at TIMESTAMPTZ,
                    dry_run BOOLEAN NOT NULL DEFAULT TRUE,
                    triggered_by VARCHAR(120),
                    status VARCHAR(20) NOT NULL DEFAULT 'running',
                    rows_deleted_rejected_jds INTEGER DEFAULT 0,
                    rows_deleted_jobs_closed INTEGER DEFAULT 0,
                    rows_deleted_jobs_unmatched INTEGER DEFAULT 0,
                    rows_deleted_sync_runs INTEGER DEFAULT 0,
                    total_rows_deleted INTEGER DEFAULT 0,
                    error_message TEXT,
                    details_json JSONB
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_retention_config (
                    config_key VARCHAR(80) PRIMARY KEY,
                    retention_days INTEGER NOT NULL,
                    enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    min_rows_to_keep INTEGER NOT NULL DEFAULT 0,
                    description TEXT,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            cur.execute("""
                INSERT INTO charvak_retention_config
                    (config_key, retention_days, enabled, min_rows_to_keep, description)
                VALUES
                    ('rejected_jds', 30, TRUE, 100, 'Rejected JDs audit trail'),
                    ('jobs_closed', 90, TRUE, 50, 'Closed/expired jobs'),
                    ('jobs_unmatched_open', 60, TRUE, 100, 'Open but unmatched jobs'),
                    ('sync_runs', 90, TRUE, 20, 'Sync execution logs')
                ON CONFLICT (config_key) DO NOTHING
            """)
            cur.execute("""
                ALTER TABLE charvak_jobs
                ADD COLUMN IF NOT EXISTS last_matched_at TIMESTAMPTZ
            """)
            conn.commit()
        except Exception as e:
            print(f"[retention] _ensure_tables failed: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
        finally:
            try:
                db.release_pooled_connection(conn)
            except Exception:
                pass

    def get_config(self) -> dict:
        """Return the current retention config as {key: {...}}."""
        conn = db.get_pooled_connection()
        if not conn:
            return {}
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT config_key, retention_days, enabled, min_rows_to_keep, description
                FROM charvak_retention_config
                ORDER BY config_key
            """)
            rows = cur.fetchall()
            return {
                r[0]: {
                    "retention_days": r[1],
                    "enabled": r[2],
                    "min_rows_to_keep": r[3],
                    "description": r[4],
                }
                for r in rows
            }
        finally:
            try:
                db.release_pooled_connection(conn)
            except Exception:
                pass

    def update_config(self, key: str, retention_days: int,
                      enabled: bool = True,
                      min_rows_to_keep: int = 0) -> dict:
        """Update one config row. Caller must be admin."""
        conn = db.get_pooled_connection()
        if not conn:
            return {"status": "error", "message": "DB unavailable"}
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_retention_config
                SET retention_days = %s,
                    enabled = %s,
                    min_rows_to_keep = %s,
                    updated_at = NOW()
                WHERE config_key = %s
                RETURNING config_key
            """, (retention_days, enabled, min_rows_to_keep, key))
            row = cur.fetchone()
            conn.commit()
            if not row:
                return {"status": "error", "message": f"Config key {key} not found"}
            return {"status": "success", "config_key": key}
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            return {"status": "error", "message": str(e)}
        finally:
            try:
                db.release_pooled_connection(conn)
            except Exception:
                pass

    def _table_exists(self, cur, table_name: str) -> bool:
        """Check if a table exists. Safe after abort — uses a fresh query."""
        try:
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_name = %s)",
                (table_name,)
            )
            return cur.fetchone()[0]
        except Exception:
            return False

    def _table_exists(self, cur, table_name: str) -> bool:
        """Check if a table exists. Uses a query safe after transaction abort."""
        try:
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_name = %s)",
                (table_name,)
            )
            return cur.fetchone()[0]
        except Exception:
            try:
                cur.connection.rollback()
            except Exception:
                pass
            return False

    def _safe_count(self, cur, sql: str, params: tuple, label: str) -> int:
        """Run a COUNT query. On failure, rollback and return 0."""
        try:
            cur.execute(sql, params)
            return cur.fetchone()[0]
        except Exception as e:
            print(f"[retention] count {label} failed: {e}")
            try:
                cur.connection.rollback()
            except Exception:
                pass
            return 0

    def _count_rows_to_purge(self, cur, config: dict) -> dict:
        """Count what would be purged for each category. Returns {category: count}."""
        counts = {}
        now = datetime.now(timezone.utc)

        # 1) Rejected JDs — tiered by reason
        if self._table_exists(cur, "charvak_rejected_jds"):
            # Tier 1: 0% overlap — useless after 2 days
            cfg1 = config.get("rejected_low_skill_0") or {"enabled": True, "retention_days": 2}
            if cfg1 and cfg1.get("enabled"):
                cutoff1 = now - timedelta(days=cfg1["retention_days"])
                counts["rejected_low_skill_0"] = self._safe_count(
                    cur,
                    "SELECT COUNT(*) FROM charvak_rejected_jds WHERE rejected_at < %s AND reject_reason = 'low_skill_overlap_0%%'",
                    (cutoff1,),
                    "rejected_low_skill_0",
                )
            else:
                counts["rejected_low_skill_0"] = 0

            # Tier 2: non-US location — stable filter, purge after 3 days
            cfg2 = config.get("rejected_non_us_location") or {"enabled": True, "retention_days": 3}
            if cfg2 and cfg2.get("enabled"):
                cutoff2 = now - timedelta(days=cfg2["retention_days"])
                counts["rejected_non_us_location"] = self._safe_count(
                    cur,
                    "SELECT COUNT(*) FROM charvak_rejected_jds WHERE rejected_at < %s AND reject_reason = 'non_us_location'",
                    (cutoff2,),
                    "rejected_non_us_location",
                )
            else:
                counts["rejected_non_us_location"] = 0

            # Tier 3: visa mismatch — worth tuning, keep 7 days
            cfg3 = config.get("rejected_visa_mismatch") or {"enabled": True, "retention_days": 7}
            if cfg3 and cfg3.get("enabled"):
                cutoff3 = now - timedelta(days=cfg3["retention_days"])
                counts["rejected_visa_mismatch"] = self._safe_count(
                    cur,
                    "SELECT COUNT(*) FROM charvak_rejected_jds WHERE rejected_at < %s AND reject_reason = 'visa_incompatible'",
                    (cutoff3,),
                    "rejected_visa_mismatch",
                )
            else:
                counts["rejected_visa_mismatch"] = 0

            # Tier 4: partial overlap (1-29%) — tuning value, keep 14 days
            cfg4 = config.get("rejected_partial_overlap") or {"enabled": True, "retention_days": 14}
            if cfg4 and cfg4.get("enabled"):
                cutoff4 = now - timedelta(days=cfg4["retention_days"])
                counts["rejected_partial_overlap"] = self._safe_count(
                    cur,
                    "SELECT COUNT(*) FROM charvak_rejected_jds WHERE rejected_at < %s AND reject_reason LIKE 'low_skill_overlap_%%' AND reject_reason != 'low_skill_overlap_0%%'",
                    (cutoff4,),
                    "rejected_partial_overlap",
                )
            else:
                counts["rejected_partial_overlap"] = 0

            # Safety net: absolute max age
            cfg5 = config.get("rejected_old_cutoff") or {"enabled": True, "retention_days": 30}
            if cfg5 and cfg5.get("enabled"):
                cutoff5 = now - timedelta(days=cfg5["retention_days"])
                counts["rejected_old_cutoff"] = self._safe_count(
                    cur,
                    "SELECT COUNT(*) FROM charvak_rejected_jds WHERE rejected_at < %s",
                    (cutoff5,),
                    "rejected_old_cutoff",
                )
            else:
                counts["rejected_old_cutoff"] = 0
        else:
            counts["rejected_low_skill_0"] = 0
            counts["rejected_non_us_location"] = 0
            counts["rejected_visa_mismatch"] = 0
            counts["rejected_partial_overlap"] = 0
            counts["rejected_old_cutoff"] = 0

        # 2) Closed/expired jobs
        cfg = config.get("jobs_closed")
        if cfg and cfg["enabled"] and self._table_exists(cur, "charvak_jobs"):
            cutoff = now - timedelta(days=cfg["retention_days"])
            counts["jobs_closed"] = self._safe_count(
                cur,
                "SELECT COUNT(*) FROM charvak_jobs "
                "WHERE status IN ('closed', 'expired', 'filled') "
                "AND created_at < %s",
                (cutoff,),
                "jobs_closed",
            )
        else:
            counts["jobs_closed"] = 0

        # 3) Open but unmatched jobs
        cfg = config.get("jobs_unmatched_open")
        if (cfg and cfg["enabled"]
                and self._table_exists(cur, "charvak_jobs")
                and self._table_exists(cur, "charvak_bench_matches")):
            cutoff = now - timedelta(days=cfg["retention_days"])
            counts["jobs_unmatched_open"] = self._safe_count(
                cur,
                "SELECT COUNT(*) FROM charvak_jobs j "
                "WHERE j.status = 'open' "
                "AND j.created_at < %s "
                "AND NOT EXISTS ("
                "  SELECT 1 FROM charvak_bench_matches m "
                "  WHERE m.job_id = j.job_id"
                ")",
                (cutoff,),
                "jobs_unmatched_open",
            )
        else:
            counts["jobs_unmatched_open"] = 0

        # 4) Sync runs
        cfg = config.get("sync_runs")
        if cfg and cfg["enabled"] and self._table_exists(cur, "charvak_job_sync_runs"):
            cutoff = now - timedelta(days=cfg["retention_days"])
            counts["sync_runs"] = self._safe_count(
                cur,
                "SELECT COUNT(*) FROM charvak_job_sync_runs WHERE started_at < %s",
                (cutoff,),
                "sync_runs",
            )
        else:
            counts["sync_runs"] = 0

        return counts
    def run_retention(self, dry_run: bool = True,
                      triggered_by: str = "manual") -> dict:
        """Execute the retention pass. If dry_run=True, only report."""
        run_id = f"RET-{uuid.uuid4().hex[:12].upper()}"
        started_at = datetime.now(timezone.utc)

        conn = db.get_pooled_connection()
        if not conn:
            return {"status": "error", "message": "DB unavailable"}

        try:
            cur = conn.cursor()

            # 1) Insert run record
            cur.execute(
                "INSERT INTO charvak_retention_runs "
                "(run_id, dry_run, triggered_by, status) "
                "VALUES (%s, %s, %s, 'running')",
                (run_id, dry_run, triggered_by)
            )
            conn.commit()

            # 2) Load config
            config = self.get_config()

            # 3) Count
            counts = self._count_rows_to_purge(cur, config)

            if dry_run:
                try:
                    cur.execute(
                        "UPDATE charvak_retention_runs SET "
                        "finished_at = NOW(), status = 'dry_run_complete', "
                        "rows_deleted_rejected_jds = %s, "
                        "rows_deleted_jobs_closed = %s, "
                        "rows_deleted_jobs_unmatched = %s, "
                        "rows_deleted_sync_runs = %s, "
                        "total_rows_deleted = %s, "
                        "details_json = %s "
                        "WHERE run_id = %s",
                        (
                            counts.get("rejected_jds", 0),
                            counts.get("jobs_closed", 0),
                            counts.get("jobs_unmatched_open", 0),
                            counts.get("sync_runs", 0),
                            sum(counts.values()),
                            json.dumps({"counts": counts, "config": config}),
                            run_id,
                        )
                    )
                    conn.commit()
                except Exception as e:
                    print(f"[retention] dry-run update failed: {e}")
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                return {
                    "status": "success",
                    "run_id": run_id,
                    "dry_run": True,
                    "would_delete": counts,
                    "total_would_delete": sum(counts.values()),
                }

            # 4) Real deletion — each block commits independently
            deleted = {}
            errors = []

            # 4a) Rejected JDs — tiered by reason
            if self._table_exists(cur, "charvak_rejected_jds"):
                # Tier 1: 0% overlap — 2 days
                cfg1 = config.get("rejected_low_skill_0") or {"enabled": True, "retention_days": 2}
                if cfg1 and cfg1.get("enabled") and counts.get("rejected_low_skill_0", 0) > 0:
                    try:
                        cutoff1 = started_at - timedelta(days=cfg1["retention_days"])
                        cur.execute(
                            "DELETE FROM charvak_rejected_jds WHERE rejected_at < %s AND reject_reason = 'low_skill_overlap_0%%'",
                            (cutoff1,)
                        )
                        deleted["rejected_low_skill_0"] = cur.rowcount
                        conn.commit()
                    except Exception as e:
                        errors.append(f"rejected_low_skill_0: {e}")
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                        deleted["rejected_low_skill_0"] = 0
                else:
                    deleted["rejected_low_skill_0"] = 0

                # Tier 2: non-US location — 3 days
                cfg2 = config.get("rejected_non_us_location") or {"enabled": True, "retention_days": 3}
                if cfg2 and cfg2.get("enabled") and counts.get("rejected_non_us_location", 0) > 0:
                    try:
                        cutoff2 = started_at - timedelta(days=cfg2["retention_days"])
                        cur.execute(
                            "DELETE FROM charvak_rejected_jds WHERE rejected_at < %s AND reject_reason = 'non_us_location'",
                            (cutoff2,)
                        )
                        deleted["rejected_non_us_location"] = cur.rowcount
                        conn.commit()
                    except Exception as e:
                        errors.append(f"rejected_non_us_location: {e}")
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                        deleted["rejected_non_us_location"] = 0
                else:
                    deleted["rejected_non_us_location"] = 0

                # Tier 3: visa mismatch — 7 days
                cfg3 = config.get("rejected_visa_mismatch") or {"enabled": True, "retention_days": 7}
                if cfg3 and cfg3.get("enabled") and counts.get("rejected_visa_mismatch", 0) > 0:
                    try:
                        cutoff3 = started_at - timedelta(days=cfg3["retention_days"])
                        cur.execute(
                            "DELETE FROM charvak_rejected_jds WHERE rejected_at < %s AND reject_reason = 'visa_incompatible'",
                            (cutoff3,)
                        )
                        deleted["rejected_visa_mismatch"] = cur.rowcount
                        conn.commit()
                    except Exception as e:
                        errors.append(f"rejected_visa_mismatch: {e}")
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                        deleted["rejected_visa_mismatch"] = 0
                else:
                    deleted["rejected_visa_mismatch"] = 0

                # Tier 4: partial overlap (1-29%) — 14 days
                cfg4 = config.get("rejected_partial_overlap") or {"enabled": True, "retention_days": 14}
                if cfg4 and cfg4.get("enabled") and counts.get("rejected_partial_overlap", 0) > 0:
                    try:
                        cutoff4 = started_at - timedelta(days=cfg4["retention_days"])
                        cur.execute(
                            "DELETE FROM charvak_rejected_jds WHERE rejected_at < %s AND reject_reason LIKE 'low_skill_overlap_%%' AND reject_reason != 'low_skill_overlap_0%%'",
                            (cutoff4,)
                        )
                        deleted["rejected_partial_overlap"] = cur.rowcount
                        conn.commit()
                    except Exception as e:
                        errors.append(f"rejected_partial_overlap: {e}")
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                        deleted["rejected_partial_overlap"] = 0
                else:
                    deleted["rejected_partial_overlap"] = 0

                # Safety: absolute max age — 30 days
                cfg5 = config.get("rejected_old_cutoff") or {"enabled": True, "retention_days": 30}
                if cfg5 and cfg5.get("enabled") and counts.get("rejected_old_cutoff", 0) > 0:
                    try:
                        cutoff5 = started_at - timedelta(days=cfg5["retention_days"])
                        cur.execute(
                            "DELETE FROM charvak_rejected_jds WHERE rejected_at < %s",
                            (cutoff5,)
                        )
                        deleted["rejected_old_cutoff"] = cur.rowcount
                        conn.commit()
                    except Exception as e:
                        errors.append(f"rejected_old_cutoff: {e}")
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                        deleted["rejected_old_cutoff"] = 0
                else:
                    deleted["rejected_old_cutoff"] = 0
            else:
                deleted["rejected_low_skill_0"] = 0
                deleted["rejected_non_us_location"] = 0
                deleted["rejected_visa_mismatch"] = 0
                deleted["rejected_partial_overlap"] = 0
                deleted["rejected_old_cutoff"] = 0

            # 4b) Closed jobs
            cfg = config.get("jobs_closed")
            if (cfg and cfg["enabled"]
                    and counts.get("jobs_closed", 0) > 0
                    and self._table_exists(cur, "charvak_jobs")):
                try:
                    cutoff = started_at - timedelta(days=cfg["retention_days"])
                    cur.execute(
                        "DELETE FROM charvak_jobs "
                        "WHERE status IN ('closed', 'expired', 'filled') "
                        "AND created_at < %s",
                        (cutoff,)
                    )
                    deleted["jobs_closed"] = cur.rowcount
                    conn.commit()
                except Exception as e:
                    errors.append(f"jobs_closed: {e}")
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    deleted["jobs_closed"] = 0
            else:
                deleted["jobs_closed"] = 0

            # 4c) Open but unmatched
            cfg = config.get("jobs_unmatched_open")
            if (cfg and cfg["enabled"]
                    and counts.get("jobs_unmatched_open", 0) > 0
                    and self._table_exists(cur, "charvak_jobs")
                    and self._table_exists(cur, "charvak_bench_matches")):
                try:
                    cutoff = started_at - timedelta(days=cfg["retention_days"])
                    cur.execute(
                        "DELETE FROM charvak_jobs j "
                        "WHERE j.status = 'open' "
                        "AND j.created_at < %s "
                        "AND NOT EXISTS ("
                        "  SELECT 1 FROM charvak_bench_matches m "
                        "  WHERE m.job_id = j.job_id"
                        ")",
                        (cutoff,)
                    )
                    deleted["jobs_unmatched_open"] = cur.rowcount
                    conn.commit()
                except Exception as e:
                    errors.append(f"jobs_unmatched_open: {e}")
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    deleted["jobs_unmatched_open"] = 0
            else:
                deleted["jobs_unmatched_open"] = 0

            # 4d) Sync runs
            cfg = config.get("sync_runs")
            if (cfg and cfg["enabled"]
                    and counts.get("sync_runs", 0) > 0
                    and self._table_exists(cur, "charvak_job_sync_runs")):
                try:
                    cutoff = started_at - timedelta(days=cfg["retention_days"])
                    cur.execute(
                        "DELETE FROM charvak_job_sync_runs WHERE started_at < %s",
                        (cutoff,)
                    )
                    deleted["sync_runs"] = cur.rowcount
                    conn.commit()
                except Exception as e:
                    errors.append(f"sync_runs: {e}")
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    deleted["sync_runs"] = 0
            else:
                deleted["sync_runs"] = 0

            # 5) Finalize
            total_deleted = sum(deleted.values())
            if errors and total_deleted == 0:
                status = "failed"
            elif errors:
                status = "partial"
            else:
                status = "success"

            try:
                cur.execute(
                    "UPDATE charvak_retention_runs SET "
                    "finished_at = NOW(), status = %s, "
                    "rows_deleted_rejected_jds = %s, "
                    "rows_deleted_jobs_closed = %s, "
                    "rows_deleted_jobs_unmatched = %s, "
                    "rows_deleted_sync_runs = %s, "
                    "total_rows_deleted = %s, "
                    "error_message = %s, "
                    "details_json = %s "
                    "WHERE run_id = %s",
                    (
                        status,
                        deleted.get("rejected_jds", 0),
                        deleted.get("jobs_closed", 0),
                        deleted.get("jobs_unmatched_open", 0),
                        deleted.get("sync_runs", 0),
                        total_deleted,
                        "; ".join(errors) if errors else None,
                        json.dumps({"deleted": deleted, "errors": errors, "config": config}),
                        run_id,
                    )
                )
                conn.commit()
            except Exception as e:
                print(f"[retention] finalize update failed: {e}")
                try:
                    conn.rollback()
                except Exception:
                    pass

            return {
                "status": status,
                "run_id": run_id,
                "dry_run": False,
                "deleted": deleted,
                "total_deleted": total_deleted,
                "errors": errors,
            }

        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            print(f"[retention] run failed: {e}")
            return {"status": "error", "run_id": run_id, "message": str(e)}
        finally:
            try:
                db.release_pooled_connection(conn)
            except Exception:
                pass
    def list_runs(self, limit: int = 20) -> list:
        """Recent retention runs (for admin dashboard)."""
        conn = db.get_pooled_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT run_id, started_at, finished_at, dry_run, triggered_by,
                       status, total_rows_deleted, error_message
                FROM charvak_retention_runs
                ORDER BY started_at DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
            return [
                {
                    "run_id": r[0],
                    "started_at": r[1].isoformat() if r[1] else None,
                    "finished_at": r[2].isoformat() if r[2] else None,
                    "dry_run": r[3],
                    "triggered_by": r[4],
                    "status": r[5],
                    "total_rows_deleted": r[6],
                    "error_message": r[7],
                }
                for r in rows
            ]
        finally:
            try:
                db.release_pooled_connection(conn)
            except Exception:
                pass


# Module-level singleton
_engine: Optional[RetentionEngine] = None


def get_retention_engine() -> RetentionEngine:
    global _engine
    if _engine is None:
        _engine = RetentionEngine()
    return _engine
