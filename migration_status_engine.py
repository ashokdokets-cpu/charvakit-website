"""
migration_status_engine.py - Session 108F

Tracks which migration files have been applied to the DB.
Does NOT auto-run migrations on startup. Provides:
  - List of all migration files
  - Applied vs pending status
  - Manual "apply" function (called from admin UI)

Safety:
  - Never runs on startup
  - Requires explicit admin action to apply
  - Logs every applied migration
  - Idempotent (ON CONFLICT DO NOTHING on the tracking table)
"""

import os
import glob
import hashlib
import logging
from datetime import datetime, timezone

from database import db

logger = logging.getLogger(__name__)


class MigrationStatusEngine:
    """Tracks migration file status."""

    MIGRATIONS_DIR = "migrations"

    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        """Create tracking table if migration not yet applied."""
        try:
            conn = db.get_pooled_connection()
            if not conn:
                return
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_schema_migrations (
                    migration_name TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    applied_by TEXT DEFAULT 'manual',
                    checksum TEXT,
                    notes TEXT
                )
            """)
            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)
        except Exception as e:
            logger.warning(f"migration_status_engine._ensure_table: {e}")

    def _get_migration_files(self):
        """Return list of migration filenames (sorted)."""
        pattern = os.path.join(self.MIGRATIONS_DIR, "*.sql")
        files = sorted([os.path.basename(p) for p in glob.glob(pattern)])
        return files

    def _get_applied_migrations(self):
        """Return dict {filename: metadata}."""
        try:
            conn = db.get_pooled_connection()
            if not conn:
                return {}
            cur = conn.cursor()
            cur.execute("""
                SELECT migration_name, applied_at, applied_by, notes
                FROM charvak_schema_migrations
                ORDER BY migration_name
            """)
            rows = cur.fetchall()
            cur.close()
            db.release_pooled_connection(conn)
            return {
                r[0]: {
                    "applied_at": r[1].isoformat() if r[1] else None,
                    "applied_by": r[2],
                    "notes": r[3],
                }
                for r in rows
            }
        except Exception as e:
            logger.warning(f"migration_status_engine._get_applied: {e}")
            return {}

    def list_migrations(self):
        """Return all migrations with status."""
        files = self._get_migration_files()
        applied = self._get_applied_migrations()
        result = []
        for f in files:
            is_applied = f in applied
            result.append({
                "name": f,
                "applied": is_applied,
                "applied_at": applied[f]["applied_at"] if is_applied else None,
                "applied_by": applied[f]["applied_by"] if is_applied else None,
                "notes": applied[f]["notes"] if is_applied else None,
            })
        total = len(result)
        applied_count = sum(1 for r in result if r["applied"])
        pending_count = sum(1 for r in result if not r["applied"])
        return {
            "status": "success",
            "total": total,
            "applied_count": applied_count,
            "pending_count": pending_count,
            "migrations": result,
        }

    def apply_migration(self, name, applied_by="admin"):
        """Apply a specific migration. Idempotent — safe to call twice."""
        if name not in self._get_migration_files():
            return {"status": "error", "message": f"Migration file not found: {name}"}

        filepath = os.path.join(self.MIGRATIONS_DIR, name)
        conn = None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                sql_content = f.read()

            checksum = hashlib.sha256(sql_content.encode("utf-8")).hexdigest()[:16]

            conn = db.get_pooled_connection()
            if not conn:
                return {"status": "error", "message": "DB unavailable"}

            cur = conn.cursor()

            # Check if already applied
            cur.execute(
                "SELECT migration_name FROM charvak_schema_migrations WHERE migration_name = %s",
                (name,)
            )
            if cur.fetchone():
                cur.close()
                db.release_pooled_connection(conn)
                return {"status": "success", "message": f"Already applied: {name}", "already_applied": True}

            # Execute the migration SQL
            cur.execute(sql_content)
            conn.commit()

            # Record in tracking table
            cur.execute("""
                INSERT INTO charvak_schema_migrations
                    (migration_name, applied_by, checksum, notes)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (migration_name) DO NOTHING
            """, (name, applied_by, checksum, f"Applied via admin UI at {datetime.now(timezone.utc).isoformat()}"))
            conn.commit()

            cur.close()
            db.release_pooled_connection(conn)

            logger.info(f"Migration applied: {name} by {applied_by}")
            return {"status": "success", "message": f"Applied: {name}", "checksum": checksum}

        except Exception as e:
            logger.error(f"Migration failed: {name} - {e}", exc_info=True)
            try:
                if conn:
                    conn.rollback()
                    db.release_pooled_connection(conn)
            except Exception:
                pass
            return {"status": "error", "message": f"Migration failed: {str(e)[:300]}"}

    def log_pending_on_startup(self):
        """Log warning if pending migrations exist. Does NOT apply them."""
        try:
            status = self.list_migrations()
            pending = status["pending_count"]
            total = status["total"]
            if pending > 0:
                logger.warning(f"[MIGRATIONS] {pending} pending migration(s) — apply at /admin/migrations")
            else:
                logger.info(f"[MIGRATIONS] All {total} migrations applied")
        except Exception as e:
            logger.warning(f"[MIGRATIONS] startup check failed: {e}")


# Singleton
migration_status_engine = MigrationStatusEngine()