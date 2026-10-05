"""
Submission Evaluation Form PDF (Session 23, Patch 4a.2)

Consumes the JSON output of client_staffing_engine.build_submission_package()
and renders a branded A4 PDF suitable for sharing with hiring managers
or attaching to a client submission.

Usage:
    from submission_pdf_engine import render_submission_evaluation_pdf
    pdf_bytes = render_submission_evaluation_pdf(package_dict)
"""
import os
from datetime import datetime
from typing import Dict

from pdf_engine import (
    CharvakReportPDF,
    COLOR_PRIMARY,
    COLOR_DARK,
    COLOR_MUTED,
    COLOR_WHITE,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
)


def _s(v, default="") -> str:
    """Null-safe string."""
    if v is None:
        return default
    return str(v)


def _safe_fname(s: str) -> str:
    """Make a safe filename fragment."""
    import re
    out = re.sub(r"[^A-Za-z0-9_-]", "_", s or "")
    return out.strip("_") or "unknown"


def render_submission_evaluation_pdf(package: Dict) -> bytes:
    """
    Render a submission evaluation form PDF.
    package = the 'package' dict from build_submission_package().
    """
    meta = package.get("meta", {}) or {}
    personal = package.get("personal", {}) or {}
    contact = package.get("contact", {}) or {}
    employment = package.get("employment", {}) or {}
    education = package.get("education", {}) or {}
    readiness = package.get("readiness", {}) or {}
    attachments = package.get("attachments", {}) or {}
    skills = package.get("skills", []) or []
    screening = package.get("screening_answers", []) or []
    candidate_summary = _s(package.get("candidate_summary"), "")

    application_id = _s(meta.get("application_id"), "N/A")
    role_title = _s(meta.get("role_title"), "Unknown Role")
    client_name = _s(meta.get("client_name"), "Confidential")
    role_priority = _s(meta.get("role_priority"), "normal")
    generated_at = _s(meta.get("generated_at"),
                      datetime.now().strftime("%B %d, %Y"))

    # ---------- Instantiate PDF ----------
    pdf = CharvakReportPDF(
        report_title="Candidate Submission - Evaluation Form",
        user_email=contact.get("primary_email"),
    )

    # Cover page
    pdf.cover_page(
        subtitle="Candidate Evaluation Form",
        generated_at=generated_at,
        report_id=application_id,
    )

    # ============================================================
    # Section 1 - Role
    # ============================================================
    pdf.add_page()
    pdf.section_heading("Role Summary", number=1)

    # Priority badge
    if role_priority == "urgent":
        pdf.severity_badge("URGENT", "high")
    else:
        pdf.severity_badge("NORMAL", "low")
    pdf.ln(3)

    pdf.key_value_row("Position", role_title)
    pdf.key_value_row("Client", client_name)
    if meta.get("role_location"):
        pdf.key_value_row("Location", _s(meta.get("role_location")))
    if meta.get("role_experience_min") is not None or meta.get("role_experience_max") is not None:
        emin = _s(meta.get("role_experience_min"), "?")
        emax = _s(meta.get("role_experience_max"), "?")
        pdf.key_value_row("Experience Required", f"{emin} - {emax} years")
    if meta.get("role_job_type"):
        pdf.key_value_row("Job Type", _s(meta.get("role_job_type")))
    if meta.get("role_skills"):
        pdf.key_value_row("Required Skills", _s(meta.get("role_skills")))

    # ============================================================
    # Section 2 - Candidate Profile
    # ============================================================
    pdf.section_heading("Candidate Profile", number=2)

    full_name = _s(personal.get("full_name")) or _s(personal.get("first_name"))
    pdf.key_value_row("Name", full_name or "Not provided")

    if contact.get("primary_email"):
        pdf.key_value_row("Primary Email", _s(contact.get("primary_email")))
    if contact.get("additional_email"):
        pdf.key_value_row("Additional Email", _s(contact.get("additional_email")))
    if contact.get("primary_phone"):
        pdf.key_value_row("Primary Phone", _s(contact.get("primary_phone")))
    if contact.get("additional_phone"):
        pdf.key_value_row("Additional Phone", _s(contact.get("additional_phone")))
    if personal.get("current_location"):
        pdf.key_value_row("Current Location", _s(personal.get("current_location")))
    if personal.get("country"):
        pdf.key_value_row("Country", _s(personal.get("country")))

    # Professional
    pdf.sub_heading("Professional")
    if employment.get("current_company"):
        pdf.key_value_row("Current Company", _s(employment.get("current_company")))
    if employment.get("current_designation"):
        pdf.key_value_row("Current Designation", _s(employment.get("current_designation")))
    if employment.get("total_experience_years") is not None:
        pdf.key_value_row("Total Experience", f"{employment.get('total_experience_years')} years")
    if employment.get("relevant_experience_years") is not None:
        pdf.key_value_row("Relevant Experience", f"{employment.get('relevant_experience_years')} years")
    if employment.get("notice_period"):
        pdf.key_value_row("Notice Period", _s(employment.get("notice_period")))
    if employment.get("availability"):
        pdf.key_value_row("Availability", _s(employment.get("availability")))

    # Compensation (only if present)
    has_comp = any([
        employment.get("current_salary"),
        employment.get("salary_expectation"),
        employment.get("expected_hike_percent"),
    ])
    if has_comp:
        pdf.sub_heading("Compensation")
        if employment.get("current_salary") is not None:
            curr = _s(employment.get("current_salary_currency"), "INR")
            pdf.key_value_row("Current Salary", f"{curr} {employment.get('current_salary')} Lakhs")
        if employment.get("salary_expectation"):
            pdf.key_value_row("Expected Salary", _s(employment.get("salary_expectation")))
        if employment.get("expected_hike_percent") is not None:
            pdf.key_value_row("Expected Hike", f"{employment.get('expected_hike_percent')}%")

    # Skills
    if skills:
        pdf.sub_heading("Skills")
        # Normalize to strings
        skill_list = [str(s).strip() for s in skills if str(s).strip()]
        if skill_list:
            pdf.bullet_list(skill_list)

    # Education
    has_edu = any([
        education.get("qualification"),
        education.get("degree"),
        education.get("university"),
        education.get("graduation_year"),
    ])
    if has_edu:
        pdf.sub_heading("Education")
        if education.get("qualification"):
            pdf.key_value_row("Qualification", _s(education.get("qualification")))
        if education.get("degree"):
            pdf.key_value_row("Degree / Major", _s(education.get("degree")))
        if education.get("university"):
            pdf.key_value_row("University", _s(education.get("university")))
        if education.get("graduation_year"):
            pdf.key_value_row("Graduation Year", _s(education.get("graduation_year")))

    # Links
    has_links = any([
        contact.get("linkedin_url"),
        contact.get("github_url"),
        contact.get("portfolio_url"),
    ])
    if has_links:
        pdf.sub_heading("Links")
        if contact.get("linkedin_url"):
            pdf.key_value_row("LinkedIn", _s(contact.get("linkedin_url")))
        if contact.get("github_url"):
            pdf.key_value_row("GitHub", _s(contact.get("github_url")))
        if contact.get("portfolio_url"):
            pdf.key_value_row("Portfolio", _s(contact.get("portfolio_url")))

    # ============================================================
    # Section 3 - Readiness Assessment
    # ============================================================
    pdf.section_heading("Readiness Assessment", number=3)

    readiness_score = readiness.get("readiness_score")
    if readiness_score is not None:
        pdf.severity_badge(f"READINESS {readiness_score}/100", "info")
        pdf.ln(3)
        if readiness.get("verdict"):
            pdf.key_value_row("Verdict", _s(readiness.get("verdict")))
        if readiness.get("percentile") is not None:
            pdf.key_value_row("Percentile", f"{readiness.get('percentile')}th")
        if readiness.get("benchmark_score") is not None:
            pdf.key_value_row("Benchmark", f"{readiness.get('benchmark_score')}/100")
        if readiness.get("certificate_id"):
            pdf.key_value_row("Certificate ID", _s(readiness.get("certificate_id")))
        if readiness.get("certificate_hash"):
            pdf.key_value_row("Verification Hash", _s(readiness.get("certificate_hash")))
        site = os.getenv("SITE_URL", "https://www.charvakit.com").rstrip("/")
        if readiness.get("certificate_id"):
            pdf.key_value_row("Verify At",
                              f"{site}/readiness/{readiness.get('certificate_id')}")
    else:
        pdf.paragraph(
            "No verified readiness certificate attached to this application. "
            "The candidate has not completed a Charvak Role Readiness assessment "
            "for this position."
        )

    # ============================================================
    # Section 4 - Screening Responses
    # ============================================================
    pdf.section_heading("Screening Responses", number=4)

    if not screening:
        pdf.paragraph("No screening responses recorded for this application.")
    else:
        for q in screening:
            qn = q.get("question_num", "")
            qtext = _s(q.get("question_text"), "")
            answer = _s(q.get("answer"), "-") or "-"
            filled_by = _s(q.get("fill_source"), "candidate")
            label = f"Q{qn}. {qtext}"
            pdf.key_value_row(label, answer)
            # Sourcing hint under the answer
            if filled_by == "charvak":
                pdf.set_font("DejaVu", "I", size=8)
                pdf.set_text_color(*COLOR_MUTED)
                pdf.set_x(pdf.l_margin + 4)
                pdf.cell(0, 4, "(filled by Charvak)", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(*COLOR_DARK)
                pdf.ln(1)

    # ============================================================
    # Section 5 - Attachments & Consent
    # ============================================================
    pdf.section_heading("Attachments & Consent", number=5)

    def _check(flag):
        return "[X]" if flag else "[ ]"

    if attachments.get("resume_available"):
        pdf.cell(0, 6, f"{_check(True)} Resume (candidate-provided)", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, f"{_check(False)} Resume (not attached)", new_x="LMARGIN", new_y="NEXT")

    if attachments.get("certificate_pdf_url"):
        pdf.cell(0, 6, f"{_check(True)} Readiness Certificate PDF", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, f"{_check(False)} Readiness Certificate PDF", new_x="LMARGIN", new_y="NEXT")

    if attachments.get("consent_recorded"):
        cid = _s(attachments.get("consent_id"), "")
        pdf.cell(0, 6, f"{_check(True)} Candidate consent recorded ({cid})",
                 new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, f"{_check(False)} Candidate consent NOT recorded",
                 new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)

    # ============================================================
    # Section 6 - Recruiter Notes
    # ============================================================
    pdf.section_heading("Recruiter Notes", number=6)
    notes = _s(meta.get("recruiter_notes"), "").strip()
    if notes:
        pdf.paragraph(notes)
    else:
        pdf.paragraph(
            "(No notes recorded. This section is filled in by the Charvak "
            "recruiter during the review process.)"
        )

    # ============================================================
    # Footer strip (last page)
    # ============================================================
    pdf.ln(6)
    pdf.divider()
    pdf.set_font("DejaVu", "I", size=8)
    pdf.set_text_color(*COLOR_MUTED)
    site = os.getenv("SITE_URL", "https://www.charvakit.com").rstrip("/")
    pdf.cell(0, 5, f"Generated by Charvak IT Consulting  |  {site}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Application ID: {application_id}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "This document contains confidential candidate information.",
             new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def submission_package_filename(package: Dict) -> str:
    """Build a sensible filename for the evaluation PDF."""
    meta = package.get("meta", {}) or {}
    personal = package.get("personal", {}) or {}
    role_title = _safe_fname(meta.get("role_title", "role"))
    name = _safe_fname(personal.get("full_name") or personal.get("first_name") or "candidate")
    app_id = _safe_fname(meta.get("application_id", "app"))
    return f"Charvak_Evaluation_{name}_{role_title}_{app_id}.pdf"

# ============================================================
# ZIP bundle (Session 23, Patch 4a.3)
# ============================================================
import io
import json as _json
import zipfile


def _decode_document(doc_row: dict) -> tuple:
    """
    Given a charvak_candidate_documents row (as dict), return (filename, bytes).
    Handles both content_base64 and storage_path storage.
    Returns (None, None) if the file cannot be loaded.
    """
    import base64
    filename = doc_row.get("filename") or "file.bin"

    # Option 1: base64 blob in DB
    b64 = doc_row.get("content_base64") or ""
    if b64:
        try:
            return filename, base64.b64decode(b64)
        except Exception:
            pass

    # Option 2: file on disk
    path = doc_row.get("storage_path") or ""
    if path:
        try:
            with open(path, "rb") as f:
                return filename, f.read()
        except Exception:
            pass

    return None, None


def _safe_zip_entry(name: str, fallback: str) -> str:
    """Sanitize a filename for use as a zip entry."""
    import re
    name = (name or "").strip() or fallback
    name = name.replace("..", "_").replace("/", "_").replace("\\", "_")
    name = re.sub(r"[^\w\.\-]+", "_", name)
    return name or fallback


def _fetch_documents_for_candidate(candidate_id: str) -> list:
    """Return all document rows for a candidate as dicts."""
    if not candidate_id:
        return []
    try:
        from database import db
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT document_id, document_type, filename, content_type,
                   size_bytes, storage_path, content_base64, uploaded_at
            FROM charvak_candidate_documents
            WHERE candidate_id = %s
            ORDER BY uploaded_at DESC
        """, (candidate_id,))
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [{
            "document_id": r[0], "document_type": r[1], "filename": r[2],
            "content_type": r[3], "size_bytes": r[4], "storage_path": r[5],
            "content_base64": r[6], "uploaded_at": r[7],
        } for r in rows]
    except Exception as e:
        print(f"WARN: _fetch_documents_for_candidate failed: {e}")
        return []


def build_submission_zip(package: dict) -> bytes:
    """
    Build the client-ready submission ZIP bundle.
    package = the 'package' dict from build_submission_package().
    Returns ZIP bytes.

    Contents:
      01_candidate_profile.json
      02_evaluation_form.pdf
      03_readiness_certificate.pdf  (if cert exists)
      04_resume.<ext>               (if uploaded or text available)
      05_consent_proof.<ext>        (if uploaded)
      README.txt                    (manifest + verify URLs)
    """
    meta = package.get("meta", {}) or {}
    readiness = package.get("readiness", {}) or {}
    attachments = package.get("attachments", {}) or {}
    candidate_id = meta.get("candidate_id")
    application_id = _s(meta.get("application_id"), "APP-UNKNOWN")

    # Gather documents once
    docs = _fetch_documents_for_candidate(candidate_id)

    # -------- README is built AFTER we know what files landed --------
    # (populated further down, right before writing the ZIP)

    # -------- Build ZIP --------
    from datetime import datetime as _dt
    site = os.getenv("SITE_URL", "https://www.charvakit.com").rstrip("/")

    buf = io.BytesIO()
    entries_written = []  # list of (label, filename, note)
    resume_note = ""

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # 01 - JSON
        z.writestr("01_candidate_profile.json",
                   _json.dumps(package, indent=2, default=str, ensure_ascii=False))
        entries_written.append(("01_candidate_profile.json", "01_candidate_profile.json",
                                 "Full structured profile data"))

        # 02 - Evaluation PDF
        try:
            pdf_bytes = render_submission_evaluation_pdf(package)
            z.writestr("02_evaluation_form.pdf", pdf_bytes)
            entries_written.append(("02_evaluation_form.pdf", "02_evaluation_form.pdf",
                                     "Charvak branded evaluation form"))
        except Exception as e:
            err_name = "02_evaluation_form_ERROR.txt"
            z.writestr(err_name, f"Could not generate evaluation PDF: {e}")
            entries_written.append((err_name, err_name, "generation failed"))

        # 03 - Readiness certificate PDF (if present)
        cert_id = readiness.get("certificate_id")
        if cert_id:
            try:
                from pdf_engine import render_readiness_certificate_pdf
                cert_pdf = render_readiness_certificate_pdf({
                    "certificate_id": cert_id,
                    "email": _s(package.get("contact", {}).get("primary_email"), ""),
                    "display_name": _s(package.get("personal", {}).get("full_name"), ""),
                    "role": _s(meta.get("role_title"), ""),
                    "readiness_score": readiness.get("readiness_score"),
                    "verdict": readiness.get("verdict"),
                    "certificate_hash": readiness.get("certificate_hash"),
                    "percentile": readiness.get("percentile"),
                    "benchmark_score": readiness.get("benchmark_score"),
                })
                z.writestr("03_readiness_certificate.pdf", cert_pdf)
                entries_written.append(("03_readiness_certificate.pdf", "03_readiness_certificate.pdf",
                                         f"Score {readiness.get('readiness_score')}/100  -  verify: {site}/readiness/{cert_id}"))
            except Exception as e:
                err_name = "03_readiness_certificate_ERROR.txt"
                z.writestr(err_name, f"Could not generate certificate PDF: {e}")
                entries_written.append((err_name, err_name, "generation failed"))

        # 04 - Resume (prefer uploaded doc, fall back to resume_text)
        resume_written = False
        for d in docs:
            if d.get("document_type") == "resume":
                fname, content = _decode_document(d)
                if content:
                    entry = "04_resume_" + _safe_zip_entry(fname, "resume.bin")
                    z.writestr(entry, content)
                    entries_written.append((entry, entry, "candidate-uploaded resume"))
                    resume_written = True
                    break

        if not resume_written:
            # Try resume_text from profile
            try:
                resume_text = ""
                if candidate_id:
                    from database import db
                    conn = db.get_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT resume_text FROM charvak_candidates WHERE candidate_id = %s",
                                (candidate_id,))
                    row = cur.fetchone()
                    cur.close(); conn.close()
                    if row and row[0]:
                        resume_text = row[0]
                if resume_text.strip():
                    z.writestr("04_resume_profile.txt", resume_text)
                    entries_written.append(("04_resume_profile.txt", "04_resume_profile.txt",
                                             "text resume from profile (no file uploaded)"))
                else:
                    resume_note = "No resume file or resume text available"
            except Exception as e:
                resume_note = f"Resume fallback failed: {e}"

        # 05 - Consent proof (if document id given AND the file can be decoded)
        consent_doc_id = attachments.get("consent_proof_doc_id") or ""
        consent_written = False
        if consent_doc_id:
            consent_doc = next((d for d in docs if d.get("document_id") == consent_doc_id), None)
            if consent_doc:
                fname, content = _decode_document(consent_doc)
                if content:
                    entry = "05_consent_proof_" + _safe_zip_entry(fname, "consent.bin")
                    z.writestr(entry, content)
                    entries_written.append((entry, entry, "uploaded consent proof"))
                    consent_written = True

        # -------- Now build README (last, so it reflects what landed) --------
        rlines = [
            "Charvak IT Consulting - Candidate Submission Package",
            "=" * 55,
            "",
            f"Application ID:   {application_id}",
            f"Role:             {_s(meta.get('role_title'), 'N/A')}",
            f"Client:           {_s(meta.get('client_name'), 'N/A')}",
            f"Priority:         {_s(meta.get('role_priority'), 'normal')}",
            f"Candidate:        {_s(package.get('personal', {}).get('full_name'), 'N/A')}",
            f"Generated:        {_dt.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"This ZIP contains {len(entries_written)} file(s):",
            "",
        ]
        for _, fname, note in entries_written:
            rlines.append(f"  {fname}")
            if note:
                rlines.append(f"      {note}")
        if resume_note:
            rlines.append("")
            rlines.append(f"  NOTE: {resume_note}")

        # Consent status (informational)
        rlines.append("")
        if consent_written:
            rlines.append(f"Consent: recorded and included ({_s(attachments.get('consent_id'), '')})")
        elif attachments.get("consent_recorded"):
            rlines.append(f"Consent: recorded in system ({_s(attachments.get('consent_id'), '')})")
            rlines.append("         (No signed proof file was uploaded separately.)")
        else:
            rlines.append("Consent: NOT RECORDED")

        rlines += [
            "",
            "How to use:",
            "  1. Open 01_candidate_profile.json for the raw data",
            "  2. Open 02_evaluation_form.pdf for the formatted summary",
            "  3. Share the package with the client via the agreed channel",
            "",
            "Confidential - do not share outside of Charvak IT Consulting.",
        ]
        readme = "\n".join(rlines)

        z.writestr("README.txt", readme)

    buf.seek(0)
    return buf.read()


def submission_zip_filename(package: dict) -> str:
    """Sensible filename for the ZIP."""
    meta = package.get("meta", {}) or {}
    personal = package.get("personal", {}) or {}
    role = _safe_fname(meta.get("role_title", "role"))
    name = _safe_fname(personal.get("full_name") or personal.get("first_name") or "candidate")
    app_id = _safe_fname(meta.get("application_id", "app"))
    return f"Charvak_Submission_{name}_{role}_{app_id}.zip"

