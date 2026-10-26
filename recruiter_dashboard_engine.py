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




    # ─── v2: level + grouping + analytics ──────────────
    def get_level_breakdown(self, recruiter_email: str) -> Dict:
        """
        Counts by experience level, per client_roles.level.
        Rows without a matching role are bucketed as 'unassigned'.
        """
        res = self.list_pipeline(recruiter_email)
        pipe = res.get("pipeline", [])

        # Fetch role_id → level map
        levels_map = {}
        try:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("SELECT role_id, COALESCE(level, 'mid') FROM charvak_client_roles")
            for role_id, level in cur.fetchall():
                levels_map[role_id] = level
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[recruiter_dashboard] levels map warn: {e}")

        buckets = {"fresher": 0, "junior": 0, "mid": 0,
                   "senior": 0, "staff": 0, "manager": 0,
                   "executive": 0, "unassigned": 0}
        for r in pipe:
            lv = levels_map.get(r.get("role_id"))
            if lv in buckets:
                buckets[lv] += 1
            else:
                buckets["unassigned"] += 1

        return {"status": "success", "levels": buckets, "total": sum(buckets.values())}

    def get_source_mix(self, recruiter_email: str) -> Dict:
        """Chart data: candidate counts by source."""
        res = self.list_pipeline(recruiter_email)
        mix = {}
        for r in res.get("pipeline", []):
            s = r.get("source") or "unknown"
            mix[s] = mix.get(s, 0) + 1
        return {"status": "success", "mix": mix}

    def get_stage_funnel(self, recruiter_email: str) -> Dict:
        """Chart data: candidate counts by stage (ordered funnel)."""
        res = self.list_pipeline(recruiter_email)
        order = ["invited", "chatting", "screened", "scheduled",
                 "applied", "referred", "hired", "disqualified"]
        counts = {}
        for r in res.get("pipeline", []):
            s = (r.get("stage") or "unknown").lower()
            counts[s] = counts.get(s, 0) + 1
        # Return in funnel order, only non-zero
        ordered = {k: counts[k] for k in order if k in counts}
        # Append any unlisted stages at the end
        for k in counts:
            if k not in ordered:
                ordered[k] = counts[k]
        return {"status": "success", "funnel": ordered}

    def list_pipeline_grouped(self, recruiter_email: str,
                               by: str = "source",
                               filters: Optional[Dict] = None) -> Dict:
        """
        Grouped view. by = source | role | level
        Returns {group_key: [rows], ..., _meta: {...}}
        """
        res = self.list_pipeline(recruiter_email, filters)
        pipe = res.get("pipeline", [])

        # For level grouping, resolve role → level
        levels_map = {}
        if by == "level":
            try:
                conn = self._conn()
                cur = conn.cursor()
                cur.execute("SELECT role_id, COALESCE(level, 'mid') FROM charvak_client_roles")
                for role_id, level in cur.fetchall():
                    levels_map[role_id] = level
                cur.close()
                conn.close()
            except Exception:
                pass

        groups = {}
        for r in pipe:
            if by == "role":
                key = r.get("role_title") or "Unassigned Role"
            elif by == "level":
                key = levels_map.get(r.get("role_id"), "unassigned")
            else:
                key = r.get("source") or "unknown"
            groups.setdefault(key, []).append(r)

        # Sort keys so charts/tables are stable
        sorted_groups = {}
        for k in sorted(groups.keys()):
            sorted_groups[k] = groups[k]

        return {
            "status": "success",
            "grouped_by": by,
            "groups": sorted_groups,
            "total": len(pipe),
        }

    def export_pipeline_pdf(self, recruiter_email: str,
                            filters: Optional[Dict] = None) -> bytes:
        """PDF export of the filtered pipeline."""
        res = self.list_pipeline(recruiter_email, filters)
        pipe = res.get("pipeline", [])

        try:
            from pdf_engine import CharvakReportPDF
        except Exception as e:
            print(f"[recruiter_dashboard] pdf_engine unavailable: {e}")
            return b""

        try:
            pdf = CharvakReportPDF(
                title="Recruiter Pipeline",
                user_email=recruiter_email,
                report_title="Recruiter Pipeline Export",
            )
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, f"Candidate Pipeline ({len(pipe)} total)", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.ln(4)

            # Column header
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(45, 6, "Name", border=0)
            pdf.cell(45, 6, "Email", border=0)
            pdf.cell(20, 6, "Source", border=0)
            pdf.cell(25, 6, "Score", border=0)
            pdf.cell(20, 6, "Stage", border=0)
            pdf.ln(6)
            pdf.set_font("Helvetica", "", 8)

            for r in pipe:
                name = (r.get("name") or "")[:28]
                email = (r.get("email") or "")[:35]
                pdf.cell(45, 5, name, border=0)
                pdf.cell(45, 5, email, border=0)
                pdf.cell(20, 5, str(r.get("source") or ""), border=0)
                pdf.cell(25, 5, str(r.get("score") if r.get("score") is not None else "—"), border=0)
                pdf.cell(20, 5, str(r.get("stage") or ""), border=0)
                pdf.ln(5)

            return pdf.output(dest="S").encode("latin-1") if hasattr(pdf.output(dest="S"), "encode") else pdf.output(dest="S")
        except Exception as e:
            print(f"[recruiter_dashboard] PDF export error: {e}")
            return b""


recruiter_dashboard_engine = RecruiterDashboardEngine()