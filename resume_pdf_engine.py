"""
Resume PDF Engine — Session 4 Feature 6
Generates a professional candidate resume PDF from profile data.
"""

import os
import json
from fpdf import FPDF

# Color scheme
NAVY = (26, 34, 72)
TEAL = (59, 165, 145)
GRAY = (100, 100, 100)


class ResumePDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, "Prepared by Ashok M - ashokcquent@gmail.com - 847-262-4000", align="C")


def _safe_multi_cell(pdf, height, text):
    """Render a multi_cell that always starts at the left margin."""
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin, height, text, new_x="LMARGIN", new_y="NEXT")


def _safe_cell(pdf, w, h, text, **kwargs):
    """Render a cell that starts at the current x and wraps to next line."""
    pdf.cell(w, h, text, new_x="LMARGIN", new_y="NEXT", **kwargs)


def _section_heading(pdf, text):
    """Draw a section heading with teal underline."""
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*NAVY)
    _safe_cell(pdf, 0, 8, text)

    # Underline
    y = pdf.get_y()
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(2)


def generate_candidate_resume_pdf(candidate: dict) -> bytes:
    print(f"[DEBUG] candidate keys: {list(candidate.keys())}")
    print(f"[DEBUG] skills raw: {candidate.get('skills')!r}")
    pdf = ResumePDF(format="Letter")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ---- Header ----
    name = candidate.get("name", "Candidate")
    phone = candidate.get("phone") or ""
    location = candidate.get("location") or ""

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*NAVY)
    _safe_cell(pdf, 0, 10, name)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GRAY)
    contact_parts = []
    if location:
        contact_parts.append(location)
    contact_parts.append("ashokcquent@gmail.com")
    if phone:
        contact_parts.append(phone)
    _safe_cell(pdf, 0, 6, " · ".join(contact_parts))

    # Divider
    y = pdf.get_y() + 2
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.8)
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(6)

    # ---- Professional Summary ----
    work_auth = candidate.get("work_auth_status") or "N/A"
    experience = candidate.get("experience_years") or 0
    availability = candidate.get("availability") or "Immediate"
    rate_min = candidate.get("rate_min")
    rate_max = candidate.get("rate_max")

    _section_heading(pdf, "PROFESSIONAL SUMMARY")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    _safe_multi_cell(pdf, 6, f"Experienced technologist with {experience}+ years of hands-on industry experience.")
    _safe_multi_cell(pdf, 6, f"Authorized to work in the US under {work_auth} status.")
    _safe_multi_cell(pdf, 6, f"Available: {availability}.")
    if rate_min and rate_max:
        _safe_multi_cell(pdf, 6, f"Target rate: ${rate_min:.0f}-${rate_max:.0f}/hr.")

    # ---- Core Skills ----
    skills = candidate.get("skills") or []
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except Exception:
            skills = [s.strip() for s in skills.split(",") if s.strip()]

    if skills:
        _section_heading(pdf, "CORE SKILLS")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)

        col_width = 90
        skills_per_row = 2
        start_y = pdf.get_y()
        for i in range(0, len(skills), skills_per_row):
            chunk = skills[i:i + skills_per_row]
            row_y = start_y + (i // skills_per_row) * 5
            for j, skill in enumerate(chunk):
                skill_text = "- " + str(skill)[:45]
                col_x = pdf.l_margin + (j * col_width)
                pdf.set_xy(col_x, row_y)
                pdf.cell(col_width, 5, skill_text, border=0)
        # Move y below the last row
        num_rows = (len(skills) + skills_per_row - 1) // skills_per_row
        pdf.set_xy(pdf.l_margin, start_y + num_rows * 5)
        pdf.ln(2)

    # ---- Work Authorization ----
    _section_heading(pdf, "WORK AUTHORIZATION")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    _safe_cell(pdf, 0, 6, f"Status: {work_auth}")

    visa_expiry = candidate.get("visa_expiry")
    if visa_expiry:
        _safe_cell(pdf, 0, 6, f"Valid until: {visa_expiry}")

    _safe_cell(pdf, 0, 6, f"Availability: {availability}")

    # ---- Compensation ----
    _section_heading(pdf, "COMPENSATION")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    if rate_min and rate_max:
        _safe_cell(pdf, 0, 6, f"Target rate: ${rate_min:.0f}-${rate_max:.0f}/hr")
    else:
        _safe_cell(pdf, 0, 6, "Rate: Negotiable")

    # ---- Footer Notes ----
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*GRAY)
    _safe_multi_cell(
        pdf, 5,
        "Full profile, references, and detailed work history available on request. "
        "Candidate can start immediately upon offer acceptance."
    )

    return bytes(pdf.output())


if __name__ == "__main__":
    test = {
        "name": "PREM CHARAN",
        "phone": "8472624000",
        "location": "Arlington Heights, IL",
        "work_auth_status": "H1B",
        "experience_years": 10,
        "availability": "immediate",
        "rate_min": 75,
        "rate_max": 90,
        "skills": ["Kubernetes", "AWS", "Docker", "Terraform", "Python", "CI/CD",
                   "Azure", "GCP", "EKS", "AKS", "OpenShift", "Helm", "Istio",
                   "Jenkins", "GitHub Actions", "Argo CD"],
    }
    pdf_bytes = generate_candidate_resume_pdf(test)
    with open("test_resume.pdf", "wb") as f:
        f.write(pdf_bytes)
    print(f"PDF generated: {len(pdf_bytes)} bytes → test_resume.pdf")
