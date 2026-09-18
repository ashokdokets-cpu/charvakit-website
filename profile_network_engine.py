"""
Charvak Profile & Network Engine
Unified Master Profile + Advanced Networking
(DB-backed - Session D/4)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.profilenetwork")


class ProfileNetworkEngine:
    """Unified profile + advanced networking (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Profile & Network Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_master_profiles (
                    profile_id   TEXT PRIMARY KEY,
                    email        TEXT UNIQUE NOT NULL,
                    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_master_profiles_email ON charvak_master_profiles(email)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_alumni_connections (
                    connection_id  TEXT PRIMARY KEY,
                    university     TEXT,
                    name           TEXT,
                    email          TEXT,
                    company        TEXT,
                    role           TEXT,
                    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_alumni_university ON charvak_alumni_connections(university)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_alumni_company    ON charvak_alumni_connections(company)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_alumni_email      ON charvak_alumni_connections(email)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_network_tracker (
                    track_id          TEXT PRIMARY KEY,
                    email             TEXT NOT NULL,
                    connection_name   TEXT,
                    company           TEXT,
                    status            TEXT DEFAULT 'pending',
                    tracked_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ntracker_email   ON charvak_network_tracker(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ntracker_company ON charvak_network_tracker(company)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"profile_network tables init failed: {e}")

    # ============================================================
    # MASTER PROFILE (Unified)
    # ============================================================

    def create_master_profile(self, data: Dict) -> Dict:
        """
        Create unified master profile.
        Pulls from candidate_engine and adds unified view.
        """
        profile_id = f"MP-{secrets.token_hex(4).upper()}"
        email = data.get("email")

        # Try to get existing candidate data (snapshot at create time)
        existing = {}
        try:
            from candidate_engine import candidate_engine
            existing = candidate_engine.get_candidate_by_email(email) or {}
        except Exception as e:
            logger.warning(f"candidate_engine lookup failed: {e}")
            existing = {}

        now = datetime.now().isoformat()
        master_profile = {
            "profile_id": profile_id,
            "email": email,
            "candidate_data": existing,
            "assessments": [],
            "applications": [],
            "courses": [],
            "network": [],
            "created_at": now,
            "updated_at": now,
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_master_profiles (profile_id, email, data)
                VALUES (%s, %s, %s::jsonb)
                ON CONFLICT (email) DO UPDATE SET
                    data = EXCLUDED.data,
                    updated_at = CURRENT_TIMESTAMP
            ''', (profile_id, email, json.dumps(master_profile)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_master_profile failed: {e}")
            return {"status": "error", "message": "Could not create profile"}

        return {
            "status": "success",
            "profile_id": profile_id,
            "message": "Master profile created! All your data in one place.",
            "profile": master_profile,
        }

    def update_master_profile(self, email: str, update_data: Dict) -> Dict:
        """Update master profile with any new data (top-level dict merge)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            # Postgres `||` on jsonb = top-level key merge, same as Python dict.update()
            cur.execute('''
                UPDATE charvak_master_profiles
                SET data = data || %s::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE email = %s
                RETURNING data, created_at, updated_at
            ''', (json.dumps(update_data), email))
            row = cur.fetchone()
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"update_master_profile failed: {e}")
            return {"status": "error", "message": "Could not update profile"}

        if not row:
            return {"status": "error", "message": "Profile not found"}

        profile = row[0] if isinstance(row[0], dict) else json.loads(row[0])
        return {"status": "success", "message": "Profile updated", "profile": profile}

    def get_master_profile(self, email: str) -> Dict:
        """Get unified master profile."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT data FROM charvak_master_profiles WHERE email = %s', (email,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_master_profile failed: {e}")
            return {"status": "error", "message": "Profile not found"}

        if not row:
            return {"status": "error", "message": "Profile not found"}

        profile = row[0] if isinstance(row[0], dict) else json.loads(row[0])
        return {"status": "success", "profile": profile}

    # ============================================================
    # ALUMNI NETWORK
    # ============================================================

    def add_alumni_connection(self, data: Dict) -> Dict:
        """Add alumni connection."""
        connection_id = f"ALUM-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_alumni_connections
                    (connection_id, university, name, email, company, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                connection_id,
                data.get("university"),
                data.get("name"),
                data.get("email"),
                data.get("company"),
                data.get("role"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"add_alumni_connection failed: {e}")
            return {"status": "error", "message": "Could not add connection"}

        return {"status": "success", "connection_id": connection_id, "message": "Alumni connection added!"}

    def find_alumni(self, university: str = None, company: str = None) -> Dict:
        """Find alumni by university or company."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            where_parts = []
            params = []
            if university:
                where_parts.append("university = %s")
                params.append(university)
            if company:
                where_parts.append("company = %s")
                params.append(company)

            sql = "SELECT connection_id, university, name, email, company, role, created_at FROM charvak_alumni_connections"
            if where_parts:
                sql += " WHERE " + " AND ".join(where_parts)
            sql += " ORDER BY created_at DESC"

            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"find_alumni failed: {e}")
            return {"status": "error", "message": "Could not load alumni"}

        alumni = [{
            "connection_id": r[0],
            "university": r[1],
            "name": r[2],
            "email": r[3],
            "company": r[4],
            "role": r[5],
            "created_at": r[6].isoformat() if hasattr(r[6], "isoformat") else str(r[6]),
        } for r in rows]

        return {"status": "success", "alumni": alumni, "count": len(alumni)}

    # ============================================================
    # REFERRAL MATCHMAKING
    # ============================================================

    def find_referral_match(self, data: Dict) -> Dict:
        """Find who can refer you at a company."""
        target_company = data.get("target_company", "")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT connection_id, university, name, email, company, role, created_at
                FROM charvak_alumni_connections
                WHERE company = %s
                ORDER BY created_at DESC
            ''', (target_company,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"find_referral_match failed: {e}")
            return {"status": "error", "message": "Could not load matches"}

        matches = [{
            "connection_id": r[0],
            "university": r[1],
            "name": r[2],
            "email": r[3],
            "company": r[4],
            "role": r[5],
            "created_at": r[6].isoformat() if hasattr(r[6], "isoformat") else str(r[6]),
        } for r in rows]

        return {
            "status": "success",
            "target_company": target_company,
            "matches": matches,
            "count": len(matches),
            "message": f"Found {len(matches)} potential referrers at {target_company}!" if matches else f"No referrers found at {target_company}",
        }

    # ============================================================
    # NETWORK TRACKER
    # ============================================================

    def track_connection(self, data: Dict) -> Dict:
        """Track a LinkedIn connection."""
        track_id = f"NET-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_network_tracker
                    (track_id, email, connection_name, company, status)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                track_id,
                data.get("email"),
                data.get("connection_name"),
                data.get("company"),
                data.get("status", "pending"),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"track_connection failed: {e}")
            return {"status": "error", "message": "Could not track connection"}

        return {"status": "success", "track_id": track_id, "message": "Connection tracked!"}

    def get_network(self, email: str) -> Dict:
        """Get user's network."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT track_id, email, connection_name, company, status, tracked_at
                FROM charvak_network_tracker
                WHERE email = %s
                ORDER BY tracked_at DESC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_network failed: {e}")
            return {"status": "error", "message": "Could not load network"}

        connections = [{
            "track_id": r[0],
            "email": r[1],
            "connection_name": r[2],
            "company": r[3],
            "status": r[4],
            "tracked_at": r[5].isoformat() if hasattr(r[5], "isoformat") else str(r[5]),
        } for r in rows]

        return {"status": "success", "connections": connections, "count": len(connections)}

    # ============================================================
    # AUTO-OUTREACH TEMPLATES (stateless)
    # ============================================================

    def generate_outreach_template(self, data: Dict) -> Dict:
        """Generate personalized outreach message."""
        template = f"""Hi {data.get('connection_name')},

I came across your profile and noticed you work at {data.get('company')} as {data.get('role')}. I'm {data.get('candidate_name')} from {data.get('university', 'the same university')} and I'm very interested in opportunities at {data.get('company')}.

Would you be open to a quick chat about your experience there?

Best regards,
{data.get('candidate_name')}"""

        return {
            "status": "success",
            "template": template,
            "message": "Outreach template generated!",
        }

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_master_profiles')
            master_profiles = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_alumni_connections')
            alumni_connections = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_network_tracker')
            network_tracked = int(cur.fetchone()[0] or 0)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "master_profiles": master_profiles,
                "alumni_connections": alumni_connections,
                "network_tracked": network_tracked,
            },
        }


profile_network_engine = ProfileNetworkEngine()