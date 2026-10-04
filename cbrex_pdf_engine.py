"""
CBREX Evaluation Form PDF (Session 23, Patch 4a.2)

Consumes the JSON output of client_staffing_engine.build_cbrex_package()
and renders a branded A4 PDF suitable for sharing with hiring managers
or attaching to a CBREX submission.

Usage:
    from cbrex_pdf_engine import render_cbrex_evaluation_pdf
    pdf_bytes = render_cbrex_evaluation_pdf(package_dict)
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


def render_cbrex_evaluation_pdf(package: Dict) -> bytes:
    """
    Render a CBREX evaluation form PDF.
    package = the 'package' dict from build_cbrex_package().
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


def cbrex_package_filename(package: Dict) -> str:
    """Build a sensible filename for the evaluation PDF."""
    meta = package.get("meta", {}) or {}
    personal = package.get("personal", {}) or {}
    role_title = _safe_fname(meta.get("role_title", "role"))
    name = _safe_fname(personal.get("full_name") or personal.get("first_name") or "candidate")
    app_id = _safe_fname(meta.get("application_id", "app"))
    return f"Charvak_Evaluation_{name}_{role_title}_{app_id}.pdf"
