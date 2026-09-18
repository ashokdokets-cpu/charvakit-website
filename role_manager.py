"""
Charvak Dynamic Role Management
Add any role - system auto-generates skills, training plan, pricing
(DB-backed - Session J/4)
"""
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger("charvakit.role_manager")


class RoleManager:
    def __init__(self):
        self._ensure_tables()
        logger.info("Role Manager ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_role_manager_custom_roles (
                    role_id       TEXT PRIMARY KEY,
                    name          TEXT,
                    category      TEXT,
                    skills        JSONB DEFAULT '[]'::jsonb,
                    description   TEXT DEFAULT '',
                    skills_count  INTEGER DEFAULT 0,
                    status        TEXT DEFAULT 'active',
                    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_rm_roles_category ON charvak_role_manager_custom_roles(category)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_rm_roles_status   ON charvak_role_manager_custom_roles(status)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"role_manager tables init failed: {e}")

    # ============================================================
    # ADD ROLE
    # ============================================================

    def add_new_role(self, role_name, category, required_skills, description=None):
        """Add a new role dynamically."""
        role_id = role_name.lower().replace(" ", "_")
        skills = required_skills if isinstance(required_skills, list) else [required_skills]

        role_data = {
            "id": role_id,
            "name": role_name,
            "category": category,
            "skills": skills,
            "description": description or f"{role_name} career path",
            "skills_count": len(skills),
            "created_at": datetime.now().isoformat(),
            "status": "active",
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_role_manager_custom_roles
                    (role_id, name, category, skills, description, skills_count, status)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s, 'active')
                ON CONFLICT (role_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    skills = EXCLUDED.skills,
                    description = EXCLUDED.description,
                    skills_count = EXCLUDED.skills_count
            ''', (
                role_id, role_name, category,
                json.dumps(skills), role_data["description"], len(skills),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"add_new_role failed: {e}")
            return {"status": "error", "message": "Could not add role"}

        # Auto-generate training plan + pricing (pure compute)
        training_plan = self._generate_training_plan(role_data)
        pricing = self._generate_pricing(role_data)

        return {
            "status": "success",
            "role": role_data,
            "training_plan": training_plan,
            "pricing": pricing,
            "message": f"Role '{role_name}' added successfully with auto-generated training plan and pricing",
        }

    # ============================================================
    # PURE COMPUTE
    # ============================================================

    def _generate_training_plan(self, role_data):
        """Auto-generate 4-phase training plan for any role (pure)."""
        skills = role_data["skills"]

        return {
            "phases": [
                {"phase": 1, "name": "Foundation", "duration": "Weeks 1-2",
                 "focus": skills[:2] if len(skills) >= 2 else skills,
                 "activities": [f"Learn {skill} basics" for skill in skills[:2]]},
                {"phase": 2, "name": "Core Skills", "duration": "Weeks 3-6",
                 "focus": skills[2:4] if len(skills) >= 4 else skills,
                 "activities": [f"Master {skill}" for skill in skills[2:4]]},
                {"phase": 3, "name": "Advanced", "duration": "Weeks 7-10",
                 "focus": skills[4:] if len(skills) > 4 else skills,
                 "activities": [f"Apply {skill} in projects" for skill in skills[4:]]},
                {"phase": 4, "name": "Placement Prep", "duration": "Weeks 11-12",
                 "focus": ["Mock Interviews", "Resume Building"],
                 "activities": ["Daily mock tests", "Company-specific preparation"]},
            ]
        }

    def _generate_pricing(self, role_data):
        """Auto-generate pricing based on role demand (pure)."""
        base_prices = {
            "Technology": 99,
            "Data & AI": 129,
            "Infrastructure": 119,
            "Security": 139,
            "Quality": 89,
            "Product": 109,
            "Business": 99,
            "Design": 89,
            "Custom": 99,
        }

        base_price = base_prices.get(role_data["category"], 99)

        return {
            "basic": base_price * 0.7,
            "standard": base_price,
            "premium": base_price * 1.5,
            "enterprise": base_price * 2.0,
        }

    # ============================================================
    # AI (static, per original)
    # ============================================================

    def add_role_with_ai(self, role_name, category, description):
        """Add role with AI-generated skills (static category defaults, per original)."""
        skills = self._generate_skills_with_ai(role_name, category)
        return self.add_new_role(role_name, category, skills, description)

    def _generate_skills_with_ai(self, role_name, category):
        """Generate skills using category-based defaults (original: no real AI call)."""
        category_skills = {
            "Technology": ["Programming", "Data Structures", "Algorithms", "SQL", "Git", "Problem Solving"],
            "Data & AI": ["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization"],
            "Infrastructure": ["Linux", "Cloud", "Networking", "Scripting", "Monitoring"],
            "Security": ["Network Security", "Cryptography", "Risk Assessment", "Security Tools"],
            "Quality": ["Testing", "Automation", "Python", "API Testing"],
            "Product": ["Product Strategy", "User Research", "Agile", "Analytics"],
            "Business": ["Requirements", "SQL", "Excel", "Process Mapping"],
            "Design": ["UI Design", "UX Research", "Prototyping", "User Testing"],
        }

        return category_skills.get(category, ["Communication", "Problem Solving", "Teamwork"])

    # ============================================================
    # READS
    # ============================================================

    def _load_custom_roles(self):
        """Load persisted custom roles keyed by role_id."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT role_id, name, category, skills, description, skills_count,
                       status, created_at
                FROM charvak_role_manager_custom_roles
                ORDER BY created_at ASC
            ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_load_custom_roles failed: {e}")
            return {}

        result = {}
        for r in rows:
            skills = r[3] if isinstance(r[3], list) else (json.loads(r[3]) if r[3] else [])
            result[r[0]] = {
                "id": r[0],
                "name": r[1],
                "category": r[2],
                "skills": skills,
                "description": r[4] or "",
                "skills_count": r[5],
                "status": r[6],
                "created_at": r[7].isoformat() if hasattr(r[7], "isoformat") else str(r[7]),
            }
        return result

    def get_all_roles(self):
        """Get all roles including custom ones."""
        from dynamic_role_engine import dynamic_role_engine
        standard_roles = dynamic_role_engine.get_all_roles()

        all_roles = standard_roles["roles"]

        customs = self._load_custom_roles()
        for role_id, role in customs.items():
            all_roles.append({
                "id": role_id,
                "name": role["name"],
                "category": role["category"],
                "skills_count": role["skills_count"],
            })

        return {"status": "success", "total": len(all_roles), "roles": all_roles}

    def get_role_details(self, role_id):
        """Get details for any role."""
        from dynamic_role_engine import dynamic_role_engine

        # Check standard roles first (matches original)
        if role_id in dynamic_role_engine.role_database:
            role = dynamic_role_engine.role_database[role_id]
            return {"status": "success", "role": role}

        # Check custom roles
        customs = self._load_custom_roles()
        if role_id in customs:
            role = customs[role_id]
            return {
                "status": "success",
                "role": role,
                "training_plan": self._generate_training_plan(role),
            }

        return {"status": "error", "message": "Role not found"}


role_manager = RoleManager()