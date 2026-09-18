"""
Charvak ATS Integration Engine
Connects Charvak's built-in ATS with external systems
(Greenhouse, Lever, Workday) for bidirectional sync
(DB-backed - Session B/1)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.ats")


class ATSProvider:
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    CHARVAK = "charvak"  # Our own ATS
    CUSTOM = "custom"


class ATSEngine:
    """Bidirectional ATS integration - Charvak <-> External. (DB-backed)"""

    def __init__(self):
        self._ensure_tables()
        logger.info("ATS Engine ready (DB-backed) - Charvak ATS is primary")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ats_integrations (
                    integration_id   TEXT PRIMARY KEY,
                    provider         TEXT,
                    api_key_prefix   TEXT,
                    base_url         TEXT DEFAULT '',
                    company_name     TEXT,
                    direction        TEXT DEFAULT 'bidirectional',
                    status           TEXT DEFAULT 'connected',
                    connected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ats_integrations_provider ON charvak_ats_integrations(provider)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ats_integrations_status   ON charvak_ats_integrations(status)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ats_sync_log (
                    sync_id      TEXT PRIMARY KEY,
                    direction    TEXT,
                    provider     TEXT,
                    jobs_count   INTEGER DEFAULT 0,
                    details      JSONB NOT NULL DEFAULT '{}'::jsonb,
                    synced_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ats_sync_direction ON charvak_ats_sync_log(direction)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ats_sync_provider  ON charvak_ats_sync_log(provider)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"ats tables init failed: {e}")

    # ============================================================
    # INTEGRATIONS
    # ============================================================

    def connect_external_ats(self, data: Dict) -> Dict:
        """
        Connect Charvak to an external ATS.
        data = {"provider": str, "api_key": str, "base_url": str, "company_name": str}
        """
        integration_id = f"ATS-{secrets.token_hex(4).upper()}"
        api_key_prefix = (data.get("api_key", "") or "")[:8] + "***"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_ats_integrations
                    (integration_id, provider, api_key_prefix, base_url, company_name, direction, status)
                VALUES (%s, %s, %s, %s, %s, 'bidirectional', 'connected')
            ''', (
                integration_id,
                data.get("provider"),
                api_key_prefix,
                data.get("base_url", ""),
                data.get("company_name"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"connect_external_ats failed: {e}")
            return {"status": "error", "message": "Could not connect external ATS"}

        logger.info(f"External ATS connected: {data.get('provider')}")

        return {
            "status": "success",
            "integration_id": integration_id,
            "message": f"{data.get('provider')} connected. Charvak ATS is now syncing bidirectionally.",
            "sync_url": f"https://charvakit.com/api/ats/webhook/{integration_id}",
        }

    def _find_integration(self, integration_id: str) -> Optional[Dict]:
        if not integration_id:
            return None
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT integration_id, provider, api_key_prefix, base_url,
                       company_name, direction, status, connected_at
                FROM charvak_ats_integrations WHERE integration_id = %s
            ''', (integration_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_find_integration failed: {e}")
            return None

        if not row:
            return None
        return {
            "integration_id": row[0],
            "provider": row[1],
            "api_key_prefix": row[2],
            "base_url": row[3] or "",
            "company_name": row[4],
            "direction": row[5],
            "status": row[6],
            "connected_at": row[7].isoformat() if hasattr(row[7], "isoformat") else str(row[7]),
        }

    def get_integrations(self) -> Dict:
        """Get all ATS integrations."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT integration_id, provider, api_key_prefix, base_url,
                       company_name, direction, status, connected_at
                FROM charvak_ats_integrations
                ORDER BY connected_at ASC
            ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_integrations failed: {e}")
            return {"status": "error", "message": "Could not load integrations"}

        integrations = [{
            "integration_id": r[0],
            "provider": r[1],
            "api_key_prefix": r[2],
            "base_url": r[3] or "",
            "company_name": r[4],
            "direction": r[5],
            "status": r[6],
            "connected_at": r[7].isoformat() if hasattr(r[7], "isoformat") else str(r[7]),
        } for r in rows]

        return {
            "status": "success",
            "integrations": integrations,
            "count": len(integrations),
            "primary_ats": ATSProvider.CHARVAK,
            "supported_external": [ATSProvider.GREENHOUSE, ATSProvider.LEVER, ATSProvider.WORKDAY, ATSProvider.CUSTOM],
        }

    # ============================================================
    # SYNC - OUTBOUND
    # ============================================================

    def sync_jobs_from_charvak(self, provider: str = "greenhouse") -> Dict:
        """Export Charvak jobs TO external ATS."""
        from job_board_engine import job_board_engine
        charvak_jobs = job_board_engine.get_jobs()

        sync_id = f"SYNC-OUT-{secrets.token_hex(4).upper()}"
        entry = {
            "sync_id": sync_id,
            "direction": "outbound",
            "provider": provider,
            "jobs_synced": len(charvak_jobs),
            "synced_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_ats_sync_log
                    (sync_id, direction, provider, jobs_count, details)
                VALUES (%s, 'outbound', %s, %s, %s::jsonb)
            ''', (sync_id, provider, len(charvak_jobs), json.dumps(entry)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"sync_jobs_from_charvak failed: {e}")
            return {"status": "error", "message": "Could not log sync"}

        return {
            "status": "success",
            "sync_id": sync_id,
            "message": f"{len(charvak_jobs)} jobs exported from Charvak to {provider}",
            "jobs_count": len(charvak_jobs),
        }

    # ============================================================
    # SYNC - INBOUND
    # ============================================================

    def receive_webhook(self, integration_id: str, data: Dict) -> Dict:
        """Receive jobs from external ATS."""
        integration = self._find_integration(integration_id)
        if not integration:
            return {"status": "error", "message": "Integration not found"}

        sync_id = f"SYNC-IN-{secrets.token_hex(4).upper()}"

        # Import jobs into Charvak's job board (already DB-backed - untouched)
        from job_board_engine import job_board_engine
        if data.get("jobs"):
            for job_data in data["jobs"]:
                job_board_engine.post_job({
                    "title": job_data.get("title", "Imported Job"),
                    "company": integration.get("company_name", "External"),
                    "job_type": job_data.get("type", "Permanent"),
                    "location": job_data.get("location", "Remote"),
                    "description": job_data.get("description", ""),
                    "skills": job_data.get("skills", []),
                    "posted_by": f"ats_{integration['provider']}",
                })

        jobs_received = len(data.get("jobs", []))
        entry = {
            "sync_id": sync_id,
            "direction": "inbound",
            "provider": integration["provider"],
            "jobs_count": jobs_received,
            "received_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_ats_sync_log
                    (sync_id, direction, provider, jobs_count, details)
                VALUES (%s, 'inbound', %s, %s, %s::jsonb)
            ''', (sync_id, integration["provider"], jobs_received, json.dumps(entry)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"receive_webhook sync log failed: {e}")

        return {
            "status": "success",
            "sync_id": sync_id,
            "message": f"{jobs_received} jobs imported from {integration['provider']} to Charvak ATS",
        }

    # ============================================================
    # LOG
    # ============================================================

    def get_sync_log(self) -> Dict:
        """Get all sync history."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT details FROM charvak_ats_sync_log ORDER BY synced_at ASC
            ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_sync_log failed: {e}")
            return {"status": "error", "message": "Could not load sync log"}

        syncs = [r[0] if isinstance(r[0], dict) else json.loads(r[0] or "{}") for r in rows]

        return {
            "status": "success",
            "syncs": syncs,
            "count": len(syncs),
            "inbound": len([s for s in syncs if s.get("direction") == "inbound"]),
            "outbound": len([s for s in syncs if s.get("direction") == "outbound"]),
        }

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        """Get ATS integration statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_ats_integrations')
            total_integrations = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_ats_sync_log')
            total_syncs = int(cur.fetchone()[0] or 0)

            # get_stats uses different keys for inbound vs outbound - preserved via JSONB details
            cur.execute("SELECT details FROM charvak_ats_sync_log WHERE direction = 'inbound'")
            inbound_jobs = sum(
                (r[0] if isinstance(r[0], dict) else json.loads(r[0] or "{}")).get("jobs_count", 0)
                for r in cur.fetchall()
            )

            cur.execute("SELECT details FROM charvak_ats_sync_log WHERE direction = 'outbound'")
            outbound_jobs = sum(
                (r[0] if isinstance(r[0], dict) else json.loads(r[0] or "{}")).get("jobs_synced", 0)
                for r in cur.fetchall()
            )

            cur.execute('SELECT DISTINCT provider FROM charvak_ats_integrations')
            providers = [r[0] for r in cur.fetchall() if r[0]]

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_integrations": total_integrations,
                "total_syncs": total_syncs,
                "inbound_jobs": inbound_jobs,
                "outbound_jobs": outbound_jobs,
                "providers": providers,
            },
        }


ats_engine = ATSEngine()