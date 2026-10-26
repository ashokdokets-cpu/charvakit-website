"""
F4 Recruiter Dashboard — unified pipeline engine.

v1 (this file): list_pipeline, get_pipeline_kpis, export_pipeline_csv
v2 additions (later): get_level_breakdown, get_source_mix, get_stage_funnel,
                      list_pipeline_grouped, export_pipeline_pdf
v3 additions (later): mark_hired, list_hires, get_hire_stats

Aggregates three sources:
  - charvak_screen_candidates (F3 AI screen agent)
  - charvak_applications       (staffing pipeline / job applications)
  - charvak_employer_referrals (F1 employer referrals)

Dedups by email. Each candidate row carries the source that produced it.
"""
import os
import csv
import io
from datetime import datetime
from typing import Dict, List, Optional

import psycopg2
import psycopg2.extras

from dotenv import load_dotenv


class RecruiterDashboardEngine:
    def __init__(self):
        self._ensured = False

    # ─── infrastructure ─────────────────────────────────
    def _conn(self):
        load_dotenv(".env.local", override=False)
        load_dotenv()
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL not set")
        conn = psycopg2.connect(url)
        conn.autocommit = False
        return conn

    def _ensure_schema(self):
        """Defensive — should already exist via migration, but safe to re-run."""
        if self._ensured:
            return
        try:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("""
                ALTER TABLE charvak_applications
                  ADD COLUMN IF NOT EXISTS candidate_email text,
                  ADD COLUMN IF NOT EXISTS candidate_name text,
                  ADD COLUMN IF NOT EXISTS hired_at timestamp,
                  ADD COLUMN IF NOT EXISTS hired_company text,
                  ADD COLUMN IF NOT EXISTS hired_ctc_inr integer
            """)
            cur.execute("""
                ALTER TABLE charvak_client_roles
                  ADD COLUMN IF NOT EXISTS level text DEFAULT 'mid'
            """)
            conn.commit()
            cur.close()
            conn.close()
            self._ensured = True
        except Exception as e:
            print(f"[recruiter_dashboard] _ensure_schema warn: {e}")

    # ─── v1: core pipeline ─────────────────────────────
    def list_pipeline(self, recruiter_email: str, filters: Optional[Dict] = None) -> Dict:
        """
        Unified pipeline across screen + applications + referrals.
        Filters: {source, stage, role_id, min_score, q (name/email search), level}
        """
        self._ensure_schema()
        filters = filters or {}
        rows = []

        try:
            conn = self._conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # ---- source 1: screen candidates ----
            cur.execute("""
                SELECT
                    sc.candidate_screen_id   AS ck,
                    sc.candidate_email       AS email,
                    sc.candidate_name        AS name,
                    'screen'                 AS source,
                    ss.role_title            AS role_title,
                    ss.role_id               AS role_id,
                    sc.qualification_score   AS score,
                    CASE
                      WHEN sc.status = 'completed' THEN 'screened'
                      WHEN sc.status = 'scheduled' THEN 'scheduled'
                      WHEN sc.status = 'consented' THEN 'screened'
                      WHEN sc.status = 'invited'   THEN 'invited'
                      ELSE sc.status
                    END                      AS stage,
                    (sc.captured_data->>'current_ctc_inr')::int  AS ctc_inr,
                    (sc.captured_data->>'notice_days')::int      AS notice_days,
                    sc.qualified             AS qualified,
                    COALESCE(sc.completed_at, sc.first_response_at, sc.invited_at) AS last_activity,
                    '/screen/session/' || ss.session_id AS detail_url
                FROM charvak_screen_candidates sc
                JOIN charvak_screen_sessions ss ON ss.session_id = sc.session_id
                WHERE ss.recruiter_email = %s
            """, (recruiter_email,))
            rows.extend([dict(r) for r in cur.fetchall()])

            # ---- source 2: applications ----
            cur.execute("""
                SELECT
                    a.application_id   AS ck,
                    COALESCE(a.candidate_email, a.user_id) AS email,
                    a.candidate_name   AS name,
                    'application'      AS source,
                    cr.title           AS role_title,
                    a.client_role_id   AS role_id,
                    COALESCE(a.readiness_score, 0) AS score,
                    COALESCE(a.status, 'applied')  AS stage,
                    NULL::int          AS ctc_inr,
                    NULL::int          AS notice_days,
                    NULL::boolean      AS qualified,
                    COALESCE(a.submitted_at, a.created_at) AS last_activity,
                    '/admin/client-roles/' || a.client_role_id AS detail_url
                FROM charvak_applications a
                LEFT JOIN charvak_client_roles cr ON cr.role_id = a.client_role_id
                WHERE a.candidate_email IS NOT NULL
                   OR a.user_id LIKE '%@%'
            """)
            rows.extend([dict(r) for r in cur.fetchall()])

            # ---- source 3: employer referrals ----
            try:
                cur.execute("""
                    SELECT
                        er.referral_id     AS ck,
                        er.candidate_email AS email,
                        er.candidate_name  AS name,
                        'referral'         AS source,
                        cr.title           AS role_title,
                        er.role_id         AS role_id,
                        NULL::int          AS score,
                        COALESCE(er.status, 'referred') AS stage,
                        NULL::int          AS ctc_inr,
                        NULL::int          AS notice_days,
                        NULL::boolean      AS qualified,
                        er.created_at      AS last_activity,
                        '/employer/refer/' || er.role_id AS detail_url
                    FROM charvak_employer_referrals er
                    LEFT JOIN charvak_client_roles cr ON cr.role_id = er.role_id
                """)
                rows.extend([dict(r) for r in cur.fetchall()])
            except Exception as e:
                # table may not have the expected shape yet — skip silently
                print(f"[recruiter_dashboard] referrals skip: {e}")
                conn.rollback()

            cur.close()
            conn.close()
        except Exception as e:
            print(f"[recruiter_dashboard] list_pipeline error: {e}")
            return {"status": "error", "message": str(e), "pipeline": [], "total": 0}

        # ---- apply filters ----
        def _matches(r):
            if filters.get("source") and r.get("source") != filters["source"]:
                return False
            if filters.get("stage") and r.get("stage") != filters["stage"]:
                return False
            if filters.get("role_id") and r.get("role_id") != filters["role_id"]:
                return False
            if filters.get("min_score"):
                try:
                    if int(r.get("score") or 0) < int(filters["min_score"]):
                        return False
                except Exception:
                    return False
            if filters.get("q"):
                q = filters["q"].lower()
                hay = " ".join(str(x or "") for x in
                               (r.get("name"), r.get("email"),
                                r.get("role_title"))).lower()
                if q not in hay:
                    return False
            return True

        rows = [r for r in rows if _matches(r)]

        # ---- sort by last_activity desc ----
        def _ts(r):
            v = r.get("last_activity")
            if isinstance(v, datetime):
                return v
            return datetime.min
        rows.sort(key=_ts, reverse=True)

        # ---- dedup by email (keep best source: screen > application > referral) ----
        by_email = {}
        priority = {"screen": 3, "application": 2, "referral": 1}
        for r in rows:
            em = (r.get("email") or "").strip().lower()
            if not em:
                continue
            if em not in by_email or priority.get(r["source"], 0) > priority.get(by_email[em]["source"], 0):
                by_email[em] = r
        deduped = list(by_email.values())

        # ---- normalize output ----
        out = []
        for r in deduped:
            out.append({
                "candidate_key": r.get("ck"),
                "name": r.get("name") or "(no name)",
                "email": r.get("email") or "",
                "source": r.get("source"),
                "role_title": r.get("role_title") or "—",
                "role_id": r.get("role_id"),
                "score": (None if r.get("score") is None else int(r.get("score") or 0)),
                "stage": r.get("stage") or "—",
                "ctc_inr": r.get("ctc_inr"),
                "notice_days": r.get("notice_days"),
                "qualified": r.get("qualified"),
                "last_activity": (r["last_activity"].isoformat()
                                  if isinstance(r.get("last_activity"), datetime)
                                  else r.get("last_activity")),
                "detail_url": r.get("detail_url") or "#",
            })

        return {
            "status": "success",
            "pipeline": out,
            "total": len(out),
            "filters_applied": filters,
        }

    def get_pipeline_kpis(self, recruiter_email: str) -> Dict:
        """Top-of-page KPI cards + (v2) source mix + stage funnel."""
        res = self.list_pipeline(recruiter_email)
        pipe = res.get("pipeline", [])

        total = len(pipe)
        screened = sum(1 for r in pipe if r.get("stage") == "screened")
        qualified = sum(1 for r in pipe if r.get("qualified") is True)
        hired = sum(1 for r in pipe if r.get("stage") == "hired")
        scores = [r["score"] for r in pipe if r.get("score") not in (None, 0) or r.get("stage") == "screened"]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0

        by_source = {}
        for r in pipe:
            s = r.get("source") or "unknown"
            by_source[s] = by_source.get(s, 0) + 1

        by_stage = {}
        for r in pipe:
            s = r.get("stage") or "unknown"
            by_stage[s] = by_stage.get(s, 0) + 1

        return {
            "status": "success",
            "total": total,
            "screened": screened,
            "qualified": qualified,
            "hired": hired,
            "avg_score": avg_score,
            "by_source": by_source,
            "by_stage": by_stage,
        }

    def export_pipeline_csv(self, recruiter_email: str,
                            filters: Optional[Dict] = None) -> str:
        """CSV string of the filtered pipeline."""
        res = self.list_pipeline(recruiter_email, filters)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "name", "email", "source", "role_title", "score",
            "stage", "ctc_inr", "notice_days", "qualified",
            "last_activity", "detail_url"
        ])
        for r in res.get("pipeline", []):
            writer.writerow([
                r.get("name"), r.get("email"), r.get("source"),
                r.get("role_title"), r.get("score"), r.get("stage"),
                r.get("ctc_inr") or "", r.get("notice_days") or "",
                r.get("qualified"), r.get("last_activity"),
                r.get("detail_url"),
            ])
        return buf.getvalue()


recruiter_dashboard_engine = RecruiterDashboardEngine()