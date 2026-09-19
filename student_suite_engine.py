"""
Student Suite Engine - Accepts both email and student_email
(DB-backed - Session E/2)
"""
import logging
import secrets
from typing import Dict, Optional

logger = logging.getLogger("charvakit.student_suite")


PLANS = {
    "free":    {"name": "Free",        "requests": 10,  "price": 0},
    "pro":     {"name": "Student Pro", "requests": 100, "price": 99},
    "premium": {"name": "Premium",     "requests": 500, "price": 499},
}


class StudentSuiteEngine:
    def __init__(self):
        self._ensure_tables()
        logger.info("Student Suite Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_student_suite_subscriptions (
                    email          TEXT PRIMARY KEY,
                    plan           TEXT NOT NULL DEFAULT 'free',
                    requests_used  INTEGER DEFAULT 0,
                    subscribed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_student_subs_plan ON charvak_student_suite_subscriptions(plan)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_student_suite_usage (
                    usage_id       TEXT PRIMARY KEY,
                    email          TEXT NOT NULL,
                    feature        TEXT NOT NULL,
                    count          INTEGER DEFAULT 1,
                    last_used_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(email, feature)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_student_usage_email   ON charvak_student_suite_usage(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_student_usage_feature ON charvak_student_suite_usage(feature)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"student_suite tables init failed: {e}")

    # ============================================================
    # SUBSCRIPTION
    # ============================================================

    def subscribe(self, email: str = None, student_email: str = None, plan: str = "free", **kwargs) -> Dict:
        """Handle subscription - accepts both email and student_email"""
        user_email = email or student_email or (kwargs.get('data') or {}).get('email')

        if not user_email:
            return {"status": "error", "message": "Email is required"}

        if plan not in PLANS:
            return {"status": "error", "message": "Invalid plan"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_student_suite_subscriptions (email, plan, requests_used)
                VALUES (%s, %s, 0)
                ON CONFLICT (email) DO UPDATE
                    SET plan = EXCLUDED.plan,
                        requests_used = 0,
                        subscribed_at = CURRENT_TIMESTAMP
            ''', (user_email, plan))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"subscribe failed: {e}")
            return {"status": "error", "message": "Could not subscribe"}

        return {
            "status": "success",
            "message": f"Subscribed to {PLANS[plan]['name']} plan",
            "plan": PLANS[plan],
            "email": user_email,
        }

    def get_plan(self, email: str) -> Dict:
        """Get user's plan"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT plan, requests_used, subscribed_at
                FROM charvak_student_suite_subscriptions WHERE email = %s
            ''', (email,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_plan failed: {e}")
            return {"status": "error", "message": "Could not load plan"}

        if not row:
            return {"status": "error", "message": "No subscription found"}

        plan_key, requests_used, subscribed_at = row
        plan_details = PLANS.get(plan_key, {})

        return {
            "status": "success",
            "subscription": {
                "plan": plan_key,
                "plan_details": plan_details,
                "subscribed_at": subscribed_at.date().isoformat() if hasattr(subscribed_at, "date") else str(subscribed_at),
                "requests_used": requests_used,
            },
        }

    # ============================================================
    # ASSISTANTS
    # ============================================================

    def _call_openai_json(self, prompt: str) -> Optional[Dict]:
        """Call OpenAI (JSON mode) via HTTP - mirrors advanced_assessment_engine pattern."""
        try:
            import os
            import json as _json
            import requests

            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                return None

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "response_format": {"type": "json_object"},
                },
                timeout=25,
            )

            data = response.json()
            content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()

            # Defensive: strip markdown fences
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            try:
                parsed = _json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
            return None
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return None

    def assist_assignment(self, email: str = None, student_email: str = None, subject: str = "", topic: str = "", **kwargs) -> Dict:
        """Assignment assistance - accepts both email formats"""
        user_email = email or student_email

        if not user_email:
            return {"status": "error", "message": "Email is required"}

        if not self._check_subscription(user_email):
            return {"status": "error", "message": "No active subscription. Please subscribe first."}

        self._track_usage(user_email, "assignment")

        # Try AI generation
        prompt = (
            f"You are a helpful academic assistant for students.\n"
            f"Subject: {subject or 'General'}\n"
            f"Topic: {topic or 'General'}\n\n"
            f"Provide clear, actionable help with this assignment.\n"
            f"Return a JSON object with these keys:\n"
            f"  - outline: array of 5-7 bullet points forming an outline\n"
            f"  - key_concepts: array of 4-6 important concepts to understand\n"
            f"  - study_tips: array of 3 practical study tips\n"
            f"  - examples: array of 2 illustrative examples"
        )
        ai_result = self._call_openai_json(prompt)

        if ai_result:
            return {
                "status": "success",
                "message": "Assignment assistance generated",
                "subject": subject,
                "topic": topic,
                "email": user_email,
                "outline": ai_result.get("outline", []),
                "key_concepts": ai_result.get("key_concepts", []),
                "study_tips": ai_result.get("study_tips", []),
                "examples": ai_result.get("examples", []),
            }

        # Fallback when AI unavailable
        return {
            "status": "success",
            "message": "Assignment assistance generated (basic — AI temporarily unavailable)",
            "subject": subject,
            "topic": topic,
            "email": user_email,
        }

    def assist_research(self, email: str = None, student_email: str = None, field: str = "", topic: str = "", **kwargs) -> Dict:
        """Research assistance - accepts both email formats"""
        user_email = email or student_email

        if not user_email:
            return {"status": "error", "message": "Email is required"}

        if not self._check_subscription(user_email):
            return {"status": "error", "message": "No active subscription. Please subscribe first."}

        self._track_usage(user_email, "research")

        # Try AI generation
        prompt = (
            f"You are a helpful academic research assistant for students.\n"
            f"Field: {field or 'General'}\n"
            f"Research topic: {topic or 'General'}\n\n"
            f"Provide clear research guidance.\n"
            f"Return a JSON object with these keys:\n"
            f"  - research_questions: array of 4-5 key research questions\n"
            f"  - methodology: array of 3-4 suggested research methods\n"
            f"  - key_sources: array of 4-5 types of sources to consult\n"
            f"  - structure: array of 4-5 sections to include in the paper"
        )
        ai_result = self._call_openai_json(prompt)

        if ai_result:
            return {
                "status": "success",
                "message": "Research assistance generated",
                "field": field,
                "topic": topic,
                "email": user_email,
                "research_questions": ai_result.get("research_questions", []),
                "methodology": ai_result.get("methodology", []),
                "key_sources": ai_result.get("key_sources", []),
                "structure": ai_result.get("structure", []),
            }

        # Fallback when AI unavailable
        return {
            "status": "success",
            "message": "Research assistance generated (basic — AI temporarily unavailable)",
            "field": field,
            "topic": topic,
            "email": user_email,
        }

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        """Get suite stats"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_student_suite_subscriptions')
            total_subscribers = cur.fetchone()[0]

            cur.execute('SELECT COUNT(*) FROM charvak_student_suite_usage')
            total_usage = cur.fetchone()[0]

            cur.execute('''
                SELECT email, feature, count
                FROM charvak_student_suite_usage
                ORDER BY email, feature
            ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        usage_by_feature: Dict = {}
        for r in rows:
            usage_by_feature.setdefault(r[0], {})[r[1]] = r[2]

        return {
            "status": "success",
            "total_subscribers": total_subscribers,
            "total_usage": total_usage,
            "usage_by_feature": usage_by_feature,
        }

    # ============================================================
    # PRIVATE HELPERS
    # ============================================================

    def _check_subscription(self, email: str) -> bool:
        """Check if user has active subscription"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT 1 FROM charvak_student_suite_subscriptions WHERE email = %s', (email,))
            found = cur.fetchone() is not None
            cur.close(); conn.close()
            return found
        except Exception as e:
            logger.error(f"_check_subscription failed: {e}")
            return False

    def _track_usage(self, email: str, feature: str) -> None:
        """Track usage"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            usage_id = f"USE-{secrets.token_hex(4).upper()}"
            cur.execute('''
                INSERT INTO charvak_student_suite_usage (usage_id, email, feature, count)
                VALUES (%s, %s, %s, 1)
                ON CONFLICT (email, feature) DO UPDATE
                    SET count = charvak_student_suite_usage.count + 1,
                        last_used_at = CURRENT_TIMESTAMP
            ''', (usage_id, email, feature))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_track_usage failed: {e}")


student_suite_engine = StudentSuiteEngine()