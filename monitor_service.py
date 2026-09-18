"""
Charvakit Silent-Killer Monitor Service
Background monitoring for websites, webhooks, and APIs
(DB-backed - Session J/5)
"""
import asyncio
import json
import logging
import os
import secrets
import time
from datetime import datetime
from typing import Dict, List

import requests

logger = logging.getLogger("charvakit.monitor")


def _ensure_tables():
    """Idempotent table creation for monitor service."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS charvak_monitor_sites (
                url               TEXT PRIMARY KEY,
                name              TEXT,
                interval_seconds  INTEGER DEFAULT 300,
                status            TEXT DEFAULT 'unknown',
                last_check        TIMESTAMP,
                issues            JSONB DEFAULT '[]'::jsonb,
                created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_monitor_sites_status ON charvak_monitor_sites(status)''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS charvak_monitor_alert_history (
                alert_id     TEXT PRIMARY KEY,
                url          TEXT NOT NULL,
                name         TEXT,
                issues       JSONB DEFAULT '[]'::jsonb,
                checked_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_monitor_alerts_url     ON charvak_monitor_alert_history(url)''')
        cur.execute('''CREATE INDEX IF NOT EXISTS idx_monitor_alerts_checked ON charvak_monitor_alert_history(checked_at)''')
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        logger.error(f"monitor tables init failed: {e}")


# Ensure tables on import
_ensure_tables()


class SiteMonitor:
    """Per-check monitor instance. Issues are rebuilt on each check."""

    def __init__(self, url: str, name: str, check_interval: int = 300):
        self.url = url
        self.name = name
        self.interval = check_interval
        self.last_check = None
        self.status = "unknown"
        self.issues = []

    async def check_site(self):
        """Check website health (async - preserves original signature)."""
        issues = []
        try:
            async with requests.Session(timeout=10) as client:
                start = time.time()
                response = await client.get(self.url)
                response_time = time.time() - start

                if response.status_code >= 400:
                    issues.append(f"HTTP {response.status_code}")

                if response_time > 3:
                    issues.append(f"Slow response: {response_time:.1f}s")

                content = response.text.lower()
                if "error" in content and "error handling" not in content:
                    issues.append("Error text detected on page")
        except Exception as e:
            issues.append(f"Connection failed: {str(e)}")

        self.last_check = datetime.now().isoformat()
        self.status = "healthy" if not issues else "issues_detected"
        self.issues = issues

        # Persist status + last check + issues on the site row
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_monitor_sites
                SET status = %s, last_check = CURRENT_TIMESTAMP, issues = %s::jsonb
                WHERE url = %s
            ''', (self.status, json.dumps(issues), self.url))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"check_site update failed: {e}")

        # Append to alert history if issues detected
        if issues:
            try:
                from database import db
                conn = db.get_connection()
                cur = conn.cursor()
                alert_id = f"ALERT-{secrets.token_hex(4).upper()}"
                cur.execute('''
                    INSERT INTO charvak_monitor_alert_history
                        (alert_id, url, name, issues)
                    VALUES (%s, %s, %s, %s::jsonb)
                ''', (alert_id, self.url, self.name, json.dumps(issues)))
                conn.commit()
                cur.close(); conn.close()
            except Exception as e:
                logger.error(f"check_site alert insert failed: {e}")

        return {"status": self.status, "issues": issues, "checked_at": self.last_check}


# Global monitor instance (kept for backwards-compat; unused)
monitor = SiteMonitor("", "")


async def add_monitor(url: str, name: str, interval: int = 300) -> Dict:
    """Add a site to monitor (upsert into DB)."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO charvak_monitor_sites (url, name, interval_seconds)
            VALUES (%s, %s, %s)
            ON CONFLICT (url) DO UPDATE SET
                name = EXCLUDED.name,
                interval_seconds = EXCLUDED.interval_seconds
        ''', (url, name, interval))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        logger.error(f"add_monitor failed: {e}")
        return {"status": "error", "message": "Could not add monitor", "url": url}

    return {"status": "added", "url": url, "name": name, "interval": interval}


async def check_all_sites() -> List[Dict]:
    """Check all monitored sites (constructs SiteMonitor on the fly from DB)."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT url, name, interval_seconds FROM charvak_monitor_sites')
        rows = cur.fetchall()
        cur.close(); conn.close()
    except Exception as e:
        logger.error(f"check_all_sites read failed: {e}")
        return []

    results = []
    for url, name, interval in rows:
        m = SiteMonitor(url, name, interval or 300)
        result = await m.check_site()
        results.append(result)
    return results


async def get_monitor_status(url: str = None) -> Dict:
    """Get status of monitored sites."""
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()

        if url:
            cur.execute('''
                SELECT url, name, status, last_check, issues
                FROM charvak_monitor_sites WHERE url = %s
            ''', (url,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return {"status": "not_found", "url": url}
            issues = row[4] if isinstance(row[4], list) else json.loads(row[4] or "[]")
            return {
                "url": row[0],
                "name": row[1],
                "status": row[2],
                "last_check": row[3].isoformat() if row[3] and hasattr(row[3], "isoformat") else None,
                "issues": issues,
            }

        # Aggregate view
        cur.execute('SELECT url, name, status FROM charvak_monitor_sites')
        site_rows = cur.fetchall()

        cur.execute('SELECT COUNT(*) FROM charvak_monitor_alert_history')
        total_alerts = int(cur.fetchone()[0] or 0)

        cur.execute('''
            SELECT url, name, issues, checked_at
            FROM charvak_monitor_alert_history
            ORDER BY checked_at DESC LIMIT 10
        ''')
        recent_rows = cur.fetchall()
        cur.close(); conn.close()
    except Exception as e:
        logger.error(f"get_monitor_status failed: {e}")
        return {"sites_monitored": 0, "total_alerts": 0, "recent_alerts": [], "sites": {}}

    recent_alerts = []
    for r in recent_rows:
        issues = r[2] if isinstance(r[2], list) else json.loads(r[2] or "[]")
        recent_alerts.append({
            "url": r[0],
            "name": r[1],
            "issues": issues,
            "time": r[3].isoformat() if r[3] and hasattr(r[3], "isoformat") else None,
        })

    sites = {r[0]: {"name": r[1], "status": r[2]} for r in site_rows}

    return {
        "sites_monitored": len(site_rows),
        "total_alerts": total_alerts,
        "recent_alerts": recent_alerts,
        "sites": sites,
    }


async def run_monitor_loop():
    """Background monitoring loop."""
    while True:
        await check_all_sites()
        await asyncio.sleep(300)