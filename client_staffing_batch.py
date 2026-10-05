"""
Batch download helper for the client staffing engine (Session 25 Patch 5c.2).
Standalone module to avoid embedding complexity inside client_staffing_engine.py.
"""
import io
import json
import re
import zipfile
import logging
from datetime import datetime

logger = logging.getLogger("charvakit.client_staffing_batch")


def _safe(s):
    s = (s or "").strip() or "candidate"
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s)[:40] or "candidate"


def build_role_batch_zip(engine, role_id):
    """
    Build a single ZIP containing one subfolder per applicant of a role.
    engine: a ClientStaffingEngine instance (for build_submission_package).
    role_id: string.
    Returns dict: {status, zip_bytes, filename, count} or {status, message}.
    """
    role_id = (role_id or "").strip()
    if not role_id:
        return {"status": "error", "message": "role_id required"}

    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT title, client_name FROM charvak_client_roles WHERE role_id = %s", (role_id,))
        role_row = cur.fetchone()
        if not role_row:
            cur.close(); conn.close()
            return {"status": "error", "message": "Role not found"}
        role_title, client_name = role_row

        cur.execute(
            "SELECT a.application_id, c.name, a.user_id "
            "FROM charvak_applications a "
            "LEFT JOIN charvak_candidates c ON c.email = a.user_id "
            "WHERE a.client_role_id = %s "
            "ORDER BY COALESCE(a.readiness_score, 0) DESC, a.created_at DESC",
            (role_id,),
        )
        apps = cur.fetchall()
        cur.close(); conn.close()
    except Exception as e:
        logger.error("build_role_batch_zip fetch failed: " + str(e))
        return {"status": "error", "message": "Fetch failed: " + str(e)}

    if not apps:
        return {"status": "error", "message": "No applicants for this role"}

    buf = io.BytesIO()
    summary_lines = [
        "Charvak IT Consulting - Batch Applicant Summary",
        "=" * 55,
        "",
        "Role:        " + str(role_title),
        "Client:      " + str(client_name),
        "Role ID:     " + role_id,
        "Applicants:  " + str(len(apps)),
        "Generated:   " + datetime.now().strftime("%Y-%m-%d %H:%M"),
        "",
        "Per-applicant folders contain:",
        "  candidate_profile.json   Full structured data",
        "  evaluation_form.pdf      Branded Charvak evaluation",
        "  README.txt               Per-applicant manifest",
        "",
        "Applicant list (ranked by readiness):",
        "",
    ]

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as outer:
        for idx, (app_id, cand_name, cand_email) in enumerate(apps, 1):
            folder = "%02d_%s_%s" % (idx, _safe(cand_name), _safe(app_id))
            summary_lines.append("  %02d. %s - %s" % (idx, cand_name or cand_email, app_id))

            try:
                pkg_result = engine.build_submission_package(app_id)
            except Exception as e:
                outer.writestr(folder + "/ERROR.txt", "Could not build package: " + str(e))
                continue

            if pkg_result.get("status") != "success":
                outer.writestr(folder + "/ERROR.txt", pkg_result.get("message", "Unknown error"))
                continue

            package = pkg_result["package"]

            outer.writestr(
                folder + "/candidate_profile.json",
                json.dumps(package, indent=2, default=str, ensure_ascii=False),
            )

            try:
                from submission_pdf_engine import render_submission_evaluation_pdf
                pdf_bytes = render_submission_evaluation_pdf(package)
                outer.writestr(folder + "/evaluation_form.pdf", pdf_bytes)
            except Exception as e:
                outer.writestr(folder + "/evaluation_form_ERROR.txt", "PDF generation failed: " + str(e))

            inner_readme = [
                "Candidate:  " + str(cand_name or cand_email),
                "Email:      " + str(cand_email),
                "App ID:     " + str(app_id),
                "Role:       " + str(role_title),
                "Client:     " + str(client_name),
                "",
                "Contains:",
                "  candidate_profile.json   Full structured data",
                "  evaluation_form.pdf      Branded Charvak evaluation",
                "",
                "Confidential.",
            ]
            outer.writestr(folder + "/README.txt", "\n".join(inner_readme))

        outer.writestr("SUMMARY.txt", "\n".join(summary_lines))

    buf.seek(0)
    zip_bytes = buf.read()

    filename = "Charvak_Submissions_" + _safe(role_id) + "_" + datetime.now().strftime("%Y%m%d") + ".zip"

    return {
        "status": "success",
        "zip_bytes": zip_bytes,
        "filename": filename,
        "count": len(apps),
    }
