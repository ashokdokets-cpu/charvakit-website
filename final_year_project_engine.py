"""
Charvak Final Year Project Assistant - AI-Powered
Personalized project support using GPT-4o-mini
(DB-backed - Session E/4)
"""
import logging
import json
import os
import secrets
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.fyp")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class FinalYearProjectEngine:
    """AI-powered final year project support (subscriptions DB-backed)."""

    PLANS = {
        "free":    {"name": "Free",    "price": 0,   "features": ["Topic suggestions (5)", "Basic outline"]},
        "pro":     {"name": "Pro",     "price": 299, "features": ["AI personalized topics (20+)", "AI proposal generation", "Tech stack suggestion"]},
        "premium": {"name": "Premium", "price": 999, "features": ["Everything in Pro", "Full AI documentation", "Viva preparation", "Code starter templates", "Priority support"]},
    }

    def __init__(self):
        self._ensure_tables()
        logger.info(f"FYP Engine ready (DB-backed) | AI: {'Enabled' if OPENAI_API_KEY else 'Fallback mode'}")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_fyp_subscriptions (
                    subscription_id  TEXT PRIMARY KEY,
                    email            TEXT NOT NULL,
                    plan             TEXT NOT NULL DEFAULT 'free',
                    price            INTEGER DEFAULT 0,
                    status           TEXT NOT NULL DEFAULT 'active',
                    subscribed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_fyp_subs_email  ON charvak_fyp_subscriptions(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_fyp_subs_plan   ON charvak_fyp_subscriptions(plan)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_fyp_subs_status ON charvak_fyp_subscriptions(status)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"fyp tables init failed: {e}")

    # ============================================================
    # AI HELPER (JSON-only response)
    # ============================================================

    def _ai_json(self, prompt: str, max_tokens: int, temperature: float):
        """Call OpenAI in JSON mode and return parsed dict, or None on failure."""
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            # Defensive: strip accidental markdown fences even in JSON mode
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            return json.loads(content)
        except Exception as e:
            logger.warning(f"AI call failed: {e}")
            return None

    # ============================================================
    # AI-POWERED TOPIC SUGGESTIONS (stateless)
    # ============================================================

    def suggest_topics_ai(self, data: Dict) -> Dict:
        branch = data.get("branch", "Computer Science")
        domain = data.get("domain", "AI/ML")
        skills = data.get("skills", [])
        interests = data.get("interests", [])
        if OPENAI_API_KEY:
            prompt = f"""Generate 10 unique final year project topics for a {branch} student.
            Domain: {domain}
            Skills: {', '.join(skills) if skills else 'General programming'}
            Interests: {', '.join(interests) if interests else 'Open to suggestions'}

            Return JSON: {{"topics": [{{"title": "...", "domain": "...", "difficulty": "...", "description": "..."}}]}}"""
            topics_data = self._ai_json(prompt, max_tokens=800, temperature=0.8)
            if topics_data is not None:
                return {"status": "success", "ai_generated": True, **topics_data}
        return self._fallback_topics(branch, domain)

    def _fallback_topics(self, branch: str, domain: str) -> Dict:
        topics = [
            {"title": "Chatbot for College Enquiry", "domain": domain, "difficulty": "Intermediate", "description": "AI chatbot answering college queries"},
            {"title": "Disease Prediction using ML", "domain": domain, "difficulty": "Advanced", "description": "Predict diseases from symptoms"},
            {"title": "Face Recognition Attendance", "domain": domain, "difficulty": "Intermediate", "description": "Automated attendance using face recognition"},
            {"title": "Sentiment Analysis Platform", "domain": domain, "difficulty": "Beginner", "description": "Analyze sentiment from reviews"},
            {"title": "Stock Price Predictor", "domain": domain, "difficulty": "Advanced", "description": "LSTM-based stock prediction"},
        ]
        return {"status": "success", "ai_generated": False, "topics": topics}

    # ============================================================
    # AI-POWERED PROPOSAL GENERATION (stateless)
    # ============================================================

    def generate_proposal_ai(self, data: Dict) -> Dict:
        topic = data.get("topic", "Project")
        student = data.get("student_name", "Student")
        college = data.get("college", "College")
        if OPENAI_API_KEY:
            prompt = f"""Generate a professional final year project proposal for:
            Student: {student}
            College: {college}
            Topic: {topic}

            Return JSON: {{"title": "...", "abstract": "...", "objectives": [...], "scope": "...", "tech_stack": [...], "modules": [...], "timeline": [...]}}"""
            proposal = self._ai_json(prompt, max_tokens=1000, temperature=0.7)
            if proposal is not None:
                return {"status": "success", "ai_generated": True, "proposal": proposal}
        return {"status": "success", "ai_generated": False, "proposal": self._fallback_proposal(topic)}

    def _fallback_proposal(self, topic: str) -> Dict:
        return {
            "title": topic,
            "abstract": f"This project focuses on {topic}.",
            "objectives": [f"Study {topic}", f"Design {topic}", f"Implement {topic}"],
            "scope": f"End-to-end development of {topic}",
            "tech_stack": ["Python", "React", "PostgreSQL"],
            "modules": ["Authentication", "Core Module", "Admin", "Reports"],
            "timeline": ["Week 1-2: Research", "Week 3-8: Development", "Week 9-12: Testing"],
        }

    # ============================================================
    # AI-POWERED DOCUMENTATION (stateless)
    # ============================================================

    def generate_documentation_ai(self, data: Dict) -> Dict:
        topic = data.get("topic", "Project")
        if OPENAI_API_KEY:
            prompt = f"""Generate complete documentation outline for final year project: {topic}
            Return JSON: {{"chapters": [{{"chapter": 1, "title": "...", "content_outline": "..."}}], "diagrams": [...], "documents": [...]}}"""
            docs = self._ai_json(prompt, max_tokens=800, temperature=0.5)
            if docs is not None:
                return {"status": "success", "ai_generated": True, "documentation": docs}
        return {"status": "success", "ai_generated": False, "documentation": self._fallback_docs(topic)}

    def _fallback_docs(self, topic: str) -> Dict:
        return {
            "chapters": [
                {"chapter": 1, "title": "Introduction", "content_outline": f"Background of {topic}"},
                {"chapter": 2, "title": "Literature Review", "content_outline": "Existing systems"},
                {"chapter": 3, "title": "System Design", "content_outline": "Architecture"},
                {"chapter": 4, "title": "Implementation", "content_outline": "Code structure"},
                {"chapter": 5, "title": "Testing", "content_outline": "Test cases"},
                {"chapter": 6, "title": "Conclusion", "content_outline": "Summary"},
            ],
            "diagrams": ["Use Case", "ER Diagram", "Class Diagram"],
            "documents": ["SRS", "SDD", "User Manual"],
        }

    # ============================================================
    # AI-POWERED VIVA PREP (stateless)
    # ============================================================

    def generate_viva_ai(self, data: Dict) -> Dict:
        topic = data.get("topic", "Project")
        if OPENAI_API_KEY:
            prompt = f"""Generate 15 viva questions specific to final year project: {topic}
            Include technical, architectural, and general questions.
            Return JSON: {{"questions": [...], "tips": [...]}}"""
            viva = self._ai_json(prompt, max_tokens=600, temperature=0.6)
            if viva is not None:
                return {"status": "success", "ai_generated": True, **viva}
        return {"status": "success", "ai_generated": False, "questions": self._fallback_questions(topic)}

    def _fallback_questions(self, topic: str) -> List[str]:
        return [
            f"Why did you choose {topic}?",
            "What technologies did you use?",
            "What challenges did you face?",
            "How does your project differ from existing solutions?",
            "What future enhancements would you suggest?",
        ]

    # ============================================================
    # MONETIZATION (DB-backed)
    # ============================================================

    def subscribe(self, data: Dict) -> Dict:
        """
        Subscribe to FYP plan.
        data = {email, plan}
        """
        plan_key = data.get("plan", "free")
        plan = self.PLANS.get(plan_key, self.PLANS["free"])
        subscription_id = f"FYP-SUB-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_fyp_subscriptions
                    (subscription_id, email, plan, price, status)
                VALUES (%s, %s, %s, %s, 'active')
            ''', (subscription_id, data.get("email"), plan_key, plan["price"]))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"subscribe failed: {e}")
            return {"status": "error", "message": "Could not subscribe"}

        return {
            "status": "success",
            "plan": plan["name"],
            "price": plan["price"],
            "features": plan["features"],
            "message": f"Subscribed to {plan['name']}!",
        }

    def get_plans(self) -> Dict:
        return {"status": "success", "plans": self.PLANS}

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*), COALESCE(SUM(price), 0) FROM charvak_fyp_subscriptions')
            row = cur.fetchone()
            total_subscriptions = row[0] or 0
            total_revenue = row[1] or 0
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_projects": 0,
                "total_subscriptions": total_subscriptions,
                "total_revenue": total_revenue,
                "ai_enabled": bool(OPENAI_API_KEY),
            },
        }


final_year_project_engine = FinalYearProjectEngine()