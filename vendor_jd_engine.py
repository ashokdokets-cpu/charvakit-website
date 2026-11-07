"""
Vendor JD Inbox Parser
Session 1 — Bench-Placement Agent

Parses vendor JD emails forwarded to jd-parser@charvakit.com,
extracts structured data, stores in charvak_vendor_jds.
"""

import os
import json
import uuid
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
import psycopg2
from dotenv import load_dotenv

from jd_parser_engine import parse_jd

load_dotenv()

logger = logging.getLogger(__name__)


class VendorJDEngine:
    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        """Self-healing DDL — creates table on first use."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_vendor_jds (
                    jd_id TEXT PRIMARY KEY,
                    source_email TEXT,
                    vendor_name TEXT,
                    vendor_contact TEXT,
                    role_title TEXT NOT NULL,
                    skills_required JSONB DEFAULT '[]'::jsonb,
                    rate_min NUMERIC,
                    rate_max NUMERIC,
                    location TEXT,
                    work_auth_required TEXT,
                    duration TEXT,
                    client_name TEXT,
                    jd_text TEXT,
                    parsed_at TIMESTAMP DEFAULT NOW(),
                    status TEXT DEFAULT 'active'
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"_ensure_table failed: {e}")

    def parse_incoming_email(self, raw_email: Dict) -> Dict:
        """
        Parse a raw email from SendGrid Inbound Parse or similar.
        
        Input shape:
        {
            "from": "vendor@techstar.com",
            "from_name": "TechStar Solutions",
            "subject": "Senior K8s Engineer - $70-85/hr",
            "text": "body text with JD",
            "html": "HTML body"
        }
        """
        try:
            from_email = raw_email.get("from", "")
            from_name = raw_email.get("from_name", "") or self._extract_name(from_email)
            subject = raw_email.get("subject", "")
            body = raw_email.get("text") or self._strip_html(raw_email.get("html", ""))
            
            # Combine subject + body for JD parsing
            jd_text = f"{subject}\n\n{body}".strip()
            
            if not jd_text or len(jd_text) < 50:
                return {"status": "error", "message": "Email too short to be a JD"}
            
            # Use existing JD parser
            parsed = parse_jd(jd_text)
            
            if parsed.get("status") != "success":
                return {"status": "error", "message": "JD parsing failed", "parsed": parsed}
            
            jd = parsed.get("parsed", {})
            
            # Extract rate (parse $XX-YY/hr from body)
            rate_min, rate_max = self._extract_rate(jd_text)
            
            # Extract work auth (H1B, OPT, GC, USC, no sponsorship, etc.)
            work_auth = self._extract_work_auth(jd_text)
            
            # Extract duration
            duration = self._extract_duration(jd_text)
            
            
            # ---- Session 108G: Bench-relevance filter ----
            from bench_jd_filter import bench_jd_filter
            jd_for_filter = {
                "role_title": jd.get("title", subject[:100]),
                "title": jd.get("title", subject[:100]),
                "company": jd.get("company", ""),
                "location": jd.get("location", ""),
                "skills_required": jd.get("skills_required", []),
                "work_auth_required": work_auth,
                "rate_min": rate_min,
                "rate_max": rate_max,
                "raw_email_subject": subject,
                "raw_email_from": from_email,
                "raw_text": jd_text,
                "source": "email",
            }
            is_relevant, reason, best_cand, best_email, overlap = bench_jd_filter.is_relevant(jd_for_filter)
            if not is_relevant:
                logger.info(f"JD rejected by bench filter: {reason} (role={jd_for_filter['role_title']}, best={best_cand})")
                return {
                    "status": "rejected_by_filter",
                    "reason": reason,
                    "best_candidate_hint": best_cand,
                    "skills_overlap_pct": overlap,
                    "role_title": jd_for_filter["role_title"],
                }
            logger.info(f"JD accepted by filter: {reason} (best match: {best_cand} at {overlap:.0%})")
            # ---- End filter ----
            
            # Store
            jd_id = self.store_jd(
                role_title=jd.get("title", subject[:100]),
                skills_required=jd.get("skills_required", []),
                rate_min=rate_min,
                rate_max=rate_max,
                location=jd.get("location", ""),
                work_auth_required=work_auth,
                duration=duration,
                client_name=jd.get("company", ""),
                jd_text=jd_text,
                source_email=from_email,
                vendor_name=from_name,
                vendor_contact=from_email,
            )
            
            return {"status": "success", "jd_id": jd_id}
            
        except Exception as e:
            logger.error(f"parse_incoming_email failed: {e}")
            return {"status": "error", "message": str(e)}

    def store_jd(self, role_title: str, skills_required: List[str] = None,
                 rate_min: float = None, rate_max: float = None,
                 location: str = None, work_auth_required: str = None,
                 duration: str = None, client_name: str = None,
                 jd_text: str = None, source_email: str = None,
                 vendor_name: str = None, vendor_contact: str = None) -> str:
        """Store a parsed JD. Returns jd_id."""
        jd_id = f"JD-{uuid.uuid4().hex[:12].upper()}"
        
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_vendor_jds (
                    jd_id, source_email, vendor_name, vendor_contact,
                    role_title, skills_required, rate_min, rate_max,
                    location, work_auth_required, duration, client_name, jd_text
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                jd_id, source_email, vendor_name, vendor_contact,
                role_title, json.dumps(skills_required or []), rate_min, rate_max,
                location, work_auth_required, duration, client_name, jd_text
            ))
            conn.commit()
            cur.close()
            conn.close()
            logger.info(f"Stored vendor JD {jd_id}: {role_title}")
            return jd_id
        except Exception as e:
            logger.error(f"store_jd failed: {e}")
            raise

    def list_jds(self, status: str = "active", work_auth: str = None,
                 rate_min: float = None, rate_max: float = None,
                 skills: str = None, search: str = None,
                 limit: int = 100, offset: int = 0) -> Dict:
        """List JDs with filters."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            
            where = ["status = %s"]
            params = [status]
            
            if work_auth and work_auth != "Any":
                where.append("work_auth_required ILIKE %s")
                params.append(f"%{work_auth}%")
            
            if rate_min is not None:
                where.append("rate_max >= %s")
                params.append(rate_min)
            
            if rate_max is not None:
                where.append("rate_min <= %s")
                params.append(rate_max)
            
            if skills:
                where.append("skills_required::text ILIKE %s")
                params.append(f"%{skills}%")
            
            if search:
                where.append("(role_title ILIKE %s OR vendor_name ILIKE %s OR client_name ILIKE %s)")
                params.extend([f"%{search}%"] * 3)
            
            where_clause = " AND ".join(where)
            
            # Count
            cur.execute(f"SELECT COUNT(*) FROM charvak_vendor_jds WHERE {where_clause}", params)
            total = cur.fetchone()[0]
            
            # Fetch
            cur.execute(f"""
                SELECT jd_id, role_title, vendor_name, vendor_contact,
                       skills_required, rate_min, rate_max, location,
                       work_auth_required, duration, client_name, parsed_at, status
                FROM charvak_vendor_jds
                WHERE {where_clause}
                ORDER BY parsed_at DESC
                LIMIT %s OFFSET %s
            """, params + [limit, offset])
            
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            jds = []
            for r in rows:
                jds.append({
                    "jd_id": r[0],
                    "role_title": r[1],
                    "vendor_name": r[2],
                    "vendor_contact": r[3],
                    "skills_required": r[4] if r[4] else [],
                    "rate_min": float(r[5]) if r[5] else None,
                    "rate_max": float(r[6]) if r[6] else None,
                    "location": r[7],
                    "work_auth_required": r[8],
                    "duration": r[9],
                    "client_name": r[10],
                    "parsed_at": r[11].isoformat() if r[11] else None,
                    "status": r[12],
                })
            
            return {"status": "success", "jds": jds, "total": total}
            
        except Exception as e:
            logger.error(f"list_jds failed: {e}")
            return {"status": "error", "message": str(e)}

    def archive_jd(self, jd_id: str) -> Dict:
        """Archive a JD."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            cur.execute("UPDATE charvak_vendor_jds SET status='archived' WHERE jd_id=%s", (jd_id,))
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_name(self, email: str) -> str:
        """Derive vendor name from email domain."""
        if "@" in email:
            domain = email.split("@")[1]
            return domain.split(".")[0].replace("-", " ").title()
        return "Unknown"

    def _strip_html(self, html: str) -> str:
        """Strip HTML tags to plain text."""
        text = re.sub(r"<[^>]+>", " ", html or "")
        return re.sub(r"\s+", " ", text).strip()

    def _extract_rate(self, text: str):
        """Extract hourly rate range from JD text."""
        # Match $XX-YY/hr or $XX/hr or $XX - $YY
        patterns = [
            r"\$(\d{2,3})\s*[-\u2013]\s*\$?(\d{2,3})\s*(?:/hr|per hour|hourly)",
            r"\$(\d{2,3})\s*(?:/hr|per hour|hourly)",
            r"(\d{2,3})\s*[-\u2013]\s*(\d{2,3})\s*(?:usd|/hr)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                if m.lastindex == 2:
                    return float(m.group(1)), float(m.group(2))
                else:
                    return float(m.group(1)), float(m.group(1))
        return None, None

    def _extract_work_auth(self, text: str) -> str:
        """Extract work auth requirement."""
        text_lower = text.lower()
        
        if "no sponsorship" in text_lower or "no h1b" in text_lower:
            return "USC/GC only"
        if "h1b transfer" in text_lower:
            return "H1B transfer"
        if "h1b" in text_lower:
            return "H1B"
        if "opt" in text_lower or "ead" in text_lower:
            return "OPT/EAD"
        if "green card" in text_lower or " gc " in text_lower:
            return "GC"
        if "usc" in text_lower or "us citizen" in text_lower:
            return "USC"
        if "any" in text_lower or "all work auth" in text_lower:
            return "Any"
        return "Any"

    def _extract_duration(self, text: str) -> str:
        """Extract duration from JD text."""
        patterns = [
            r"(\d{1,2})\s*(?:month|months|mos)\s*(?:contract|project|engagement)",
            r"(\d{1,2})\s*(?:month|months|mos)",
            r"(\d{1,2})\s*(?:year|years|yr)",
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(0)
        return "Not specified"


# Singleton
vendor_jd_engine = VendorJDEngine()