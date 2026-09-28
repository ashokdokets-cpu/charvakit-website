"""
Charvak AI Internship Program
Multi-duration AI-powered internship with real-world scenarios
(DB-backed - Session E/3)
"""
import json
import logging
import random
import re
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

            # --- Phase 1: tiers + custom programs + scenario cache ---
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ai_internship_tiers (
                    tier_key        TEXT PRIMARY KEY,
                    tier_name       TEXT NOT NULL,
                    weeks           INTEGER NOT NULL,
                    business_days   INTEGER NOT NULL,
                    price_inr       INTEGER NOT NULL,
                    price_usd       INTEGER NOT NULL,
                    display_order   INTEGER NOT NULL,
                    is_active       INTEGER DEFAULT 1,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ai_internship_custom_programs (
                    program_id      TEXT PRIMARY KEY,
                    name            TEXT NOT NULL,
                    role_title      TEXT NOT NULL,
                    category        TEXT DEFAULT 'Custom',
                    skills          JSONB DEFAULT '[]'::jsonb,
                    deliverables    JSONB DEFAULT '[]'::jsonb,
                    outline         JSONB DEFAULT '[]'::jsonb,
                    max_days        INTEGER DEFAULT 80,
                    requested_by    TEXT,
                    is_public       INTEGER DEFAULT 1,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ai_internship_scenarios (
                    scenario_id         TEXT PRIMARY KEY,
                    program_id          TEXT NOT NULL,
                    tier_key            TEXT NOT NULL,
                    day                 INTEGER NOT NULL,
                    role_title          TEXT NOT NULL,
                    title               TEXT NOT NULL,
                    overview            TEXT NOT NULL,
                    learning_objectives JSONB DEFAULT '[]'::jsonb,
                    step_by_step        JSONB DEFAULT '[]'::jsonb,
                    deliverable         TEXT,
                    acceptance_criteria JSONB DEFAULT '[]'::jsonb,
                    resources           JSONB DEFAULT '[]'::jsonb,
                    mentor_note         TEXT,
                    estimated_time      TEXT,
                    difficulty          TEXT,
                    raw_json            JSONB,
                    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(program_id, tier_key, day)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_ai_intern_scen_lookup
                ON charvak_ai_internship_scenarios(program_id, tier_key, day)''')

            cur.execute('''
                ALTER TABLE charvak_ai_internship_enrollments
                ADD COLUMN IF NOT EXISTS tier_key TEXT DEFAULT 'standard'
            ''')
            cur.execute('''
                ALTER TABLE charvak_ai_internship_enrollments
                ADD COLUMN IF NOT EXISTS mentor_asks_used INTEGER DEFAULT 0
            ''')
            cur.execute('''
                ALTER TABLE charvak_ai_internship_enrollments
                ADD COLUMN IF NOT EXISTS amount_paid_inr INTEGER DEFAULT 0
            ''')
            cur.execute('''
                ALTER TABLE charvak_ai_internship_enrollments
                ADD COLUMN IF NOT EXISTS razorpay_payment_id TEXT
            ''')

            # Seed tiers (idempotent)
            tiers_seed = [
                ("sprint",          "Sprint (2 weeks)",       2,  10, 1299,  16, 1),
                ("standard",        "Standard (4 weeks)",     4,  20, 2499,  30, 2),
                ("extended",        "Extended (6 weeks)",     6,  30, 3499,  42, 3),
                ("immersive",       "Immersive (8 weeks)",    8,  40, 4499,  54, 4),
                ("semester_lite",   "Semester Lite (10 wk)", 10,  50, 5499,  66, 5),
                ("semester",        "Semester (12 weeks)",   12,  60, 6499,  78, 6),
                ("semester_plus",   "Semester Plus (14 wk)", 14,  70, 7499,  90, 7),
                ("capstone",        "Capstone (16 weeks)",   16,  80, 8499, 102, 8),
            ]
            for tk, tn, wk, bd, inr, usd, order in tiers_seed:
                cur.execute('''
                    INSERT INTO charvak_ai_internship_tiers
                        (tier_key, tier_name, weeks, business_days, price_inr, price_usd, display_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tier_key) DO NOTHING
                ''', (tk, tn, wk, bd, inr, usd, order))

            # Refresh prices for existing rows (idempotent, keeps in sync with seed)
            cur.execute('''
                UPDATE charvak_ai_internship_tiers SET
                    price_inr = v.price_inr, price_usd = v.price_usd,
                    tier_name = v.tier_name, weeks = v.weeks, business_days = v.business_days
                FROM (VALUES
                    ('sprint', 'Sprint (2 weeks)', 2, 10, 1299, 16),
                    ('standard', 'Standard (4 weeks)', 4, 20, 2499, 30),
                    ('extended', 'Extended (6 weeks)', 6, 30, 3499, 42),
                    ('immersive', 'Immersive (8 weeks)', 8, 40, 4499, 54),
                    ('semester_lite', 'Semester Lite (10 wk)', 10, 50, 5499, 66),
                    ('semester', 'Semester (12 weeks)', 12, 60, 6499, 78),
                    ('semester_plus', 'Semester Plus (14 wk)', 14, 70, 7499, 90),
                    ('capstone', 'Capstone (16 weeks)', 16, 80, 8499, 102)
                ) AS v(tier_key, tier_name, weeks, business_days, price_inr, price_usd)
                WHERE charvak_ai_internship_tiers.tier_key = v.tier_key
            ''')

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

    def create_custom_program(self, email, role_title, duration_weeks=4, tier_key="standard"):
        """Design a custom internship program via AI. Returns a program dict compatible with get_programs()."""
        role_title = (role_title or "").strip()[:80]
        if not role_title:
            return {"status": "error", "message": "Role title is required"}

        prompt = (
            f"Design a {duration_weeks}-week internship curriculum for the role: {role_title}.\n\n"
            "Return STRICT JSON only with this exact shape:\n"
            "{\n"
            '  "name": "<Internship program name>",\n'
            '  "category": "<one of: Engineering, Science, Management, Masters, Design, Custom>",\n'
            '  "skills": ["<4-6 core skills>"],\n'
            '  "deliverables": ["<3-4 concrete deliverables>"],\n'
            '  "outline": [{"week": 1, "focus": "<theme>", "deliverable": "<what they ship>"}, ...]\n'
            "}"
        )
        outline = self._call_openai_json(prompt)

        if not outline or not isinstance(outline, dict):
            logger.warning(f"AI custom program failed for '{role_title}' - using stub")
            outline = {
                "name": f"{role_title} Internship",
                "category": "Custom",
                "skills": [role_title, "Communication", "Problem Solving"],
                "deliverables": ["Project", "Report", "Presentation"],
                "outline": [
                    {"week": i + 1, "focus": f"Week {i + 1} - {role_title} practice", "deliverable": "Weekly task"}
                    for i in range(duration_weeks)
                ],
            }

        def _clean_list(v, n=6):
            if not isinstance(v, list):
                return []
            return [str(x)[:120] for x in v[:n] if x]

        name = str(outline.get("name") or f"{role_title} Internship")[:120]
        category = str(outline.get("category") or "Custom")[:40]
        skills = _clean_list(outline.get("skills")) or [role_title]
        deliverables = _clean_list(outline.get("deliverables")) or ["Project"]
        raw_outline = outline.get("outline") if isinstance(outline.get("outline"), list) else []
        outline_weeks = [w for w in raw_outline if isinstance(w, dict)][:12]

        program_id = f"CUSTOM-{secrets.token_hex(4).upper()}"
        max_days = max(1, int(duration_weeks) * 5)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_ai_internship_custom_programs
                    (program_id, name, role_title, category, skills, deliverables, outline, max_days, requested_by, is_public)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s, 0)
            ''', (
                program_id, name, role_title, category,
                json.dumps(skills), json.dumps(deliverables), json.dumps(outline_weeks),
                max_days, email,
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_custom_program insert failed: {e}")
            return {"status": "error", "message": "Could not save custom program"}

        return {
            "status": "success",
            "program": {
                "id": program_id,
                "name": name,
                "duration": f"{duration_weeks} weeks",
                "price": 1299,  # minimum tier price (sprint)
                "category": category,
                "skills": skills,
                "deliverables": deliverables,
                "is_custom": True,
            },
        }

    def _resolve_program(self, program_id, email=None):
        """Look up a program_id in static first, then custom. Returns a dict or None."""
        if program_id in self.programs:
            p = self.programs[program_id]
            return {
                "id": program_id,
                "name": p["name"],
                "duration": p["duration"],
                "price": p["price"],
                "category": p.get("category", "General"),
                "skills": p["skills"],
                "deliverables": p["deliverables"],
                "is_custom": False,
            }
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT program_id, name, role_title, category, skills, deliverables, max_days, requested_by "
                "FROM charvak_ai_internship_custom_programs WHERE program_id = %s",
                (program_id,),
            )
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return None
            weeks = max(1, (row[6] or 20) // 5)
            return {
                "id": row[0],
                "name": row[1],
                "duration": f"{weeks} weeks",
                "price": 0,
                "category": row[3] or "Custom",
                "skills": row[4] if isinstance(row[4], list) else [],
                "deliverables": row[5] if isinstance(row[5], list) else [],
                "is_custom": True,
                "requested_by": row[7],
            }
        except Exception as e:
            logger.error(f"_resolve_program custom lookup failed: {e}")
            return None

    # ============================================================
    # CATALOG
    # ============================================================

    def _get_tier_by_key(self, tier_key):
        """Fetch a single tier row. Returns dict or None."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT tier_key, tier_name, weeks, business_days, price_inr, price_usd "
                "FROM charvak_ai_internship_tiers WHERE tier_key = %s AND is_active = 1",
                (tier_key,),
            )
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return None
            return {
                "tier_key": row[0], "tier_name": row[1], "weeks": row[2],
                "business_days": row[3], "price_inr": row[4], "price_usd": row[5],
            }
        except Exception as e:
            logger.error(f"_get_tier_by_key failed: {e}")
            return None

    def get_tiers(self):
        """Return the duration tiers sorted by display order."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT tier_key, tier_name, weeks, business_days, price_inr, price_usd, display_order
                FROM charvak_ai_internship_tiers
                WHERE is_active = 1
                ORDER BY display_order ASC
            """)
            rows = cur.fetchall()
            cur.close(); conn.close()
            tiers = [
                {
                    "tier_key": r[0], "tier_name": r[1], "weeks": r[2],
                    "business_days": r[3], "price_inr": r[4],
                    "price_usd": r[5], "display_order": r[6],
                }
                for r in rows
            ]
            return {"status": "success", "tiers": tiers}
        except Exception as e:
            logger.error(f"get_tiers failed: {e}")
            return {"status": "error", "message": "Could not load tiers", "tiers": []}

    # ============================================================
    # RICH SCENARIO GENERATION (Phase 2)
    # ============================================================

    def _call_openai_json(self, prompt):
        """Call OpenAI in JSON mode. Mirrors student_suite_engine pattern."""
        try:
            import os
            import requests as _requests
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set — cannot generate scenario")
                return None
            response = _requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a curriculum designer. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.6,
                    "response_format": {"type": "json_object"},
                },
                timeout=25,
            )
            if response.status_code != 200:
                logger.error(f"OpenAI HTTP {response.status_code}: {response.text[:200]}")
                return None
            body = response.json()
            content = body["choices"][0]["message"]["content"]
            # Defensive fence strip
            content = content.strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*", "", content)
                content = re.sub(r"\s*```$", "", content)
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return None

    def _stub_scenario(self, role_title, day, program):
        """Fallback shape so the page never breaks."""
        total = program.get("_total_days", 14)
        return {
            "title": f"Day {day} with {role_title}",
            "overview": f"You are working as a {role_title} intern. Focus today on practicing the core skills of the role and applying them to a real task.",
            "learning_objectives": [
                f"Apply {role_title} fundamentals to a real task",
                "Document your approach and reasoning",
                "Identify one area to improve next",
            ],
            "step_by_step": [
                {"step": 1, "title": "Review the goal", "detail": "Read the task carefully and note what success looks like.", "time": "10 min"},
                {"step": 2, "title": "Plan your approach", "detail": "Sketch 2-3 approaches and pick the cleanest one.", "time": "15 min"},
                {"step": 3, "title": "Execute", "detail": f"Carry out the task as a {role_title} would.", "time": "30 min"},
                {"step": 4, "title": "Reflect", "detail": "Write 2-3 sentences on what you learned and what was hard.", "time": "10 min"},
            ],
            "deliverable": "A short writeup of what you did and what you learned.",
            "acceptance_criteria": [
                "You finished the core task",
                "You documented your approach",
                "You identified one improvement for tomorrow",
            ],
            "resources": [],
            "mentor_note": "Every day is a small step. Consistency beats intensity.",
            "estimated_time": "60-90 min",
            "difficulty": "beginner" if day <= total // 3 else ("intermediate" if day <= 2 * total // 3 else "advanced"),
        }

    def _generate_rich_scenario(self, program, program_id, tier_key, day):
        """Generate a full structured scenario for one day."""
        role_title = program.get("_role_title") or program["name"].replace(" Internship", "").strip()
        skills = program.get("skills", [])
        total_days = program.get("_total_days", 14)
        program_name = program["name"]

        first_third = max(1, total_days // 3)
        second_third = max(first_third + 1, (2 * total_days) // 3)

        prompt = f"""You are a senior {role_title} designing Day {day} of a {total_days}-day internship curriculum.

Program: {program_name}
Core skills being developed: {", ".join(skills)}
Student level: beginner on Day 1, advancing to strong intermediate by the final day.
This is Day {day} of {total_days}. Difficulty should scale accordingly:
- Days 1-{first_third}: beginner (foundations, setup, orientation)
- Days {first_third + 1}-{second_third}: intermediate (real work, iteration)
- Days {second_third + 1}-{total_days}: advanced (deep work, polish, presentation)

Return STRICT JSON only. No prose, no markdown fences.

{{
  "title": "short title, max 8 words, no 'Day N:' prefix",
  "overview": "2-3 sentences: what this day covers and why it matters for a {role_title}",
  "learning_objectives": [
    "verb-first objective, 1 sentence",
    "3-5 items total"
  ],
  "step_by_step": [
    {{
      "step": 1,
      "title": "short step name",
      "detail": "actionable instructions — include exact tools, filenames, commands, URLs where relevant. 2-4 sentences.",
      "time": "15 min"
    }}
  ],
  "deliverable": "one sentence: the concrete artifact the student produces and hands in today",
  "acceptance_criteria": [
    "checkable item the student can self-verify",
    "3-4 items total"
  ],
  "resources": [
    {{"title": "resource name", "url": "https://..."}}
  ],
  "mentor_note": "one short sentence of voice-of-mentor guidance — warm, specific to today",
  "estimated_time": "45 min",
  "difficulty": "beginner"
}}

Rules:
- Be specific to {role_title}, not generic advice.
- Onboarding/setup days: real commands and file paths.
- Mid-program days: real deliverables (code, docs, models, reports).
- Final days: presentation, portfolio, packaging.
- Resources: 2-3 real, working URLs (docs, tutorials, GitHub repos). If none fit, use an empty array.
- step_by_step: 4-6 steps.
- Do NOT include any text outside the JSON object."""

        result = self._call_openai_json(prompt)
        if not result or not isinstance(result, dict):
            logger.warning(f"AI generation failed for {program_id}/{tier_key}/day{day} — using stub")
            return self._stub_scenario(role_title, day, program)

        # Normalize + guard mandatory keys
        required = ["title", "overview", "learning_objectives", "step_by_step",
                    "deliverable", "acceptance_criteria", "resources",
                    "mentor_note", "estimated_time", "difficulty"]
        for key in required:
            if key not in result:
                result[key] = self._stub_scenario(role_title, day, program).get(key)
        if not isinstance(result.get("learning_objectives"), list):
            result["learning_objectives"] = [str(result.get("learning_objectives", ""))]
        if not isinstance(result.get("step_by_step"), list):
            result["step_by_step"] = []
        if not isinstance(result.get("acceptance_criteria"), list):
            result["acceptance_criteria"] = []
        if not isinstance(result.get("resources"), list):
            result["resources"] = []
        return result

    def get_or_create_scenario(self, program_id, tier_key, day):
        """Cache-first: return scenario from DB, or generate + cache."""
        # 1. Cache lookup
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT scenario_id, title, overview, learning_objectives, step_by_step,
                       deliverable, acceptance_criteria, resources, mentor_note,
                       estimated_time, difficulty
                FROM charvak_ai_internship_scenarios
                WHERE program_id = %s AND tier_key = %s AND day = %s
            """, (program_id, tier_key, day))
            row = cur.fetchone()
            cur.close(); conn.close()
            if row:
                return {
                    "status": "success",
                    "day": day,
                    "title": row[1],
                    "overview": row[2],
                    "learning_objectives": row[3] or [],
                    "step_by_step": row[4] or [],
                    "deliverable": row[5],
                    "acceptance_criteria": row[6] or [],
                    "resources": row[7] or [],
                    "mentor_note": row[8],
                    "estimated_time": row[9],
                    "difficulty": row[10],
                    "cached": True,
                }
        except Exception as e:
            logger.error(f"scenario cache lookup failed: {e}")

        # 2. Look up the program
        program = self.programs.get(program_id)
        if not program:
            return {"status": "error", "message": "Program not found"}

        # 3. Resolve total_days from tier
        total_days = 14
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT business_days FROM charvak_ai_internship_tiers WHERE tier_key = %s", (tier_key,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if row:
                total_days = row[0]
        except Exception:
            pass
        program["_total_days"] = total_days
        program["_role_title"] = program["name"].replace(" Internship", "").strip()

        # 4. Generate
        generated = self._generate_rich_scenario(program, program_id, tier_key, day)

        # 5. Cache
        try:
            from database import db
            scenario_id = f"SCN-{secrets.token_hex(6).upper()}"
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_ai_internship_scenarios
                    (scenario_id, program_id, tier_key, day, role_title, title, overview,
                     learning_objectives, step_by_step, deliverable, acceptance_criteria,
                     resources, mentor_note, estimated_time, difficulty, raw_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s::jsonb,
                        %s::jsonb, %s, %s, %s, %s::jsonb)
                ON CONFLICT (program_id, tier_key, day) DO NOTHING
            """, (
                scenario_id, program_id, tier_key, day,
                program.get("_role_title", ""), generated["title"], generated["overview"],
                json.dumps(generated["learning_objectives"]),
                json.dumps(generated["step_by_step"]),
                generated["deliverable"],
                json.dumps(generated["acceptance_criteria"]),
                json.dumps(generated["resources"]),
                generated.get("mentor_note", ""),
                generated["estimated_time"], generated["difficulty"],
                json.dumps(generated),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"scenario cache insert failed: {e}")

        return {
            "status": "success",
            "day": day,
            "title": generated["title"],
            "overview": generated["overview"],
            "learning_objectives": generated["learning_objectives"],
            "step_by_step": generated["step_by_step"],
            "deliverable": generated["deliverable"],
            "acceptance_criteria": generated["acceptance_criteria"],
            "resources": generated["resources"],
            "mentor_note": generated.get("mentor_note", ""),
            "estimated_time": generated["estimated_time"],
            "difficulty": generated["difficulty"],
            "cached": False,
        }

    def get_my_enrollments(self, email):
        """Return all active enrollments for an email — powers the Resume banner."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT enrollment_id, program_id, duration, total_days,
                       current_day, status, start_date, tier_key
                FROM charvak_ai_internship_enrollments
                WHERE email = %s AND status = 'active'
                ORDER BY start_date DESC
            """, (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            enrollments = []
            for r in rows:
                program = self.programs.get(r[1])
                program_name = program["name"] if program else r[1]
                role_title = program_name.replace(" Internship", "").strip() if program else r[1]
                enrollments.append({
                    "enrollment_id": r[0],
                    "program_id": r[1],
                    "program_name": program_name,
                    "role_title": role_title,
                    "duration": r[2],
                    "total_days": r[3],
                    "current_day": r[4] or 1,
                    "status": r[5],
                    "start_date": r[6].isoformat() if hasattr(r[6], "isoformat") else str(r[6]),
                    "tier_key": r[7] or "standard",
                })
            return {"status": "success", "enrollments": enrollments}
        except Exception as e:
            logger.error(f"get_my_enrollments failed: {e}")
            return {"status": "error", "message": "Could not load enrollments", "enrollments": []}

    def record_day_viewed(self, enrollment_id, day):
        """Bump current_day forward (never backward) when a day loads."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_ai_internship_enrollments
                SET current_day = GREATEST(COALESCE(current_day, 1), %s)
                WHERE enrollment_id = %s
            """, (day, enrollment_id))
            conn.commit()
            cur.close(); conn.close()
            return True
        except Exception as e:
            logger.error(f"record_day_viewed failed: {e}")
            return False

    def abandon_enrollment(self, enrollment_id, email=None):
        """Mark an enrollment as abandoned. If email is provided, checks ownership."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if email:
                cur.execute('''
                    UPDATE charvak_ai_internship_enrollments
                    SET status = 'abandoned'
                    WHERE enrollment_id = %s AND email = %s AND status = 'active'
                ''', (enrollment_id, email))
            else:
                cur.execute('''
                    UPDATE charvak_ai_internship_enrollments
                    SET status = 'abandoned'
                    WHERE enrollment_id = %s AND status = 'active'
                ''', (enrollment_id,))
            rows = cur.rowcount
            conn.commit()
            cur.close(); conn.close()
            if rows == 0:
                return {"status": "error", "message": "Enrollment not found or already inactive"}
            return {"status": "success", "enrollment_id": enrollment_id}
        except Exception as e:
            logger.error(f"abandon_enrollment failed: {e}")
            return {"status": "error", "message": "Could not abandon enrollment"}

    def get_programs(self, email=None):
        """Get all internship programs. If email provided, also includes that user's custom programs."""
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
                "is_custom": False,
            })
        if email:
            try:
                from database import db
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute(
                    "SELECT program_id, name, category, skills, deliverables, max_days "
                    "FROM charvak_ai_internship_custom_programs "
                    "WHERE requested_by = %s ORDER BY created_at DESC",
                    (email,),
                )
                for row in cur.fetchall():
                    weeks = max(1, (row[5] or 20) // 5)
                    programs.append({
                        "id": row[0],
                        "name": row[1],
                        "duration": f"{weeks} weeks",
                        "price": 1299,  # minimum tier price (sprint)
                        "category": row[2] or "Custom",
                        "skills": row[3] if isinstance(row[3], list) else [],
                        "deliverables": row[4] if isinstance(row[4], list) else [],
                        "is_custom": True,
                    })
                cur.close(); conn.close()
            except Exception as e:
                logger.error(f"get_programs custom merge failed: {e}")
        return {"status": "success", "programs": programs}

    # ============================================================
    # ENROLLMENT
    # ============================================================

    def enroll(self, email, program_id, duration="standard"):
        """Enroll student with duration option."""
        resolved = self._resolve_program(program_id, email)
        if not resolved:
            return {"status": "error", "message": "Program not found"}
        duration_days = {"quick": 14, "standard": 28, "professional": 42}
        total_days = duration_days.get(duration, 28)
        enrollment_id = f"INT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(2).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            # Auto-abandon any prior active enrollment for the same (email, program_id).
            # Rationale: a user re-enrolling in the same program is almost always a restart.
            # Different programs remain active so users can pursue more than one at a time.
            cur.execute('''
                UPDATE charvak_ai_internship_enrollments
                SET status = 'abandoned'
                WHERE email = %s AND program_id = %s AND status = 'active'
            ''', (email, program_id))
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

    def find_enrollment_by_payment(self, payment_id):
        """Return enrollment_id if a payment_id already has an enrollment. Idempotency check."""
        if not payment_id:
            return None
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT enrollment_id FROM charvak_ai_internship_enrollments "
                "WHERE razorpay_payment_id = %s LIMIT 1",
                (payment_id,),
            )
            row = cur.fetchone()
            cur.close(); conn.close()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"find_enrollment_by_payment failed: {e}")
            return None

    def enroll_paid(self, email, program_id, tier_key, payment_id, amount_paid_inr):
        """Create a paid enrollment. Caller MUST have verified the Razorpay payment first."""
        tier = self._get_tier_by_key(tier_key)
        if not tier:
            return {"status": "error", "message": "Invalid tier"}
        resolved = self._resolve_program(program_id, email)
        if not resolved:
            return {"status": "error", "message": "Program not found"}

        enrollment_id = f"INT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(2).upper()}"
        total_days = tier["business_days"]
        # duration string used by existing scenario-generator code paths
        duration = tier_key

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE charvak_ai_internship_enrollments "
                "SET status = 'abandoned' "
                "WHERE email = %s AND program_id = %s AND status = 'active'",
                (email, program_id),
            )
            cur.execute('''
                INSERT INTO charvak_ai_internship_enrollments
                    (enrollment_id, email, program_id, duration, total_days,
                     current_day, status, tier_key, amount_paid_inr, razorpay_payment_id,
                     mentor_asks_used)
                VALUES (%s, %s, %s, %s, %s, 1, 'active', %s, %s, %s, 0)
            ''', (
                enrollment_id, email, program_id, duration, total_days,
                tier_key, amount_paid_inr, payment_id,
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"enroll_paid failed: {e}")
            return {"status": "error", "message": "Could not create enrollment"}

        # Send confirmation email (non-fatal: enrollment already created)
        try:
            from enhanced_email import enhanced_email
            _name = ""
            try:
                from database import db as _db
                _c = _db.get_connection(); _cur = _c.cursor()
                _cur.execute("SELECT name FROM users WHERE email = %s LIMIT 1", (email,))
                _row = _cur.fetchone()
                _name = (_row[0] if _row and _row[0] else "")
                _cur.close(); _c.close()
            except Exception:
                pass
            enhanced_email.send_internship_enrollment(
                email=email,
                name=_name,
                program_name=resolved.get("name") or program_id,
                tier_name=tier.get("tier_name") or tier_key,
                amount_inr=amount_paid_inr,
                enrollment_id=enrollment_id,
                duration_weeks=tier.get("weeks", 4),
                total_days=total_days,
            )
        except Exception as mail_e:
            logger.warning(f"enroll_paid confirmation email failed (non-fatal): {mail_e}")

        return {
            "status": "success",
            "enrollment_id": enrollment_id,
            "total_days": total_days,
            "tier_key": tier_key,
            "amount_paid_inr": amount_paid_inr,
        }

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
        """Get daily scenario for intern — rich, AI-generated, cached."""
        enrollment = self._get_enrollment(enrollment_id)
        if not enrollment:
            return {"status": "error", "message": "Enrollment not found"}
        program_id = enrollment["program_id"]
        tier_key = enrollment.get("tier_key") or "standard"
        total_days = enrollment.get("total_days", 14)
        if day > total_days:
            return {"status": "error", "message": "Internship completed"}
        result = self.get_or_create_scenario(program_id, tier_key, day)
        if result.get("status") == "success":
            result["program_id"] = program_id
            result["tier_key"] = tier_key
            result["total_days"] = total_days
            # Remember progress so the user can resume from any device
            self.record_day_viewed(enrollment_id, day)
        return result

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

    def _call_openai_json_mentor(self, prompt):
        """Call OpenAI in JSON mode. Mirrors student_suite_engine pattern."""
        try:
            import os
            import requests as _requests
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set - cannot call OpenAI")
                return None
            response = _requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are an experienced technical mentor. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"},
                },
                timeout=25,
            )
            if response.status_code != 200:
                logger.error(f"OpenAI HTTP {response.status_code}: {response.text[:200]}")
                return None
            body = response.json()
            content = (body.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith("json"):
                    content = content[4:].strip()
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
            except Exception as e:
                logger.error(f"OpenAI JSON parse failed: {e}")
            return None
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return None

    def _stub_feedback(self):
        """Fallback feedback if AI fails so the page never breaks."""
        return {
            "score": random.randint(7, 10),
            "strengths": ["Submission received", "Task attempted"],
            "improvements": ["AI feedback unavailable - try again later"],
            "next_steps": "Proceed to next day's task",
        }

    def _evaluate_submission_ai(self, day, program_name, role_title, submission_text):
        """Evaluate a student submission with OpenAI. Returns structured feedback."""
        prompt = (
            f"You are a senior {role_title} mentoring a student in a {program_name} internship.\n\n"
            f"Today is Day {day}. The student submitted their work for today's task. "
            "Evaluate it as a mentor would:\n"
            "- Be encouraging but honest\n"
            "- Point out concrete strengths in what they did\n"
            "- Identify specific, actionable improvements\n"
            "- Give a clear next step\n\n"
            "Student submission:\n---\n"
            f"{submission_text[:4000]}\n---\n\n"
            "Return STRICT JSON only with keys: score (int 1-10), strengths (list of 3 short sentences), "
            "improvements (list of 3 short actionable sentences), next_steps (one sentence)."
        )

        result = self._call_openai_json_mentor(prompt)
        if not result or "score" not in result:
            logger.warning(f"AI eval failed for day {day} - using stub")
            return self._stub_feedback()

        try:
            score = int(result.get("score", 7))
        except Exception:
            score = 7
        score = max(1, min(10, score))

        def _clean_list(val):
            if not isinstance(val, list):
                return []
            return [str(x)[:200] for x in val[:5] if x]

        return {
            "score": score,
            "strengths": _clean_list(result.get("strengths")) or ["Submission received"],
            "improvements": _clean_list(result.get("improvements")) or ["Keep iterating"],
            "next_steps": str(result.get("next_steps") or "Proceed to next day's task")[:300],
        }

    def submit_work(self, enrollment_id, day, submission_text):
        """Submit daily work for AI review."""
        enrollment = self._get_enrollment(enrollment_id)
        if not enrollment:
            return {"status": "error", "message": "Enrollment not found"}

        program = self.programs.get(enrollment.get("program_id"))
        program_name = program["name"] if program else "Internship"
        role_title = program_name.replace(" Internship", "").strip() if program else "intern"

        feedback = self._evaluate_submission_ai(day, program_name, role_title, submission_text)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            submission_id = f"SUB-{secrets.token_hex(4).upper()}"
            sql = (
                '''
                INSERT INTO charvak_ai_internship_submissions
                    (submission_id, enrollment_id, day, submission, ai_feedback)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (enrollment_id, day) DO UPDATE
                    SET submission = EXCLUDED.submission,
                        ai_feedback = EXCLUDED.ai_feedback,
                        submitted_at = CURRENT_TIMESTAMP
                '''
            )
            cur.execute(sql, (submission_id, enrollment_id, day, submission_text, json.dumps(feedback)))
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
