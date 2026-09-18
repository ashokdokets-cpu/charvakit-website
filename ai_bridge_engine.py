"""
Charvak AI Bridge Engine
AI-powered personalized assessment with monetization
Uses GPT-4o-mini for question generation and answer evaluation
(DB-backed - Session H/6)
"""
import json
import logging
import os
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.aibridge")

try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class AIBridgeEngine:
    """AI-powered career assessment with personalized feedback (DB-backed)."""

    ROLES = ["Software Developer", "Data Scientist", "UI/UX Designer", "Marketing Specialist", "Business Analyst", "DevOps Engineer"]
    INDUSTRIES = ["IT/Tech", "Finance", "Healthcare", "E-commerce", "Manufacturing", "Education"]
    LEVELS = ["Fresher", "Mid-Level", "Senior"]

    def __init__(self):
        self._ensure_tables()
        logger.info("AI Bridge Engine ready (DB-backed) | OpenAI: %s",
                    "Available" if OPENAI_AVAILABLE and OPENAI_API_KEY else "Not Configured")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ai_bridge_sessions (
                    session_id   TEXT PRIMARY KEY,
                    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
                    started_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_aib_sessions_started ON charvak_ai_bridge_sessions(started_at)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_ai_bridge_premium_reports (
                    premium_id    TEXT PRIMARY KEY,
                    session_id    TEXT NOT NULL,
                    data          JSONB NOT NULL DEFAULT '{}'::jsonb,
                    price         INTEGER DEFAULT 99,
                    purchased_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_aib_premium_session ON charvak_ai_bridge_premium_reports(session_id)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"ai_bridge tables init failed: {e}")

    # ============================================================
    # SESSION STORAGE
    # ============================================================

    def _find_session(self, session_id: str):
        if not session_id:
            return None
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT data FROM charvak_ai_bridge_sessions WHERE session_id = %s', (session_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return None
            return row[0] if isinstance(row[0], dict) else json.loads(row[0] or "{}")
        except Exception as e:
            logger.error(f"_find_session failed: {e}")
            return None

    def _save_session(self, session: Dict) -> bool:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_ai_bridge_sessions
                SET data = %s::jsonb, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            ''', (json.dumps(session), session["session_id"]))
            conn.commit()
            cur.close(); conn.close()
            return True
        except Exception as e:
            logger.error(f"_save_session failed: {e}")
            return False

    # ============================================================
    # AI HELPER (JSON mode)
    # ============================================================

    def _ai_json(self, prompt: str, max_tokens: int, temperature: float) -> Optional[Dict]:
        """Call OpenAI in JSON mode and return parsed dict, or None on failure."""
        if not (OPENAI_AVAILABLE and OPENAI_API_KEY):
            return None
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            content = (response.choices[0].message.content or "").strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return None

    # ============================================================
    # START ASSESSMENT
    # ============================================================

    def start_ai_assessment(self, data: Dict) -> Dict:
        """
        Start AI-powered assessment.
        data = {role, industry, experience_level, name, email}
        """
        session_id = f"AIB-{secrets.token_hex(4).upper()}"

        role = data.get("role", "Software Developer")
        industry = data.get("industry", "IT/Tech")
        level = data.get("experience_level", "Fresher")

        questions = self._generate_ai_questions(role, industry, level)

        session = {
            "session_id": session_id,
            "role": role,
            "industry": industry,
            "level": level,
            "name": data.get("name", "Candidate"),
            "email": data.get("email", ""),
            "questions": questions,
            "answers": [],
            "current_question": 0,
            "started_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_ai_bridge_sessions (session_id, data)
                VALUES (%s, %s::jsonb)
            ''', (session_id, json.dumps(session)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"start_ai_assessment failed: {e}")
            return {"status": "error", "message": "Could not start assessment"}

        return {
            "status": "success",
            "session_id": session_id,
            "questions_count": len(questions),
            "first_question": questions[0] if questions else None,
            "message": f"AI assessment started for {role} ({level}) in {industry}",
        }

    def _generate_ai_questions(self, role: str, industry: str, level: str) -> List[Dict]:
        """Generate role-specific questions using AI or fallback."""
        fallback = [
            {"id": "q1", "prompt": f"Describe a real-world {role} challenge you've faced and how you solved it.", "type": "open_ended"},
            {"id": "q2", "prompt": f"What tools and technologies do you use daily as a {role}?", "type": "open_ended"},
            {"id": "q3", "prompt": f"How do you handle feedback and criticism in your {role} work?", "type": "open_ended"},
            {"id": "q4", "prompt": f"Describe a time you had to learn something new quickly for your {role} role.", "type": "open_ended"},
            {"id": "q5", "prompt": f"What's your approach to collaborating with team members in {industry}?", "type": "open_ended"},
        ]

        prompt = (
            f"Generate 5 open-ended scenario questions for a {level} {role} in {industry}.\n"
            'Return a JSON object: {"questions":[{"id":"q1","prompt":"question text","type":"open_ended"}]}\n'
            "Questions should assess real skills, not trivia."
        )
        parsed = self._ai_json(prompt, max_tokens=500, temperature=0.7)
        if parsed and isinstance(parsed.get("questions"), list) and parsed["questions"]:
            return parsed["questions"]

        return fallback

    # ============================================================
    # ANSWER + REPORT
    # ============================================================

    def submit_ai_answer(self, data: Dict) -> Dict:
        """
        Submit an open-ended answer.
        data = {session_id, question_id, answer_text}
        """
        session_id = data.get("session_id")
        session = self._find_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}

        answer = {
            "question_id": data.get("question_id"),
            "answer_text": data.get("answer_text", ""),
            "submitted_at": datetime.now().isoformat(),
        }
        session["answers"].append(answer)

        if len(session["answers"]) >= len(session["questions"]):
            return self._generate_report(session)

        next_index = len(session["answers"])
        self._save_session(session)
        return {
            "status": "success",
            "complete": False,
            "answered": len(session["answers"]),
            "total": len(session["questions"]),
            "next_question": session["questions"][next_index],
        }

    def _generate_report(self, session: Dict) -> Dict:
        """Generate AI-powered personalized report."""
        answers_text = "\n".join(
            [f"Q: {a['question_id']}\nA: {a['answer_text']}" for a in session["answers"]]
        )

        prompt = (
            f"Evaluate these assessment answers for a {session['level']} {session['role']} in {session['industry']}.\n\n"
            f"{answers_text}\n\n"
            'Return a JSON object: {"score": 0-100, "strengths": [3 items], "weaknesses": [3 items], '
            '"learning_path": [3 recommendations], "job_recommendations": [3 roles]}'
        )

        report = self._ai_json(prompt, max_tokens=600, temperature=0.5)
        if report and isinstance(report, dict) and "score" in report:
            report["session_id"] = session["session_id"]
            report["generated_at"] = datetime.now().isoformat()
            report["ai_generated"] = True
            session["report"] = report
            self._save_session(session)
            return {
                "status": "success",
                "complete": True,
                "report": report,
                "premium_available": True,
                "premium_price": 99,
                "message": "AI assessment complete! Upgrade for full report.",
            }

        # Fallback report
        report = {
            "session_id": session["session_id"],
            "score": 72,
            "strengths": ["Good communication", "Practical approach", "Willingness to learn"],
            "weaknesses": ["Need more hands-on experience", "Could improve technical depth"],
            "learning_path": ["Complete 2 micro-internships", "Take advanced courses", "Build portfolio projects"],
            "job_recommendations": [session["role"], f"Junior {session['role']}"],
            "generated_at": datetime.now().isoformat(),
            "ai_generated": False,
        }

        session["report"] = report
        self._save_session(session)

        return {
            "status": "success",
            "complete": True,
            "report": report,
            "premium_available": True,
            "premium_price": 99,
            "message": "Assessment complete! Upgrade for full report.",
        }

    # ============================================================
    # PREMIUM REPORT (monetized)
    # ============================================================

    def get_premium_report(self, session_id: str) -> Dict:
        """Get premium report (monetized)."""
        session = self._find_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}

        # K#33 fix: idempotency - return existing report if already purchased
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT premium_id, data, purchased_at FROM charvak_ai_bridge_premium_reports WHERE session_id = %s LIMIT 1",
                (session_id,)
            )
            existing = cur.fetchone()
            cur.close(); conn.close()
            if existing:
                existing_data = existing[1] if isinstance(existing[1], dict) else json.loads(existing[1] or "{}")
                existing_data["already_purchased"] = True
                return {"status": "success", "premium_report": existing_data}
        except Exception as e:
            logger.error(f"get_premium_report idempotency check failed: {e}")

        premium_id = f"PREM-{secrets.token_hex(4).upper()}"

        premium_report = {
            "premium_id": premium_id,
            "session_id": session_id,
            "report": session.get("report", {}),
            "detailed_feedback": self._generate_detailed_feedback(session),
            "learning_path": session.get("report", {}).get("learning_path", []),
            "badge_issued": True,
            "price": 99,
            "purchased_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_ai_bridge_premium_reports (premium_id, session_id, data, price)
                VALUES (%s, %s, %s::jsonb, 99)
            ''', (premium_id, session_id, json.dumps(premium_report)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_premium_report failed: {e}")
            return {"status": "error", "message": "Could not create premium report"}

        return {
            "status": "success",
            "premium_report": premium_report,
            "message": "Premium report unlocked!",
            "revenue_earned": 99,
        }

    def _generate_detailed_feedback(self, session: Dict) -> str:
        """Generate detailed feedback."""
        return (
            f"Based on your answers, you demonstrate solid potential as a "
            f"{session['level']} {session['role']}. Focus on building real project "
            "experience and continuous learning."
        )

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_ai_bridge_sessions')
            total_sessions = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COUNT(*) FROM charvak_ai_bridge_premium_reports')
            premium_reports = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COALESCE(SUM(price), 0) FROM charvak_ai_bridge_premium_reports')
            total_revenue = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_sessions": total_sessions,
                "premium_reports": premium_reports,
                "total_revenue": total_revenue,
                "openai_available": OPENAI_AVAILABLE and bool(OPENAI_API_KEY),
            },
        }


ai_bridge_engine = AIBridgeEngine()