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
# Session 43-D (A2.1): QR code helper for PDFs
# ============================================================
def _generate_qr_png(text: str, box_size: int = 6, border: int = 2) -> bytes:
    """
    Generate a QR code as PNG bytes.
    Used to embed a scan-to-verify QR on certificates.

    Requires the `qrcode[pil]` package (installed via requirements.txt).
    Silent-fail on any error — returns b"" if the QR cannot be generated.
    """
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as _e:
        try:
            import logging
            logging.getLogger("charvakit.pdf").warning(f"QR generation failed: {_e}")
        except Exception:
            pass
        return b""



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

    def mc_full_width(self, h, text, *args, **kwargs):
        """multi_cell(0, h, text) with X reset to the left margin first.
        Prevents the 'Not enough horizontal space' crash when previous
        multi_cell calls left X near the right edge."""
        self.set_x(self.l_margin)
        return self.multi_cell(0, h, text, *args, **kwargs)

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


def render_readiness_certificate_pdf(cert: Dict, report_type: str = "readiness") -> bytes:
    """
    Render a Role Readiness Certificate as a branded, framed PDF.
    cert = certificate dict from /api/readiness/{id}.
    """
    # Session 69: report_type-based branding
    if report_type == "career_certification":
        _branding_title_line = "Verified Career Assessment  ·  Independently Benchmarked"
        _branding_cert_line = "Certificate of Expertise"
        _branding_demonstrate = "has demonstrated proven expertise in"
        _branding_report_title = "Career Assessment Certification"
    else:
        _branding_title_line = "Verified Role Readiness  ·  Independently Benchmarked"
        _branding_cert_line = "Certificate of Readiness"
        _branding_demonstrate = "has demonstrated readiness for the role of"
        _branding_report_title = "Role Readiness Certificate"

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
        report_title=_branding_report_title,
        user_email=cert.get("email"),
    )
    # Single-page certificate — disable auto page break entirely so
    # nothing spills to a second page.
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    # --- Watermark (Session 43-D A2.2, v3) ---
    # Subtle diagonal 'CHARVAK' behind all content. Much lighter color
    # and smaller font so it acts as a genuine background watermark,
    # not a foreground element.
    try:
        _wm_text = "CHARVAK"
        # Very light teal — barely visible on white, but a photocopy
        # would still show it. (250, 253, 252) = ~2% tint.
        _wm_color = (228, 245, 240)
        pdf.set_text_color(*_wm_color)
        pdf.set_font("DejaVu", "B", 55)
        # Anchor at the center of the A4 page.
        # FPDF2 rotation rotates around (x, y) — the anchor point.
        # We place the text so that its center is at the page center.
        with pdf.rotation(30, x=105, y=148):
            _wm_w = pdf.get_string_width(_wm_text)
            _wm_h = 20  # line height
            # set_xy sets the top-left of the cell in un-rotated coords
            pdf.set_xy(105 - _wm_w / 2, 148 - _wm_h / 2)
            pdf.cell(_wm_w, _wm_h, _wm_text, align="C")
        pdf.set_text_color(0, 0, 0)
        print("WATERMARK DRAWN OK")
    except Exception as _e:
        import traceback
        print(f"WATERMARK FAILED: {_e}")
        traceback.print_exc()

    # --- End watermark ---
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

    # --- Logo / wordmark (centered top) ---
    # If a high-res logo-wordmark.png exists (>=700px wide), use it
    # as an image. Otherwise render the wordmark as crisp vector text
    # using the brand teal. This keeps the certificate sharp
    # regardless of the source image resolution.
    _wordmark_drawn = False
    try:
        _wm = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                            "static", "images", "logo-wordmark.png")
        if _os.path.exists(_wm):
            try:
                from PIL import Image as _PILImage
                with _PILImage.open(_wm) as _im:
                    _w, _h = _im.size
                if _w >= 700:
                    _draw_w = 55.0
                    _draw_h = _draw_w * (_h / float(_w))
                    pdf.image(_wm, x=W / 2 - _draw_w / 2, y=14,
                              w=_draw_w, h=_draw_h)
                    _wordmark_drawn = True
            except Exception:
                pass
    except Exception:
        pass

    if not _wordmark_drawn:
        # Vector-text wordmark fallback
        pdf.set_xy(0, 14)
        pdf.set_font("DejaVu", "B", size=26)
        pdf.set_text_color(*TEAL)
        pdf.cell(W, 12, "Charvak", align="C")
        pdf.set_xy(0, 26)
        pdf.set_font("DejaVu", "B", size=9)
        pdf.set_text_color(*INK)
        pdf.cell(W, 5, "I T   C O N S U L T I N G", align="C")

    # --- Tagline (replaces the old duplicate-wordmark eyebrow) ---
    pdf.set_xy(0, 52)
    pdf.set_font("DejaVu", "I", size=10)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 5, _branding_title_line, align="C")

    # --- Title ---
    pdf.set_xy(0, 62)
    pdf.set_font("DejaVu", "B", size=30)
    pdf.set_text_color(*INK)
    pdf.cell(W, 14, _branding_cert_line, align="C")

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
    pdf.cell(W, 6, _branding_demonstrate, align="C")

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
        parts.append("Your Score: " + str(cert.get("readiness_score")))
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

    verify_path = cert.get("verify_url_path") or "/api/readiness/verify/"
    verify_url = site + verify_path + str(cert.get("certificate_hash") or "")
    pdf.set_xy(0, 240)
    pdf.set_font("DejaVu", size=7)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 4, "Verify at:  " + verify_url, align="C")

    # --- Signature block ---
    sig_y = 258
    # Signature line
    pdf.set_draw_color(*INK)
    # --- Signature block ---
    sig_y = 258
    # Optional handwritten signature image (drop a PNG in
    # static/images/signature.png and it appears automatically).
    try:
        import os as _sig_os
        sig_img = _sig_os.path.join("static", "images", "signature.png")
        if _sig_os.path.exists(sig_img):
            # Left column is 38..90 (52 wide). Right column 120..172.
            # Signature sits just above the line.
            pdf.image(sig_img, x=44, y=sig_y - 14, w=40)
    except Exception:
        pass

    # Signature line
    pdf.set_draw_color(*INK)
    pdf.set_line_width(0.4)
    pdf.line(38, sig_y, 90, sig_y)
    pdf.line(120, sig_y, 172, sig_y)

    # Labels under the line
    pdf.set_font("DejaVu", size=8)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(38, sig_y + 2)
    pdf.cell(52, 4, "Authorized Signatory", align="C")
    pdf.set_xy(120, sig_y + 2)
    pdf.cell(52, 4, "Date of Issue", align="C")

    # Signatory name + title (bold, in ink), and the issue date.
    pdf.set_xy(38, sig_y + 6)
    pdf.set_font("DejaVu", "B", size=9)
    pdf.set_text_color(*INK)
    pdf.cell(52, 4, "Bhavya M", align="C")
    pdf.set_xy(120, sig_y + 6)
    pdf.set_font("DejaVu", size=9)
    pdf.set_text_color(*INK)
    pdf.cell(52, 4, issued or "", align="C")

    # Signatory title (small, muted) below the name, on the left only.
    pdf.set_xy(38, sig_y + 10)
    pdf.set_font("DejaVu", "I", size=8)
    pdf.set_text_color(*MUTED)
    pdf.cell(52, 4, "Founder & CEO, Charvak IT Consulting", align="C")

    # --- Footer strip ---
    pdf.set_xy(0, 275)
    pdf.set_font("DejaVu", size=7)
    pdf.set_text_color(*MUTED)
    pdf.cell(W, 4, "This certificate can be independently verified at the URL above.",
             align="C")

    # --- QR code (Session 43-D A2.1) ---
    # Embed a scan-to-verify QR pointing at the public verify URL.
    # Silent-fail: if QR generation fails, the certificate still renders.
    try:
        _hash = cert.get("certificate_hash") or ""
        if _hash:
            _verify_url = f"{site}/api/readiness/verify/{_hash}"
            _qr_bytes = _generate_qr_png(_verify_url, box_size=5, border=1)
            if _qr_bytes:
                from io import BytesIO as _BytesIO
                _qr_w = 28.0  # mm
                _qr_h = 28.0
                # Place bottom-right, above the footer strip
                pdf.image(_BytesIO(_qr_bytes),
                          x=W - 22 - _qr_w, y=H - 52 - _qr_h,
                          w=_qr_w, h=_qr_h)
                # Small caption under the QR
                pdf.set_xy(W - 22 - _qr_w - 4, H - 52 + 2)
                pdf.set_font("DejaVu", size=7)
                pdf.set_text_color(*MUTED)
                pdf.cell(_qr_w + 8, 4, "Scan to verify", align="C")
    except Exception as _e:
        try:
            import logging
            logging.getLogger("charvakit.pdf").warning(f"QR embed failed: {_e}")
        except Exception:
            pass

    return bytes(pdf.output())

# ============================================================
# Session 43-A1.7: IELTS Deep Report PDF
# ============================================================

def render_ielts_deep_report_pdf(report: Dict, meta: Dict) -> bytes:
    """
    Render the IELTS deep-report as a branded PDF.

    report: the AI-generated JSON (from ielts_deep_report_engine.generate_report)
    meta:   {report_id, test_type, email, band (optional)}

    Returns bytes of the PDF.
    """
    pdf = CharvakReportPDF(
        report_title="Charvak IELTS Deep Report",
        user_email=meta.get("email"),
    )

    # ---- Cover page ----
    pdf.add_page()

    # Header band
    pdf.set_fill_color(59, 165, 145)   # Charvak green
    pdf.rect(0, 0, 210, 40, style="F")

    pdf.set_y(14)
    pdf.set_font("DejaVu", "B", 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Charvak IELTS Deep Report", ln=True, align="C")

    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 6, "Examiner-grade diagnostic - not affiliated with IELTS", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)

    pdf.set_y(50)

    # Meta box
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 8, "Report details", ln=True)

    pdf.set_font("DejaVu", "", 10)
    test_type = str(meta.get("test_type", "")).capitalize()
    report_id = str(meta.get("report_id", ""))
    email = str(meta.get("email", ""))
    band = meta.get("band") or report.get("band")

    pdf.cell(0, 6, f"Test type: IELTS {test_type}", ln=True)
    pdf.cell(0, 6, f"Report ID: {report_id}", ln=True)
    if band is not None:
        pdf.set_font("DejaVu", "B", 13)
        pdf.cell(0, 8, f"Overall Band: {band}", ln=True)
    pdf.set_font("DejaVu", "", 10)

    pdf.ln(4)

    # Summary
    if report.get("summary"):
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 7, "Summary", ln=True)
        pdf.set_font("DejaVu", "", 10)
        pdf.mc_full_width(5, str(report["summary"]))
        pdf.ln(3)

    # Sub-band reasoning
    sub = report.get("sub_band_reasoning") or {}
    if sub:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Sub-band reasoning", ln=True)
        pdf.ln(2)
        for key, val in sub.items():
            pdf.set_font("DejaVu", "B", 11)
            pdf.cell(0, 6, key.replace("_", " ").title(), ln=True)
            pdf.set_font("DejaVu", "", 10)
            pdf.mc_full_width(5, str(val))
            pdf.ln(2)

    # Grammar corrections
    gc = report.get("grammar_corrections") or []
    if gc:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Grammar corrections", ln=True)
        pdf.ln(2)
        for i, item in enumerate(gc, 1):
            pdf.set_font("DejaVu", "B", 10)
            pdf.mc_full_width(5, f"{i}. Original: {item.get('original', '')}")
            pdf.set_font("DejaVu", "", 10)
            pdf.mc_full_width(5, f"   Corrected: {item.get('corrected', '')}")
            pdf.mc_full_width(5, f"   Rule: {item.get('rule', '')}")
            pdf.mc_full_width(5, f"   Why: {item.get('explanation', '')}")
            pdf.ln(2)

    # Vocabulary upgrades
    vu = report.get("vocabulary_upgrades") or []
    if vu:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Vocabulary upgrades", ln=True)
        pdf.ln(2)
        for i, item in enumerate(vu, 1):
            pdf.set_font("DejaVu", "B", 10)
            pdf.mc_full_width(5, f"{i}. Original: {item.get('original', '')}")
            pdf.set_font("DejaVu", "", 10)
            better = item.get("better") or []
            if isinstance(better, list):
                better_str = ", ".join(str(b) for b in better)
            else:
                better_str = str(better)
            pdf.mc_full_width(5, f"   Better: {better_str}")
            if item.get("context"):
                pdf.mc_full_width(5, f"   When: {item.get('context')}")
            pdf.ln(2)

    # Example high-band rewrite (writing) OR example answer (speaking)
    rewrite = report.get("example_high_band_rewrite") or {}
    if rewrite:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Example high-band rewrite", ln=True)
        pdf.ln(2)
        for i, key in enumerate(["paragraph_1", "paragraph_2"]):
            if rewrite.get(key):
                pdf.set_font("DejaVu", "B", 11)
                pdf.cell(0, 6, f"Paragraph {i+1}", ln=True)
                pdf.set_font("DejaVu", "", 10)
                pdf.mc_full_width(5, str(rewrite[key]))
                pdf.ln(3)

    example_answer = report.get("example_high_band_answer") or {}
    if example_answer:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Example high-band answer", ln=True)
        pdf.ln(2)
        if example_answer.get("question"):
            pdf.set_font("DejaVu", "B", 10)
            pdf.mc_full_width(5, f"Question: {example_answer['question']}")
        pdf.set_font("DejaVu", "", 10)
        if example_answer.get("band_8_answer"):
            pdf.mc_full_width(5, str(example_answer["band_8_answer"]))

    # Response by response (speaking)
    rbr = report.get("response_by_response") or []
    if rbr:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Response-by-response review", ln=True)
        pdf.ln(2)
        for i, item in enumerate(rbr, 1):
            pdf.set_font("DejaVu", "B", 10)
            pdf.mc_full_width(5, f"Part {item.get('part', '?')}: {item.get('question', '')[:80]}")
            pdf.set_font("DejaVu", "", 10)
            if item.get("strength"):
                pdf.mc_full_width(5, f"   + Strength: {item['strength']}")
            if item.get("improvement"):
                pdf.mc_full_width(5, f"   - Improve: {item['improvement']}")
            pdf.ln(2)

    # Pronunciation notes (speaking)
    pn = report.get("pronunciation_notes") or []
    if pn:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Pronunciation notes", ln=True)
        pdf.ln(2)
        for item in pn:
            pdf.set_font("DejaVu", "B", 10)
            pdf.mc_full_width(5, f"Sounds: {item.get('sounds', '')}")
            pdf.set_font("DejaVu", "", 10)
            pdf.mc_full_width(5, f"   Tip: {item.get('tip', '')}")
            pdf.ln(2)

    # Common pitfalls
    cp = report.get("common_pitfalls") or []
    if cp:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Common pitfalls in this attempt", ln=True)
        pdf.ln(2)
        pdf.set_font("DejaVu", "", 10)
        for item in cp:
            pdf.mc_full_width(5, f"- {item}")

    # Exercises
    ex = report.get("exercises") or []
    if ex:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, "Recommended exercises", ln=True)
        pdf.ln(2)
        for i, item in enumerate(ex, 1):
            pdf.set_font("DejaVu", "B", 10)
            pdf.mc_full_width(5, f"{i}. {item.get('topic', '')}")
            pdf.set_font("DejaVu", "", 10)
            pdf.mc_full_width(5, f"   Task: {item.get('task', '')}")
            if item.get("rationale"):
                pdf.mc_full_width(5, f"   Why: {item.get('rationale')}")
            pdf.ln(2)

    # Footer
    pdf.ln(6)
    pdf.set_font("DejaVu", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Issued by Charvak IT Consulting Pvt Ltd - charvakit.com", ln=True, align="C")
    pdf.cell(0, 6, "This report is generated by AI for study guidance and is not affiliated with IELTS or its governing bodies.", ln=True, align="C")

    return bytes(pdf.output())
