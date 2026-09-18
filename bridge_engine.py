"""
Charvak Bridge Engine
5-step assessment journey, radar chart data, revenue calculator
Integrates with existing engines without breaking
(DB-backed - Session H/4)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.bridge")


class BridgeEngine:
    """5-step journey: Diagnose -> Measure -> Bridge -> Match -> Monetize. (DB-backed)"""

    CATEGORIES = [
        {"key": "comm", "label": "Communication"},
        {"key": "prob", "label": "Problem Solving"},
        {"key": "tech", "label": "Technical Execution"},
        {"key": "dom", "label": "Domain Knowledge"},
        {"key": "adapt", "label": "Adaptability"},
    ]

    THRESHOLD = 75

    QUESTIONS = [
        {"id": "comm", "prompt": "A client emails asking for an update on a delayed project. What's your first move?",
         "options": ["Wait for full solution", "Forward to manager", "Reply immediately with revised timeline"],
         "scores": [40, 55, 95]},
        {"id": "prob", "prompt": "Code passes sample tests but fails hidden tests. What do you do?",
         "options": ["Ask for help", "Rewrite everything", "Find edge cases and test"],
         "scores": [40, 55, 95]},
        {"id": "tech", "prompt": "Fixing a bug in unfamiliar codebase. Your approach?",
         "options": ["Random fixes", "Rewrite module", "Trace stack + reproduce locally"],
         "scores": [40, 60, 95]},
        {"id": "dom", "prompt": "Stakeholder uses an unfamiliar industry term. What do you do?",
         "options": ["Nod and move on", "Look it up later", "Ask them directly"],
         "scores": [40, 65, 90]},
        {"id": "adapt", "prompt": "Team switches tools mid-project. How do you respond?",
         "options": ["Push back", "Complain but comply", "Learn new tool quickly"],
         "scores": [40, 55, 95]},
    ]

    def __init__(self):
        self._ensure_tables()
        logger.info("Bridge Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_bridge_sessions (
                    session_id    TEXT PRIMARY KEY,
                    current_step  INTEGER DEFAULT 1,
                    answers       JSONB DEFAULT '{}'::jsonb,
                    scores        JSONB DEFAULT '{}'::jsonb,
                    readiness     INTEGER DEFAULT 0,
                    started_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_bridge_started ON charvak_bridge_sessions(started_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"bridge tables init failed: {e}")

    @staticmethod
    def _row_to_session(row) -> Dict:
        if not row:
            return {}
        def _d(x, default):
            if isinstance(x, type(default)) or x is None:
                return x if x is not None else default
            try:
                return json.loads(x)
            except Exception:
                return default
        return {
            "session_id": row[0],
            "current_step": row[1],
            "answers": _d(row[2], {}),
            "scores": _d(row[3], {}),
            "readiness": row[4],
            "started_at": row[5].isoformat() if hasattr(row[5], "isoformat") else str(row[5]),
            "updated_at": row[6].isoformat() if hasattr(row[6], "isoformat") else str(row[6]),
        }

    # ============================================================
    # SESSION MANAGEMENT
    # ============================================================

    def start_journey(self, data: Dict = None) -> Dict:
        """Start 5-step assessment journey."""
        session_id = f"BRIDGE-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_bridge_sessions
                    (session_id, current_step, answers, scores, readiness)
                VALUES (%s, 1, '{}'::jsonb, '{}'::jsonb, 0)
            ''', (session_id,))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"start_journey failed: {e}")
            return {"status": "error", "message": "Could not start session"}

        return {
            "status": "success",
            "session_id": session_id,
            "steps": ["diagnose", "measure", "bridge", "match", "monetize"],
            "current_step": 1,
            "first_question": self.QUESTIONS[0],
        }

    def _find_session(self, session_id: str):
        """Load session row as dict (or None)."""
        if not session_id:
            return None
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT session_id, current_step, answers, scores, readiness,
                       started_at, updated_at
                FROM charvak_bridge_sessions WHERE session_id = %s
            ''', (session_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            return self._row_to_session(row) if row else None
        except Exception as e:
            logger.error(f"_find_session failed: {e}")
            return None

    def _save_session(self, session: Dict) -> bool:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_bridge_sessions
                SET current_step = %s, answers = %s::jsonb, scores = %s::jsonb,
                    readiness = %s, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            ''', (
                session.get("current_step", 1),
                json.dumps(session.get("answers", {})),
                json.dumps(session.get("scores", {})),
                session.get("readiness", 0),
                session["session_id"],
            ))
            conn.commit()
            cur.close(); conn.close()
            return True
        except Exception as e:
            logger.error(f"_save_session failed: {e}")
            return False

    # ============================================================
    # ANSWER + SCORING
    # ============================================================

    def submit_answer(self, data: Dict) -> Dict:
        """Submit answer and get next question."""
        session_id = data.get("session_id")
        question_id = data.get("question_id")
        answer_index = data.get("answer_index", 0)

        session = self._find_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}

        question = next((q for q in self.QUESTIONS if q["id"] == question_id), None)
        if not question:
            return {"status": "error", "message": "Question not found"}

        score = question["scores"][answer_index] if 0 <= answer_index < len(question["scores"]) else 0
        session["scores"][question_id] = score

        answered = len(session["scores"])
        if answered >= len(self.QUESTIONS):
            session["current_step"] = 2
            session["readiness"] = self._calculate_readiness(session["scores"])
            self._save_session(session)
            return {
                "status": "success",
                "complete": True,
                "readiness": session["readiness"],
                "next_step": "measure",
                "radar_data": self.get_radar_data(session["scores"]),
            }

        self._save_session(session)
        next_question = self.QUESTIONS[answered]
        return {
            "status": "success",
            "complete": False,
            "answered": answered,
            "total": len(self.QUESTIONS),
            "next_question": next_question,
        }

    def _calculate_readiness(self, scores: Dict) -> int:
        """Calculate average readiness score."""
        if not scores:
            return 0
        return round(sum(scores.values()) / len(scores))

    def get_radar_data(self, scores: Dict) -> Dict:
        """Generate radar chart data."""
        return {
            "status": "success",
            "threshold": self.THRESHOLD,
            "radar": [
                {"category": c["label"], "score": scores.get(c["key"], 0), "threshold": self.THRESHOLD}
                for c in self.CATEGORIES
            ],
            "gaps": [
                {"category": c["label"], "score": scores.get(c["key"], 0),
                 "gap": max(0, self.THRESHOLD - scores.get(c["key"], 0))}
                for c in self.CATEGORIES
            ],
        }

    def get_learning_path(self, scores: Dict) -> Dict:
        """Generate learning path based on gaps."""
        modules = {
            "comm": {"title": "Client Communication Under Pressure", "duration": "2 hrs"},
            "prob": {"title": "Debugging Ambiguous Failures", "duration": "3 hrs"},
            "tech": {"title": "Reproduce, Isolate, Fix", "duration": "4 hrs"},
            "dom": {"title": "Industry Vocabulary Sprints", "duration": "1 hr"},
            "adapt": {"title": "Tool-Switch Fire Drill", "duration": "1.5 hrs"},
        }

        gaps = [
            {"category": c["key"], "label": c["label"],
             "gap": max(0, self.THRESHOLD - scores.get(c["key"], 0)),
             "module": modules.get(c["key"])}
            for c in self.CATEGORIES
            if max(0, self.THRESHOLD - scores.get(c["key"], 0)) > 0
        ]

        gaps.sort(key=lambda g: g["gap"], reverse=True)

        return {"status": "success", "learning_path": gaps, "total_modules": len(gaps)}

    # ============================================================
    # REVENUE CALCULATOR (pure)
    # ============================================================

    def calculate_revenue(self, data: Dict) -> Dict:
        """Calculate 4 revenue streams with ISA model."""
        students = int(data.get("students", 1000))
        placement_rate = float(data.get("placement_rate", 45))
        avg_salary = float(data.get("avg_salary", 600000))
        isa_percent = float(data.get("isa_percent", 12))
        isa_months = int(data.get("isa_months", 24))

        placed = round(students * placement_rate / 100)
        isa_revenue = round(placed * avg_salary * isa_percent / 100 * isa_months / 12)
        employer_partners = max(4, round(students / 50))
        corp_subs = employer_partners * 300000
        college_partners = max(2, round(students / 200))
        licensing = college_partners * 500000
        premium_students = round(students * 0.2)
        premium = premium_students * 4999
        total = isa_revenue + corp_subs + licensing + premium

        return {
            "status": "success",
            "revenue_streams": {
                "isa": {"label": "ISA Revenue", "amount": isa_revenue, "detail": f"{placed} placements x {isa_percent}% x {isa_months}mo"},
                "corporate": {"label": "Corporate Subscriptions", "amount": corp_subs, "detail": f"{employer_partners} partners x Rs.3L/yr"},
                "licensing": {"label": "College Licensing", "amount": licensing, "detail": f"{college_partners} licenses x Rs.5L/yr"},
                "premium": {"label": "Premium Tier", "amount": premium, "detail": f"{premium_students} students x Rs.4,999"},
            },
            "total": total,
            "placed_students": placed,
            "per_student": round(total / students, 2) if students > 0 else 0,
        }

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_bridge_sessions')
            total = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_sessions": total,
                "total_questions": len(self.QUESTIONS),
                "categories": len(self.CATEGORIES),
            },
        }


bridge_engine = BridgeEngine()