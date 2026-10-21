"""Common brand utilities for Charvak PDF reports."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Brand colors
TEAL = colors.HexColor('#3ba591')
DARK_TEAL = colors.HexColor('#1e7a68')
LIGHT_TEAL = colors.HexColor('#e6f4f0')
CHARCOAL = colors.HexColor('#1a1a1a')
MID_GRAY = colors.HexColor('#6b7280')
LIGHT_GRAY = colors.HexColor('#f3f4f6')
YELLOW = colors.HexColor('#f5b944')
RED = colors.HexColor('#dc3545')
GREEN = colors.HexColor('#22c55e')
CREAM = colors.HexColor('#fafafa')
WHITE = colors.white

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4  # 595 x 842 points


def draw_rounded_rect(c, x, y, w, h, radius=8, fill_color=None, stroke_color=None):
    """Draw a rounded rectangle."""
    if fill_color:
        c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
    c.roundRect(x, y, w, h, radius, fill=1 if fill_color else 0, stroke=1 if stroke_color else 0)


def draw_sample_badge(c, x=None, y=None):
    """Draw a red SAMPLE badge in top-right corner."""
    if x is None:
        x = PAGE_WIDTH - 90
    if y is None:
        y = PAGE_HEIGHT - 45
    c.setFillColor(RED)
    c.roundRect(x, y, 70, 22, 4, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(x + 35, y + 7, 'SAMPLE')


def draw_header_bar(c, title, subtitle=None):
    """Draw a teal header bar with title text."""
    c.setFillColor(TEAL)
    c.rect(0, PAGE_HEIGHT - 60, PAGE_WIDTH, 60, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 18)
    c.drawString(40, PAGE_HEIGHT - 38, title)
    if subtitle:
        c.setFont('Helvetica', 10)
        c.setFillColor(colors.HexColor('#e0f0ec'))
        c.drawString(40, PAGE_HEIGHT - 52, subtitle)


def draw_footer(c, text='Charvak IT Consulting Pvt Ltd  ·  https://www.charvakit.com'):
    """Draw footer at bottom of page."""
    c.setFillColor(MID_GRAY)
    c.setFont('Helvetica', 8)
    c.drawCentredString(PAGE_WIDTH / 2, 20, text)


def draw_page_number(c, num, total):
    """Draw page number bottom-right."""
    c.setFillColor(MID_GRAY)
    c.setFont('Helvetica', 8)
    c.drawRightString(PAGE_WIDTH - 30, 20, f'Page {num} of {total}')


def draw_stat_card(c, x, y, w, h, value, label, sublabel=None, bg_color=TEAL):
    """Draw a stat card with big value + label."""
    draw_rounded_rect(c, x, y, w, h, radius=10, fill_color=bg_color)
    # Value (big)
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 26)
    c.drawCentredString(x + w / 2, y + h - 40, str(value))
    # Label
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(x + w / 2, y + h - 60, label)
    # Sublabel
    if sublabel:
        c.setFont('Helvetica', 8)
        c.setFillColor(colors.HexColor('#e0f0ec'))
        c.drawCentredString(x + w / 2, y + h - 74, sublabel)


def draw_horizontal_bar(c, x, y, w, h, pct, fill_color=TEAL, bg_color=LIGHT_GRAY):
    """Draw a horizontal progress bar."""
    # Background
    c.setFillColor(bg_color)
    c.roundRect(x, y, w, h, h / 2, fill=1, stroke=0)
    # Fill
    fill_w = max(0, min(1, pct)) * w
    if fill_w > 0:
        c.setFillColor(fill_color)
        c.roundRect(x, y, fill_w, h, h / 2, fill=1, stroke=0)


def draw_card(c, x, y, w, h, left_color=None, bg_color=WHITE, border_color=None):
    """Draw a card (optionally with colored left border)."""
    draw_rounded_rect(c, x, y, w, h, radius=8, fill_color=bg_color,
                      stroke_color=border_color or LIGHT_GRAY)
    if left_color:
        c.setFillColor(left_color)
        c.rect(x, y + 4, 4, h - 8, fill=1, stroke=0)


def wrap_text(c, text, x, y, max_width, font='Helvetica', size=10, line_height=None, max_lines=None):
    """Draw text on canvas, wrapping at max_width (in points).
    Returns the number of lines drawn."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    if line_height is None:
        line_height = size + 2

    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        test = (current + ' ' + word) if current else word
        if stringWidth(test, font, size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    if max_lines and len(lines) > max_lines:
        # Truncate with ellipsis
        last = lines[max_lines - 1]
        while stringWidth(last + '...', font, size) > max_width and len(last) > 0:
            last = last[:-1]
        lines = lines[:max_lines - 1] + [last + '...']

    c.setFont(font, size)
    for i, line in enumerate(lines):
        c.drawString(x, y - (i * line_height), line)
    return len(lines)


def check_fit(c, text, x, y, max_width, font='Helvetica', size=10):
    """Return True if text fits in max_width at given font/size."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    return stringWidth(text, font, size) <= max_width