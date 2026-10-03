"""
Charvak Premium Report Engine (Session 16)
AI-enriched PDF reports built on top of free-tier scan data.
"""
import os
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.premium_report")


REPORT_TYPES = {
    "auditbot": {
        "title": "AuditBot Security Report",
        "subtitle": "Deep security analysis and prioritized action plan",
        "context": "You are a senior application security auditor. Produce a detailed executive report from the raw scan findings. Be specific about risks and prioritization.",
    },
    "lock_in_breaker": {
        "title": "Lock-In Breaker Analysis",
        "subtitle": "Vendor lock-in assessment and multi-cloud migration path",
        "context": "You are a cloud architecture consultant specializing in vendor lock-in assessment. Produce a strategic report with a concrete migration path.",
    },
    "skill_twin": {
        "title": "Skill-Twin Verification Report",
        "subtitle": "Deep skills analysis and career readiness plan",
        "context": "You are a senior career coach with deep knowledge of technical hiring. Produce a personalized skills report.",
    },
}


class PremiumReportEngine:
    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_premium_reports (
                    report_id       TEXT PRIMARY KEY,
                    email           TEXT NOT NULL,
                    report_type     TEXT NOT NULL,
                    source_id       TEXT,
                    source_data     JSONB NOT NULL DEFAULT '{}'::jsonb,
                    title           TEXT,
                    subtitle        TEXT,
                    content_json    JSONB NOT NULL DEFAULT '{}'::jsonb,
                    credits_used    INTEGER NOT NULL DEFAULT 400,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_premium_reports_email ON charvak_premium_reports (email, created_at DESC)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_premium_reports_type ON charvak_premium_reports (report_type, created_at DESC)")
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"premium report table init failed: {e}")
    def generate_report(self, data):
        email = (data.get("email") or "").strip().lower()
        report_type = (data.get("report_type") or "").strip().lower()
        source_data = data.get("source_data") or {}
        source_id = data.get("source_id")

        if not email:
            return {"status": "error", "message": "email required"}
        if report_type not in REPORT_TYPES:
            return {"status": "error", "message": "Unknown report_type: " + report_type}
        if not isinstance(source_data, dict) or not source_data:
            return {"status": "error", "message": "source_data must be a non-empty dict"}

        rt = REPORT_TYPES[report_type]
        report_id = "PR-" + secrets.token_hex(8).upper()
        generated_at = datetime.now().strftime("%B %d, %Y")

        sections = self._call_openai_for_sections(report_type, source_data, email)

        content = {
            "report_title": rt["title"],
            "subtitle": rt["subtitle"],
            "user_email": email,
            "report_id": report_id,
            "generated_at": generated_at,
            "executive_summary": sections.get("executive_summary", ""),
            "full_report_sections": self._extract_free_sections(source_data),
            "deep_analysis": sections.get("deep_analysis", []),
            "action_roadmap": sections.get("action_roadmap", []),
            "benchmarks": sections.get("benchmarks", []),
            "custom_recommendations": sections.get("custom_recommendations", []),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_premium_reports
                    (report_id, email, report_type, source_id, source_data,
                     title, subtitle, content_json, credits_used)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb, 400)
            """, (
                report_id, email, report_type, source_id,
                json.dumps(source_data, default=str),
                rt["title"], rt["subtitle"],
                json.dumps(content, default=str),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"premium_report persist failed: {e}")
            return {"status": "error", "message": "Could not save report"}

        return {
            "status": "success",
            "report_id": report_id,
            "report_type": report_type,
            "title": rt["title"],
            "subtitle": rt["subtitle"],
            "content": content,
            "created_at": datetime.now().isoformat(),
        }

    def _extract_free_sections(self, source_data):
        sections = []
        for key, value in source_data.items():
            heading = key.replace("_", " ").title()
            if isinstance(value, (dict, list)):
                content = json.dumps(value, indent=2, default=str)[:2000]
            else:
                content = str(value)
            sections.append({"heading": heading, "content": content})
        return sections[:20]
    def _call_openai_for_sections(self, report_type, source_data, email):
        import requests
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            logger.warning("OPENAI_API_KEY missing - using fallback sections")
            return self._fallback_sections(source_data)

        rt = REPORT_TYPES[report_type]
        source_str = json.dumps(source_data, indent=2, default=str)
        if len(source_str) > 6000:
            source_str = source_str[:6000] + " ...(truncated)"

        prompt = (
            rt["context"] + "\n\n"
            + "SOURCE DATA (free-tier scan result from " + report_type + "):\n"
            + source_str + "\n\n"
            + "Generate a PREMIUM REPORT with these five sections. Return STRICT JSON with keys: "
            + "executive_summary (2-3 paragraphs), "
            + "deep_analysis (3-5 items, each {heading, content}), "
            + "action_roadmap (4-6 items, each {priority, action, eta}), "
            + "benchmarks (3-5 items, each {metric, your_value, industry_avg}), "
            + "custom_recommendations (3-5 items, each {title, body}).\n\n"
            + "Rules:\n"
            + "- Be SPECIFIC. Reference actual values from the source data.\n"
            + "- Do NOT invent data not present in the source data.\n"
            + "- Benchmarks should be realistic industry comparisons.\n"
            + "- Actions must be concrete.\n"
            + "- Return ONLY the JSON object."
        )

        fence = chr(96) * 3  # three backticks, built without literal backticks

        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": "Bearer " + api_key},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"},
                },
                timeout=60,
            )
            data = resp.json()
            content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
            if content.startswith(fence):
                content = content.split(fence, 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = json.loads(content)
            return {
                "executive_summary": parsed.get("executive_summary", ""),
                "deep_analysis": parsed.get("deep_analysis", []),
                "action_roadmap": parsed.get("action_roadmap", []),
                "benchmarks": parsed.get("benchmarks", []),
                "custom_recommendations": parsed.get("custom_recommendations", []),
            }
        except Exception as e:
            logger.error(f"Premium report OpenAI call failed: {e}")
            return self._fallback_sections(source_data)

    def _fallback_sections(self, source_data):
        return {
            "executive_summary": "This report was generated from your free-tier scan result. The premium AI analysis is temporarily unavailable, but the raw findings are included below.",
            "deep_analysis": [{"heading": "Summary of findings", "content": "Review the free-tier result section for the detailed data points."}],
            "action_roadmap": [{"priority": "high", "action": "Review the free-tier findings and prioritize the highest-impact item", "eta": "24 hours"}],
            "benchmarks": [],
            "custom_recommendations": [],
        }
    def get_report(self, report_id, user_email):
        report_id = (report_id or "").strip()
        user_email = (user_email or "").strip().lower()
        if not report_id or not user_email:
            return {"status": "error", "message": "report_id and email required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT report_id, email, report_type, source_id, source_data,
                       title, subtitle, content_json, credits_used, created_at
                FROM charvak_premium_reports WHERE report_id = %s
            """, (report_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_report failed: {e}")
            return {"status": "error", "message": "Could not load report"}

        if not row:
            return {"status": "error", "message": "Report not found"}
        if row[1] != user_email:
            return {"status": "error", "message": "Not your report"}

        return {
            "status": "success",
            "report": {
                "report_id": row[0],
                "email": row[1],
                "report_type": row[2],
                "source_id": row[3],
                "source_data": row[4],
                "title": row[5],
                "subtitle": row[6],
                "content": row[7],
                "credits_used": row[8],
                "created_at": row[9].isoformat() if row[9] else None,
            },
        }

    def list_reports(self, email):
        email = (email or "").strip().lower()
        if not email:
            return {"status": "error", "message": "email required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT report_id, report_type, title, created_at
                FROM charvak_premium_reports
                WHERE email = %s
                ORDER BY created_at DESC LIMIT 50
            """, (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"list_reports failed: {e}")
            return {"status": "error", "message": "Could not list reports"}

        reports = [
            {"report_id": r[0], "report_type": r[1], "title": r[2],
             "created_at": r[3].isoformat() if r[3] else None}
            for r in rows
        ]
        return {"status": "success", "reports": reports, "count": len(reports)}


premium_report_engine = PremiumReportEngine()