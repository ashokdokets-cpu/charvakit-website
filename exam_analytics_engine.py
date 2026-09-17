"""
Charvak Exam Analytics Engine
Tracks performance, identifies weak/strong areas, provides AI advice
(DB-backed - Session F/1)
"""
import logging
import secrets
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.exam_analytics")


class ExamAnalyticsEngine:
    def __init__(self):
        self._ensure_tables()
        logger.info("Exam Analytics Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_exam_analytics_performance (
                    email       TEXT NOT NULL,
                    exam_id     TEXT NOT NULL,
                    topic       TEXT NOT NULL,
                    total       INTEGER DEFAULT 0,
                    correct     INTEGER DEFAULT 0,
                    wrong       INTEGER DEFAULT 0,
                    accuracy    NUMERIC(5,2) DEFAULT 0,
                    avg_time    NUMERIC(8,2) DEFAULT 0,
                    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (email, exam_id, topic)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_analytics_perf_email ON charvak_exam_analytics_performance(email)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_exam_analytics_history (
                    history_id   TEXT PRIMARY KEY,
                    email        TEXT NOT NULL,
                    exam_id      TEXT NOT NULL,
                    topic        TEXT NOT NULL,
                    question_id  INTEGER,
                    correct      BOOLEAN DEFAULT FALSE,
                    time_taken   INTEGER DEFAULT 0,
                    recorded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_analytics_hist_email ON charvak_exam_analytics_history(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_analytics_hist_date  ON charvak_exam_analytics_history(recorded_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"exam_analytics tables init failed: {e}")

    # ============================================================
    # RECORD
    # ============================================================

    def record_answer(self, email: str, exam_id: str, topic: str, question_id: int, correct: bool, time_taken: int) -> Dict:
        """Record user answer."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Upsert performance row
            cur.execute('''
                INSERT INTO charvak_exam_analytics_performance
                    (email, exam_id, topic, total, correct, wrong, accuracy, avg_time)
                VALUES (%s, %s, %s, 0, 0, 0, 0, 0)
                ON CONFLICT (email, exam_id, topic) DO NOTHING
            ''', (email, exam_id, topic))

            # Read current counters (with row lock)
            cur.execute('''
                SELECT total, correct, wrong, accuracy, avg_time
                FROM charvak_exam_analytics_performance
                WHERE email = %s AND exam_id = %s AND topic = %s
                FOR UPDATE
            ''', (email, exam_id, topic))
            total, corr, wrong, acc, avg_time = cur.fetchone()
            total = int(total or 0)
            corr = int(corr or 0)
            wrong = int(wrong or 0)
            avg_time = float(avg_time or 0)

            new_total = total + 1
            new_correct = corr + (1 if correct else 0)
            new_wrong = wrong + (0 if correct else 1)
            new_accuracy = round((new_correct / new_total) * 100, 2)
            new_avg_time = round(((avg_time * total) + time_taken) / new_total, 2)

            cur.execute('''
                UPDATE charvak_exam_analytics_performance
                SET total = %s, correct = %s, wrong = %s,
                    accuracy = %s, avg_time = %s, updated_at = CURRENT_TIMESTAMP
                WHERE email = %s AND exam_id = %s AND topic = %s
            ''', (new_total, new_correct, new_wrong, new_accuracy, new_avg_time,
                  email, exam_id, topic))

            # Append history
            history_id = f"HIST-{secrets.token_hex(4).upper()}"
            cur.execute('''
                INSERT INTO charvak_exam_analytics_history
                    (history_id, email, exam_id, topic, question_id, correct, time_taken)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (history_id, email, exam_id, topic, question_id, correct, time_taken))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"record_answer failed: {e}")
            return {"status": "error", "message": "Could not record answer"}

        perf = {
            "total": new_total,
            "correct": new_correct,
            "wrong": new_wrong,
            "accuracy": new_accuracy,
            "avg_time": new_avg_time,
        }
        return {"status": "success", "performance": perf}

    # ============================================================
    # ANALYTICS
    # ============================================================

    def get_analytics(self, email: str) -> Dict:
        """Get complete analytics for user."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT exam_id, topic, total, correct, wrong, accuracy, avg_time
                FROM charvak_exam_analytics_performance
                WHERE email = %s
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_analytics failed: {e}")
            return {"status": "success", "message": "No data yet", "analytics": {}}

        if not rows:
            return {"status": "success", "message": "No data yet", "analytics": {}}

        # Rebuild the composite-key perf dict
        perf = {}
        for r in rows:
            key = f"{r[0]}_{r[1]}"
            perf[key] = {
                "total": int(r[2] or 0),
                "correct": int(r[3] or 0),
                "wrong": int(r[4] or 0),
                "accuracy": float(r[5]) if r[5] is not None else 0,
                "avg_time": float(r[6]) if r[6] is not None else 0,
            }

        strengths = []
        weaknesses = []
        for key, data in perf.items():
            if data["accuracy"] >= 70:
                strengths.append({"topic": key, "accuracy": data["accuracy"]})
            elif data["accuracy"] < 50:
                weaknesses.append({"topic": key, "accuracy": data["accuracy"]})

        advice = []
        if weaknesses:
            advice.append(f"Focus on improving: {', '.join(w['topic'] for w in weaknesses[:3])}")
        if strengths:
            advice.append(f"Strong areas: {', '.join(s['topic'] for s in strengths[:3])}")
        advice.append("Practice 30 minutes daily for best results")
        advice.append("Take mock tests weekly to track improvement")

        total_q = sum(d["total"] for d in perf.values())
        total_c = sum(d["correct"] for d in perf.values())

        return {
            "status": "success",
            "analytics": {
                "total_questions": total_q,
                "total_correct": total_c,
                "overall_accuracy": round(total_c / max(total_q, 1) * 100, 2),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "ai_advice": advice,
                "topics": perf,
            },
        }

    def get_improvement(self, email: str) -> Dict:
        """Track improvement over time (grouped by date)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT TO_CHAR(recorded_at, 'YYYY-MM-DD') AS day,
                       COUNT(*),
                       COALESCE(SUM(CASE WHEN correct THEN 1 ELSE 0 END), 0)
                FROM charvak_exam_analytics_history
                WHERE email = %s
                GROUP BY day
                ORDER BY day ASC
            ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_improvement failed: {e}")
            return {"status": "success", "improvement": []}

        if not rows:
            return {"status": "success", "improvement": []}

        improvement = [
            {"date": r[0], "accuracy": round((int(r[2]) / max(int(r[1]), 1)) * 100, 2)}
            for r in rows
        ]
        return {"status": "success", "improvement": improvement}


exam_analytics_engine = ExamAnalyticsEngine()