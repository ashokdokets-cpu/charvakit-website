"""
Charvak Complete Training Mapping System
AI-Driven: Skill Gap to Job Market Ready
(DB-backed - Session H/5)
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.training_mapping")


class TrainingMappingEngine:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.skill_matrix = self._initialize_skill_matrix()
        self._ensure_tables()
        logger.info("Training Mapping Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_training_plans (
                    email        TEXT PRIMARY KEY,
                    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_training_created ON charvak_training_plans(created_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"training_mapping tables init failed: {e}")

    def _initialize_skill_matrix(self):
        """Complete skill-to-job mapping matrix (static)."""
        return {
            "software_developer": {
                "role": "Software Developer",
                "required_skills": ["Data Structures", "Algorithms", "Python/Java", "SQL", "System Design", "Git", "Problem Solving"],
                "assessment_topics": ["Coding", "DSA", "Database", "System Design"],
                "training_path": ["Basic Programming", "DSA", "Projects", "Mock Interviews"],
            },
            "data_scientist": {
                "role": "Data Scientist",
                "required_skills": ["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization", "Deep Learning"],
                "assessment_topics": ["ML", "Statistics", "Python", "SQL"],
                "training_path": ["Python Basics", "Statistics", "ML Algorithms", "Projects"],
            },
            "devops_engineer": {
                "role": "DevOps Engineer",
                "required_skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS/Azure", "Scripting", "Monitoring"],
                "assessment_topics": ["Linux", "Docker", "K8s", "Cloud"],
                "training_path": ["Linux", "Containerization", "CI/CD", "Cloud"],
            },
            "cybersecurity_analyst": {
                "role": "Cybersecurity Analyst",
                "required_skills": ["Network Security", "Cryptography", "Ethical Hacking", "Security Tools", "Risk Assessment"],
                "assessment_topics": ["Security", "Networking", "Cryptography"],
                "training_path": ["Networking", "Security Basics", "Pen Testing", "Certifications"],
            },
            "frontend_developer": {
                "role": "Frontend Developer",
                "required_skills": ["HTML/CSS", "JavaScript", "React/Angular", "UI/UX", "Responsive Design", "API Integration"],
                "assessment_topics": ["JavaScript", "React", "CSS", "Web"],
                "training_path": ["HTML/CSS", "JavaScript", "React", "Projects"],
            },
            "fullstack_developer": {
                "role": "Full Stack Developer",
                "required_skills": ["Frontend", "Backend", "Database", "API Design", "DevOps Basics", "System Design"],
                "assessment_topics": ["Frontend", "Backend", "DB", "System Design"],
                "training_path": ["Frontend", "Backend", "Database", "Full Stack Projects"],
            },
        }

    # ============================================================
    # STATIC CATALOG
    # ============================================================

    def get_skill_matrix(self):
        """Get complete skill-to-job mapping."""
        return {"status": "success", "roles": list(self.skill_matrix.keys()), "matrix": self.skill_matrix}

    # ============================================================
    # PLANS
    # ============================================================

    def create_training_plan(self, email, target_role, current_skills, weeks=12):
        """Create personalized AI-driven training plan."""
        if target_role not in self.skill_matrix:
            return {"status": "error", "message": f"Role {target_role} not found"}

        role_data = self.skill_matrix[target_role]
        required = role_data["required_skills"]
        current = current_skills or []

        gaps = [skill for skill in required if skill not in current]
        strengths = [skill for skill in required if skill in current]
        gap_percentage = (len(gaps) / len(required)) * 100 if required else 0

        weekly_plan = self._generate_weekly_plan(gaps, weeks, target_role)
        recommendations = self._generate_recommendations(gaps, strengths, target_role)

        plan = {
            "email": email,
            "target_role": target_role,
            "role_name": role_data["role"],
            "required_skills": required,
            "current_skills": strengths,
            "skill_gaps": gaps,
            "gap_percentage": round(gap_percentage, 1),
            "weeks": weeks,
            "weekly_plan": weekly_plan,
            "recommendations": recommendations,
            "created_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_training_plans (email, data)
                VALUES (%s, %s::jsonb)
                ON CONFLICT (email) DO UPDATE SET
                    data = EXCLUDED.data,
                    updated_at = CURRENT_TIMESTAMP
            ''', (email, json.dumps(plan)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_training_plan failed: {e}")
            return {"status": "error", "message": "Could not create training plan"}

        return {"status": "success", "plan": plan}

    def _generate_weekly_plan(self, gaps, weeks, role):
        """Generate week-by-week training plan (pure)."""
        if not gaps:
            return []

        weekly_plan = []
        skills_per_week = max(1, len(gaps) // max(1, weeks // 2))

        for week in range(1, weeks + 1):
            start_idx = (week - 1) * skills_per_week
            end_idx = min(start_idx + skills_per_week, len(gaps))
            week_skills = gaps[start_idx:end_idx]

            if week <= 2:
                phase = "Assessment & Foundation"
            elif week <= 6:
                phase = "Core Skill Building"
            elif week <= 10:
                phase = "Advanced Practice"
            else:
                phase = "Placement Preparation"

            weekly_plan.append({
                "week": week,
                "phase": phase,
                "focus_skills": week_skills,
                "activities": [f"Daily practice on {skill}" for skill in week_skills],
                "milestone": f"Complete {len(week_skills)} skills",
            })

        return weekly_plan

    def _generate_recommendations(self, gaps, strengths, role):
        """Generate AI-driven recommendations (pure)."""
        recommendations = []

        if gaps:
            recommendations.append(f"Priority: Close {len(gaps)} skill gaps for {role}")
            recommendations.append(f"Start with: {', '.join(gaps[:3])}")

        if strengths:
            recommendations.append(f"Leverage existing strengths in: {', '.join(strengths[:3])}")

        recommendations.append("Complete daily mock tests")
        recommendations.append("Participate in weekly coding challenges")
        recommendations.append("Build 2-3 portfolio projects")

        return recommendations

    def _get_plan(self, email):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT data FROM charvak_training_plans WHERE email = %s', (email,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_get_plan failed: {e}")
            return None

        if not row:
            return None
        return row[0] if isinstance(row[0], dict) else json.loads(row[0] or "{}")

    def get_training_plan(self, email):
        """Get existing training plan."""
        plan = self._get_plan(email)
        if not plan:
            return {"status": "error", "message": "No training plan found"}
        return {"status": "success", "plan": plan}

    def update_progress(self, email, week, skills_completed):
        """Update training progress (REPLACES progress key - preserves original behavior)."""
        plan = self._get_plan(email)
        if not plan:
            return {"status": "error", "message": "No training plan found"}

        plan["progress"] = {
            "current_week": week,
            "skills_completed": skills_completed,
            "updated_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_training_plans
                SET data = %s::jsonb, updated_at = CURRENT_TIMESTAMP
                WHERE email = %s
            ''', (json.dumps(plan), email))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"update_progress failed: {e}")
            return {"status": "error", "message": "Could not update progress"}

        return {"status": "success", "plan": plan}

    # ============================================================
    # JOB MARKET INSIGHTS (static)
    # ============================================================

    def get_job_market_insights(self, role):
        """Get job market insights for a role."""
        insights = {
            "software_developer": {"demand": "Very High", "avg_salary": "Rs.6L - Rs.25L", "companies_hiring": 5000, "growth": "25% YoY"},
            "data_scientist": {"demand": "High", "avg_salary": "Rs.8L - Rs.30L", "companies_hiring": 3000, "growth": "35% YoY"},
            "devops_engineer": {"demand": "Very High", "avg_salary": "Rs.8L - Rs.28L", "companies_hiring": 2500, "growth": "30% YoY"},
            "cybersecurity_analyst": {"demand": "Critical", "avg_salary": "Rs.7L - Rs.25L", "companies_hiring": 2000, "growth": "40% YoY"},
        }

        return {"status": "success", "role": role, "insights": insights.get(role, {"demand": "Moderate", "avg_salary": "Varies"})}


training_mapping_engine = TrainingMappingEngine()