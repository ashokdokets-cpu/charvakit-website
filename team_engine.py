"""
Charvak Team Engine
Multi-user team accounts with role-based access
(DB-backed - Session E/1)
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.team")


class TeamRole:
    ADMIN = "admin"
    RECRUITER = "recruiter"
    VIEWER = "viewer"


class TeamEngine:
    """Handles team accounts and member management (Postgres-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Team Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_teams (
                    team_id        TEXT PRIMARY KEY,
                    company_name   TEXT,
                    admin_email    TEXT,
                    admin_name     TEXT,
                    member_count   INTEGER DEFAULT 1,
                    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_teams_admin_email ON charvak_teams(admin_email)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_team_members (
                    member_id   TEXT PRIMARY KEY,
                    team_id     TEXT NOT NULL,
                    name        TEXT,
                    email       TEXT NOT NULL,
                    role        TEXT NOT NULL DEFAULT 'recruiter',
                    joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(team_id, email)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_team_members_team  ON charvak_team_members(team_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_team_members_email ON charvak_team_members(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_team_members_role  ON charvak_team_members(role)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"team tables init failed: {e}")

    def create_team(self, data: Dict) -> Dict:
        team_id = f"TEAM-{secrets.token_hex(4).upper()}"
        member_id = f"MEM-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_teams
                    (team_id, company_name, admin_email, admin_name, member_count)
                VALUES (%s, %s, %s, %s, 1)
            ''', (team_id, data.get("company_name"), data.get("admin_email"), data.get("admin_name")))
            cur.execute('''
                INSERT INTO charvak_team_members
                    (member_id, team_id, name, email, role)
                VALUES (%s, %s, %s, %s, %s)
            ''', (member_id, team_id, data.get("admin_name"), data.get("admin_email"), TeamRole.ADMIN))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_team failed: {e}")
            return {"status": "error", "message": "Could not create team"}
        return {
            "status": "success",
            "team_id": team_id,
            "message": "Team created! Invite your first member.",
            "invite_link": f"https://charvakit.com/team/join/{team_id}",
        }

    def invite_member(self, data: Dict) -> Dict:
        team = self._find_team(data.get("team_id"))
        if not team:
            return {"status": "error", "message": "Team not found"}
        member_id = f"MEM-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_team_members
                    (member_id, team_id, name, email, role)
                VALUES (%s, %s, %s, %s, %s)
            ''', (member_id, data.get("team_id"), data.get("name"), data.get("email"), data.get("role", TeamRole.RECRUITER)))
            cur.execute('''
                UPDATE charvak_teams SET member_count = member_count + 1 WHERE team_id = %s
            ''', (data.get("team_id"),))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            msg = str(e).lower()
            if "unique" in msg or "duplicate" in msg:
                return {"status": "error", "message": f"{data.get('email')} is already a member of this team"}
            logger.error(f"invite_member failed: {e}")
            return {"status": "error", "message": "Could not invite member"}
        return {
            "status": "success",
            "member_id": member_id,
            "message": f"{data.get('name')} invited to {team['company_name']}!",
        }

    def get_team(self, team_id: str) -> Dict:
        team = self._find_team(team_id)
        if not team:
            return {"status": "error", "message": "Team not found"}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT member_id, team_id, name, email, role, joined_at
                FROM charvak_team_members WHERE team_id = %s ORDER BY joined_at ASC
            ''', (team_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_team failed: {e}")
            return {"status": "error", "message": "Could not load team"}
        members = [{
            "member_id": r[0], "team_id": r[1], "name": r[2], "email": r[3],
            "role": r[4],
            "joined_at": r[5].isoformat() if hasattr(r[5], "isoformat") else str(r[5]),
        } for r in rows]
        return {
            "status": "success",
            "team": team,
            "members": members,
            "roles": [TeamRole.ADMIN, TeamRole.RECRUITER, TeamRole.VIEWER],
        }

    def update_member_role(self, member_id: str, new_role: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('UPDATE charvak_team_members SET role = %s WHERE member_id = %s', (new_role, member_id))
            affected = cur.rowcount
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"update_member_role failed: {e}")
            return {"status": "error", "message": "Could not update role"}
        if affected == 0:
            return {"status": "error", "message": "Member not found"}
        return {"status": "success", "message": f"Role updated to {new_role}"}

    def remove_member(self, member_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT team_id FROM charvak_team_members WHERE member_id = %s', (member_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Member not found"}
            team_id = row[0]
            cur.execute('DELETE FROM charvak_team_members WHERE member_id = %s', (member_id,))
            cur.execute('UPDATE charvak_teams SET member_count = GREATEST(member_count - 1, 0) WHERE team_id = %s', (team_id,))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"remove_member failed: {e}")
            return {"status": "error", "message": "Could not remove member"}
        return {"status": "success", "message": "Member removed"}

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_teams'); total_teams = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM charvak_team_members'); total_members = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM charvak_team_members WHERE role = %s', (TeamRole.ADMIN,)); admins = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM charvak_team_members WHERE role = %s', (TeamRole.RECRUITER,)); recruiters = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM charvak_team_members WHERE role = %s', (TeamRole.VIEWER,)); viewers = cur.fetchone()[0]
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}
        return {
            "status": "success",
            "stats": {
                "total_teams": total_teams,
                "total_members": total_members,
                "admins": admins,
                "recruiters": recruiters,
                "viewers": viewers,
            },
        }

    def _find_team(self, team_id: str) -> Optional[Dict]:
        if not team_id:
            return None
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT team_id, company_name, admin_email, admin_name, member_count, created_at FROM charvak_teams WHERE team_id = %s', (team_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return None
            return {
                "team_id": row[0],
                "company_name": row[1],
                "admin_email": row[2],
                "admin_name": row[3],
                "member_count": row[4],
                "created_at": row[5].isoformat() if hasattr(row[5], "isoformat") else str(row[5]),
            }
        except Exception as e:
            logger.error(f"_find_team failed: {e}")
            return None


team_engine = TeamEngine()