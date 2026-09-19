"""
Charvak Advanced Assessment & Training System
Completely AI-Driven: Versant, MCQ, Company Patterns, Skill-Gap Analysis
Integrates with: AI Bridge, Training Engine, LMS, Question Generator
(DB-backed - Session H/8)
"""
import json
import logging
import os
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.advanced_assessment")


class AdvancedAssessmentEngine:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.assessments = self._initialize_assessments()
        self.training_modules = self._initialize_training()
        self._ensure_tables()
        logger.info("Advanced Assessment Engine ready (DB-backed) | AI: %s",
                    "ENABLED" if self.openai_api_key else "DISABLED")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_advanced_ai_sessions (
                    session_id   TEXT PRIMARY KEY,
                    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
                    started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_adv_sessions_started ON charvak_advanced_ai_sessions(started_at)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_advanced_mock_drives (
                    drive_id     TEXT PRIMARY KEY,
                    email        TEXT,
                    company      TEXT,
                    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
                    started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_adv_drives_email   ON charvak_advanced_mock_drives(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_adv_drives_company ON charvak_advanced_mock_drives(company)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_advanced_skill_gaps (
                    email        TEXT PRIMARY KEY,
                    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
                    analyzed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_adv_skill_gaps_analyzed ON charvak_advanced_skill_gaps(analyzed_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"advanced_assessment tables init failed: {e}")

    # ============================================================
    # STATIC CATALOGS
    # ============================================================

    def _initialize_assessments(self):
        """Initialize all assessment types (static)."""
        return {
            "versant": {
                "name": "Versant English Assessment",
                "duration": "50 minutes",
                "ai_scored": True,
                "sections": [
                    {"id": "read_aloud", "name": "Read Aloud", "questions": 8, "time": "15 sec each", "skill": "pronunciation"},
                    {"id": "repeats", "name": "Repeats", "questions": 16, "time": "10 sec each", "skill": "listening"},
                    {"id": "sentence_builds", "name": "Sentence Builds", "questions": 10, "time": "15 sec each", "skill": "grammar"},
                    {"id": "conversations", "name": "Conversations", "questions": 10, "time": "20 sec each", "skill": "comprehension"},
                    {"id": "story_retelling", "name": "Story Retelling", "questions": 3, "time": "30 sec each", "skill": "retention"},
                    {"id": "summary_opinion", "name": "Summary & Opinion", "questions": 1, "time": "18 min", "skill": "writing"},
                ],
                "scoring_metrics": ["sentence_mastery", "vocabulary", "fluency", "pronunciation"],
                "cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
            },
            "mcq": {
                "name": "MCQ Assessment",
                "ai_generated": True,
                "categories": {
                    "aptitude": {
                        "name": "Aptitude & Logical",
                        "topics": ["Quant", "Probability", "Data Interpretation", "Logical Reasoning", "Syllogisms", "Coding-Decoding", "Pattern Recognition"],
                    },
                    "technical_cs": {
                        "name": "Technical CS Fundamentals",
                        "topics": ["Data Structures", "Algorithms", "OOPs", "Operating Systems", "DBMS/SQL", "Computer Networks"],
                    },
                    "pseudocode": {
                        "name": "Pseudocode & Code Output",
                        "topics": ["C", "C++", "Java", "Python"],
                    },
                    "domain": {
                        "name": "Domain-Specific",
                        "topics": ["Cloud", "Web Development", "Cybersecurity", "Agile"],
                    },
                },
            },
            "company_patterns": {
                "tcs_nqt": {
                    "name": "TCS NQT",
                    "platform": "iON",
                    "sections": [
                        {"name": "Foundation", "components": ["Aptitude", "Logical", "Verbal"], "time": "75 min"},
                        {"name": "Advanced", "components": ["Advanced Quant", "Advanced Logic"], "time": "25 min"},
                        {"name": "Coding", "components": ["2 DSA Problems"], "time": "55 min"},
                    ],
                },
                "cognizant": {
                    "name": "Cognizant GenC",
                    "platform": "Mettl/Superset",
                    "sections": [
                        {"name": "Aptitude", "components": ["Quantitative", "Analytical", "Verbal"], "time": "60 min"},
                        {"name": "Communication", "components": ["Speaking"], "time": "20 min"},
                        {"name": "Programming", "components": ["SQL", "Debugging"], "time": "45 min"},
                    ],
                },
                "wipro": {
                    "name": "Wipro Elite NTH",
                    "platform": "AMCAT/SHL",
                    "sections": [
                        {"name": "Aptitude", "components": ["Logical", "Quant"], "time": "48 min"},
                        {"name": "Communication", "components": ["Essay", "Email"], "time": "20 min"},
                        {"name": "Coding", "components": ["2 Questions"], "time": "45 min"},
                    ],
                },
                "hcl": {
                    "name": "HCLTech",
                    "platform": "Custom",
                    "sections": [
                        {"name": "Aptitude", "components": ["Core Aptitude", "English"], "time": "60 min"},
                        {"name": "Technical", "components": ["CS Fundamentals"], "time": "30 min"},
                        {"name": "Coding", "components": ["Basic Coding"], "time": "30 min"},
                    ],
                },
            },
        }

    def _initialize_training(self):
        """Initialize AI-driven 4-Phase Training (static)."""
        return {
            "phases": [
                {"phase": 1, "name": "AI Diagnostic Assessment", "duration": "Week 1", "ai_driven": True,
                 "activities": ["AI-powered skill evaluation", "Automated gap analysis", "Personalized learning path generation"],
                 "categorization": {"Group A": "Advanced (75%+)", "Group B": "Intermediate (50-74%)", "Group C": "Foundational (<50%)"}},
                {"phase": 2, "name": "AI-Guided Bootcamp", "duration": "Weeks 2-6", "ai_driven": True,
                 "daily_schedule": [
                     {"activity": "AI Quant Practice", "time": "1.5 hrs"},
                     {"activity": "AI Speaking Coach", "time": "1 hr"},
                     {"activity": "AI Coding Mentor", "time": "2 hrs"},
                 ]},
                {"phase": 3, "name": "AI Skill Building", "duration": "Weeks 7-10", "ai_driven": True,
                 "activities": ["AI-generated coding patterns", "Daily adaptive MCQ drills", "AI mock interviews"]},
                {"phase": 4, "name": "AI Placement Simulation", "duration": "Weeks 11-12", "ai_driven": True,
                 "activities": ["Company-specific AI mock drives", "Automated scorecards", "AI feedback loop"]},
            ]
        }

    # ============================================================
    # STATIC READS
    # ============================================================

    def get_assessment_types(self):
        """Get all AI-driven assessment types."""
        return {
            "status": "success",
            "ai_driven": True,
            "assessments": [
                {"id": "versant", "name": "AI Versant Assessment", "duration": "50 min", "ai_scored": True},
                {"id": "mcq", "name": "AI MCQ Assessment", "categories": 4, "ai_generated": True},
                {"id": "company_patterns", "name": "Company Patterns", "companies": 4, "ai_simulated": True},
            ],
        }

    def get_versant_details(self):
        """Get Versant assessment details."""
        return {"status": "success", "assessment": self.assessments["versant"]}

    def get_training_phases(self):
        """Get AI-driven training phases."""
        return {"status": "success", "ai_driven": True, "phases": self.training_modules["phases"]}

    def get_company_patterns(self):
        """Get all company patterns."""
        companies = []
        for key, company in self.assessments["company_patterns"].items():
            companies.append({
                "id": key,
                "name": company["name"],
                "platform": company["platform"],
                "sections": company["sections"],
            })
        return {"status": "success", "companies": companies}

    # ============================================================
    # VERSANT SESSIONS
    # ============================================================

    def start_versant_assessment(self, email):
        """Start AI-driven Versant assessment."""
        session_id = f"VERSANT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        session = {
            "session_id": session_id,
            "email": email,
            "type": "versant",
            "sections": self.assessments["versant"]["sections"],
            "current_section": 0,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_advanced_ai_sessions (session_id, data)
                VALUES (%s, %s::jsonb)
            ''', (session_id, json.dumps(session)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"start_versant_assessment failed: {e}")
            return {"status": "error", "message": "Could not start assessment"}

        return {
            "status": "success",
            "session_id": session_id,
            "sections": self.assessments["versant"]["sections"],
            "message": "AI Versant assessment started",
        }

    def _get_ai_session(self, session_id: str):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT data FROM charvak_advanced_ai_sessions WHERE session_id = %s', (session_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return None
            return row[0] if isinstance(row[0], dict) else json.loads(row[0] or "{}")
        except Exception as e:
            logger.error(f"_get_ai_session failed: {e}")
            return None

    def get_versant_section(self, session_id, section_index):
        """Get AI-generated Versant questions for section."""
        session = self._get_ai_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}

        sections = session["sections"]
        if section_index >= len(sections):
            return {"status": "error", "message": "Invalid section"}

        section = sections[section_index]
        questions = self._generate_versant_questions(section)

        return {"status": "success", "section": section, "questions": questions}

    def _generate_versant_questions(self, section):
        """Generate Versant questions (pure static prompts)."""
        prompts = {
            "read_aloud": [
                "The company will announce quarterly results next week.",
                "Please submit your assignment by Friday afternoon.",
                "The new software update includes several improvements.",
                "Our team meeting has been rescheduled to Monday.",
            ],
            "repeats": [
                "The quick brown fox jumps over the lazy dog.",
                "Could you please repeat the last sentence?",
                "I would like to schedule an appointment for tomorrow.",
                "The conference will be held at the convention center.",
            ],
            "sentence_builds": [
                "the / meeting / at / starts / nine / o'clock / sharp",
                "please / the / report / by / submit / Friday / evening",
                "the / team / successfully / completed / the / project",
                "we / will / discuss / the / budget / next / week",
            ],
            "conversations": [
                "Would you find a stove in a kitchen or a bedroom?",
                "What would you do if you missed an important deadline?",
                "How would you explain a complex idea to a colleague?",
                "What's the best way to handle a difficult customer?",
            ],
            "story_retelling": [
                "A young engineer joined a startup and learned to build scalable systems within six months.",
                "The marketing team launched a campaign that doubled their customer base in three months.",
                "A student practiced coding daily and got placed at a top tech company.",
            ],
            "summary_opinion": [
                "Write a summary of the impact of artificial intelligence on modern workplaces.",
            ],
        }

        section_prompts = list(prompts.get(section["id"], ["Sample question"]))
        declared_count = section["questions"]

        # If AI available and we need more prompts than the static list, generate extras
        if self.openai_api_key and len(section_prompts) < declared_count:
            needed = declared_count - len(section_prompts)
            try:
                extra = self._generate_versant_prompts_with_openai(section["id"], needed)
                section_prompts.extend(extra)
            except Exception as e:
                logger.error(f"Versant AI generation failed: {e}")

        # Cap at declared count
        section_prompts = section_prompts[:declared_count]

        questions = []
        for i, prompt in enumerate(section_prompts):
            questions.append({
                "id": i + 1,
                "question": prompt,
                "type": section["id"],
                "skill": section.get("skill", "general"),
                "time_limit": section["time"],
            })

        return questions

    def _generate_versant_prompts_with_openai(self, section_id, count):
        """Generate additional Versant prompts via OpenAI (JSON mode)."""
        try:
            import requests

            section_hints = {
                "read_aloud": "short English sentences suitable for reading aloud practice (business/professional context)",
                "repeats": "short English sentences suitable for listen-and-repeat practice",
                "sentence_builds": "jumbled word sequences separated by ' / ' that form a complete English sentence when reordered",
                "conversations": "open-ended conversational questions with realistic scenarios",
                "story_retelling": "short 1-2 sentence narratives suitable for retelling practice",
                "summary_opinion": "essay-style prompts requesting a summary and opinion",
            }
            hint = section_hints.get(section_id, "practice prompts")

            prompt = (
                f"Generate {count} unique prompts of type '{section_id}' for a Versant English test.\n"
                f"Description: {hint}\n"
                f"Return a JSON object: {{\"prompts\": [\"prompt 1\", \"prompt 2\", ...]}}"
            )

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.9,
                    "response_format": {"type": "json_object"},
                },
                timeout=25,
            )

            data = response.json()
            content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()

            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "prompts" in parsed:
                    return list(parsed["prompts"])[:count]
            except Exception:
                pass
            return []
        except Exception as e:
            logger.error(f"Versant prompt AI error: {e}")
            return []

    # ============================================================
    # MCQ GENERATION
    # ============================================================

    def generate_mcq_questions(self, category, topic, count=10, email=None):
        """Generate AI-driven MCQ questions."""
        if self.openai_api_key:
            try:
                questions = self._generate_mcq_with_openai(category, topic, count)
                if questions:
                    return {"status": "success", "questions": questions, "ai_generated": True}
            except Exception as e:
                logger.error(f"OpenAI MCQ generation failed: {e}")

        from ai_question_generator import ai_question_generator
        questions = ai_question_generator.generate_questions(
            exam_id=f"mcq_{category}",
            topic=topic,
            count=count,
            user_email=email,
        )

        return {"status": "success", "questions": questions, "ai_generated": False}

    def _generate_mcq_with_openai(self, category, topic, count):
        """Generate MCQs using OpenAI (JSON mode)."""
        try:
            import requests

            prompt = (
                f"Generate {count} multiple-choice questions for {topic} (category: {category}). "
                'Return a JSON object: {"questions":[{"question":"...","options":["A","B","C","D"],'
                '"correct_index":0,"explanation":"..."}]}'
            )

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "response_format": {"type": "json_object"},
                },
                timeout=20,
            )

            data = response.json()
            content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()

            # Defensive: strip markdown fences
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            # Try direct JSON (response_format=json_object returns pure JSON)
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "questions" in parsed:
                    return parsed["questions"]
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass

            # Fallback: regex-extract array from prose/fence-wrapped output
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return []
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return []

    # ============================================================
    # MOCK DRIVES
    # ============================================================

    def start_mock_drive(self, company_id, email):
        """Start AI-simulated company mock drive."""
        if company_id not in self.assessments["company_patterns"]:
            return {"status": "error", "message": "Company not found"}

        drive_id = f"DRIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        company = self.assessments["company_patterns"][company_id]

        drive = {
            "drive_id": drive_id,
            "company": company["name"],
            "email": email,
            "sections": company["sections"],
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
            "ai_simulated": True,
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_advanced_mock_drives (drive_id, email, company, data)
                VALUES (%s, %s, %s, %s::jsonb)
            ''', (drive_id, email, company["name"], json.dumps(drive)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"start_mock_drive failed: {e}")
            return {"status": "error", "message": "Could not start mock drive"}

        return {
            "status": "success",
            "drive_id": drive_id,
            "company": company["name"],
            "platform": company["platform"],
            "sections": company["sections"],
        }

    # ============================================================
    # SKILL GAP ANALYSIS
    # ============================================================

    def analyze_skill_gap(self, email, scores):
        """AI-driven skill gap analysis (overwrites on repeat)."""
        total_score = sum(scores.values()) / len(scores) if scores else 0

        if total_score >= 75:
            category = "Group A (Advanced)"
        elif total_score >= 50:
            category = "Group B (Intermediate)"
        else:
            category = "Group C (Foundational)"

        weak_areas = [k for k, v in scores.items() if v < 50]
        strong_areas = [k for k, v in scores.items() if v >= 75]

        recommendations = []
        for weak in weak_areas:
            recommendations.append(f"Focus on improving {weak} with daily practice")
        for strong in strong_areas:
            recommendations.append(f"Maintain your strength in {strong}")

        analysis = {
            "scores": scores,
            "total_score": total_score,
            "category": category,
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
            "ai_recommendations": recommendations,
            "analyzed_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_advanced_skill_gaps (email, data)
                VALUES (%s, %s::jsonb)
                ON CONFLICT (email) DO UPDATE SET
                    data = EXCLUDED.data,
                    updated_at = CURRENT_TIMESTAMP
            ''', (email, json.dumps(analysis)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"analyze_skill_gap failed: {e}")
            return {"status": "error", "message": "Could not analyze skill gap"}

        return {
            "status": "success",
            "total_score": round(total_score, 1),
            "category": category,
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
            "ai_recommendations": recommendations,
        }

    def get_scorecard(self, email):
        """Get detailed AI scorecard."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT data FROM charvak_advanced_skill_gaps WHERE email = %s', (email,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_scorecard failed: {e}")
            return {"status": "error", "message": "No assessment found"}

        if not row:
            return {"status": "error", "message": "No assessment found"}

        scorecard = row[0] if isinstance(row[0], dict) else json.loads(row[0] or "{}")
        return {"status": "success", "scorecard": scorecard}


advanced_assessment_engine = AdvancedAssessmentEngine()
