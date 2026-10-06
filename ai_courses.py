"""
Charvak AI-Driven Course System
AI plans curriculum, delivers content, assists projects, issues certificates.
Database-backed: charvak_courses, charvak_enrollments, charvak_course_lessons, charvak_certificates.
"""
import os
import json
import logging
import secrets
import requests
from datetime import datetime, timedelta

logger = logging.getLogger("charvakit.ai_courses")


class AICourseSystem:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self._ensure_tables()
        self._seed_catalog_if_empty()
        logger.info(f"AI Course System ready (DB-backed) - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")

    def _ensure_tables(self):
        """Idempotent table creation."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_courses (
                    course_id TEXT PRIMARY KEY,
                    course_name TEXT NOT NULL UNIQUE,
                    category TEXT DEFAULT 'Technology',
                    duration_weeks INTEGER DEFAULT 8,
                    price_inr INTEGER DEFAULT 0,
                    description TEXT DEFAULT '',
                    level TEXT DEFAULT 'Beginner',
                    icon TEXT DEFAULT '',
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_enrollments (
                    enrollment_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    course_name TEXT NOT NULL,
                    duration_weeks INTEGER DEFAULT 8,
                    user_level TEXT DEFAULT 'beginner',
                    curriculum JSONB,
                    progress INTEGER DEFAULT 0,
                    total_weeks INTEGER DEFAULT 8,
                    status TEXT DEFAULT 'active',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            # Session 18: recipient_name for certificate printing
            # (was referenced by get_enrollment but never added to DDL)
            cur.execute("""
                ALTER TABLE charvak_enrollments
                    ADD COLUMN IF NOT EXISTS recipient_name TEXT
            """)

            # Session 36: paid_unlock column distinguishes free 2-week preview
            # enrollments from full-course unlocks. Custom AI courses start
            # with paid_unlock = FALSE and require a 150-credit unlock to access
            # Weeks 3+, the certificate, and the AI tutor.
            cur.execute("""
                ALTER TABLE charvak_enrollments
                    ADD COLUMN IF NOT EXISTS paid_unlock BOOLEAN DEFAULT FALSE
            """)

            # Session 36: grandfather existing enrollments (one-time, self-limiting).
            # The first time this runs, every enrollment row has paid_unlock = NULL
            # (because the column was just added). We flip those to TRUE so
            # existing users keep full access. On every subsequent run there are
            # no NULLs, so the UPDATE matches zero rows.
            cur.execute("""
                UPDATE charvak_enrollments SET paid_unlock = TRUE
                WHERE paid_unlock IS NULL
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_course_lessons (
                    lesson_id TEXT PRIMARY KEY,
                    enrollment_id TEXT NOT NULL,
                    week_num INTEGER NOT NULL,
                    topic TEXT DEFAULT '',
                    lesson_content JSONB,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(enrollment_id, week_num)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_certificates (
                    certificate_id TEXT PRIMARY KEY,
                    enrollment_id TEXT NOT NULL,
                    email TEXT NOT NULL,
                    course_name TEXT NOT NULL,
                    duration_weeks INTEGER,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Session 18: recipient_name was referenced by complete_course()
            # but never added to the DDL — certificates silently failed.
            cur.execute("""
                ALTER TABLE charvak_certificates
                    ADD COLUMN IF NOT EXISTS recipient_name TEXT
            """)
            # Session 18: custom-course generator columns
            cur.execute("""
                ALTER TABLE charvak_courses
                    ADD COLUMN IF NOT EXISTS is_custom BOOLEAN DEFAULT FALSE
            """)
            cur.execute("""
                ALTER TABLE charvak_courses
                    ADD COLUMN IF NOT EXISTS generated_for_email TEXT
            """)
            cur.execute("""
                ALTER TABLE charvak_courses
                    ADD COLUMN IF NOT EXISTS generated_from_topic TEXT
            """)
            cur.execute("""
                ALTER TABLE charvak_courses
                    ADD COLUMN IF NOT EXISTS generated_at TIMESTAMP
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_courses_generated_for
                    ON charvak_courses (generated_for_email)
                    WHERE generated_for_email IS NOT NULL
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Courses table init failed: {e}")

    def _seed_catalog_if_empty(self):
        """Seed the 25-course catalog if the table is empty."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM charvak_courses")
            if cur.fetchone()[0] > 0:
                cur.close()
                conn.close()
                return

            catalog = [
                ("Full Stack Web Development", "Technology", 12, 4999, "Very High", "Beginner"),
                ("Data Science & ML", "Technology", 16, 5999, "Very High", "Intermediate"),
                ("Python Programming", "Technology", 6, 999, "Very High", "Beginner"),
                ("AWS Cloud Computing", "Cloud", 10, 3999, "Critical", "Intermediate"),
                ("DevOps Engineering", "Cloud", 12, 4999, "Very High", "Intermediate"),
                ("Cybersecurity", "Security", 14, 4999, "Critical", "Intermediate"),
                ("Java Development", "Technology", 10, 2999, "High", "Beginner"),
                ("React & Frontend", "Technology", 8, 2499, "High", "Beginner"),
                ("SQL & Database", "Data", 4, 999, "High", "Beginner"),
                ("Docker & Kubernetes", "Cloud", 6, 2499, "Very High", "Intermediate"),
                ("AI & Deep Learning", "Technology", 16, 6999, "Very High", "Advanced"),
                ("Mobile App Development", "Technology", 12, 3999, "High", "Intermediate"),
                ("Blockchain Development", "Technology", 12, 4999, "High", "Advanced"),
                ("Data Analytics", "Data", 8, 2999, "High", "Beginner"),
                ("UI/UX Design", "Design", 6, 1999, "Moderate", "Beginner"),
                ("Cloud Architecture", "Cloud", 14, 5999, "Critical", "Advanced"),
                ("Node.js Backend", "Technology", 8, 2499, "High", "Intermediate"),
                ("Python for Data Science", "Data", 10, 3999, "Very High", "Intermediate"),
                ("Machine Learning Ops", "Technology", 12, 4999, "High", "Advanced"),
                ("Spring Boot", "Technology", 8, 2499, "High", "Intermediate"),
                ("Angular Development", "Technology", 6, 1999, "Moderate", "Beginner"),
                ("Ethical Hacking", "Security", 12, 5999, "Critical", "Advanced"),
                ("Big Data", "Data", 12, 4999, "High", "Advanced"),
                ("Software Testing", "Technology", 4, 999, "Moderate", "Beginner"),
                ("Git & DevOps Tools", "Technology", 2, 499, "High", "Beginner"),
            ]

            for name, category, weeks, price, demand, level in catalog:
                course_id = f"CRS-{secrets.token_hex(4).upper()}"
                cur.execute("""
                    INSERT INTO charvak_courses
                        (course_id, course_name, category, duration_weeks, price_inr, description, level, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
                    ON CONFLICT (course_name) DO NOTHING
                """, (course_id, name, category, weeks, price, f"{name} - {demand} demand course", level))

            conn.commit()
            cur.close()
            conn.close()
            logger.info(f"Seeded {len(catalog)} courses into catalog")
        except Exception as e:
            logger.error(f"Seed catalog failed: {e}")

    def _call_openai_json(self, prompt: str, max_tokens: int = 3000) -> dict:
        """Call OpenAI and parse JSON response."""
        if not self.openai_api_key:
            return None
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": max_tokens,
                    "response_format": {"type": "json_object"}
                },
                timeout=30
            )
            data = response.json()
            return json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            logger.error(f"OpenAI JSON call failed: {e}")
            return None

    def _call_openai_text(self, prompt: str, max_tokens: int = 1500) -> str:
        """Call OpenAI and return raw text."""
        if not self.openai_api_key:
            return None
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                },
                timeout=25
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI text call failed: {e}")
            return None

    # ============================================================
    # CATALOG
    # ============================================================

    def get_catalog(self, category: str = None) -> dict:
        """Get all active courses."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if category:
                cur.execute("""
                    SELECT course_id, course_name, category, duration_weeks, price_inr, description, level
                    FROM charvak_courses WHERE status = 'active' AND category = %s
                    ORDER BY course_name
                """, (category,))
            else:
                cur.execute("""
                    SELECT course_id, course_name, category, duration_weeks, price_inr, description, level
                    FROM charvak_courses WHERE status = 'active'
                    ORDER BY course_name
                """)
            courses = [
                {
                    "course_id": r[0],
                    "course_name": r[1],
                    "category": r[2],
                    "duration_weeks": r[3],
                    "price_inr": r[4],
                    "description": r[5],
                    "level": r[6]
                }
                for r in cur.fetchall()
            ]
            cur.close()
            conn.close()
            return {"status": "success", "courses": courses, "count": len(courses)}
        except Exception as e:
            logger.error(f"get_catalog failed: {e}")
            return {"status": "error", "courses": [], "count": 0}

    def get_course(self, course_name: str) -> dict:
        """Get one course by name."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT course_id, course_name, category, duration_weeks, price_inr, description, level
                FROM charvak_courses WHERE course_name = %s
            """, (course_name,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return {"status": "error", "message": "Course not found"}
            return {
                "status": "success",
                "course": {
                    "course_id": row[0],
                    "course_name": row[1],
                    "category": row[2],
                    "duration_weeks": row[3],
                    "price_inr": row[4],
                    "description": row[5],
                    "level": row[6]
                }
            }
        except Exception as e:
            logger.error(f"get_course failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # CURRICULUM
    # ============================================================

    def plan_curriculum(self, course_name: str, duration_weeks: int, user_level: str = "beginner") -> dict:
        """AI plans curriculum."""
        if self.openai_api_key:
            curriculum = self._call_openai_json(
                f"Create a {duration_weeks}-week curriculum for '{course_name}' for {user_level} level. Include weekly topics, learning objectives (3-5 each), and a project. Return JSON: {{\"course\": \"...\", \"weeks\": [{{\"week\": 1, \"topic\": \"...\", \"objectives\": [...], \"project\": \"...\"}}]}}",
                max_tokens=3000
            )
            if curriculum:
                return curriculum
        return self._fallback_curriculum(course_name, duration_weeks)

    def _fallback_curriculum(self, course_name: str, duration_weeks: int) -> dict:
        weeks = []
        for i in range(1, duration_weeks + 1):
            weeks.append({
                "week": i,
                "topic": f"{course_name} - Week {i}",
                "objectives": [f"Understand concept {i}", f"Apply {i} in practice"],
                "project": f"Week {i} mini-project"
            })
        return {"course": course_name, "duration_weeks": duration_weeks, "weeks": weeks}

    # ============================================================
    # Session 18: Custom course generator
    # ============================================================

    def _slugify_course_name(self, topic: str, level: str) -> str:
        """Build a descriptive, URL-safe course name from a topic."""
        import re as _re
        clean = _re.sub(r"[^\w\s\-]", "", topic).strip()
        clean = _re.sub(r"\s+", " ", clean)
        # Truncate to keep course_name under 80 chars
        if len(clean) > 60:
            clean = clean[:60].rsplit(" ", 1)[0]
        lvl = (level or "mid").strip().title()
        return f"{clean} ({lvl} Intensive)"

    def generate_custom_course(self, email: str, topic: str, level: str = "mid",
                                weeks: int = 4, role_hint: str = "") -> dict:
        """
        Generate a private custom course for one user. Reuses plan_curriculum()
        but persists a new row to charvak_courses with is_custom=TRUE and
        generated_for_email=email.

        Idempotent per (email, topic, level): if a matching custom course
        already exists for this user, returns it without regenerating.
        """
        email = (email or "").strip().lower()
        topic = (topic or "").strip()
        level = (level or "mid").strip().lower()
        if not email or not topic:
            return {"status": "error", "message": "email and topic required"}

        # Clamp weeks to a sane range
        try:
            weeks = max(2, min(12, int(weeks)))
        except Exception:
            weeks = 4

        self._ensure_tables()

        course_name = self._slugify_course_name(topic, level)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Idempotency: same user + same topic + same level = return existing
            cur.execute("""
                SELECT course_id, course_name, duration_weeks, description
                FROM charvak_courses
                WHERE generated_for_email = %s
                  AND generated_from_topic = %s
                  AND level = %s
                  AND is_custom = TRUE
                LIMIT 1
            """, (email, topic, level.title()))
            existing = cur.fetchone()
            if existing:
                cur.close(); conn.close()
                return {
                    "status": "success",
                    "already_existed": True,
                    "course_id": existing[0],
                    "course_name": existing[1],
                    "duration_weeks": existing[2],
                    "description": existing[3],
                    "topic": topic,
                    "level": level,
                }

            # Generate the curriculum via AI (same path as plan_curriculum)
            curriculum = self.plan_curriculum(course_name, weeks, level)

            course_id = f"CRS-CUSTOM-{secrets.token_hex(4).upper()}"
            description = (
                f"Personalized {weeks}-week course on {topic}, generated "
                f"specifically for your {level} level gap"
            )
            if role_hint:
                description += f" (for {role_hint})"

            cur.execute("""
                INSERT INTO charvak_courses
                    (course_id, course_name, category, duration_weeks, price_inr,
                     description, level, icon, status,
                     is_custom, generated_for_email, generated_from_topic, generated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                        TRUE, %s, %s, NOW())
            """, (
                course_id, course_name, "Custom", weeks, 0,
                description, level.title(), "", "active",
                email, topic,
            ))
            conn.commit()
            cur.close(); conn.close()

            return {
                "status": "success",
                "already_existed": False,
                "course_id": course_id,
                "course_name": course_name,
                "duration_weeks": weeks,
                "description": description,
                "topic": topic,
                "level": level,
                "curriculum_weeks": len(curriculum.get("weeks", [])) if isinstance(curriculum, dict) else 0,
            }
        except Exception as e:
            logger.error(f"generate_custom_course failed: {e}")
            return {"status": "error", "message": f"Could not generate course: {e}"}

    # ============================================================
    # ENROLLMENT (free)
    # ============================================================

    def enroll_student(self, email: str, course_name: str, duration_weeks: int = 8, user_level: str = "beginner") -> dict:
        """Free enrollment. Generates curriculum via AI. Persists to DB."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Check existing
            cur.execute("""
                SELECT enrollment_id FROM charvak_enrollments
                WHERE email = %s AND course_name = %s AND status = 'active'
            """, (email, course_name))
            existing = cur.fetchone()
            if existing:
                cur.close()
                conn.close()
                return {"status": "exists", "message": "Already enrolled", "enrollment_id": existing[0]}

            enrollment_id = f"ENROLL-{secrets.token_hex(4).upper()}"
            curriculum = self.plan_curriculum(course_name, duration_weeks, user_level)

            cur.execute("""
                INSERT INTO charvak_enrollments
                    (enrollment_id, email, course_name, duration_weeks, user_level,
                     curriculum, total_weeks, status)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, 'active')
            """, (enrollment_id, email, course_name, duration_weeks, user_level,
                  json.dumps(curriculum), duration_weeks))
            conn.commit()
            cur.close()
            conn.close()

            logger.info(f"Enrolled: {email} -> {course_name} ({enrollment_id})")

            return {
                "status": "success",
                "enrollment": {
                    "enrollment_id": enrollment_id,
                    "email": email,
                    "course": course_name,
                    "duration_weeks": duration_weeks,
                    "curriculum": curriculum,
                    "progress": 0,
                    "status": "active"
                }
            }
        except Exception as e:
            logger.error(f"enroll_student failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_user_enrollments(self, email: str) -> dict:
        """Get all enrollments for a user."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT enrollment_id, course_name, duration_weeks, progress, total_weeks,
                       status, started_at, completed_at
                FROM charvak_enrollments WHERE email = %s
                ORDER BY started_at DESC
            """, (email,))
            enrollments = [
                {
                    "enrollment_id": r[0],
                    "course_name": r[1],
                    "duration_weeks": r[2],
                    "progress": r[3],
                    "total_weeks": r[4],
                    "status": r[5],
                    "started_at": r[6].isoformat() if r[6] else None,
                    "completed_at": r[7].isoformat() if r[7] else None
                }
                for r in cur.fetchall()
            ]
            cur.close()
            conn.close()
            return {"status": "success", "enrollments": enrollments, "count": len(enrollments)}
        except Exception as e:
            logger.error(f"get_user_enrollments failed: {e}")
            return {"status": "error", "enrollments": [], "count": 0}

    def get_enrollment(self, enrollment_id: str) -> dict:
        """Get full enrollment state including lessons."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT enrollment_id, email, course_name, duration_weeks, user_level,
                       curriculum, progress, total_weeks, status, started_at, completed_at,
                       recipient_name
                FROM charvak_enrollments WHERE enrollment_id = %s
            """, (enrollment_id,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Enrollment not found"}

            enrollment = {
                "enrollment_id": row[0],
                "email": row[1],
                "course_name": row[2],
                "duration_weeks": row[3],
                "user_level": row[4],
                "curriculum": row[5],
                "progress": row[6],
                "total_weeks": row[7],
                "status": row[8],
                "started_at": row[9].isoformat() if row[9] else None,
                "completed_at": row[10].isoformat() if row[10] else None,
                "recipient_name": row[11]
            }

            # Load lessons
            cur.execute("""
                SELECT week_num, topic, lesson_content, completed
                FROM charvak_course_lessons WHERE enrollment_id = %s ORDER BY week_num
            """, (enrollment_id,))
            lessons = []
            for r in cur.fetchall():
                lessons.append({
                    "week_num": r[0],
                    "topic": r[1],
                    "content": r[2],
                    "completed": r[3]
                })
            enrollment["lessons"] = lessons

            # Determine next week
            completed_weeks = {l["week_num"] for l in lessons if l["completed"]}
            next_week = None
            for w in range(1, enrollment["total_weeks"] + 1):
                if w not in completed_weeks:
                    next_week = w
                    break
            enrollment["next_week"] = next_week

            cur.close()
            conn.close()
            return {"status": "success", "enrollment": enrollment}
        except Exception as e:
            logger.error(f"get_enrollment failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # LESSONS
    # ============================================================

    def get_course_lesson(self, enrollment_id: str, week_num: int) -> dict:
        """Get lesson for a week. Caches AI output in DB."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Check cache
            cur.execute("""
                SELECT lesson_content FROM charvak_course_lessons
                WHERE enrollment_id = %s AND week_num = %s
            """, (enrollment_id, week_num))
            cached = cur.fetchone()
            if cached and cached[0]:
                cur.close()
                conn.close()
                return {"status": "success", "cached": True, "lesson": cached[0]}

            # Get enrollment for context
            cur.execute("""
                SELECT course_name, curriculum FROM charvak_enrollments WHERE enrollment_id = %s
            """, (enrollment_id,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Enrollment not found"}

            course_name, curriculum = row
            weeks = (curriculum or {}).get("weeks", [])
            week_data = next((w for w in weeks if w.get("week") == week_num), {})
            topic = week_data.get("topic", f"Week {week_num}")

            # Generate lesson via AI
            lesson_content = self._generate_lesson(course_name, week_num, topic)

            # Cache it
            lesson_id = f"LES-{secrets.token_hex(4).upper()}"
            cur.execute("""
                INSERT INTO charvak_course_lessons
                    (lesson_id, enrollment_id, week_num, topic, lesson_content, completed)
                VALUES (%s, %s, %s, %s, %s::jsonb, FALSE)
                ON CONFLICT (enrollment_id, week_num) DO UPDATE
                    SET lesson_content = EXCLUDED.lesson_content
            """, (lesson_id, enrollment_id, week_num, topic, json.dumps(lesson_content)))
            conn.commit()
            cur.close()
            conn.close()

            return {"status": "success", "cached": False, "lesson": lesson_content}
        except Exception as e:
            logger.error(f"get_course_lesson failed: {e}")
            return {"status": "error", "message": str(e)}

    def _generate_lesson(self, course_name: str, week_num: int, topic: str) -> dict:
        """Generate lesson content via AI."""
        if self.openai_api_key:
            content = self._call_openai_json(
                f"""Generate a comprehensive lesson for Week {week_num} of the '{course_name}' course.

Topic: {topic}

Return JSON:
{{
  "explanation": "detailed explanation (200-400 words)",
  "examples": ["code example 1", "code example 2"],
  "practice": ["exercise 1", "exercise 2", "exercise 3"],
  "key_takeaways": ["point 1", "point 2", "point 3"]
}}""",
                max_tokens=2500
            )
            if content:
                return content
        return {
            "explanation": f"Week {week_num} covers {topic} for {course_name}.",
            "examples": [f"Example for {topic}"],
            "practice": ["Practice exercise 1", "Practice exercise 2"],
            "key_takeaways": [f"Key concept of {topic}"]
        }

    def complete_week(self, enrollment_id: str, week_num: int) -> dict:
        """Mark a week as completed. Updates progress."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE charvak_course_lessons SET completed = TRUE
                WHERE enrollment_id = %s AND week_num = %s
            """, (enrollment_id, week_num))

            cur.execute("""
                SELECT COUNT(*) FROM charvak_course_lessons
                WHERE enrollment_id = %s AND completed = TRUE
            """, (enrollment_id,))
            completed_count = cur.fetchone()[0]

            cur.execute("""
                UPDATE charvak_enrollments SET progress = %s
                WHERE enrollment_id = %s RETURNING total_weeks
            """, (completed_count, enrollment_id))
            row = cur.fetchone()
            total_weeks = row[0] if row else 0

            conn.commit()
            cur.close()
            conn.close()

            # Session 18: auto-issue certificate when the final week completes
            # This was previously a silent no-op — the enrollment was marked
            # 'completed' but no row was inserted into charvak_certificates.
            course_completed = completed_count >= total_weeks
            certificate_id = None
            # Session 36: gate certificate issuance behind the full-course unlock
            # for custom AI courses. Catalog courses are unaffected.
            if course_completed:
                _is_custom = False
                _paid_unlock = True
                try:
                    cur.execute("""
                        SELECT c.is_custom, e.paid_unlock
                        FROM charvak_courses c
                        JOIN charvak_enrollments e ON e.course_name = c.course_name
                        WHERE e.enrollment_id = %s
                    """, (enrollment_id,))
                    _cm = cur.fetchone()
                    if _cm:
                        _is_custom = bool(_cm[0])
                        _paid_unlock = bool(_cm[1])
                except Exception as _ce:
                    logger.warning(f"cert gate lookup failed: {_ce}")

                if _is_custom and not _paid_unlock:
                    # Custom course without the paid unlock: no cert yet.
                    # Week count updates normally; only issuance is gated.
                    return {
                        "status": "success",
                        "progress": completed_count,
                        "total_weeks": total_weeks,
                        "course_completed": True,
                        "certificate_id": None,
                        "certificate_locked": True,
                        "unlock_type": "full_course",
                        "unlock_amount_credits": 150,
                        "message": "Week complete! Unlock the full course to earn your certificate.",
                    }
                cert_result = self.complete_course(enrollment_id)
                if isinstance(cert_result, dict) and cert_result.get("status") == "success":
                    certificate_id = (cert_result.get("certificate") or {}).get("certificate_id")

            return {
                "status": "success",
                "progress": completed_count,
                "total_weeks": total_weeks,
                "course_completed": course_completed,
                "certificate_id": certificate_id
            }
        except Exception as e:
            logger.error(f"complete_week failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # CERTIFICATES
    # ============================================================

    def set_recipient_name(self, enrollment_id: str, name: str) -> dict:
        """Save a custom recipient name for the certificate."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_enrollments SET recipient_name = %s
                WHERE enrollment_id = %s
            """, (name.strip()[:100], enrollment_id))
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "recipient_name": name.strip()[:100]}
        except Exception as e:
            logger.error(f"set_recipient_name failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def complete_course(self, enrollment_id: str) -> dict:
        """Issue a certificate on completion. Uses recipient_name if set, else user's real name from users table."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Session 36: certificate is a paid artifact. Custom AI courses
            # require the 150-credit full-course unlock before certificate
            # issuance. Catalog courses with paid installments are unaffected.
            cur.execute("""
                SELECT c.is_custom, e.paid_unlock
                FROM charvak_courses c
                JOIN charvak_enrollments e ON e.course_name = c.course_name
                WHERE e.enrollment_id = %s
            """, (enrollment_id,))
            _cm = cur.fetchone()
            _is_custom = bool(_cm[0]) if _cm else False
            _paid_unlock = bool(_cm[1]) if _cm else True
            if _is_custom and not _paid_unlock:
                cur.close(); conn.close()
                return {
                    "status": "locked",
                    "message": "Unlock the full course to earn your certificate.",
                    "unlock_type": "full_course",
                    "unlock_amount_credits": 150,
                }

            cur.execute("""
                SELECT email, course_name, duration_weeks, recipient_name
                FROM charvak_enrollments WHERE enrollment_id = %s
            """, (enrollment_id,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Enrollment not found"}

            email, course_name, duration_weeks, recipient_name = row

            # If enrollment has no name, look up the user's real name
            if not recipient_name:
                cur.execute("SELECT name FROM users WHERE email = %s", (email,))
                user_row = cur.fetchone()
                if user_row and user_row[0]:
                    recipient_name = user_row[0]
                else:
                    recipient_name = email.split('@')[0]

            cert_id = f"CERT-{secrets.token_hex(6).upper()}"

            cur.execute("""
                INSERT INTO charvak_certificates
                    (certificate_id, enrollment_id, email, course_name, duration_weeks, recipient_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cert_id, enrollment_id, email, course_name, duration_weeks, recipient_name))

            cur.execute("""
                UPDATE charvak_enrollments
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE enrollment_id = %s
            """, (enrollment_id,))

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "certificate": {
                    "certificate_id": cert_id,
                    "enrollment_id": enrollment_id,
                    "email": email,
                    "course_name": course_name,
                    "duration_weeks": duration_weeks,
                    "recipient_name": recipient_name,
                    "issued_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"complete_course failed: {e}")
            return {"status": "error", "message": str(e)}

    def check_unlock_status(self, enrollment_id: str, email: str) -> dict:
        """
        Session 36: idempotency check for the full-course unlock.
        Returns {status, already_unlocked, enrollment_id, owns_it}.
        """
        email = (email or "").strip().lower()
        if not email or not enrollment_id:
            return {"status": "error", "message": "email and enrollment_id required"}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT email, paid_unlock FROM charvak_enrollments
                WHERE enrollment_id = %s
            """, (enrollment_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return {"status": "error", "message": "Enrollment not found"}
            owner_email, paid_unlock = row[0], bool(row[1])
            return {
                "status": "success",
                "enrollment_id": enrollment_id,
                "owns_it": (owner_email or "").lower() == email,
                "already_unlocked": paid_unlock,
            }
        except Exception as e:
            logger.error(f"check_unlock_status failed: {e}")
            return {"status": "error", "message": str(e)}

    def unlock_full_course(self, enrollment_id: str, email: str) -> dict:
        """
        Session 36: flip paid_unlock to TRUE for a custom-course enrollment.

        Called AFTER the credit deduction. Idempotent: if paid_unlock is
        already TRUE, no-op and return success with already_unlocked=True.

        Returns {status, enrollment_id, paid_unlock, already_unlocked}.
        """
        email = (email or "").strip().lower()
        if not email or not enrollment_id:
            return {"status": "error", "message": "email and enrollment_id required"}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT email, paid_unlock FROM charvak_enrollments
                WHERE enrollment_id = %s
            """, (enrollment_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Enrollment not found"}

            owner_email, paid_unlock = row[0], bool(row[1])
            if (owner_email or "").lower() != email:
                cur.close(); conn.close()
                return {"status": "error", "message": "Not your enrollment"}

            if paid_unlock:
                cur.close(); conn.close()
                return {
                    "status": "success",
                    "enrollment_id": enrollment_id,
                    "paid_unlock": True,
                    "already_unlocked": True,
                }

            cur.execute("""
                UPDATE charvak_enrollments
                SET paid_unlock = TRUE
                WHERE enrollment_id = %s
            """, (enrollment_id,))
            conn.commit()
            cur.close(); conn.close()

            return {
                "status": "success",
                "enrollment_id": enrollment_id,
                "paid_unlock": True,
                "already_unlocked": False,
            }
        except Exception as e:
            logger.error(f"unlock_full_course failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_certificate(self, certificate_id: str) -> dict:
        """Fetch a certificate for display."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT certificate_id, enrollment_id, email, course_name, duration_weeks, issued_at, recipient_name
                FROM charvak_certificates WHERE certificate_id = %s
            """, (certificate_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return {"status": "error", "message": "Certificate not found"}
            return {
                "status": "success",
                "certificate": {
                    "certificate_id": row[0],
                    "enrollment_id": row[1],
                    "email": row[2],
                    "course_name": row[3],
                    "duration_weeks": row[4],
                    "issued_at": row[5].isoformat() if row[5] else None,
                    "recipient_name": row[6] or row[2].split('@')[0]
                }
            }
        except Exception as e:
            logger.error(f"get_certificate failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # AI TUTOR (charges credits)
    # ============================================================

    def assist_project(self, enrollment_id: str, project_question: str) -> dict:
        """AI helps with a project question. Charges credits."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT email, course_name FROM charvak_enrollments WHERE enrollment_id = %s", (enrollment_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return {"status": "error", "message": "Enrollment not found"}
            email, course_name = row

            # Charge credits
            try:
                from ai_credit_engine import ai_credit_engine
                credit_result = ai_credit_engine.check_and_deduct(email, "chatbot_query")
                if credit_result.get("status") != "success":
                    return {
                        "status": "error",
                        "message": credit_result.get("message", "Insufficient credits"),
                        "top_up_url": "/pricing"
                    }
            except Exception as e:
                logger.error(f"Credit deduction failed: {e}")

            # Get AI answer
            if self.openai_api_key:
                answer = self._call_openai_text(
                    f"Student enrolled in '{course_name}' asks: {project_question}\n\nProvide step-by-step guidance with code examples and best practices. Max 400 words."
                )
                if answer:
                    return {"status": "success", "assistance": answer, "credits_charged": 2}

            return {"status": "success", "assistance": "Please review the lesson material and try again.", "credits_charged": 0}
        except Exception as e:
            logger.error(f"assist_project failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # PAID ENROLLMENT + EMI (Tier 3 - 2026-09-16)
    # Delegates to ai_courses_payments. Existing methods above are
    # unchanged. Free enroll_student() still exists for price-0 courses.
    # ============================================================

    def enroll_student_paid(self, email: str, course_name: str,
                            duration_weeks: int = None,
                            country_code: str = "IN", level: str = "intermediate") -> dict:
        """Paid enrollment: creates the enrollment + (for EMI countries)
        the installment schedule via ai_courses_payments. Returns the plan
        the frontend should charge against."""
        try:
            from ai_courses_payments import ai_course_payments
            plan = ai_course_payments.create_enrollment_paid(
                email=email,
                course_name=course_name,
                duration_weeks=duration_weeks,
                country_code=country_code,
                level=level,
            )
            if plan.get("status") == "exists":
                return plan
            if plan.get("status") != "success":
                return plan
            # Generate + persist curriculum so lessons can start immediately
            # once the first payment confirms.
            try:
                curriculum = self.plan_curriculum(course_name, duration_weeks, level)
                from database import db
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE charvak_enrollments SET curriculum = %s::jsonb, user_level = %s WHERE enrollment_id = %s",
                    (json.dumps(curriculum), level, plan["enrollment_id"]),
                )
                conn.commit()
                cur.close()
                conn.close()
                plan["curriculum_ready"] = True
            except Exception as ce:
                logger.warning(f"curriculum pre-gen failed (non-fatal): {ce}")
                plan["curriculum_ready"] = False
            return plan
        except Exception as e:
            logger.error(f"enroll_student_paid failed: {e}")
            return {"status": "error", "message": str(e)}

    def check_course_access(self, enrollment_id: str, week_num: int) -> dict:
        """Returns {allowed: True} OR the full unlock offer with installment
        details, amount, due date, and resume week."""
        try:
            from ai_courses_payments import ai_course_payments
            return ai_course_payments.check_access(enrollment_id, week_num)
        except Exception as e:
            logger.error(f"check_course_access failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_course_installments(self, enrollment_id: str) -> dict:
        """Return the installment schedule for an enrollment."""
        try:
            from ai_courses_payments import ai_course_payments
            return ai_course_payments.get_installments(enrollment_id)
        except Exception as e:
            logger.error(f"get_course_installments failed: {e}")
            return {"status": "error", "installments": [], "count": 0}

    def record_course_payment(self, enrollment_id: str, email: str,
                              course_name: str, country_code: str,
                              currency: str, amount_local,
                              amount_inr: int, payment_type: str,
                              gateway: str, installment_num=None,
                              razorpay_payment_id=None,
                              razorpay_order_id=None,
                              paypal_order_id=None) -> dict:
        """Record a captured payment. Idempotent on razorpay_payment_id."""
        try:
            from ai_courses_payments import ai_course_payments
            return ai_course_payments.record_payment(
                enrollment_id=enrollment_id,
                email=email,
                course_name=course_name,
                country_code=country_code,
                currency=currency,
                amount_local=amount_local,
                amount_inr=amount_inr,
                payment_type=payment_type,
                gateway=gateway,
                installment_num=installment_num,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_order_id=razorpay_order_id,
                paypal_order_id=paypal_order_id,
            )
        except Exception as e:
            logger.error(f"record_course_payment failed: {e}")
            return {"status": "error", "message": str(e)}

ai_courses = AICourseSystem()