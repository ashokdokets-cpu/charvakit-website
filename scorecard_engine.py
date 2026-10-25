"""
scorecard_engine.py

Public shareable candidate scorecards.

Creates a public, no-login URL for any completed assessment showing
the candidate's full verified profile. Shareable with hiring managers.

Public URL: /scorecard/{id}
API URL: /api/scorecard/{id}
"""

import os
import json
import secrets
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.scorecard")

# Percentile benchmarks per role level (approximate, can be tuned)
PERCENTILE_BENCHMARKS = {
    "intern":    {"p50": 55, "p75": 72, "p90": 85},
    "junior":    {"p50": 58, "p75": 75, "p90": 88},
    "mid":       {"p50": 60, "p75": 76, "p90": 89},
    "senior":    {"p50": 62, "p75": 78, "p90": 90},
    "staff":     {"p50": 65, "p75": 80, "p90": 92},
    "principal": {"p50": 65, "p75": 80, "p90": 92},
    "manager":   {"p50": 65, "p75": 80, "p90": 92},
    "executive": {"p50": 65, "p75": 80, "p90": 92},
}


class ScorecardEngine:
    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        """Self-healing DDL."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_scorecards (
                    scorecard_id TEXT PRIMARY KEY,
                    assessment_id TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT,
                    industry TEXT,
                    level TEXT,
                    format TEXT,
                    overall_score INTEGER,
                    overall_percentile INTEGER,
                    passed BOOLEAN,
                    payload_json JSONB NOT NULL,
                    integrity_risk TEXT DEFAULT 'clean',
                    certificate_id TEXT,
                    certificate_verify_hash TEXT,
                    shares_count INTEGER DEFAULT 0,
                    views_count INTEGER DEFAULT 0,
                    last_shared_at TIMESTAMP,
                    last_viewed_at TIMESTAMP,
                    public BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.debug(f"_ensure_tables: {e}")

    def _mask_email(self, email: str) -> str:
        if not email or "@" not in email:
            return "anonymous"
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "*" * max(1, len(local) - 1)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"

    def _compute_percentile(self, score: int, level: str) -> int:
        """Estimate percentile from benchmark."""
        benchmarks = PERCENTILE_BENCHMARKS.get((level or "").lower(), PERCENTILE_BENCHMARKS["mid"])
        if score >= benchmarks["p90"]:
            return 90 + min(9, (score - benchmarks["p90"]) // 2)
        elif score >= benchmarks["p75"]:
            return 75 + ((score - benchmarks["p75"]) * 15) // (benchmarks["p90"] - benchmarks["p75"] or 1)
        elif score >= benchmarks["p50"]:
            return 50 + ((score - benchmarks["p50"]) * 25) // (benchmarks["p75"] - benchmarks["p50"] or 1)
        else:
            return max(1, (score * 50) // (benchmarks["p50"] or 1))

    def _compute_skill_breakdown(self, questions: List[Dict]) -> List[Dict]:
        """Group questions by topic and compute score per topic."""
        if not questions:
            return []
        by_topic: Dict[str, Dict] = {}
        for q in questions:
            if not isinstance(q, dict):
                continue
            topic = (q.get("topic") or "General").strip()
            if topic not in by_topic:
                by_topic[topic] = {"correct": 0, "total": 0}
            by_topic[topic]["total"] += 1
            if q.get("is_correct"):
                by_topic[topic]["correct"] += 1
        result = []
        for topic, data in by_topic.items():
            pct = round((data["correct"] / data["total"]) * 100) if data["total"] else 0
            result.append({
                "topic": topic,
                "correct": data["correct"],
                "total": data["total"],
                "score": pct,
                "status": "strong" if pct >= 80 else "mixed" if pct >= 55 else "weak",
            })
        result.sort(key=lambda x: (-x["score"], x["topic"]))
        return result

    def _compute_integrity_summary(self, integrity_data) -> Dict:
        """Normalize integrity summary from assessment."""
        if not integrity_data:
            return {"risk_level": "clean", "total_events": 0, "event_counts": {}, "note": "No signals recorded."}
        if isinstance(integrity_data, str):
            try:
                integrity_data = json.loads(integrity_data)
            except Exception:
                integrity_data = {}
        total = integrity_data.get("total_events", 0)
        event_counts = integrity_data.get("event_counts", {}) or {}
        risk = integrity_data.get("risk_level")
        if not risk:
            if total == 0:
                risk = "clean"
            elif total <= 5:
                risk = "minor"
            elif total <= 15:
                risk = "moderate"
            else:
                risk = "elevated"
        note_map = {
            "clean": "Assessment completed with no environmental signals.",
            "minor": "A few environmental signals recorded. Typical of normal assessment conditions.",
            "moderate": "Several signals recorded. Review the certificate alongside the assessment.",
            "elevated": "Multiple signals recorded. Consider a live verification round.",
        }
        return {
            "risk_level": risk,
            "total_events": total,
            "event_counts": event_counts,
            "note": note_map.get(risk, ""),
        }

    def _build_recommendation(self, assessment: Dict, breakdown: List[Dict], integrity: Dict) -> str:
        """Rule-based 2-3 sentence recommendation."""
        score = assessment.get("score", 0)
        role = assessment.get("role", "this role")
        level = assessment.get("level", "mid")
        passed = assessment.get("passed", False)
        risk = integrity.get("risk_level", "clean")
        
        if passed and score >= 85:
            prefix = f"Strong fit for {role} at the {level} level — scored {score}/100, above benchmark."
        elif passed and score >= 70:
            prefix = f"Solid fit for {role} at the {level} level — scored {score}/100, above the pass threshold."
        elif score >= 60:
            prefix = f"Borderline fit for {role} — scored {score}/100. Suggest a trial-to-hire engagement before a full-time commitment."
        else:
            prefix = f"Below benchmark for {role} at the {level} level — scored {score}/100. Recommend additional screening or an alternative candidate."
        
        if breakdown:
            strongest = breakdown[0]["topic"]
            weakest = breakdown[-1]["topic"] if len(breakdown) > 1 else None
            if weakest and breakdown[-1]["status"] != "strong":
                suffix = f"Strongest area: {strongest}. Growth area: {weakest}."
            else:
                suffix = f"Strongest area: {strongest}. No significant gaps detected."
        else:
            suffix = ""
        
        integrity_note = ""
        if risk == "clean":
            integrity_note = "Integrity profile is clean."
        elif risk == "minor":
            integrity_note = "Minor integrity signals recorded — normal for assessment conditions."
        elif risk in ("moderate", "elevated"):
            integrity_note = f"Integrity risk: {risk}. Recommend live verification round."
        
        return " ".join(filter(None, [prefix, suffix, integrity_note]))

    def create_scorecard(self, assessment_id: str, email: str) -> Dict:
        """Build a scorecard for a completed assessment."""
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()

        # Load assessment
        cur.execute("""
            SELECT assessment_id, email, role, industry, level, format, size,
                   num_questions, questions_json, status, score, passed,
                   correct_count, completed_at, integrity_summary
            FROM charvak_career_assessments
            WHERE assessment_id = %s AND LOWER(email) = LOWER(%s)
        """, (assessment_id, email))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            return {"status": "error", "message": "Assessment not found or does not belong to this email."}
        
        if row[9] != "completed":
            cur.close(); conn.close()
            return {"status": "error", "message": "Assessment is not yet completed."}

        assessment = {
            "assessment_id": row[0],
            "email": row[1],
            "role": row[2],
            "industry": row[3],
            "level": row[4],
            "format": row[5],
            "size": row[6],
            "num_questions": row[7],
            "questions": row[8] if isinstance(row[8], list) else (json.loads(row[8]) if row[8] else []),
            "score": row[10] or 0,
            "passed": row[11] or False,
            "correct_count": row[12] or 0,
            "completed_at": row[13].isoformat() if row[13] else None,
            "integrity_summary": row[14],
        }

        # Load certificate if exists
        # Table may not exist on some environments (older DBs) — handle gracefully
        cert_row = None
        try:
            cur.execute("""
                SELECT cert_id, badge_tier, certification_hash, issued_at
                FROM charvak_career_certifications
                WHERE assessment_id = %s AND revoked_at IS NULL
                LIMIT 1
            """, (assessment_id,))
            cert_row = cur.fetchone()
        except Exception as _cert_err:
            logger.debug(f"Certificate lookup skipped (table may not exist): {_cert_err}")
            try:
                conn.rollback()
            except Exception:
                pass
            cert_row = None

        # Build skill breakdown
        breakdown = self._compute_skill_breakdown(assessment["questions"])
        
        # Build integrity summary
        integrity = self._compute_integrity_summary(assessment["integrity_summary"])
        
        # Percentile
        percentile = self._compute_percentile(assessment["score"], assessment["level"])
        
        # Recommendation
        recommendation = self._build_recommendation(assessment, breakdown, integrity)

        # Build payload
        payload = {
            "candidate": {
                "name_masked": self._mask_email(assessment["email"]),
                "email_masked": self._mask_email(assessment["email"]),
            },
            "assessment": {
                "role": assessment["role"],
                "industry": assessment["industry"],
                "level": assessment["level"],
                "format": assessment["format"],
                "size": assessment["size"],
                "num_questions": assessment["num_questions"],
                "completed_at": assessment["completed_at"],
            },
            "scores": {
                "overall": assessment["score"],
                "percentile": percentile,
                "passed": assessment["passed"],
                "correct_count": assessment["correct_count"],
                "total_questions": assessment["num_questions"],
            },
            "skills": breakdown,
            "integrity": integrity,
            "certificate": None,
            "recommendation": recommendation,
        }

        if cert_row:
            payload["certificate"] = {
                "cert_id": cert_row[0],
                "tier": cert_row[1],
                "verify_hash": cert_row[2],
                "issued_at": cert_row[3].isoformat() if cert_row[3] else None,
                "verify_url_path": f"/api/career-certification/verify/{cert_row[2]}" if cert_row[2] else None,
            }

        # Check if scorecard already exists for this assessment
        cur.execute("SELECT scorecard_id FROM charvak_scorecards WHERE assessment_id = %s", (assessment_id,))
        existing = cur.fetchone()
        
        if existing:
            scorecard_id = existing[0]
            cur.execute("""
                UPDATE charvak_scorecards SET
                    payload_json = %s,
                    overall_score = %s,
                    overall_percentile = %s,
                    passed = %s,
                    integrity_risk = %s,
                    certificate_id = %s,
                    certificate_verify_hash = %s
                WHERE scorecard_id = %s
            """, (
                json.dumps(payload),
                assessment["score"],
                percentile,
                assessment["passed"],
                integrity["risk_level"],
                cert_row[0] if cert_row else None,
                cert_row[2] if cert_row else None,
                scorecard_id,
            ))
            conn.commit()
            cur.close(); conn.close()
            return {
                "status": "success",
                "scorecard_id": scorecard_id,
                "action": "updated",
                "public_url": f"/scorecard/{scorecard_id}",
                "api_url": f"/api/scorecard/{scorecard_id}",
            }
        
        # Create new
        scorecard_id = f"SC-{secrets.token_hex(6).upper()}"
        cur.execute("""
            INSERT INTO charvak_scorecards (
                scorecard_id, assessment_id, email, role, industry, level, format,
                overall_score, overall_percentile, passed, payload_json,
                integrity_risk, certificate_id, certificate_verify_hash
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            scorecard_id,
            assessment_id,
            assessment["email"],
            assessment["role"],
            assessment["industry"],
            assessment["level"],
            assessment["format"],
            assessment["score"],
            percentile,
            assessment["passed"],
            json.dumps(payload),
            integrity["risk_level"],
            cert_row[0] if cert_row else None,
            cert_row[2] if cert_row else None,
        ))
        conn.commit()
        cur.close(); conn.close()
        
        return {
            "status": "success",
            "scorecard_id": scorecard_id,
            "action": "created",
            "public_url": f"/scorecard/{scorecard_id}",
            "api_url": f"/api/scorecard/{scorecard_id}",
        }

    def get_scorecard(self, scorecard_id: str, track_view: bool = True) -> Dict:
        """Read a scorecard. Public — no auth."""
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT scorecard_id, assessment_id, email, role, industry, level,
                   format, overall_score, overall_percentile, passed, payload_json,
                   integrity_risk, certificate_id, certificate_verify_hash,
                   shares_count, views_count, public, created_at
            FROM charvak_scorecards
            WHERE scorecard_id = %s AND public = TRUE
        """, (scorecard_id,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            return {"status": "error", "message": "Scorecard not found."}
        
        if track_view:
            try:
                cur.execute("""
                    UPDATE charvak_scorecards
                    SET views_count = views_count + 1, last_viewed_at = NOW()
                    WHERE scorecard_id = %s
                """, (scorecard_id,))
                conn.commit()
            except Exception:
                conn.rollback()
        
        payload = row[10] if isinstance(row[10], dict) else json.loads(row[10])
        cur.close(); conn.close()
        
        return {
            "status": "success",
            "scorecard_id": row[0],
            "assessment_id": row[1],
            "candidate_email_masked": self._mask_email(row[2]),
            "role": row[3],
            "industry": row[4],
            "level": row[5],
            "format": row[6],
            "overall_score": row[7],
            "overall_percentile": row[8],
            "passed": row[9],
            "payload": payload,
            "integrity_risk": row[11],
            "certificate_id": row[12],
            "certificate_verify_hash": row[13],
            "shares_count": row[14],
            "views_count": row[15],
            "created_at": row[17].isoformat() if row[17] else None,
        }

    def track_share(self, scorecard_id: str, channel: str = "link") -> Dict:
        """Increment share count."""
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE charvak_scorecards
            SET shares_count = shares_count + 1, last_shared_at = NOW()
            WHERE scorecard_id = %s AND public = TRUE
        """, (scorecard_id,))
        conn.commit()
        affected = cur.rowcount
        cur.close(); conn.close()
        if affected == 0:
            return {"status": "error", "message": "Scorecard not found."}
        return {"status": "success", "channel": channel}

    def list_scorecards_for_email(self, email: str) -> List[Dict]:
        """List all scorecards for an email. Auth-gated at route level."""
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT scorecard_id, role, level, overall_score, overall_percentile,
                   passed, integrity_risk, shares_count, views_count, created_at
            FROM charvak_scorecards
            WHERE LOWER(email) = LOWER(%s) AND public = TRUE
            ORDER BY created_at DESC
        """, (email,))
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [
            {
                "scorecard_id": r[0],
                "role": r[1],
                "level": r[2],
                "overall_score": r[3],
                "overall_percentile": r[4],
                "passed": r[5],
                "integrity_risk": r[6],
                "shares_count": r[7],
                "views_count": r[8],
                "created_at": r[9].isoformat() if r[9] else None,
                "public_url": f"/scorecard/{r[0]}",
            }
            for r in rows
        ]


# Singleton
scorecard_engine = ScorecardEngine()