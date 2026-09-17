"""
Charvak Dynamic AI Role Mapping System
Automatically recommends roles, creates training paths, and tracks progress
(DB-backed - Session F/4)
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.dynamic_roles")


class DynamicRoleMappingEngine:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.role_database = self._initialize_roles()
        self._ensure_tables()
        logger.info("Dynamic Role Mapping Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_dynamic_role_profiles (
                    email             TEXT PRIMARY KEY,
                    skills            JSONB DEFAULT '[]'::jsonb,
                    interests         JSONB DEFAULT '[]'::jsonb,
                    experience_level  TEXT DEFAULT 'fresher',
                    recommendations   JSONB DEFAULT '[]'::jsonb,
                    ai_insights       JSONB DEFAULT '[]'::jsonb,
                    analyzed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_dynrole_profiles_level ON charvak_dynamic_role_profiles(experience_level)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_dynamic_custom_roles (
                    role_id         TEXT PRIMARY KEY,
                    name            TEXT NOT NULL,
                    category        TEXT DEFAULT 'Custom',
                    skills          JSONB DEFAULT '[]'::jsonb,
                    tools           JSONB DEFAULT '[]'::jsonb,
                    certifications  JSONB DEFAULT '[]'::jsonb,
                    created_by      TEXT,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_dynrole_custom_created_by ON charvak_dynamic_custom_roles(created_by)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"dynamic_role tables init failed: {e}")

    # ============================================================
    # STATIC BASE CATALOG
    # ============================================================

    def _initialize_roles(self):
        """Initialize extensive role database (base catalog - static)."""
        return {
            "software_developer": {"name": "Software Developer", "category": "Technology", "skills": ["Python", "Java", "DSA", "SQL", "Git", "Problem Solving"], "tools": ["VS Code", "GitHub", "JIRA"], "certifications": ["AWS Certified Developer", "Oracle Java"]},
            "fullstack_developer": {"name": "Full Stack Developer", "category": "Technology", "skills": ["HTML/CSS", "JavaScript", "React", "Node.js", "MongoDB", "API Design"], "tools": ["VS Code", "Docker", "Postman"], "certifications": ["AWS Certified Developer", "MongoDB Certified"]},
            "frontend_developer": {"name": "Frontend Developer", "category": "Technology", "skills": ["HTML", "CSS", "JavaScript", "React", "UI/UX", "Responsive Design"], "tools": ["Figma", "VS Code", "Chrome DevTools"], "certifications": ["Meta Frontend Developer"]},
            "backend_developer": {"name": "Backend Developer", "category": "Technology", "skills": ["Python", "Java", "Node.js", "SQL", "Redis", "Microservices"], "tools": ["Postman", "Docker", "Kubernetes"], "certifications": ["AWS Solutions Architect"]},
            "data_scientist": {"name": "Data Scientist", "category": "Data & AI", "skills": ["Python", "Statistics", "ML", "Deep Learning", "SQL", "Data Viz"], "tools": ["Jupyter", "TensorFlow", "Tableau"], "certifications": ["Google Data Analytics", "AWS ML Specialty"]},
            "data_analyst": {"name": "Data Analyst", "category": "Data & AI", "skills": ["SQL", "Excel", "Python", "Tableau", "Power BI", "Statistics"], "tools": ["Excel", "Tableau", "Power BI"], "certifications": ["Google Data Analytics"]},
            "ml_engineer": {"name": "Machine Learning Engineer", "category": "Data & AI", "skills": ["Python", "ML", "Deep Learning", "TensorFlow", "PyTorch", "MLOps"], "tools": ["TensorFlow", "PyTorch", "Kubeflow"], "certifications": ["AWS ML Specialty", "Google ML Engineer"]},
            "devops_engineer": {"name": "DevOps Engineer", "category": "Infrastructure", "skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform"], "tools": ["Docker", "Kubernetes", "Jenkins", "Terraform"], "certifications": ["AWS DevOps", "CKA"]},
            "cloud_architect": {"name": "Cloud Architect", "category": "Infrastructure", "skills": ["AWS", "Azure", "GCP", "Networking", "Security", "Architecture"], "tools": ["AWS Console", "Terraform", "CloudFormation"], "certifications": ["AWS Solutions Architect", "Azure Architect"]},
            "cybersecurity_analyst": {"name": "Cybersecurity Analyst", "category": "Security", "skills": ["Network Security", "Cryptography", "Ethical Hacking", "SIEM", "Risk Assessment"], "tools": ["Wireshark", "Metasploit", "Nmap"], "certifications": ["CEH", "Security+", "CISSP"]},
            "qa_engineer": {"name": "QA Engineer", "category": "Quality", "skills": ["Testing", "Selenium", "Python", "API Testing", "Automation", "Agile"], "tools": ["Selenium", "JIRA", "Postman"], "certifications": ["ISTQB"]},
            "mobile_developer": {"name": "Mobile Developer", "category": "Technology", "skills": ["Android", "iOS", "Flutter", "React Native", "Kotlin", "Swift"], "tools": ["Android Studio", "Xcode", "Flutter"], "certifications": ["Google Associate Android Developer"]},
            "product_manager": {"name": "Product Manager", "category": "Product", "skills": ["Product Strategy", "User Research", "Agile", "Analytics", "Roadmapping"], "tools": ["JIRA", "Figma", "Mixpanel"], "certifications": ["PMP", "Scrum Product Owner"]},
            "business_analyst": {"name": "Business Analyst", "category": "Business", "skills": ["Requirements Gathering", "SQL", "Excel", "Process Mapping", "Stakeholder Management"], "tools": ["Excel", "JIRA", "Visio"], "certifications": ["CBAP", "PMI-PBA"]},
            "ui_ux_designer": {"name": "UI/UX Designer", "category": "Design", "skills": ["UI Design", "UX Research", "Figma", "Prototyping", "User Testing"], "tools": ["Figma", "Sketch", "Adobe XD"], "certifications": ["Google UX Design"]},
        }

    # ============================================================
    # CUSTOM ROLES (DB-backed)
    # ============================================================

    def _load_custom_roles(self) -> Dict:
        """Load persisted custom roles into a dict keyed by role_id."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT role_id, name, category, skills, tools, certifications
                FROM charvak_dynamic_custom_roles
            ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_load_custom_roles failed: {e}")
            return {}

        def _d(x, default):
            if isinstance(x, type(default)) or x is None:
                return x if x is not None else default
            try:
                return json.loads(x)
            except Exception:
                return default

        return {
            r[0]: {
                "name": r[1],
                "category": r[2],
                "skills": _d(r[3], []),
                "tools": _d(r[4], []),
                "certifications": _d(r[5], []),
            }
            for r in rows
        }

    def _all_roles(self) -> Dict:
        """Base catalog + persisted custom roles (customs override base on collision)."""
        merged = dict(self.role_database)
        merged.update(self._load_custom_roles())
        return merged

    # ============================================================
    # PUBLIC METHODS
    # ============================================================

    def get_all_roles(self):
        """Get all available roles."""
        roles = []
        # Base catalog first (stable order)
        for key, role in self.role_database.items():
            roles.append({
                "id": key,
                "name": role["name"],
                "category": role["category"],
                "skills_count": len(role["skills"]),
            })
        # Then customs (from DB), skipping any that already existed in base
        customs = self._load_custom_roles()
        for key, role in customs.items():
            if key in self.role_database:
                continue
            roles.append({
                "id": key,
                "name": role["name"],
                "category": role["category"],
                "skills_count": len(role["skills"]),
            })
        return {"status": "success", "total": len(roles), "roles": roles}

    def analyze_skills_and_recommend(self, email, skills, interests=None, experience_level="fresher"):
        """Analyze skills and recommend best-fit roles."""
        all_roles = self._all_roles()
        recommendations = []

        for role_id, role in all_roles.items():
            required = set(role["skills"])
            user_skills = set(skills)
            matched = required & user_skills
            match_percentage = (len(matched) / len(required)) * 100 if required else 0
            gaps = list(required - user_skills)

            if match_percentage >= 30:
                recommendations.append({
                    "role_id": role_id,
                    "role_name": role["name"],
                    "category": role["category"],
                    "match_percentage": round(match_percentage, 1),
                    "matched_skills": list(matched),
                    "skill_gaps": gaps,
                    "tools_needed": role["tools"],
                    "certifications": role["certifications"],
                })

        recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
        ai_insights = self._generate_ai_insights(skills, recommendations[:3])

        profile = {
            "email": email,
            "skills": skills,
            "interests": interests,
            "experience_level": experience_level,
            "recommendations": recommendations[:5],
            "ai_insights": ai_insights,
            "analyzed_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_dynamic_role_profiles
                    (email, skills, interests, experience_level, recommendations, ai_insights, analyzed_at)
                VALUES (%s, %s::jsonb, %s::jsonb, %s, %s::jsonb, %s::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT (email) DO UPDATE SET
                    skills = EXCLUDED.skills,
                    interests = EXCLUDED.interests,
                    experience_level = EXCLUDED.experience_level,
                    recommendations = EXCLUDED.recommendations,
                    ai_insights = EXCLUDED.ai_insights,
                    analyzed_at = CURRENT_TIMESTAMP
            ''', (
                email,
                json.dumps(skills),
                json.dumps(interests or []),
                experience_level,
                json.dumps(profile["recommendations"]),
                json.dumps(ai_insights),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"analyze_skills_and_recommend write failed: {e}")

        return {"status": "success", "profile": profile}

    def _generate_ai_insights(self, skills, top_roles):
        """Generate AI insights based on skills."""
        insights = []
        if not top_roles:
            insights.append("Start with fundamental programming skills")
            insights.append("Focus on Python, SQL, and Data Structures")
            return insights
        best_role = top_roles[0]
        insights.append(f"Best match: {best_role['role_name']} ({best_role['match_percentage']}% match)")
        if best_role["skill_gaps"]:
            insights.append(f"Priority skills to learn: {', '.join(best_role['skill_gaps'][:3])}")
        if len(top_roles) > 1:
            insights.append(f"Alternative path: {top_roles[1]['role_name']}")
        return insights

    def create_dynamic_training_plan(self, email, role_id, weeks=12):
        """Create dynamic training plan for any role (stateless - plan is returned, not stored)."""
        all_roles = self._all_roles()
        if role_id not in all_roles:
            return {"status": "error", "message": "Role not found"}

        role = all_roles[role_id]
        skills = role["skills"]

        phases = [
            {"phase": 1, "name": "Foundation", "weeks": "1-2", "focus": skills[:2],
             "activities": [f"Learn {skill} basics" for skill in skills[:2]]},
            {"phase": 2, "name": "Core Skills", "weeks": "3-6", "focus": skills[2:4],
             "activities": [f"Master {skill}" for skill in skills[2:4]]},
            {"phase": 3, "name": "Advanced", "weeks": "7-10", "focus": skills[4:],
             "activities": [f"Apply {skill} in projects" for skill in skills[4:]]},
            {"phase": 4, "name": "Placement Prep", "weeks": "11-12",
             "focus": ["Mock Interviews", "Resume Building"],
             "activities": ["Daily mock tests", "Company-specific preparation"]},
        ]

        plan = {
            "email": email,
            "role": role["name"],
            "role_id": role_id,
            "weeks": weeks,
            "phases": phases,
            "tools_to_learn": role["tools"],
            "certifications": role["certifications"],
            "created_at": datetime.now().isoformat(),
        }

        return {"status": "success", "plan": plan}

    def recommend_custom_role(self, email, role_name, required_skills, category="Custom"):
        """Add and recommend a custom role (persisted globally)."""
        role_id = role_name.lower().replace(" ", "_")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_dynamic_custom_roles
                    (role_id, name, category, skills, tools, certifications, created_by)
                VALUES (%s, %s, %s, %s::jsonb, '[]'::jsonb, '[]'::jsonb, %s)
                ON CONFLICT (role_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    skills = EXCLUDED.skills
            ''', (role_id, role_name, category, json.dumps(required_skills), email))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"recommend_custom_role failed: {e}")
            return {"status": "error", "message": "Could not add custom role"}

        return {
            "status": "success",
            "message": f"Custom role '{role_name}' added",
            "role_id": role_id,
        }


dynamic_role_engine = DynamicRoleMappingEngine()
