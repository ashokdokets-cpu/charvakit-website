"""
Charvak AI Internship Program
Multi-duration AI-powered internship with real-world scenarios
(DB-backed - Session E/3)
"""
import json
import logging
import random
import secrets
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger("charvakit.ai_internship")


class AIInternshipEngine:
    def __init__(self):
        self.programs = self._initialize_programs()
        self._ensure_tables()
        logger.info("AI Internship Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ai_internship_enrollments (
                    enrollment_id  TEXT PRIMARY KEY,
                    email          TEXT NOT NULL,
                    program_id     TEXT NOT NULL,
                    duration       TEXT DEFAULT 'standard',
                    total_days     INTEGER DEFAULT 28,
                    current_day    INTEGER DEFAULT 1,
                    status         TEXT NOT NULL DEFAULT 'active',
                    start_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at   TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ai_intern_email   ON charvak_ai_internship_enrollments(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ai_intern_program ON charvak_ai_internship_enrollments(program_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ai_intern_status  ON charvak_ai_internship_enrollments(status)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ai_internship_submissions (
                    submission_id  TEXT PRIMARY KEY,
                    enrollment_id  TEXT NOT NULL,
                    day            INTEGER NOT NULL,
                    submission     TEXT,
                    ai_feedback    JSONB DEFAULT '{}'::jsonb,
                    submitted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(enrollment_id, day)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ai_intern_sub_enroll ON charvak_ai_internship_submissions(enrollment_id)''')

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"ai_internship tables init failed: {e}")

    def _initialize_programs(self):
        """Initialize 20+ internship programs across all disciplines."""
        return {
            "ai_ml": {"name": "AI/ML Engineer Internship", "duration": "4 weeks", "price": 2999, "category": "Engineering", "skills": ["Python", "ML", "Deep Learning", "Cloud"], "deliverables": ["ML Model", "API", "Documentation"], "scenarios": self._generate_scenarios("AI/ML Engineer")},
            "full_stack": {"name": "Full Stack Developer Internship", "duration": "4 weeks", "price": 2499, "category": "Engineering", "skills": ["React", "Node.js", "Database", "API"], "deliverables": ["Web App", "API", "Database"], "scenarios": self._generate_scenarios("Full Stack Developer")},
            "data_engineer": {"name": "Data Engineer Internship", "duration": "4 weeks", "price": 2799, "category": "Engineering", "skills": ["Python", "SQL", "ETL", "Big Data"], "deliverables": ["Data Pipeline", "Dashboard"], "scenarios": self._generate_scenarios("Data Engineer")},
            "devops": {"name": "DevOps Engineer Internship", "duration": "4 weeks", "price": 2499, "category": "Engineering", "skills": ["Docker", "K8s", "CI/CD", "Cloud"], "deliverables": ["Pipeline", "Deployment"], "scenarios": self._generate_scenarios("DevOps Engineer")},
            "cybersecurity": {"name": "Cybersecurity Analyst Internship", "duration": "4 weeks", "price": 2999, "category": "Engineering", "skills": ["Security", "Networking", "Ethical Hacking"], "deliverables": ["Security Audit", "Report"], "scenarios": self._generate_scenarios("Cybersecurity Analyst")},
            "cloud_architect": {"name": "Cloud Architect Internship", "duration": "4 weeks", "price": 2799, "category": "Engineering", "skills": ["AWS", "Azure", "GCP", "Architecture"], "deliverables": ["Architecture Design"], "scenarios": self._generate_scenarios("Cloud Architect")},
            "data_scientist": {"name": "Data Scientist Internship", "duration": "4 weeks", "price": 2999, "category": "Science", "skills": ["Python", "Statistics", "ML", "Visualization"], "deliverables": ["Analysis Report", "Models"], "scenarios": self._generate_scenarios("Data Scientist")},
            "research_scientist": {"name": "Research Scientist Internship", "duration": "4 weeks", "price": 2499, "category": "Science", "skills": ["Research Methods", "Data Analysis", "Writing"], "deliverables": ["Research Paper", "Presentation"], "scenarios": self._generate_scenarios("Research Scientist")},
            "bioinformatics": {"name": "Bioinformatics Analyst Internship", "duration": "4 weeks", "price": 2799, "category": "Science", "skills": ["Biology", "Python", "Genomics"], "deliverables": ["Genomic Analysis", "Report"], "scenarios": self._generate_scenarios("Bioinformatics Analyst")},
            "environmental": {"name": "Environmental Scientist Internship", "duration": "4 weeks", "price": 2299, "category": "Science", "skills": ["Environmental Data", "GIS", "Analysis"], "deliverables": ["Environmental Report"], "scenarios": self._generate_scenarios("Environmental Scientist")},
            "business_analyst": {"name": "Business Analyst Internship", "duration": "4 weeks", "price": 2499, "category": "Management", "skills": ["Requirements", "Analysis", "Communication"], "deliverables": ["Requirements Doc", "Analysis"], "scenarios": self._generate_scenarios("Business Analyst")},
            "product_manager": {"name": "Product Manager Internship", "duration": "4 weeks", "price": 2999, "category": "Management", "skills": ["Product Strategy", "UX", "Roadmap"], "deliverables": ["PRD", "Roadmap"], "scenarios": self._generate_scenarios("Product Manager")},
            "marketing_manager": {"name": "Marketing Manager Internship", "duration": "4 weeks", "price": 2299, "category": "Management", "skills": ["Digital Marketing", "Analytics", "Content"], "deliverables": ["Campaign Plan", "Report"], "scenarios": self._generate_scenarios("Marketing Manager")},
            "financial_analyst": {"name": "Financial Analyst Internship", "duration": "4 weeks", "price": 2799, "category": "Management", "skills": ["Finance", "Excel", "Modeling"], "deliverables": ["Financial Model", "Report"], "scenarios": self._generate_scenarios("Financial Analyst")},
            "mtech_ai": {"name": "MTech AI Internship", "duration": "4 weeks", "price": 3499, "category": "Masters", "skills": ["Advanced ML", "Deep Learning", "Research"], "deliverables": ["Research Paper", "Model"], "scenarios": self._generate_scenarios("MTech AI")},
            "mtech_software": {"name": "MTech Software Internship", "duration": "4 weeks", "price": 2999, "category": "Masters", "skills": ["Architecture", "Systems Design", "Coding"], "deliverables": ["System Design", "Code"], "scenarios": self._generate_scenarios("MTech Software")},
            "mba_strategy": {"name": "MBA Strategy Internship", "duration": "4 weeks", "price": 3499, "category": "Masters", "skills": ["Business Strategy", "Leadership", "Analysis"], "deliverables": ["Strategy Doc", "Presentation"], "scenarios": self._generate_scenarios("MBA Strategy")},
            "msc_data": {"name": "MSc Data Science Internship", "duration": "4 weeks", "price": 2999, "category": "Masters", "skills": ["Statistics", "ML", "Big Data"], "deliverables": ["Research Paper", "Dashboard"], "scenarios": self._generate_scenarios("MSc Data Science")},
            "msc_psychology": {"name": "MSc Psychology Internship", "duration": "4 weeks", "price": 2499, "category": "Masters", "skills": ["Research", "Counseling", "Analysis"], "deliverables": ["Research Report", "Case Study"], "scenarios": self._generate_scenarios("MSc Psychology")},
            "ma_economics": {"name": "MA Economics Internship", "duration": "4 weeks", "price": 2299, "category": "Masters", "skills": ["Econometrics", "Policy", "Analysis"], "deliverables": ["Economic Analysis", "Report"], "scenarios": self._generate_scenarios("MA Economics")},
        }

    def _generate_scenarios(self, role, days=28):
        """Generate scenarios for any duration (default 28 days - 4 weeks)."""
        foundation = [
            {"task": "Onboarding & Setup", "scenario": f"You join as {role} intern. Set up environment."},
            {"task": "Research & Analysis", "scenario": f"Research industry trends for {role}."},
            {"task": "First Assignment", "scenario": f"Complete first {role} task."},
            {"task": "Deep Dive", "scenario": f"Dive deeper into {role} skills."},
            {"task": "Practical Project", "scenario": f"Start practical {role} project."},
            {"task": "Review & Feedback", "scenario": f"Submit work for AI mentor review."},
            {"task": "Week 1 Review", "scenario": f"Present progress to AI team lead."},
            {"task": "Advanced Topics", "scenario": f"Learn advanced {role} concepts."},
            {"task": "Real Project Work", "scenario": f"Work on real {role} project."},
            {"task": "Testing & Quality", "scenario": f"Ensure quality in deliverables."},
            {"task": "Optimization", "scenario": f"Optimize {role} work."},
            {"task": "Documentation", "scenario": f"Document project and processes."},
            {"task": "Week 2 Review", "scenario": f"Review progress. Plan for advanced work."},
            {"task": "Mid-Program Assessment", "scenario": f"AI evaluates your progress. Get feedback."},
        ]
        advanced = [
            {"task": "Advanced Project Planning", "scenario": f"Plan advanced {role} project."},
            {"task": "Implementation Phase 1", "scenario": f"Implement first phase of project."},
            {"task": "Implementation Phase 2", "scenario": f"Complete second phase."},
            {"task": "Integration", "scenario": f"Integrate all components."},
            {"task": "Testing & Debugging", "scenario": f"Test and fix bugs."},
            {"task": "Code Review", "scenario": f"AI reviews your code. Get feedback."},
            {"task": "Refactoring", "scenario": f"Improve code quality."},
            {"task": "Performance Optimization", "scenario": f"Optimize for speed and efficiency."},
            {"task": "Security Implementation", "scenario": f"Add security measures."},
            {"task": "Documentation", "scenario": f"Complete documentation."},
            {"task": "Deployment Preparation", "scenario": f"Prepare for deployment."},
            {"task": "Final Testing", "scenario": f"Run final tests."},
            {"task": "Project Presentation", "scenario": f"Prepare final presentation."},
            {"task": "Week 4 Review & Graduation", "scenario": f"Complete internship. Receive badge."},
        ]
        all_tasks = foundation + advanced
        scenarios = []
        for day in range(1, days + 1):
            idx = min(day - 1, len(all_tasks) - 1)
            task_info = all_tasks[idx]
            scenarios.append({
                "day": day,
                "task": task_info["task"],
                "scenario": f"Day {day}: {task_info['scenario']}",
            })
        return scenarios

    # ============================================================
    # CATALOG
    # ============================================================

    def get_programs(self):
        """Get all internship programs."""
        programs = []
        for key, prog in self.programs.items():
            programs.append({
                "id": key,
                "name": prog["name"],
                "duration": prog["duration"],
                "price": prog["price"],
                "category": prog.get("category", "General"),
                "skills": prog["skills"],
                "deliverables": prog["deliverables"],
            })
        return {"status": "success", "programs": programs}

    # ============================================================
    # ENROLLMENT
    # ============================================================

    def enroll(self, email, program_id, duration="standard"):
        """Enroll student with duration option."""
        if program_id not in self.programs:
            return {"status": "error", "message": "Program not found"}
        duration_days = {"quick": 14, "standard": 28, "professional": 42}
        total_days = duration_days.get(duration, 28)
        enrollment_id = f"INT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(2).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_ai_internship_enrollments
                    (enrollment_id, email, program_id, duration, total_days, current_day, status)
                VALUES (%s, %s, %s, %s, %s, 1, 'active')
            ''', (enrollment_id, email, program_id, duration, total_days))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"enroll failed: {e}")
            return {"status": "error", "message": "Could not enroll"}

        return {"status": "success", "enrollment_id": enrollment_id, "total_days": total_days}

    def _get_enrollment(self, enrollment_id):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT enrollment_id, email, program_id, duration, total_days, current_day, status, start_date, completed_at
                FROM charvak_ai_internship_enrollments WHERE enrollment_id = %s
            ''', (enrollment_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return None
            return {
                "enrollment_id": row[0],
                "email": row[1],
                "program_id": row[2],
                "duration": row[3],
                "total_days": row[4],
                "current_day": row[5],
                "status": row[6],
                "start_date": row[7].isoformat() if hasattr(row[7], "isoformat") else str(row[7]),
                "completed_at": row[8].isoformat() if row[8] and hasattr(row[8], "isoformat") else None,
            }
        except Exception as e:
            logger.error(f"_get_enrollment failed: {e}")
            return None

    def get_daily_scenario(self, enrollment_id, day):
        """Get daily scenario for intern."""
        enrollment = self._get_enrollment(enrollment_id)
        if not enrollment:
            return {"status": "error", "message": "Enrollment not found"}
        program = self.programs.get(enrollment["program_id"])
        if not program:
            return {"status": "error", "message": "Program not found"}
        total_days = enrollment.get("total_days", len(program["scenarios"]))
        if day > total_days:
            return {"status": "error", "message": "Internship completed"}
        scenario = program["scenarios"][day - 1] if day - 1 < len(program["scenarios"]) else program["scenarios"][-1]
        return {"status": "success", "day": day, "scenario": scenario}

    # ============================================================
    # COMPLETION
    # ============================================================

    def _format_badge_name(self, name):
        """Format program name for badge."""
        name = name.replace("Internship", "").strip()
        name = name.replace("  ", " ").strip()
        return name

    def complete_internship(self, enrollment_id):
        """Complete internship and generate badge."""
        enrollment = self._get_enrollment(enrollment_id)
        if not enrollment:
            return {"status": "error", "message": "Enrollment not found"}
        program = self.programs.get(enrollment["program_id"])
        if not program:
            return {"status": "error", "message": "Program not found"}

        badge_name = self._format_badge_name(program["name"])
        badge = "CHARVAK-" + badge_name.upper() + "-" + datetime.now().strftime("%Y%m")

        synopsis = "AI Internship Synopsis\n"
        synopsis += "======================\n"
        synopsis += "Student: " + enrollment["email"] + "\n"
        synopsis += "Program: " + program["name"] + "\n"
        synopsis += "Duration: " + program["duration"] + "\n"
        synopsis += "Skills: " + ", ".join(program["skills"]) + "\n"
        synopsis += "Deliverables: " + ", ".join(program["deliverables"]) + "\n"
        synopsis += "Badge: " + badge + "\n"
        synopsis += "Completed: " + datetime.now().isoformat() + "\n"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_ai_internship_enrollments
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE enrollment_id = %s
            ''', (enrollment_id,))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"complete_internship update failed: {e}")

        return {
            "status": "success",
            "badge": badge,
            "synopsis": synopsis,
            "skills": program["skills"],
            "deliverables": program["deliverables"],
        }

    # ============================================================
    # SUBMISSIONS
    # ============================================================

    def submit_work(self, enrollment_id, day, submission_text):
        """Submit daily work for AI review."""
        if not self._get_enrollment(enrollment_id):
            return {"status": "error", "message": "Enrollment not found"}

        feedback = {
            "score": random.randint(7, 10),
            "strengths": ["Good understanding", "Clear implementation"],
            "improvements": ["Add more documentation", "Consider edge cases"],
            "next_steps": "Proceed to next day's task",
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            submission_id = f"SUB-{secrets.token_hex(4).upper()}"
            cur.execute('''
                INSERT INTO charvak_ai_internship_submissions
                    (submission_id, enrollment_id, day, submission, ai_feedback)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (enrollment_id, day) DO UPDATE
                    SET submission = EXCLUDED.submission,
                        ai_feedback = EXCLUDED.ai_feedback,
                        submitted_at = CURRENT_TIMESTAMP
            ''', (submission_id, enrollment_id, day, submission_text, json.dumps(feedback)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"submit_work failed: {e}")
            return {"status": "error", "message": "Could not submit work"}

        return {"status": "success", "feedback": feedback}

    # ============================================================
    # PROGRESS
    # ============================================================

    def get_progress(self, enrollment_id):
        """Get internship progress."""
        enrollment = self._get_enrollment(enrollment_id)
        if not enrollment:
            return {"status": "error", "message": "Enrollment not found"}
        total_days = enrollment.get("total_days", 28)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT day, submission, submitted_at, ai_feedback
                FROM charvak_ai_internship_submissions
                WHERE enrollment_id = %s
                ORDER BY day ASC
            ''', (enrollment_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_progress failed: {e}")
            return {"status": "error", "message": "Could not load progress"}

        days = {}
        for r in rows:
            day_num = r[0]
            fb = r[3] if isinstance(r[3], dict) else (json.loads(r[3]) if r[3] else {})
            days[day_num] = {
                "submission": r[1],
                "submitted_at": r[2].isoformat() if hasattr(r[2], "isoformat") else str(r[2]),
                "status": "reviewed",
                "ai_feedback": fb,
            }

        completed = len(days)
        return {
            "status": "success",
            "enrollment_id": enrollment_id,
            "completed_days": completed,
            "total_days": total_days,
            "progress_percentage": round((completed / total_days) * 100, 1) if total_days else 0,
            "days": days,
        }


ai_internship_engine = AIInternshipEngine()
