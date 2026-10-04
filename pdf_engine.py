"""
Charvak PDF Engine
Session 16 - Premium Report PDF generation via fpdf2 + DejaVu Sans.
"""
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from fpdf import FPDF


# ============================================================
# Font paths (shipped with the repo)
# ============================================================
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "fonts")
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_ITALIC = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")
FONT_BOLD_ITALIC = os.path.join(FONT_DIR, "DejaVuSans-BoldOblique.ttf")


# ============================================================
# Brand colors (RGB)
# ============================================================
COLOR_PRIMARY = (13, 110, 253)      # Bootstrap blue
COLOR_DARK = (33, 37, 41)
COLOR_MUTED = (108, 117, 125)
COLOR_SUCCESS = (25, 135, 84)
COLOR_WARNING = (255, 193, 7)
COLOR_DANGER = (220, 53, 69)
COLOR_LIGHT_BG = (248, 249, 250)
COLOR_WHITE = (255, 255, 255)


# ============================================================
# PDF class
# ============================================================
class CharvakReportPDF(FPDF):
    """Charvak-branded PDF with header, footer, and section helpers."""

    def __init__(self, report_title: str = "Charvak Premium Report",
                 user_email: Optional[str] = None):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.report_title = report_title
        self.user_email = user_email
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(20, 20, 20)

        # Register DejaVu fonts
        self.add_font("DejaVu", "", FONT_REGULAR)
        self.add_font("DejaVu", "B", FONT_BOLD)
        self.add_font("DejaVu", "I", FONT_ITALIC)
        self.add_font("DejaVu", "BI", FONT_BOLD_ITALIC)

        # Default font
        self.set_font("DejaVu", size=11)

    def _ensure_space(self, needed_height: float = 20):
        """
        Ensure `needed_height` mm of space remains on the current page.
        If not, add a new page. Uses fpdf2's own will_page_break check.
        """
        try:
            # fpdf2 has will_page_break(h) since 2.7.6
            if self.will_page_break(needed_height):
                self.add_page()
        except AttributeError:
            # Fallback for older versions
            if self.get_y() + needed_height > self.h - self.b_margin:
                self.add_page()

    # ---------- Page chrome ----------
    def header(self):
        """Brand bar on every page except the cover."""
        if self.page_no() == 1:
            return  # Skip on cover page
        self.set_font("DejaVu", "B", size=9)
        self.set_text_color(*COLOR_MUTED)
        self.cell(0, 6, self.report_title, new_x="LMARGIN", new_y="NEXT", align="R")
        self.set_draw_color(*COLOR_MUTED)
        self.set_line_width(0.2)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)

    def footer(self):
        """Page number + generated-for line."""
        self.set_y(-18)
        self.set_font("DejaVu", size=8)
        self.set_text_color(*COLOR_MUTED)
        if self.user_email:
            self.cell(0, 5, "Generated for " + self.user_email, align="L")
        self.set_x(-40)
        self.cell(20, 5, "Page " + str(self.page_no()), align="R")

    # ---------- Cover page ----------
    def cover_page(self, subtitle: str, generated_at: str, report_id: str):
        """Cover page with brand banner."""
        self.add_page()

        # Blue banner across top
        self.set_fill_color(*COLOR_PRIMARY)
        self.rect(0, 0, 210, 60, style="F")

        # Brand
        self.set_y(15)
        self.set_font("DejaVu", "B", size=14)
        self.set_text_color(*COLOR_WHITE)
        self.cell(0, 8, "CHARVAK IT CONSULTING", align="C", new_x="LMARGIN", new_y="NEXT")

        # Report title
        self.set_font("DejaVu", "B", size=24)
        self.cell(0, 14, self.report_title, align="C", new_x="LMARGIN", new_y="NEXT")

        # Subtitle
        self.set_font("DejaVu", size=12)
        self.cell(0, 8, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")

        # Body
        self.set_y(80)
        self.set_text_color(*COLOR_DARK)
        self.set_font("DejaVu", size=12)

        self.cell(0, 8, "Prepared for: " + (self.user_email or "Valued Customer"),
                  new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 8, "Report ID: " + report_id, new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 8, "Generated: " + generated_at, new_x="LMARGIN", new_y="NEXT")

    # ---------- Content helpers ----------
    def section_heading(self, text: str, number: Optional[int] = None):
        """Colored section heading with accent underline."""
        self.ln(4)
        self.set_font("DejaVu", "B", size=14)
        self.set_text_color(*COLOR_PRIMARY)
        title = (str(number) + ". " + text) if number else text
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*COLOR_PRIMARY)
        self.set_line_width(0.4)
        self.line(20, self.get_y(), 80, self.get_y())
        self.ln(4)
        self.set_text_color(*COLOR_DARK)

    def sub_heading(self, text: str):
        """Bold sub-heading."""
        self._ensure_space(needed_height=20)
        self.ln(2)
        self.set_font("DejaVu", "B", size=12)
        self.set_text_color(*COLOR_DARK)
        self.set_x(self.l_margin)
        self.cell(self.w - self.l_margin - self.r_margin, 7, text,
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def paragraph(self, text: str):
        """Body text with word wrap and explicit width."""
        self.set_font("DejaVu", size=11)
        self.set_text_color(*COLOR_DARK)
        # Estimate lines: A4 width minus margins is ~170mm, size 11 fits ~95 chars
        estimated_lines = max(1, (len(text) // 95) + 1)
        needed = estimated_lines * 6 + 4
        self._ensure_space(needed_height=min(needed, 40))
        # Force X to left margin before writing
        self.set_x(self.l_margin)
        # Explicit width so the text always wraps to the right margin
        self.multi_cell(self.w - self.l_margin - self.r_margin, 6, text,
                        new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def bullet_list(self, items: List[str], bullet: str = "•"):
        """Bulleted list with page-break awareness."""
        self.set_font("DejaVu", size=11)
        self.set_text_color(*COLOR_DARK)
        content_width = self.w - self.l_margin - self.r_margin - 8
        for item in items:
            self._ensure_space(needed_height=10)
            self.set_x(self.l_margin)
            self.cell(8, 6, bullet, new_x="END", new_y="TOP")
            self.multi_cell(content_width, 6, str(item), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def key_value_row(self, label: str, value: str):
        """
        Stacked label/value. Label on top (muted, bold), value below (indented).
        Simple, always renders correctly.
        """
        label_str = str(label)
        value_str = str(value)

        # Estimate total height (label + value lines)
        value_lines = max(1, (len(value_str) // 95) + 1)
        needed = 7 + value_lines * 6 + 4
        self._ensure_space(needed_height=needed)

        # Label
        self.set_font("DejaVu", "B", size=10)
        self.set_text_color(*COLOR_MUTED)
        self.set_x(self.l_margin)
        self.cell(self.w - self.l_margin - self.r_margin, 7, label_str,
                  new_x="LMARGIN", new_y="NEXT")

        # Value (indented)
        self.set_font("DejaVu", size=11)
        self.set_text_color(*COLOR_DARK)
        self.set_x(self.l_margin + 4)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 4, 6,
                        value_str, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def severity_badge(self, label: str, severity: str):
        """Colored inline badge."""
        color_map = {
            "high": COLOR_DANGER,
            "critical": COLOR_DANGER,
            "medium": COLOR_WARNING,
            "warning": COLOR_WARNING,
            "low": COLOR_SUCCESS,
            "info": COLOR_PRIMARY,
        }
        color = color_map.get(severity.lower(), COLOR_MUTED)
        self.set_fill_color(*color)
        self.set_text_color(*COLOR_WHITE)
        self.set_font("DejaVu", "B", size=9)
        self.cell(len(label) * 2.5 + 4, 6, " " + label + " ", fill=True)
        self.set_text_color(*COLOR_DARK)

    def divider(self):
        """Thin horizontal rule."""
        self.set_draw_color(*COLOR_MUTED)
        self.set_line_width(0.2)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)


# ============================================================
# Public API
# ============================================================
def render_premium_report_pdf(report_data: Dict) -> bytes:
    """
    Build a complete Premium Report PDF from a report_data dict.
    Returns PDF bytes for StreamingResponse.

    Expected report_data keys:
        report_title, subtitle, user_email, report_id, generated_at,
        executive_summary, full_report_sections (list of {heading, content}),
        deep_analysis (list of {heading, paragraph}),
        action_roadmap (list of {priority, action, eta}),
        benchmarks (list of {metric, your_value, industry_avg}),
        custom_recommendations (list of {title, body})
    """
    pdf = CharvakReportPDF(
        report_title=report_data.get("report_title", "Premium Report"),
        user_email=report_data.get("user_email"),
    )

    # Cover page
    pdf.cover_page(
        subtitle=report_data.get("subtitle", "Detailed Analysis & Action Plan"),
        generated_at=report_data.get("generated_at",
                                     datetime.now().strftime("%B %d, %Y")),
        report_id=report_data.get("report_id", "N/A"),
    )

    # 1. Executive summary
    pdf.add_page()
    pdf.section_heading("Executive Summary", number=1)
    pdf.paragraph(report_data.get("executive_summary", "No summary available."))

    # 2. Full report
    pdf.section_heading("Full Report", number=2)
    for section in report_data.get("full_report_sections", []):
        pdf.sub_heading(section.get("heading", ""))
        pdf.paragraph(section.get("content", ""))

    # 3. Deep analysis
    # Accept either "paragraph" or "content" as the key name.
    pdf.section_heading("Deeper Analysis", number=3)
    for item in report_data.get("deep_analysis", []):
        pdf.sub_heading(item.get("heading", ""))
        text = item.get("paragraph") or item.get("content") or ""
        pdf.paragraph(text)

    # 4. Action roadmap
    pdf.section_heading("Action Roadmap", number=4)
    roadmap = report_data.get("action_roadmap", [])
    if roadmap:
        for step in roadmap:
            priority = step.get("priority", "info")
            action = step.get("action", "")
            eta = step.get("eta", "")
            pdf.severity_badge(priority.upper(), priority)
            pdf.set_font("DejaVu", size=10)
            pdf.set_text_color(*COLOR_DARK)
            pdf.cell(0, 6, " " + action, new_x="LMARGIN", new_y="NEXT")
            if eta:
                pdf.set_font("DejaVu", "I", size=9)
                pdf.set_text_color(*COLOR_MUTED)
                pdf.cell(0, 5, "  ETA: " + eta, new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(*COLOR_DARK)
            pdf.ln(1)

    # 5. Benchmarks
    pdf.section_heading("Industry Benchmarks", number=5)
    for bm in report_data.get("benchmarks", []):
        metric = bm.get("metric", "")
        your_value = bm.get("your_value", "")
        industry_avg = bm.get("industry_avg", "")
        if industry_avg:
            combined = str(your_value) + "  (industry average: " + str(industry_avg) + ")"
        else:
            combined = str(your_value)
        pdf.key_value_row(metric, combined)

    # 6. Custom recommendations
    pdf.section_heading("Custom Recommendations", number=6)
    for rec in report_data.get("custom_recommendations", []):
        pdf.sub_heading(rec.get("title", ""))
        pdf.paragraph(rec.get("body", ""))

    # Return bytes
    return bytes(pdf.output())


def render_simple_pdf(title: str, body_lines: List[str],
                      user_email: Optional[str] = None) -> bytes:
    """Simpler PDF renderer for receipts / non-report uses."""
    pdf = CharvakReportPDF(report_title=title, user_email=user_email)
    pdf.cover_page(
        subtitle="",
        generated_at=datetime.now().strftime("%B %d, %Y"),
        report_id="N/A",
    )
    pdf.add_page()
    pdf.set_font("DejaVu", size=11)
    for line in body_lines:
        pdf.multi_cell(0, 6, str(line))
    return bytes(pdf.output())


def render_readiness_certificate_pdf(cert: Dict) -> bytes:
    """
    Render a Role Readiness Certificate as a branded, framed PDF.
    cert = certificate dict from /api/readiness/{id}.
    """
    import os as _os
    site = _os.getenv("SITE_URL", "https://www.charvakit.com").rstrip("/")

    # Brand colors (teal, matching the site)
    TEAL = (59, 165, 145)
    TEAL_DARK = (42, 128, 112)
    INK = (17, 24, 39)
    MUTED = (107, 114, 128)
    SOFT = (229, 231, 235)
    WHITE = (255, 255, 255)
    TEAL_LIGHT = (240, 253, 249)

    pdf = CharvakReportPDF(
        report_title="Role Readiness Certificate",
        user_email=cert.get("email"),
    )
    # Single-page certificate — disable auto page break entirely so
    # nothing spills to a second page.
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    # Suppress the base-class header/footer chrome (this certificate has
    # its own frame and footer strip).
    pdf.header = lambda: None
    pdf.footer = lambda: None

    W = 210.0  # A4 width
    H = 297.0

    # --- Double frame ---
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(1.5)
    pdf.rect(10, 10, W - 20, H - 20, style="D")
    pdf.set_line_width(0.4)
    pdf.rect(14, 14, W - 28, H - 28, style="D")

    # --- Logo (centered top) ---
    logo_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                              "static", "images", "logo.png")
    if _os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=W / 2 - 12, y=22, w=24)
        except Exception:
            pass

    # --- "CERTIFICATE" eyebrow ---
    pdf.set_xy(0, 52)
    pdf.set_font("DejaVu", "B", size=10)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 5, "C H A R V A K  I T  C O N S U L T I N G", align="C")

    # --- Title ---
    pdf.set_xy(0, 62)
    pdf.set_font("DejaVu", "B", size=30)
    pdf.set_text_color(*INK)
    pdf.cell(W, 14, "Certificate of Readiness", align="C")

    # --- Ornamental divider (short teal line centered) ---
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.8)
    pdf.line(90, 82, 120, 82)
    # decorative dots
    pdf.set_fill_color(*TEAL)
    pdf.circle(88, 82, 0.7, style="F")
    pdf.circle(122, 82, 0.7, style="F")

    # --- "This certifies that" ---
    pdf.set_xy(0, 92)
    pdf.set_font("DejaVu", size=11)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 6, "This certifies that", align="C")

    # --- Candidate name ---
    name = str(cert.get("candidate_display") or "Verified Candidate")
    pdf.set_xy(0, 102)
    pdf.set_font("DejaVu", "B", size=26)
    pdf.set_text_color(*TEAL)
    pdf.cell(W, 12, name, align="C")

    # Underline under the name
    name_w = pdf.get_string_width(name) + 8
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.5)
    pdf.line((W - name_w) / 2, 116, (W + name_w) / 2, 116)

    # --- "has demonstrated readiness for" ---
    pdf.set_xy(0, 124)
    pdf.set_font("DejaVu", size=11)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 6, "has demonstrated readiness for the role of", align="C")

    # --- Role ---
    role = str(cert.get("role") or "")
    pdf.set_xy(0, 132)
    pdf.set_font("DejaVu", "B", size=16)
    pdf.set_text_color(*INK)
    pdf.cell(W, 9, role, align="C")

    # --- Industry · Level ---
    industry = str(cert.get("industry") or "")
    level = str(cert.get("level") or "").capitalize()
    pdf.set_xy(0, 142)
    pdf.set_font("DejaVu", size=10)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 5, industry + "  |  " + level, align="C")

    # --- Score badge (rounded teal box, centered) ---
    badge_w = 70
    badge_h = 26
    bx = (W - badge_w) / 2
    by = 158
    pdf.set_fill_color(*TEAL)
    pdf.set_draw_color(*TEAL)
    # fpdf2 supports rounded rect via rect(style='DF', round_corners=True)
    try:
        pdf.rect(bx, by, badge_w, badge_h, style="F", round_corners=True, corner_radius=4)
    except TypeError:
        pdf.rect(bx, by, badge_w, badge_h, style="F")

    score_val = cert.get("readiness_score")
    score_str = str(score_val) if score_val is not None else "--"
    pdf.set_xy(bx, by + 2)
    pdf.set_font("DejaVu", "B", size=24)
    pdf.set_text_color(*WHITE)
    pdf.cell(badge_w, 12, score_str, align="C")
    pdf.set_xy(bx, by + 15)
    pdf.set_font("DejaVu", size=9)
    pdf.cell(badge_w, 5, "out of 100", align="C")

    # --- Verdict + benchmark line ---
    pdf.set_xy(0, by + badge_h + 4)
    pdf.set_font("DejaVu", size=10)
    pdf.set_text_color(*INK)
    pdf.cell(W, 6, str(cert.get("verdict") or ""), align="C")

    # --- Secondary metrics row ---
    pdf.set_xy(0, by + badge_h + 12)
    pdf.set_font("DejaVu", size=9)
    pdf.set_text_color(*MUTED)
    bm = cert.get("benchmark_score")
    pct = cert.get("percentile")
    parts = []
    if bm is not None:
        parts.append("Benchmark: " + str(bm))
    if pct is not None:
        parts.append("Percentile: " + str(pct))
    if parts:
        pdf.cell(W, 5, "   |   ".join(parts), align="C")

    # --- Verification divider ---
    pdf.set_draw_color(*SOFT)
    pdf.set_line_width(0.3)
    pdf.line(30, 218, 180, 218)

    # --- Verification block ---
    pdf.set_xy(0, 222)
    pdf.set_font("DejaVu", "B", size=9)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 5, "VERIFICATION", align="C")
    pdf.set_xy(0, 228)
    pdf.set_font("DejaVu", size=9)
    pdf.set_text_color(*INK)
    cert_id = str(cert.get("certificate_id") or "")
    pdf.cell(W, 5, "Certificate ID:  " + cert_id, align="C")

    issued = ""
    try:
        ca = cert.get("created_at")
        if ca:
            from datetime import datetime as _dt
            issued = _dt.fromisoformat(ca.replace("Z", "+00:00")).strftime("%B %d, %Y")
    except Exception:
        issued = str(cert.get("created_at") or "")

    pdf.set_xy(0, 234)
    pdf.cell(W, 5, "Issued:  " + (issued or "N/A"), align="C")

    verify_url = site + "/api/readiness/verify/" + str(cert.get("certificate_hash") or "")
    pdf.set_xy(0, 240)
    pdf.set_font("DejaVu", size=7)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 4, "Verify at:  " + verify_url, align="C")

    # --- Signature block ---
    sig_y = 258
    # Signature line
    pdf.set_draw_color(*INK)
    pdf.set_line_width(0.4)
    pdf.line(38, sig_y, 90, sig_y)
    pdf.line(120, sig_y, 172, sig_y)

    pdf.set_xy(0, sig_y + 2)
    pdf.set_font("DejaVu", size=8)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(38, sig_y + 2)
    pdf.cell(52, 4, "Authorized Signatory", align="C")
    pdf.set_xy(120, sig_y + 2)
    pdf.cell(52, 4, "Date of Issue", align="C")

    pdf.set_xy(38, sig_y + 7)
    pdf.set_font("DejaVu", "B", size=9)
    pdf.set_text_color(*TEAL_DARK)
    pdf.cell(52, 4, "Charvak IT Consulting", align="C")
    pdf.set_xy(120, sig_y + 7)
    pdf.set_font("DejaVu", size=9)
    pdf.set_text_color(*INK)
    pdf.cell(52, 4, issued or "", align="C")

    # --- Footer strip ---
    pdf.set_xy(0, 275)
    pdf.set_font("DejaVu", size=7)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 4, "This certificate can be independently verified at the URL above.",
             align="C")

    return bytes(pdf.output())



