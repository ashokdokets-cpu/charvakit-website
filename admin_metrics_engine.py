"""
Charvak Admin Metrics Engine (Z3)
Real, DB-backed analytics for the admin dashboard.
"""
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.admin_metrics")


class AdminMetricsEngine:
    """DB-backed metrics for admin analytics dashboard."""

    def __init__(self):
        logger.info("Admin Metrics Engine ready")

    def _query_one(self, sql: str, params: tuple = None) -> Dict:
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute(sql, params or ())
            row = cur.fetchone()
            cols = [d[0] for d in cur.description] if cur.description else []
            cur.close()
            db.release_pooled_connection(conn)
            if not row:
                return {}
            return dict(zip(cols, row))
        except Exception as e:
            logger.error(f"query_one failed: {e}")
            return {}

    def _query_all(self, sql: str, params: tuple = None, _retry: bool = True) -> List[Dict]:
        conn = None
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute(sql, params or ())
            if cur.description is None:
                cur.close()
                return []
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            cur.close()
            if not rows:
                return []
            return [dict(zip(cols, r)) for r in rows]
        except Exception as e:
            logger.error(f"query_all failed: {e}")
            # One retry on transient pool issues
            if _retry:
                logger.info("Retrying query_all once with fresh connection")
                return self._query_all(sql, params, _retry=False)
            return []
        finally:
            if conn:
                try:
                    from database import db
                    db.release_pooled_connection(conn)
                except Exception:
                    pass

    def get_user_stats(self) -> Dict:
        try:
            total = self._query_one("SELECT COUNT(*) as n FROM users").get("n", 0)
            verified = self._query_one("SELECT COUNT(*) as n FROM users WHERE verified = TRUE").get("n", 0)
            new_7d = self._query_one("SELECT COUNT(*) as n FROM users WHERE created_at > NOW() - INTERVAL '7 days'").get("n", 0)
            active_7d = self._query_one("SELECT COUNT(DISTINCT email) as n FROM charvak_assessment_results WHERE completed_at > NOW() - INTERVAL '7 days'").get("n", 0)
            return {
                "status": "success",
                "total": total,
                "verified": verified,
                "new_7d": new_7d,
                "active_7d": active_7d,
                "verification_rate": round((verified / total * 100), 1) if total else 0,
            }
        except Exception as e:
            logger.error(f"get_user_stats failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_revenue_stats(self) -> Dict:
        try:
            totals = self._query_one("SELECT COUNT(*) as purchases, COALESCE(SUM(credits_added), 0) as credits_sold, COALESCE(SUM(price), 0) as revenue_inr FROM charvak_credit_purchases WHERE status = 'completed'")
            by_plan = self._query_all("SELECT plan, COUNT(*) as count, COALESCE(SUM(price), 0) as revenue FROM charvak_credit_purchases WHERE status = 'completed' GROUP BY plan ORDER BY revenue DESC")
            credits_used = self._query_one("SELECT COALESCE(SUM(credits_used), 0) as n FROM charvak_credit_usage_history").get("n", 0)
            return {
                "status": "success",
                "purchases": totals.get("purchases", 0),
                "credits_sold": totals.get("credits_sold", 0),
                "revenue_inr": float(totals.get("revenue_inr", 0) or 0),
                "credits_used": int(credits_used),
                "by_plan": by_plan,
            }
        except Exception as e:
            logger.error(f"get_revenue_stats failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_funnel_stats(self) -> Dict:
        try:
            registered = self._query_one("SELECT COUNT(*) as n FROM users").get("n", 0)
            verified = self._query_one("SELECT COUNT(*) as n FROM users WHERE verified = TRUE").get("n", 0)
            took_test = self._query_one("SELECT COUNT(DISTINCT email) as n FROM charvak_assessment_results").get("n", 0)
            purchased = self._query_one("SELECT COUNT(DISTINCT email) as n FROM charvak_credit_purchases WHERE status = 'completed' AND plan != 'free'").get("n", 0)
            def pct(a, b):
                return round((a / b * 100), 1) if b else 0
            return {
                "status": "success",
                "registered": registered,
                "verified": verified,
                "took_test": took_test,
                "purchased": purchased,
                "verify_rate": pct(verified, registered),
                "test_rate": pct(took_test, verified),
                "purchase_rate": pct(purchased, took_test),
                "overall_conversion": pct(purchased, registered),
            }
        except Exception as e:
            logger.error(f"get_funnel_stats failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_ielts_usage(self) -> Dict:
        try:
            rows = self._query_all("SELECT assessment_type, COUNT(*) as n FROM charvak_assessment_results WHERE assessment_type LIKE 'ielts_%' GROUP BY assessment_type ORDER BY n DESC")
            counts = {r["assessment_type"]: r["n"] for r in rows}
            return {
                "status": "success",
                "listening": counts.get("ielts_listening", 0),
                "reading": counts.get("ielts_reading", 0),
                "writing": counts.get("ielts_writing", 0),
                "speaking": counts.get("ielts_speaking", 0),
                "total": sum(counts.values()),
            }
        except Exception as e:
            logger.error(f"get_ielts_usage failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_exam_usage(self, limit: int = 10) -> List[Dict]:
        try:
            return self._query_all("SELECT assessment_name, COUNT(*) as n FROM charvak_assessment_results GROUP BY assessment_name ORDER BY n DESC LIMIT %s", (limit,))
        except Exception as e:
            logger.error(f"get_exam_usage failed: {e}")
            return []

    def get_question_bank_health(self) -> Dict:
        try:
            totals = self._query_one("SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE reviewed = TRUE) as reviewed, COUNT(*) FILTER (WHERE reported = TRUE) as reported FROM charvak_exam_question_bank")
            top_exams = self._query_all("SELECT exam_id, COUNT(*) as n, COUNT(*) FILTER (WHERE reviewed = TRUE) as reviewed FROM charvak_exam_question_bank GROUP BY exam_id ORDER BY n DESC LIMIT 10")
            return {
                "status": "success",
                "total": totals.get("total", 0),
                "reviewed": totals.get("reviewed", 0),
                "reported": totals.get("reported", 0),
                "review_rate": round((totals.get("reviewed", 0) / totals.get("total", 1) * 100), 1) if totals.get("total") else 0,
                "top_exams": top_exams,
            }
        except Exception as e:
            logger.error(f"get_question_bank_health failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_full_dashboard(self) -> Dict:
        return {
            "status": "success",
            "generated_at": datetime.now().isoformat(),
            "users": self.get_user_stats(),
            "revenue": self.get_revenue_stats(),
            "funnel": self.get_funnel_stats(),
            "ielts": self.get_ielts_usage(),
            "exams": self.get_exam_usage(),
            "bank": self.get_question_bank_health(),
        }


admin_metrics = AdminMetricsEngine()
