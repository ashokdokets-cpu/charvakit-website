"""
Shared PDF helpers for Charvak one-pagers.
Used by generate_employer_onepager.py and generate_institution_onepager.py.
"""
import os
import sys
from datetime import datetime

# Add parent dir to path so we can import pdf_engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_engine import CharvakReportPDF


# Emoji -> DejaVu-compatible Unicode symbol mapping
# fpdf2's DejaVu font can't render color emoji, but supports these
_ICON_MAP = {
    "🎯": "◆",
    "🔐": "●",
    "💬": "▶",
    "📊": "◆",
    "🌍": "●",
    "🔥": "▲",
    "🆓": "✓",
    "📜": "◆",
    "🏛️": "◆",
    "🏢": "◆",
    "👤": "●",
    "🎬": "▶",
    "🌏": "●",
    "📅": "◆",
    "🚀": "▲",
    "✅": "✓",
    "🛡️": "●",
    "💳": "◆",
    "💻": "◆",
    "🎫": "◆",
}


def _normalize_icon(icon):
    """Replace emoji with a DejaVu-compatible Unicode symbol."""
    return _ICON_MAP.get(icon, icon)

# Brand colors (R, G, B)
TEAL = (59, 165, 145)
TEAL_DARK = (42, 128, 112)
INK = (17, 24, 39)
MUTED = (107, 114, 128)
SOFT = (229, 231, 235)
WHITE = (255, 255, 255)
GREEN_LIGHT = (240, 253, 244)
GREEN_BORDER = (134, 239, 172)
GREEN_TEXT = (22, 101, 52)
AMBER = (245, 158, 11)

# Page dimensions
W = 210.0  # A4 width mm
H = 297.0  # A4 height mm


def draw_brand_header(pdf, title_text="EMPLOYER ONE-PAGER", subtitle_text=None):
    """Draw Charvak wordmark + teal bar at top of page."""
    # Top teal bar
    pdf.set_fill_color(*TEAL)
    pdf.rect(0, 0, W, 3, style="F")

    # Charvak wordmark
    pdf.set_xy(20, 12)
    pdf.set_font("DejaVu", "B", size=14)
    pdf.set_text_color(*TEAL)
    pdf.cell(50, 6, "Charvak", align="L")

    pdf.set_xy(20, 19)
    pdf.set_font("DejaVu", "B", size=6)
    pdf.set_text_color(*INK)
    pdf.cell(50, 4, "I T   C O N S U L T I N G", align="L")

    # Right side label
    pdf.set_xy(120, 14)
    pdf.set_font("DejaVu", "B", size=8)
    pdf.set_text_color(*MUTED)
    pdf.cell(70, 5, title_text, align="R")

    # Divider line
    pdf.set_draw_color(*TEAL)
    pdf.set_line_width(0.4)
    pdf.line(20, 28, W - 20, 28)


def draw_title(pdf, title, subtitle=None, y=36):
    """Draw main title + optional subtitle. Returns Y position after subtitle (or title if no subtitle)."""
    pdf.set_xy(20, y)
    pdf.set_font("DejaVu", "B", size=22)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W - 40, 9, title, align="L")
    title_end_y = pdf.get_y()

    if subtitle:
        subtitle_y = title_end_y + 4  # 4mm gap after title
        pdf.set_xy(20, subtitle_y)
        pdf.set_font("DejaVu", size=11)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(W - 40, 6, subtitle, align="L")
        return pdf.get_y() + 4  # 4mm gap after subtitle
    
    return title_end_y + 4


def draw_stat_row(pdf, stats, y):
    """Draw 3-column stat row. stats = [(label, value), ...]"""
    col_w = (W - 40) / len(stats)
    for i, (value, label) in enumerate(stats):
        x = 20 + i * col_w
        pdf.set_xy(x, y)
        pdf.set_font("DejaVu", "B", size=20)
        pdf.set_text_color(*TEAL)
        pdf.cell(col_w, 10, value, align="C")
        pdf.set_xy(x, y + 10)
        pdf.set_font("DejaVu", size=9)
        pdf.set_text_color(*MUTED)
        pdf.cell(col_w, 5, label, align="C")


def draw_feature_block(pdf, icon_emoji, title, description, y, height=22):
    """Draw a feature block with icon, title, description."""
    # Icon box
    pdf.set_fill_color(*GREEN_LIGHT)
    pdf.set_draw_color(*GREEN_BORDER)
    pdf.set_line_width(0.3)
    pdf.rect(20, y, 12, 12, style="DF")

    # Icon (emoji replaced with DejaVu-compatible Unicode)
    pdf.set_xy(20, y + 2)
    pdf.set_font("DejaVu", "B", size=12)
    pdf.set_text_color(*TEAL)
    pdf.cell(12, 8, _normalize_icon(icon_emoji), align="C")

    # Title
    pdf.set_xy(36, y)
    pdf.set_font("DejaVu", "B", size=11)
    pdf.set_text_color(*INK)
    pdf.cell(W - 56, 6, title, align="L")

    # Description
    pdf.set_xy(36, y + 7)
    pdf.set_font("DejaVu", size=9.5)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(W - 56, 4.5, description, align="L")


def draw_section_divider(pdf, y, color=TEAL):
    """Draw a subtle section divider line."""
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.3)
    pdf.line(20, y, W - 20, y)


def draw_cta_strip(pdf, main_text, url_text, y):
    """Draw bottom CTA strip."""
    pdf.set_fill_color(*TEAL)
    pdf.rect(20, y, W - 40, 14, style="F")

    pdf.set_xy(24, y + 3)
    pdf.set_font("DejaVu", "B", size=10)
    pdf.set_text_color(*WHITE)
    pdf.cell(W - 48, 5, main_text, align="L")

    pdf.set_xy(24, y + 8)
    pdf.set_font("DejaVu", size=8)
    pdf.set_text_color(*WHITE)
    pdf.cell(W - 48, 4, url_text, align="L")


def draw_numbered_step(pdf, num, title, description, y, height=20):
    """Draw a numbered step with title + description."""
    # Number circle
    pdf.set_fill_color(*TEAL)
    pdf.circle(26, y + 5, 4, style="F")
    pdf.set_xy(22, y + 2)
    pdf.set_font("DejaVu", "B", size=10)
    pdf.set_text_color(*WHITE)
    pdf.cell(8, 6, str(num), align="C")

    # Title
    pdf.set_xy(36, y)
    pdf.set_font("DejaVu", "B", size=10.5)
    pdf.set_text_color(*INK)
    pdf.cell(W - 56, 6, title, align="L")

    # Description
    pdf.set_xy(36, y + 7)
    pdf.set_font("DejaVu", size=9)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(W - 56, 4.2, description, align="L")


def draw_pricing_table(pdf, tiers, y):
    """Draw pricing tier row. tiers = [(name, price, features_str), ...]"""
    col_w = (W - 40) / len(tiers)
    for i, (name, price, features) in enumerate(tiers):
        x = 20 + i * col_w
        # Card bg
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(*SOFT)
        pdf.set_line_width(0.3)
        pdf.rect(x + 1, y, col_w - 2, 40, style="DF")

        # Tier name
        pdf.set_xy(x + 2, y + 3)
        pdf.set_font("DejaVu", "B", size=9)
        pdf.set_text_color(*MUTED)
        pdf.cell(col_w - 4, 4, name.upper(), align="C")

        # Price
        pdf.set_xy(x + 2, y + 8)
        pdf.set_font("DejaVu", "B", size=14)
        pdf.set_text_color(*TEAL)
        pdf.cell(col_w - 4, 8, price, align="C")

        # Features
        pdf.set_xy(x + 4, y + 18)
        pdf.set_font("DejaVu", size=8)
        pdf.set_text_color(*INK)
        pdf.multi_cell(col_w - 8, 4, features, align="L")


def draw_page_footer(pdf, page_label, total_pages, year=2026):
    """Custom page footer for one-pagers."""
    pdf.set_y(-15)
    pdf.set_draw_color(*SOFT)
    pdf.set_line_width(0.2)
    pdf.line(20, pdf.get_y() - 2, W - 20, pdf.get_y() - 2)

    pdf.set_font("DejaVu", size=7)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 4, "Charvak IT Consulting Pvt Ltd  ·  https://www.charvakit.com  ·  hr@charvakit.com  ·  +91 799 7871 701", align="L")
    pdf.set_x(-40)
    pdf.cell(20, 4, f"{page_label}  {page_label.split()[1]}/{total_pages}", align="R")